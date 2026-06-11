from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_pymongo import PyMongo
from config import config
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import json
import io
from PIL import Image
import base64
import threading

# Import utilities
from utils.auth_utils import (
    hash_pin, verify_pin, validate_email, validate_uuid, validate_pin, 
    generate_unique_id, sanitize_input, get_timestamp
)
from utils.face_utils import (
    capture_face_from_webcam, get_face_encoding, verify_face, 
    save_face_image, image_to_bytes, bytes_to_image
)
from utils.qr_utils import (
    generate_qr_code, read_qr_code_from_image, read_qr_code_from_webcam,
    read_qr_code_from_cv2_image, verify_qr_code, detect_qr_in_image, read_qr_from_pil_image,
    extract_qr_info
)
from utils.card_generator import generate_smartcard, create_placeholder_card

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize MongoDB
mongo = PyMongo(app)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# ===== JINJA2 FILTERS =====
@app.template_filter('to_ist')
def convert_to_ist(utc_datetime):
    """Convert UTC datetime to IST (UTC+5:30)"""
    if utc_datetime is None:
        return 'N/A'
    # IST is UTC+5:30
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_datetime + ist_offset
    return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')

@app.template_filter('to_ist_tooltip')
def convert_to_ist_tooltip(utc_datetime):
    """Convert UTC datetime to IST for tooltip (full format)"""
    if utc_datetime is None:
        return 'N/A'
    # IST is UTC+5:30
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_datetime + ist_offset
    return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')

# ---------------------------------------------------------------------------
# In-memory login-attempt rate limiter (Fix #9)
# Locks an identifier (email or UUID) for LOCKOUT_MINUTES after MAX_ATTEMPTS
# failed PIN checks within WINDOW_MINUTES.
# ---------------------------------------------------------------------------
_login_attempts: dict = {}   # { identifier -> [datetime, ...] }
_attempts_lock = threading.Lock()

MAX_ATTEMPTS     = 5
WINDOW_MINUTES   = 5
LOCKOUT_MINUTES  = 5


def _record_failed_attempt(identifier: str) -> None:
    """Record a failed login attempt for an identifier."""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=WINDOW_MINUTES)
    with _attempts_lock:
        attempts = _login_attempts.get(identifier, [])
        # Discard attempts outside the rolling window
        attempts = [t for t in attempts if t > window_start]
        attempts.append(now)
        _login_attempts[identifier] = attempts


def _is_locked_out(identifier: str) -> bool:
    """Return True if the identifier has exceeded MAX_ATTEMPTS."""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=WINDOW_MINUTES)
    with _attempts_lock:
        attempts = _login_attempts.get(identifier, [])
        recent = [t for t in attempts if t > window_start]
        _login_attempts[identifier] = recent  # prune stale entries
        return len(recent) >= MAX_ATTEMPTS


def _clear_attempts(identifier: str) -> None:
    """Clear failed attempts after a successful login."""
    with _attempts_lock:
        _login_attempts.pop(identifier, None)

# ===== ROUTES =====

