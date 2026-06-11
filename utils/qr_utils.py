import qrcode
from pyzbar.pyzbar import decode
import cv2
import numpy as np
from PIL import Image
import os
import hmac
import hashlib


def _decode_qr_data(image_cv2):
    """Decode QR data from an OpenCV image with multiple fallbacks."""
    if image_cv2 is None:
        return None

    # Primary: pyzbar
    try:
        decoded_objects = decode(image_cv2)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8').strip()
    except Exception as e:
        print(f"pyzbar decode warning: {e}")

    # Fallback: OpenCV QRCodeDetector
    try:
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(image_cv2)
        if data:
            return data.strip()
    except Exception as e:
        print(f"OpenCV QR decode warning: {e}")

    return None

def _sign_qr_payload(unique_id, secret_key):
    """
    Create an HMAC-SHA256 signature of the unique_id.

    Args:
        unique_id (str): The user's unique ID.
        secret_key (str): The application secret key.

    Returns:
        str: Hex-encoded HMAC digest.
    """
    key = secret_key.encode('utf-8') if isinstance(secret_key, str) else secret_key
    uid = unique_id.upper().encode('utf-8')
    return hmac.new(key, uid, hashlib.sha256).hexdigest()


def generate_qr_code(data, filepath, secret_key=None):
    """
    Generate QR code image.

    When *secret_key* is supplied the QR payload is HMAC-signed:
        ``{unique_id}:{hmac_hex}``
    This prevents forging a valid card by simply printing someone
    else's UUID.

    Args:
        data (str): Data to encode in QR code (the user's unique_id).
        filepath (str): Path to save QR code image.
        secret_key (str | None): App secret key for HMAC signing.

    Returns:
        bool: True if generated successfully
    """
    try:
        payload = data
        if secret_key:
            sig = _sign_qr_payload(data, secret_key)
            payload = f"{data.upper()}:{sig}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        return True
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return False

def read_qr_code_from_image(image_path):
    """
    Read QR code from image file.
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        str: Decoded QR code data or None
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        decoded_objects = decode(image)
        
        if len(decoded_objects) == 0:
            return None
        
        # Get first QR code
        qr_data = decoded_objects[0].data.decode('utf-8')
        return qr_data.strip()
    except Exception as e:
        print(f"Error reading QR code from image: {e}")
        return None

def read_qr_code_from_cv2_image(image_cv2):
    """
    Read QR code from OpenCV image.
    
    Args:
        image_cv2: OpenCV image (BGR format)
        
    Returns:
        str: Decoded QR code data or None
    """
    try:
        return _decode_qr_data(image_cv2)
    except Exception as e:
        print(f"Error reading QR code from CV2 image: {e}")
        return None

def read_qr_code_from_webcam():
    """
    Capture and read QR code from webcam.
    
    Returns:
        str: Decoded QR code data or None
    """
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Try to decode QR code
            qr_data = _decode_qr_data(frame)
            
            # Draw rectangles around QR codes
            try:
                decoded_objects = decode(frame)
                for obj in decoded_objects:
                    points = obj.polygon
                    if len(points) > 0:
                        pts = np.array(points, np.int32)
                        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            except Exception:
                pass
            
            cv2.imshow('QR Code Scanner - Show card, press SPACE to capture, ESC to cancel', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE key
                if qr_data:
                    cap.release()
                    cv2.destroyAllWindows()
                    return qr_data
                else:
                    print("QR code not detected. Please try again.")
            elif key == 27:  # ESC key
                cap.release()
                cv2.destroyAllWindows()
                return None
    except Exception as e:
        print(f"Error reading QR code from webcam: {e}")
        return None

def read_qr_from_pil_image(pil_image):
    """
    Read QR code from PIL image.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        str: Decoded QR code data or None
    """
    try:
        # Convert PIL to OpenCV
        image_np = np.array(pil_image)
        image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        return read_qr_code_from_cv2_image(image_cv2)
    except Exception as e:
        print(f"Error reading QR from PIL image: {e}")
        return None

def verify_qr_code(qr_data, unique_id, secret_key=None):
    """
    Verify if QR code data matches unique_id.

    Handles new format with NAME|UNIQUE_ID, signed payloads (``{uuid}:{hmac}``), 
    and legacy plain UUID payloads for backward compatibility.

    Args:
        qr_data (str): Data decoded from the QR code (can be "NAME|UNIQUE_ID" format).
        unique_id (str): User's unique ID from the session.
        secret_key (str | None): App secret key used during card generation.

    Returns:
        bool: True if QR matches and signature is valid.
    """
    if qr_data is None or unique_id is None:
        return False

    qr_data   = qr_data.strip()
    unique_id = unique_id.strip().upper()
    
    # New format: "NAME|UNIQUE_ID"
    if '|' in qr_data:
        parts = qr_data.split('|', 1)
        qr_uid = parts[1].strip().upper()
        
        # Verify the unique_id portion matches
        if qr_uid != unique_id:
            return False
        
        # Name|UID format is valid if UID matches
        return True
    
    qr_data = qr_data.upper()

    # Signed payload: "{UUID}:{HMAC}"
    if ':' in qr_data:
        parts = qr_data.split(':', 1)
        qr_uid, qr_sig = parts[0], parts[1]

        if qr_uid != unique_id:
            return False

        if secret_key:
            expected_sig = _sign_qr_payload(unique_id, secret_key).upper()
            # Use hmac.compare_digest for timing-safe comparison
            return hmac.compare_digest(qr_sig, expected_sig)
        # No key supplied — accept any matching UUID portion
        return True

    # Legacy plain UUID (no HMAC) — accept only if no secret_key enforced
    if secret_key:
        print("Warning: received unsigned QR but HMAC verification is active.")
        return False

    return qr_data == unique_id

def extract_qr_info(qr_data):
    """
    Extract name and ID from QR code data.
    Handles "NAME|UNIQUE_ID" format, returning both components.
    
    Args:
        qr_data (str): Data decoded from the QR code
        
    Returns:
        tuple: (name, unique_id) or (None, unique_id) if not in NAME|ID format
    """
    if qr_data is None:
        return None, None
    
    qr_data = qr_data.strip()
    
    # New format: "NAME|UNIQUE_ID"
    if '|' in qr_data:
        parts = qr_data.split('|', 1)
        name = parts[0].strip()
        unique_id = parts[1].strip()
        return name, unique_id
    
    # Legacy format: just UNIQUE_ID
    return None, qr_data

def detect_qr_in_image(image_cv2):
    """
    Detect if QR code exists in image.
    
    Args:
        image_cv2: OpenCV image
        
    Returns:
        bool: True if QR code detected
    """
    try:
        decoded_objects = decode(image_cv2)
        return len(decoded_objects) > 0
    except Exception as e:
        print(f"Error detecting QR code: {e}")
        return False
