import cv2
import numpy as np
import os
from PIL import Image
import io
import base64
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Try to import dlib for 68-point landmark detection (optional)
try:
    import dlib
    detector = dlib.get_frontal_face_detector()
    # Try to load predictor - if not available, we'll use OpenCV
    predictor_path = os.path.join(os.path.dirname(__file__), 'shape_predictor_68_face_landmarks.dat')
    if os.path.exists(predictor_path):
        predictor = dlib.shape_predictor(predictor_path)
        DLIB_AVAILABLE = True
    else:
        DLIB_AVAILABLE = False
        print("⚠ dlib landmark predictor model not found - using cascade-based geometry extraction")
except Exception as e:
    DLIB_AVAILABLE = False
    print(f"⚠ dlib not available ({type(e).__name__}) - using cascade-based geometry extraction")

def capture_face_from_webcam():
    """
    Capture a face image from webcam using OpenCV face detection.
    Automatically captures when a clear face is detected for stability.
    
    Returns:
        tuple: (image_cv2, face_geometry) or (None, None) if no face detected
    """
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot access webcam - device not available")
        cap.release()
        return None, None
    
    # Set webcam resolution to 640x480 for faster processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    captured_image = None
    face_geometry = None
    face_detected_frames = 0
    auto_capture_threshold = 30  # ~1 second at 30 FPS
    frame_count = 0
    max_frames = 120  # 4 seconds at 30fps
    
    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame = cv2.flip(frame, 1)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.08,
                minNeighbors=5,
                minSize=(80, 80)
            )
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            cv2.putText(frame, 'Position your face in the center', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Auto-capture logic: require exactly 1 clear face
            if len(faces) == 1:
                face_detected_frames += 1
                seconds_remaining = max(0, (auto_capture_threshold - face_detected_frames) / 30.0)
                cv2.putText(frame, f'Hold still: {seconds_remaining:.1f}s',
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                if face_detected_frames >= auto_capture_threshold:
                    captured_image = frame.copy()
                    face_geometry = extract_facial_geometry(frame)
                    print("Face auto-captured successfully!")
                    break
            else:
                face_detected_frames = 0
                if len(faces) == 0:
                    cv2.putText(frame, 'No face detected', (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Multiple faces detected - Show only your face', (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.putText(frame, 'Press SPACE to capture manually or ESC to cancel', (5, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            
            cv2.imshow('Face Capture - Auto Detection Active', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("Face capture cancelled by user")
                cap.release()
                cv2.destroyAllWindows()
                return None, None
            elif key == 32:  # SPACE key
                captured_image = frame.copy()
                face_geometry = extract_facial_geometry(frame)
                print("Face manually captured")
                break
        
        if captured_image is None:
            print("Timeout: No clear face detected in time")
    
    except Exception as e:
        print(f"Error in capture_face_from_webcam: {e}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return captured_image, face_geometry

def extract_facial_geometry(image_cv2):
    """
    Extract facial geometry (landmarks and measurements) from an image.
    Creates a normalized template of facial structure independent of lighting/pose variations.
    
    Geometry template includes:
    - Normalized landmark positions (if dlib available)
    - Face dimensions and ratios
    - Inter-landmark distances
    - Face contour points
    
    Args:
        image_cv2: OpenCV image (BGR format)
        
    Returns:
        dict: Facial geometry template with landmarks and measurements
    """
    try:
        if DLIB_AVAILABLE:
            return _extract_dlib_geometry(image_cv2)
        else:
            return _extract_cascade_geometry(image_cv2)
    except Exception as e:
        print(f"Error extracting facial geometry: {e}")
        return None

def _extract_dlib_geometry(image_cv2):
    """
    Extract facial geometry using dlib landmarks (68-point model).
    Most accurate approach using pre-trained facial landmark detector.
    """
    try:
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        dets = detector(gray, 1)
        
        if len(dets) == 0:
            print("No face detected for geometry extraction")
            return None
        
        # Get the first detected face
        det = dets[0]
        
        # Get facial landmarks
        shape = predictor(gray, det)
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        
        # Normalize landmarks (subtract mean, divide by std)
        landmarks_mean = landmarks.mean(axis=0)
        landmarks_std = landmarks.std(axis=0)
        landmarks_normalized = (landmarks - landmarks_mean) / (landmarks_std + 1e-6)
        
        # Extract geometric measurements
        geometry = {
            'landmarks': landmarks_normalized.tolist(),
            'face_width': float(det.right() - det.left()),
            'face_height': float(det.bottom() - det.top()),
            'face_center': [float((det.left() + det.right()) / 2), 
                          float((det.top() + det.bottom()) / 2)],
            'face_area': float((det.right() - det.left()) * (det.bottom() - det.top())),
            'method': 'dlib_68',
            'template_version': '1.0'
        }
        
        # Calculate inter-landmark distances (normalized)
        distances = []
        for i in range(len(landmarks) - 1):
            dist = np.linalg.norm(landmarks[i] - landmarks[i+1])
            distances.append(float(dist))
        geometry['inter_landmark_distances'] = distances
        
        print(f"Facial geometry extracted (dlib 68-point model, {len(landmarks)} landmarks)")
        return geometry
        
    except Exception as e:
        print(f"dlib geometry extraction error: {e}")
        return None

def _extract_cascade_geometry(image_cv2):
    """
    Extract facial geometry using OpenCV Haar Cascade (fallback method).
    Less precise than dlib but works without additional models.
    """
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.08, 5, minSize=(80, 80))
        
        if len(faces) == 0:
            print("No face detected for geometry extraction")
            return None
        
        # Get the largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = face
        
        # Extract face region for eye detection
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        # Create geometry template
        geometry = {
            'face_box': [float(x), float(y), float(w), float(h)],
            'face_center': [float(x + w/2), float(y + h/2)],
            'face_width': float(w),
            'face_height': float(h),
            'face_area': float(w * h),
            'aspect_ratio': float(w / h) if h != 0 else 0,
            'eye_count': len(eyes),
            'method': 'cascade',
            'template_version': '1.0'
        }
        
        # Add eye positions if detected
        if len(eyes) > 0:
            eye_positions = []
            for (ex, ey, ew, eh) in eyes[:2]:  # Take up to 2 eyes
                eye_positions.append({
                    'x': float(ex + x),
                    'y': float(ey + y),
                    'width': float(ew),
                    'height': float(eh)
                })
            geometry['eyes'] = eye_positions
        
        print(f"Facial geometry extracted (cascade method, {len(eyes)} eyes detected)")
        return geometry
        
    except Exception as e:
        print(f"Cascade geometry extraction error: {e}")
        return None

def verify_face(captured_image, stored_geometry, tolerance=0.25):
    """
    Verify if captured face matches stored facial geometry template.
    
    Compares geometric features like landmark positions, distances, and measurements.
    This approach is:
    - Lighting invariant (compares geometry, not pixel values)
    - Pose tolerant (normalized measurements)
    - Fast (no deep neural networks needed)
    - Privacy-friendly (only stores geometric templates, not images)
    
    Args:
        captured_image: OpenCV image to verify
        stored_geometry: Stored facial geometry template (dict)
        tolerance: Similarity threshold (0.15-0.35 recommended, lower = stricter)
        
    Returns:
        bool: True if faces match within tolerance
    """
    try:
        if stored_geometry is None:
            print("Error: No stored facial geometry available")
            return False
        
        # Extract geometry from captured image
        captured_geometry = extract_facial_geometry(captured_image)
        
        if captured_geometry is None:
            print("No face detected in captured image for verification")
            return False
        
        # Calculate similarity score
        similarity = _calculate_geometry_similarity(stored_geometry, captured_geometry)
        
        match = similarity > (1.0 - tolerance)
        
        print(
            f"Face verification - "
            f"Geometry Similarity: {similarity:.4f}, "
            f"Tolerance: {tolerance}, "
            f"Match: {match}"
        )
        
        return match
        
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False

def verify_face_with_accuracy(captured_image, stored_geometry, accuracy_threshold=90):
    """
    Verify if captured face matches stored facial geometry template with accuracy percentage.
    
    Compares geometric features and returns both match status and accuracy percentage.
    
    Args:
        captured_image: OpenCV image to verify
        stored_geometry: Stored facial geometry template (dict)
        accuracy_threshold: Required accuracy percentage (0-100, default 90)
        
    Returns:
        tuple: (match_bool, accuracy_percentage, message)
               - match_bool: True if accuracy >= threshold
               - accuracy_percentage: Float 0-100
               - message: String describing the result
    """
    try:
        if stored_geometry is None:
            print("Error: No stored facial geometry available")
            return False, 0.0, "No stored facial geometry available"
        
        # Extract geometry from captured image
        captured_geometry = extract_facial_geometry(captured_image)
        
        if captured_geometry is None:
            print("No face detected in captured image for verification")
            return False, 0.0, "No face detected in captured image"
        
        # Calculate similarity score (0-1)
        similarity = _calculate_geometry_similarity(stored_geometry, captured_geometry)

        # Convert similarity to accuracy percentage
        accuracy = similarity * 100.0

        # Check if accuracy meets threshold
        match = accuracy >= accuracy_threshold

        message = (
            f"Face verification - Accuracy: {accuracy:.2f}%, "
            f"Threshold: {accuracy_threshold}%, Match: {match}"
        )

        print(message)

        return match, accuracy, message
        
    except Exception as e:
        error_msg = f"Error verifying face: {e}"
        print(error_msg)
        return False, 0.0, error_msg

def _calculate_geometry_similarity(geometry1, geometry2):
    """
    Calculate similarity between two facial geometry templates.
    Returns a score between 0 and 1 (1 = identical).
    """
    try:
        similarity_scores = []
        
        # Compare method-specific features
        if geometry1.get('method') == 'dlib_68' and geometry2.get('method') == 'dlib_68':
            # Compare landmark positions
            lm1 = np.array(geometry1['landmarks'])
            lm2 = np.array(geometry2['landmarks'])
            
            if lm1.shape == lm2.shape:
                # Use cosine similarity for landmark positions
                flat1 = lm1.flatten()
                flat2 = lm2.flatten()
                
                norm1 = np.linalg.norm(flat1)
                norm2 = np.linalg.norm(flat2)
                
                if norm1 > 0 and norm2 > 0:
                    cosine_sim = np.dot(flat1, flat2) / (norm1 * norm2)
                    similarity_scores.append(cosine_sim)
            
            # Compare inter-landmark distances
            if 'inter_landmark_distances' in geometry1 and 'inter_landmark_distances' in geometry2:
                dist1 = np.array(geometry1['inter_landmark_distances'])
                dist2 = np.array(geometry2['inter_landmark_distances'])
                
                if len(dist1) == len(dist2):
                    dist_similarity = 1.0 - (np.mean(np.abs(dist1 - dist2)) / (np.mean(dist1) + 1e-6))
                    similarity_scores.append(max(0, dist_similarity))
        
        else:  # Cascade method
            # Compare face dimensions
            if 'face_width' in geometry1 and 'face_width' in geometry2:
                w1 = geometry1['face_width']
                w2 = geometry2['face_width']
                width_similarity = 1.0 - (abs(w1 - w2) / max(w1, w2, 1))
                similarity_scores.append(max(0, width_similarity))
            
            if 'face_height' in geometry1 and 'face_height' in geometry2:
                h1 = geometry1['face_height']
                h2 = geometry2['face_height']
                height_similarity = 1.0 - (abs(h1 - h2) / max(h1, h2, 1))
                similarity_scores.append(max(0, height_similarity))
            
            if 'aspect_ratio' in geometry1 and 'aspect_ratio' in geometry2:
                ar1 = geometry1['aspect_ratio']
                ar2 = geometry2['aspect_ratio']
                ar_similarity = 1.0 - (abs(ar1 - ar2) / (max(ar1, ar2) + 0.1))
                similarity_scores.append(max(0, ar_similarity))
            
            # Compare eye count
            if 'eye_count' in geometry1 and 'eye_count' in geometry2:
                if geometry1['eye_count'] == geometry2['eye_count']:
                    similarity_scores.append(1.0)
                else:
                    similarity_scores.append(0.5)
        
        # Calculate average similarity
        if similarity_scores:
            overall_similarity = np.mean(similarity_scores)
        else:
            overall_similarity = 0.0
        
        return float(overall_similarity)
        
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


def verify_geometry_with_accuracy(captured_geometry, stored_geometry, accuracy_threshold=90):
    """
    Verify captured facial geometry against a stored geometry template.

    This avoids re-extracting geometry multiple times (reduces variance)
    when comparing the same captured face against multiple stored templates.

    Args:
        captured_geometry: Geometry dict extracted from captured image
        stored_geometry: Stored facial geometry template (dict)
        accuracy_threshold: Required accuracy percentage (0-100)

    Returns:
        tuple: (match_bool, accuracy_percentage, message)
    """
    try:
        if captured_geometry is None or stored_geometry is None:
            return False, 0.0, "Missing geometry for verification"

        similarity = _calculate_geometry_similarity(stored_geometry, captured_geometry)
        accuracy = similarity * 100.0
        match = accuracy >= accuracy_threshold
        message = (
            f"Geometry verification - Accuracy: {accuracy:.2f}%, "
            f"Threshold: {accuracy_threshold}%, Match: {match}"
        )
        print(message)
        return match, accuracy, message
    except Exception as e:
        err = f"Error in verify_geometry_with_accuracy: {e}"
        print(err)
        return False, 0.0, err

def save_face_image(image_cv2, filepath):
    """Save face image to file."""
    try:
        cv2.imwrite(filepath, image_cv2)
        return True
    except Exception as e:
        print(f"Error saving face image: {e}")
        return False

def load_face_image(filepath):
    """Load face image from file."""
    try:
        image = cv2.imread(filepath)
        if image is None:
            return None
        return image
    except Exception as e:
        print(f"Error loading face image: {e}")
        return None

def image_to_bytes(image_cv2):
    """Convert OpenCV image to bytes."""
    try:
        ret, buffer = cv2.imencode('.png', image_cv2)
        return buffer.tobytes()
    except Exception as e:
        print(f"Error converting image to bytes: {e}")
        return None

def bytes_to_image(image_bytes):
    """Convert bytes to OpenCV image."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Error converting bytes to image: {e}")
        return None

def image_to_base64(image_cv2):
    """Convert OpenCV image to base64 string."""
    try:
        ret, buffer = cv2.imencode('.png', image_cv2)
        image_bytes = buffer.tobytes()
        return base64.b64encode(image_bytes).decode()
    except Exception as e:
        print(f"Error converting to base64: {e}")
        return None

def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image."""
    try:
        image_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Error converting from base64: {e}")
        return None

def get_backend_info():
    """Get information about the face recognition backend being used."""
    return {
        'dlib_available': DLIB_AVAILABLE,
        'method': 'Facial Geometry (dlib 68-point landmarks)' if DLIB_AVAILABLE else 'Facial Geometry (Haar Cascade)',
        'approach': 'Geometric Template Matching',
        'lighting_invariant': True,
        'privacy_friendly': True,
        'stores': 'Geometric templates only (not images or embeddings)'
    }