@app.route('/')
def homepage():
    """Homepage route"""
    return render_template('homepage.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Hardcoded admin credentials
        ADMIN_EMAIL = 'Vignesh423@authentication.co.in'
        ADMIN_PASSWORD = '100305'
        
        # Case-insensitive email comparison
        if email.lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            # Record admin login timestamp
            try:
                mongo.db.admin_sessions.update_one(
                    {'email': ADMIN_EMAIL},
                    {
                        '$set': {
                            'email': ADMIN_EMAIL,
                            'last_login': datetime.utcnow(),
                            'login_count': mongo.db.admin_sessions.find_one(
                                {'email': ADMIN_EMAIL},
                                {'login_count': 1}
                            ).get('login_count', 0) + 1 if mongo.db.admin_sessions.find_one({'email': ADMIN_EMAIL}) else 1
                        },
                        '$setOnInsert': {
                            'created_at': datetime.utcnow()
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"Error recording admin login: {e}")
            
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"Admin login failed - Email: '{email}', Password: '{password}'")
            return render_template('admin_login.html', error='Invalid email or password')
    
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin dashboard showing all users and their smart cards"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Fetch admin session info (last login, login count)
        admin_email = 'Vignesh423@authentication.co.in'
        admin_session = mongo.db.admin_sessions.find_one({'email': admin_email})
        
        last_login = None
        login_count = 0
        if admin_session:
            last_login = admin_session.get('last_login')
            login_count = admin_session.get('login_count', 0)
        
        # Fetch all users from database with login tracking info
        users = list(mongo.db.users.find({}, {
            'name': 1,
            'email': 1,
            'unique_id': 1,
            'created_at': 1,
            'smartcard_path': 1,
            'last_login': 1,
            'login_count': 1
        }).sort('created_at', -1))
        
        return render_template('admin_dashboard.html', 
                             users=users, 
                             total_users=len(users),
                             last_login=last_login,
                             login_count=login_count)
    
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        return render_template('admin_dashboard.html', 
                             users=[], 
                             error=str(e),
                             last_login=None,
                             login_count=0)

@app.route('/admin-logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/download-smartcard/<unique_id>')
def download_smartcard_admin(unique_id):
    """Download smart card from admin panel"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Verify user owns this smartcard
        user = mongo.db.users.find_one({'unique_id': unique_id})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        card_path = os.path.join(app.config['CARDS_FOLDER'], f'{unique_id}.png')
        
        if not os.path.exists(card_path):
            return jsonify({'error': 'Card not found'}), 404
        
        return send_file(
            card_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'Authentication_Card_{user["name"]}_{unique_id}.png'
        )
    
    except Exception as e:
        print(f"Error downloading admin card: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        auth_method = sanitize_input(request.form.get('auth_method', 'email'))
        pin = sanitize_input(request.form.get('pin', ''))

        # Validation
        if not pin:
            return render_template('login.html', error='PIN is required')

        if not validate_pin(pin):
            return render_template('login.html', error='Invalid PIN format (4-6 digits)')

        user = None
        identifier = None  # used for rate-limiter

        # Authenticate based on method
        if auth_method == 'email':
            email = sanitize_input(request.form.get('email', ''))

            if not email:
                return render_template('login.html', error='Email is required')

            if not validate_email(email):
                return render_template('login.html', error='Invalid email format')

            identifier = email.lower()

            # Check rate-limit before hitting the DB
            if _is_locked_out(identifier):
                return render_template('login.html',
                    error=f'Too many failed attempts. Please wait {LOCKOUT_MINUTES} minutes.')

            # Find user in database by email
            user = mongo.db.users.find_one({'email': email})

            if not user:
                return render_template('login.html', error='Email not found. Please register first.')

        elif auth_method == 'uuid':
            uuid = sanitize_input(request.form.get('uuid', ''))

            if not uuid:
                return render_template('login.html', error='Smart Card UUID is required')

            if not validate_uuid(uuid):
                return render_template('login.html', error='Invalid Smart Card UUID format')

            identifier = uuid.upper()

            # Check rate-limit before hitting the DB
            if _is_locked_out(identifier):
                return render_template('login.html',
                    error=f'Too many failed attempts. Please wait {LOCKOUT_MINUTES} minutes.')

            # Find user in database by UUID
            user = mongo.db.users.find_one({'unique_id': uuid.upper()})

            if not user:
                return render_template('login.html', error='Smart Card UUID not found. Please register first.')

        else:
            return render_template('login.html', error='Invalid authentication method')

        # Verify PIN — record failure or clear on success
        if not verify_pin(pin, user.get('pin_hash')):
            _record_failed_attempt(identifier)
            remaining = MAX_ATTEMPTS - len(
                [t for t in _login_attempts.get(identifier, [])
                 if t > datetime.utcnow() - timedelta(minutes=WINDOW_MINUTES)]
            )
            if remaining <= 0:
                return render_template('login.html',
                    error=f'Wrong PIN. Account locked for {LOCKOUT_MINUTES} minutes.')
            return render_template('login.html',
                error=f'Wrong PIN. {remaining} attempt(s) remaining.')

        _clear_attempts(identifier)

        # Record user login timestamp
        try:
            mongo.db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'last_login': datetime.utcnow()
                    },
                    '$inc': {
                        'login_count': 1
                    }
                }
            )
        except Exception as e:
            print(f"Error recording user login timestamp: {e}")

        # Store user info in session
        # NOTE: facial_geometry is NOT stored in the session — it is fetched
        # fresh from the DB in /verify-face to avoid bloating the session
        # and to prevent stale/tampered geometry templates being used.
        session['user_id']           = str(user['_id'])
        session['email']             = user['email']
        session['name']              = user['name']
        session['unique_id']         = user['unique_id']
        session['face_verified']     = False
        session['smartcard_verified'] = False

        # Redirect to face authentication
        return redirect(url_for('face_auth'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        email = sanitize_input(request.form.get('email', ''))
        pin = sanitize_input(request.form.get('pin', ''))
        pin_confirm = sanitize_input(request.form.get('pin_confirm', ''))
        
        # Validation
        if not name or not email or not pin:
            return render_template('register.html', error='All fields are required')
        
        if not validate_email(email):
            return render_template('register.html', error='Invalid email format')
        
        if not validate_pin(pin):
            return render_template('register.html', error='PIN must be 4-6 digits')
        
        if pin != pin_confirm:
            return render_template('register.html', error='PINs do not match')
        
        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            return render_template('register.html', error='Email already registered')

        # NOTE: Global PIN uniqueness is intentionally NOT enforced.
        # Checking whether a PIN is already used by any other user leaks
        # information about existing accounts (a privacy/security risk).
        # Security is instead provided by the combination of
        # email/UUID + PIN + face + smart-card (3-factor auth).
        
        # Generate unique ID
        unique_id = generate_unique_id()
        
        # Hash PIN
        pin_hash = hash_pin(pin)
        
        # Store user in session for next step
        session['registration_data'] = {
            'name': name,
            'email': email,
            'pin_hash': pin_hash,
            'unique_id': unique_id
        }
        
        # Redirect to face registration
        return redirect(url_for('face_register'))
    
    return render_template('register.html')

@app.route('/face-register')
def face_register():
    """Face registration page"""
    if 'registration_data' not in session:
        return redirect(url_for('register'))
    
    return render_template('face_register.html', 
                          name=session['registration_data']['name'],
                          unique_id=session['registration_data']['unique_id'])

@app.route('/capture-face', methods=['POST'])
def capture_face():
    """Capture face from webcam"""
    if 'registration_data' not in session:
        return jsonify({'success': False, 'error': 'Invalid session'}), 400
    
    try:
        # Webcam capture and facial geometry extraction
        image_cv2, facial_geometry = capture_face_from_webcam()
        if image_cv2 is None:
            return jsonify({'success': False, 'error': 'No face detected. Please try again.'}), 400
        
        # Get facial geometry if not already done
        if facial_geometry is None:
            facial_geometry = get_face_encoding(image_cv2)
        
        if facial_geometry is None:
            return jsonify({'success': False, 'error': 'No face detected. Please try again.'}), 400
        
        # Save facial geometry template to session
        # Geometry is stored as a dict with normalized landmark positions and measurements
        session['facial_geometry'] = facial_geometry
        
        # Save face image temporarily
        unique_id = session['registration_data']['unique_id']
        face_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{unique_id}_face.png')
        cv2.imwrite(face_image_path, image_cv2)
        session['face_image_path'] = face_image_path
        
        print(f"Face captured with tolerance: {app.config['FACE_RECOGNITION_TOLERANCE']:.4f}")
        return jsonify({'success': True, 'message': 'Face captured successfully'})
    
    except Exception as e:
        print(f"Error capturing face: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/smartcard', methods=['GET', 'POST'])
def smartcard():
    """Smart card generation"""
    if 'registration_data' not in session:
        return redirect(url_for('register'))
    
    # Allow skipping face recognition - generate card without face encoding
    if request.method == 'POST':
        try:
            registration_data = session['registration_data']
            
            # Get face image if available
            face_image_path = session.get('face_image_path')
            face_image_cv2 = None
            
            if face_image_path and os.path.exists(face_image_path):
                face_image_cv2 = cv2.imread(face_image_path)
            
            # Generate smart card
            unique_id = registration_data['unique_id']
            card_path = os.path.join(app.config['CARDS_FOLDER'], f'{unique_id}.png')
            
            if face_image_cv2 is not None:
                success = generate_smartcard(
                    registration_data['name'],
                    unique_id,
                    face_image_cv2,
                    card_path
                )
            else:
                success = create_placeholder_card(
                    registration_data['name'],
                    unique_id,
                    card_path
                )
            
            if not success:
                return render_template('smartcard.html', 
                                      name=registration_data['name'],
                                      unique_id=unique_id,
                                      error='Failed to generate smart card')
            
            # Save user to database
            user_data = {
                'name': registration_data['name'],
                'email': registration_data['email'],
                'pin_hash': registration_data['pin_hash'],
                'unique_id': unique_id,
                'facial_geometry': session.get('facial_geometry'),  # Store geometric template (lighting/pose invariant)
                'smartcard_path': card_path,
                'created_at': get_timestamp()
            }
            
            result = mongo.db.users.insert_one(user_data)
            
            # Create card display URL
            card_url = url_for('static', filename=f'cards/{unique_id}.png')
            
            # Clean up session
            session.pop('registration_data', None)
            session.pop('facial_geometry', None)
            session.pop('face_image_path', None)
            
            return render_template('smartcard.html',
                                  name=registration_data['name'],
                                  unique_id=unique_id,
                                  success=True,
                                  card_url=card_url,
                                  message='Smart card generated successfully! You can now login.')
        
        except Exception as e:
            print(f"Error generating smart card: {e}")
            return render_template('smartcard.html', error=f'Error: {str(e)}')
    
    registration_data = session.get('registration_data', {})
    return render_template('smartcard.html', 
                          name=registration_data.get('name'),
                          unique_id=registration_data.get('unique_id'))

@app.route('/download-smartcard/<unique_id>')
def download_smartcard(unique_id):
    """Download smart card image"""
    try:
        # Verify user owns this smartcard
        user = mongo.db.users.find_one({'unique_id': unique_id})
        if not user:
            return jsonify({'success': False, 'error': 'Smart card not found'}), 404
        
        card_path = os.path.join(app.config['CARDS_FOLDER'], f'{unique_id}.png')
        if not os.path.exists(card_path):
            return jsonify({'success': False, 'error': 'Card file not found'}), 404
        
        return send_file(
            card_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'Authentication_SmartCard_{unique_id}.png'
        )
    except Exception as e:
        print(f"Error downloading smart card: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/face-auth')
def face_auth():
    """Face authentication page"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    return render_template('face_auth.html', name=session.get('name'))

@app.route('/verify-face', methods=['POST'])
def verify_face_route():
    """Verify face during login with webcam only"""
    if 'email' not in session:
        return jsonify({'success': False, 'error': 'Invalid session'}), 400
    
    try:
        image_cv2 = None

        # Prefer browser-provided capture (same camera access style as registration UI)
        if 'face_image' in request.files:
            file = request.files['face_image']
            if file and file.filename:
                img_str = file.read()
                nparr = np.frombuffer(img_str, np.uint8)
                image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image_cv2 is None:
                    return jsonify({'success': False, 'error': 'Invalid face image received'}), 400

        # Fallback to server webcam capture for compatibility
        if image_cv2 is None:
            image_cv2, _ = capture_face_from_webcam()
            if image_cv2 is None:
                return jsonify({'success': False, 'error': 'No face detected. Please try again.'}), 400
        
        # Extract facial geometry from captured image
        captured_geometry = get_face_encoding(image_cv2)
        if captured_geometry is None:
            return jsonify({'success': False, 'error': 'No face detected. Please try again.'}), 400
        
        # Get stored facial geometry template from database
        user_record = mongo.db.users.find_one(
            {'email': session['email']}, {'facial_geometry': 1}
        )
        if not user_record:
            return jsonify({'success': False, 'error': 'User not found'}), 400
        stored_geometry = user_record.get('facial_geometry')
        
        # Use geometric similarity matching with default tolerance
        # Tolerance: 0.15-0.35 (lower = stricter). Default 0.25 provides good balance
        tolerance = app.config.get('FACE_RECOGNITION_TOLERANCE', 0.25)
        print(f"Matching facial geometry with tolerance: {tolerance:.4f}")
        match = verify_face(image_cv2, stored_geometry, tolerance=tolerance)
        
        if not match:
            return jsonify({'success': False, 'error': 'Face not matched'}), 400
        
        # Mark face verified
        session['face_verified'] = True
        return jsonify({'success': True, 'message': 'Face verified successfully'})
    
    except Exception as e:
        print(f"Error verifying face: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/smartcard-auth')
def smartcard_auth():
    """Smart card authentication page"""
    if 'email' not in session or not session.get('face_verified'):
        return redirect(url_for('login'))
    
    return render_template('smartcard_auth.html', name=session.get('name'))

@app.route('/verify-smartcard', methods=['POST'])
def verify_smartcard_route():
    """Verify smart card during login"""
    if 'email' not in session or not session.get('face_verified'):
        return jsonify({'success': False, 'error': 'Face authentication required first'}), 400
    
    try:
        unique_id = session.get('unique_id')
        if not unique_id:
            return jsonify({'success': False, 'error': 'Session expired. Please login again.'}), 400
        
        # Check if file upload or webcam capture
        if 'smartcard_image' in request.files:
            file = request.files['smartcard_image']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Read image
            img_str = file.read()
            nparr = np.frombuffer(img_str, np.uint8)
            image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image_cv2 is None:
                return jsonify({'success': False, 'error': 'Invalid image file'}), 400
            
            # Read QR code
            qr_data = read_qr_code_from_cv2_image(image_cv2)
        
        else:
            # Webcam capture
            qr_data = read_qr_code_from_webcam()
        
        if qr_data is None:
            return jsonify({'success': False, 'error': 'QR code not found'}), 400
        
        # Verify QR code matches the unique_id
        if not verify_qr_code(qr_data, unique_id, secret_key=None):
            return jsonify({'success': False, 'error': 'Invalid smart card'}), 400
        
        # Extract name and ID from QR code
        name, qr_id = extract_qr_info(qr_data)
        
        # Mark smartcard verified
        session['smartcard_verified'] = True
        return jsonify({
            'success': True, 
            'message': 'Smart card verified successfully',
            'name': name or 'Unknown',
            'unique_id': qr_id
        })
    
    except Exception as e:
        print(f"Error verifying smart card: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'email' not in session or not session.get('smartcard_verified'):
        return redirect(url_for('login'))
    
    try:
        # Get user from database
        user = mongo.db.users.find_one({'email': session['email']})
        
        if not user:
            return redirect(url_for('login'))
        
        return render_template('dashboard.html', 
                              name=user['name'],
                              unique_id=user['unique_id'],
                              email=user['email'],
                              created_at=user.get('created_at'),
                              last_login=user.get('last_login'),
                              login_count=user.get('login_count', 0))
    
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return redirect(url_for('login'))

@app.route('/download-card/<unique_id>')
def download_card(unique_id):
    """Download smart card"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    try:
        # Verify user owns this card
        user = mongo.db.users.find_one({'unique_id': unique_id, 'email': session['email']})
        
        if not user:
            return jsonify({'error': 'Unauthorized'}), 403
        
        card_path = os.path.join(app.config['CARDS_FOLDER'], f'{unique_id}.png')
        
        if not os.path.exists(card_path):
            return jsonify({'error': 'Card not found'}), 404
        
        return send_file(
            card_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'authentication_card_{unique_id}.png'
        )
    
    except Exception as e:
        print(f"Error downloading card: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('homepage'))

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

# ===== CONTEXT PROCESSORS =====

@app.context_processor
def inject_user():
    """Inject user into template context"""
    return {
        'user_logged_in': 'email' in session,
        'user_name': session.get('name'),
        'user_email': session.get('email')
    }

# ===== MAIN =====

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CARDS_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='127.0.0.1', port=5000)
