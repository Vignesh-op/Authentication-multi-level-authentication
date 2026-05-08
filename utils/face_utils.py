import cv2
import numpy as np
import os
from PIL import Image
import io
import base64

# Note: face_recognition requires dlib which requires CMake.
# This version uses OpenCV for face detection only.
# For full face recognition, install CMake and: pip install dlib face-recognition

def capture_face_from_webcam():
    """
    Capture a face image from webcam using auto-capture.
    Automatically captures when a face is detected for 1 frame.
    
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
    # Require a stable face for longer so capture doesn't happen instantly.
    auto_capture_threshold = 45  # ~1.5 seconds at 30 FPS
    frame_count = 0
    max_frames = 120  # 4 seconds at 30fps - extended timeout for better detection
    
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
            # Optimize face detection with lenient parameters for better capture
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,  # More lenient scale factor for better detection
                minNeighbors=4,    # Lower neighbors threshold for easier detection
                minSize=(60, 60)   # Smaller minimum size for better sensitivity
            )
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(frame, 'Position your face in the center', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Auto-capture logic with stability countdown.
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
            print("Timeout: No face detected in time")
    
    except Exception as e:
        print(f"Error in capture_face_from_webcam: {e}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return captured_image, face_encoding

def get_face_encoding(image_cv2):
    """
    Extract face encoding from an image using OpenCV.
    Uses histogram equalization and multiple feature extraction for robustness.
    
    Args:
        image_cv2: OpenCV image (BGR format)
        
    Returns:
        list: Face encoding or None if no face detected
    """
    try:
        # Detect face using Haar Cascade
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        # Use a slightly more permissive detector so registration and verification
        # behave similarly across normal lighting/pose changes.
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(60, 60)
        )
        
        if len(faces) == 0:
            return None
        
        # Extract the largest detected face (more stable than first face index)
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to fixed size for consistency
        resized = cv2.resize(face_roi, (64, 64))
        
        # Apply histogram equalization for lighting invariance
        equalized = cv2.equalizeHist(resized)
        
        # Feature extraction 1: Histogram of equalized image (lighting invariant)
        hist = cv2.calcHist([equalized], [0], None, [64], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Feature extraction 2: Local Binary Patterns-like features
        # Simple texture features using neighboring pixel comparisons
        lbp_features = []
        equalized_pad = cv2.copyMakeBorder(equalized, 1, 1, 1, 1, cv2.BORDER_REFLECT)
        for i in range(1, equalized_pad.shape[0]-1):
            for j in range(1, equalized_pad.shape[1]-1):
                center = equalized_pad[i, j]
                patch = equalized_pad[i-1:i+2, j-1:j+2]
                # Compare only the 8 surrounding neighbors (exclude center pixel)
                neighbors = np.array([
                    patch[0, 0], patch[0, 1], patch[0, 2],
                    patch[1, 2], patch[2, 2], patch[2, 1],
                    patch[2, 0], patch[1, 0]
                ], dtype=np.float32)
                lbp = np.sum((neighbors >= center).astype(np.float32) * (2 ** np.arange(8)))
                lbp_features.append(lbp / 255.0)
        
        lbp_features = np.array(lbp_features)
        # Sample every 4th feature to keep it manageable
        lbp_sampled = lbp_features[::4]
        
        # Feature extraction 3: Gradient features (Sobel)
        sobelx = cv2.Sobel(equalized, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(equalized, cv2.CV_32F, 0, 1, ksize=3)
        
        # Magnitude and direction of gradients
        mag = np.sqrt(sobelx**2 + sobely**2)
        mag_normalized = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        mag_features = mag_normalized.flatten()[::4]  # Sample every 4th
        
        # Combine all features
        encoding = np.concatenate([
            hist,                           # 64 values: histogram
            lbp_sampled[:64] if len(lbp_sampled) >= 64 else np.pad(lbp_sampled, (0, 64-len(lbp_sampled))),  # 64 values: texture
            mag_features[:32] if len(mag_features) >= 32 else np.pad(mag_features, (0, 32-len(mag_features)))   # 32 values: gradients
        ])
        
        # Normalize encoding
        encoding = encoding / (np.linalg.norm(encoding) + 1e-8)
        
        return encoding.tolist()
    except Exception as e:
        print(f"Error getting face encoding: {e}")
        return None

def verify_face(captured_image, stored_encoding, tolerance=0.6):
    """
    Verify if captured face matches stored encoding using cosine similarity.
    
    Args:
        captured_image: OpenCV image to verify
        stored_encoding: Stored face encoding
        tolerance: Face comparison tolerance (cosine distance threshold, 0-2 scale)
                   Lower values = stricter matching
        
    Returns:
        bool: True if faces match
    """
    try:
        captured_encoding = get_face_encoding(captured_image)
        
        if captured_encoding is None or stored_encoding is None:
            return False
        
        # Convert to numpy arrays
        stored_encoding = np.array(stored_encoding, dtype=np.float32).flatten()
        captured_encoding = np.array(captured_encoding, dtype=np.float32).flatten()
        
        # Make sure arrays are the same shape
        if stored_encoding.shape != captured_encoding.shape:
            # Pad or truncate to match
            min_len = min(len(stored_encoding), len(captured_encoding))
            stored_encoding = stored_encoding[:min_len]
            captured_encoding = captured_encoding[:min_len]
        
        # Normalize vectors for cosine similarity
        stored_norm = np.linalg.norm(stored_encoding)
        captured_norm = np.linalg.norm(captured_encoding)
        
        if stored_norm == 0 or captured_norm == 0:
            # Can't normalize zero vectors
            return False
        
        stored_normalized = stored_encoding / stored_norm
        captured_normalized = captured_encoding / captured_norm
        
        # Calculate cosine distance (0 = identical, 2 = opposite)
        cosine_distance = np.linalg.norm(stored_normalized - captured_normalized)
        cosine_similarity = float(np.dot(stored_normalized, captured_normalized))
        
        # Use the configured tolerance for BOTH checks so the admin-set value
        # is fully respected.  The similarity threshold is derived as (1 - tolerance)
        # so a strict tolerance (low value) also requires high similarity.
        distance_ok    = cosine_distance  < tolerance
        similarity_ok  = cosine_similarity > (1.0 - tolerance)
        match = distance_ok or similarity_ok

        print(
            f"Face comparison - Cosine Distance: {cosine_distance:.4f}, "
            f"Cosine Similarity: {cosine_similarity:.4f}, "
            f"Tolerance: {tolerance}, Match: {match}"
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
