import cv2
import numpy as np
import os
from PIL import Image
import io
import base64
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Use OpenCV's built-in ORB (Oriented FAST and Rotated BRIEF) for feature matching
# This provides robust, lightweight face recognition without external ML frameworks

def capture_face_from_webcam():
    """
    Capture a face image from webcam using OpenCV face detection.
    Automatically captures when a clear face is detected for stability.
    
    Returns:
        tuple: (image_cv2, face_encoding) or (None, None) if no face detected
    """
    cap = cv2.VideoCapture(0)
    
    # Set timeout for webcam opening
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
    face_encoding = None
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
            
            # Flip for selfie view
            frame = cv2.flip(frame, 1)
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces with tuned parameters for better accuracy
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.08,
                minNeighbors=5,
                minSize=(80, 80)
            )
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(frame, 'Position your face in the center', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Auto-capture logic: require exactly 1 clear face
            if len(faces) == 1:
                face_detected_frames += 1
                seconds_remaining = max(0, (auto_capture_threshold - face_detected_frames) / 30.0)
                cv2.putText(frame, f'Hold still: {seconds_remaining:.1f}s',
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                if face_detected_frames >= auto_capture_threshold:
                    # Auto-capture the face
                    captured_image = frame.copy()
                    face_encoding = get_face_encoding(frame)
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
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("Face capture cancelled by user")
                cap.release()
                cv2.destroyAllWindows()
                return None, None
            elif key == 32:  # SPACE key for manual capture
                captured_image = frame.copy()
                face_encoding = get_face_encoding(frame)
                print("Face manually captured")
                break
        
        if captured_image is None:
            print("Timeout: No clear face detected in time")
    
    except Exception as e:
        print(f"Error in capture_face_from_webcam: {e}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return captured_image, face_encoding

def get_face_encoding(image_cv2):
    """
    Extract face encoding using OpenCV feature descriptors (ORB + region analysis).
    Creates a robust embedding using keypoint detection and histogram analysis.
    
    Args:
        image_cv2: OpenCV image (BGR format)
        
    Returns:
        list: Face encoding vector or None if no face detected
    """
    try:
        # Detect face using Haar Cascade
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with optimized parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=5,
            minSize=(80, 80)
        )
        
        if len(faces) == 0:
            print("No face detected for encoding")
            return None
        
        # Extract the largest/most prominent detected face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+h, x:x+w]
        
        # Standardize face region for consistent encoding
        face_roi_resized = cv2.resize(face_roi, (128, 128))
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for lighting invariance
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face_roi_enhanced = clahe.apply(face_roi_resized)
        
        # Feature 1: ORB keypoints and descriptors for robust matching
        orb = cv2.ORB_create(nfeatures=500, scaleFactor=1.2, nlevels=8)
        kp, des = orb.detectAndCompute(face_roi_enhanced, None)
        
        # Flatten ORB descriptors if available (each is 32 bytes = 32 * 8 bits)
        if des is not None and len(des) > 0:
            # Average the descriptors for a compact encoding
            orb_encoding = np.mean(des, axis=0).flatten()
        else:
            orb_encoding = np.zeros(32, dtype=np.uint8)
        
        # Feature 2: Histogram of equalized face (lighting invariant)
        hist_encoding = cv2.calcHist([face_roi_enhanced], [0], None, [64], [0, 256])
        hist_encoding = cv2.normalize(hist_encoding, hist_encoding).flatten()
        
        # Feature 3: Texture features using Canny edge detection
        edges = cv2.Canny(face_roi_enhanced, 50, 150)
        edge_hist = cv2.calcHist([edges], [0], None, [32], [0, 256])
        edge_hist = cv2.normalize(edge_hist, edge_hist).flatten()
        
        # Feature 4: Regional statistics (mean, std, variance by quadrants)
        h_q, w_q = face_roi_enhanced.shape[0]//2, face_roi_enhanced.shape[1]//2
        quadrants = [
            face_roi_enhanced[0:h_q, 0:w_q],
            face_roi_enhanced[0:h_q, w_q:],
            face_roi_enhanced[h_q:, 0:w_q],
            face_roi_enhanced[h_q:, w_q:]
        ]
        quad_stats = []
        for quad in quadrants:
            quad_stats.extend([np.mean(quad), np.std(quad)])
        quad_stats = np.array(quad_stats, dtype=np.float32)
        
        # Combine all features into unified encoding
        encoding = np.concatenate([
            orb_encoding.astype(np.float32) / 255.0,  # Normalize ORB to 0-1
            hist_encoding,                             # Histogram
            edge_hist,                                 # Edge histogram
            quad_stats                                 # Regional statistics
        ])
        
        # Normalize the final encoding
        encoding = encoding / (np.linalg.norm(encoding) + 1e-10)
        
        print(f"Face encoding generated successfully (dimension: {len(encoding)})")
        return encoding.tolist()
        
    except Exception as e:
        print(f"Error getting face encoding: {e}")
        return None

def verify_face(captured_image, stored_encoding, tolerance=0.35):
    """
    Verify if captured face matches stored encoding using feature matching.
    Compares ORB keypoint descriptors and histogram patterns for robust matching.
    
    Args:
        captured_image: OpenCV image to verify
        stored_encoding: Stored face encoding (list/array of features)
        tolerance: Distance threshold (0.25-0.45 recommended, lower = stricter)
                   Euclidean distance in normalized feature space
        
    Returns:
        bool: True if faces match, False otherwise
    """
    try:
        if stored_encoding is None:
            print("Error: No stored face encoding available")
            return False
        
        # Get captured face encoding using same method as storage
        captured_encoding = get_face_encoding(captured_image)
        
        if captured_encoding is None:
            print("No face detected in captured image for verification")
            return False
        
        # Convert to numpy arrays for distance calculation
        stored_array = np.array(stored_encoding, dtype=np.float32)
        captured_array = np.array(captured_encoding, dtype=np.float32)
        
        # Ensure arrays are same length by padding if necessary
        max_len = max(len(stored_array), len(captured_array))
        if len(stored_array) < max_len:
            stored_array = np.pad(stored_array, (0, max_len - len(stored_array)), mode='constant')
        if len(captured_array) < max_len:
            captured_array = np.pad(captured_array, (0, max_len - len(captured_array)), mode='constant')
        
        # Normalize both vectors to unit length for meaningful distance calculation
        stored_norm = np.linalg.norm(stored_array)
        captured_norm = np.linalg.norm(captured_array)
        
        if stored_norm < 1e-10 or captured_norm < 1e-10:
            print("Error: Invalid face encoding (zero norm)")
            return False
        
        stored_normalized = stored_array / stored_norm
        captured_normalized = captured_array / captured_norm
        
        # Calculate Euclidean distance between normalized feature vectors
        # Distance 0 = identical faces, ~2.0 = completely different
        distance = np.linalg.norm(stored_normalized - captured_normalized)
        
        # Also calculate cosine similarity for additional confidence
        cosine_similarity = float(np.dot(stored_normalized, captured_normalized))
        
        # Match if distance is below threshold AND cosine similarity is high
        distance_match = distance < tolerance
        similarity_match = cosine_similarity > 0.65  # Require decent similarity
        
        match = distance_match and similarity_match
        
        print(
            f"Face verification - "
            f"Euclidean Distance: {distance:.4f}, "
            f"Cosine Similarity: {cosine_similarity:.4f}, "
            f"Tolerance: {tolerance}, "
            f"Distance OK: {distance_match}, "
            f"Similarity OK: {similarity_match}, "
            f"Match: {match}"
        )
        
        return match
        
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False

def save_face_image(image_cv2, filepath):
    """
    Save face image to file.
    
    Args:
        image_cv2: OpenCV image
        filepath: Path to save image
        
    Returns:
        bool: True if saved successfully
    """
    try:
        cv2.imwrite(filepath, image_cv2)
        return True
    except Exception as e:
        print(f"Error saving face image: {e}")
        return False

def load_face_image(filepath):
    """
    Load face image from file.
    
    Args:
        filepath: Path to image file
        
    Returns:
        OpenCV image or None
    """
    try:
        image = cv2.imread(filepath)
        if image is None:
            return None
        return image
    except Exception as e:
        print(f"Error loading face image: {e}")
        return None

def image_to_bytes(image_cv2):
    """
    Convert OpenCV image to bytes.
    
    Args:
        image_cv2: OpenCV image
        
    Returns:
        bytes: Image as PNG bytes
    """
    try:
        ret, buffer = cv2.imencode('.png', image_cv2)
        return buffer.tobytes()
    except Exception as e:
        print(f"Error converting image to bytes: {e}")
        return None

def bytes_to_image(image_bytes):
    """
    Convert bytes to OpenCV image.
    
    Args:
        image_bytes: Image as bytes
        
    Returns:
        OpenCV image
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Error converting bytes to image: {e}")
        return None

def image_to_base64(image_cv2):
    """
    Convert OpenCV image to base64 string.
    
    Args:
        image_cv2: OpenCV image
        
    Returns:
        str: Base64 encoded image
    """
    try:
        ret, buffer = cv2.imencode('.png', image_cv2)
        image_bytes = buffer.tobytes()
        return base64.b64encode(image_bytes).decode()
    except Exception as e:
        print(f"Error converting to base64: {e}")
        return None

def base64_to_image(base64_string):
    """
    Convert base64 string to OpenCV image.
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        OpenCV image or None
    """
    try:
        image_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Error converting from base64: {e}")
        return None
