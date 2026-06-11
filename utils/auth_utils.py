import bcrypt
import re
import secrets
import string
from datetime import datetime

def hash_pin(pin):
    """
    Hash a PIN using bcrypt.
    
    Args:
        pin (str): The PIN to hash
        
    Returns:
        str: The hashed PIN
    """
    if not isinstance(pin, bytes):
        pin = pin.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pin, salt).decode('utf-8')

def verify_pin(pin, pin_hash):
    """
    Verify a PIN against its hash.
    
    Args:
        pin (str): The PIN to verify
        pin_hash (str): The hashed PIN
        
    Returns:
        bool: True if PIN matches, False otherwise
    """
    try:
        if not isinstance(pin, bytes):
            pin = pin.encode('utf-8')
        if isinstance(pin_hash, str):
            pin_hash = pin_hash.encode('utf-8')
        return bcrypt.checkpw(pin, pin_hash)
    except Exception as e:
        print(f"Error verifying PIN: {e}")
        return False

def validate_email(email):
    """
    Validate email format - must be @authentication.in domain.
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if valid email format with @authentication.in domain
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@authentication\.in$'
    return re.match(pattern, email) is not None

def validate_pin(pin):
    """
    Validate PIN format (4-6 digits).
    
    Args:
        pin (str): PIN to validate
        
    Returns:
        bool: True if valid PIN format
    """
    return pin.isdigit() and 4 <= len(pin) <= 6

def validate_uuid(uuid):
    """
    Validate UUID format (AUTHENTICATION-XXXXXX).
    
    Args:
        uuid (str): UUID to validate
        
    Returns:
        bool: True if valid UUID format
    """
    pattern = r'^AUTHENTICATION-[A-Z0-9]{6}$'
    return re.match(pattern, uuid.upper()) is not None

def generate_unique_id():
    """
    Generate a cryptographically secure unique user ID.

    Uses the ``secrets`` module (CSPRNG) instead of ``random`` to ensure
    IDs cannot be predicted even if an attacker knows the generation time.

    Returns:
        str: Unique ID in format AUTHENTICATION-XXXXXX
    """
    alphabet = string.ascii_uppercase + string.digits
    random_str = ''.join(secrets.choice(alphabet) for _ in range(6))
    return f"AUTHENTICATION-{random_str}"

def sanitize_input(text):
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return text
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove potential script tags and dangerous characters.
    # Note: apostrophe (') is intentionally excluded so names like
    # "O'Brien" are preserved — apostrophes are safe in HTML-escaped output.
    dangerous_chars = ['<', '>', '{', '}', ';', '"']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text

def get_timestamp():
    """
    Get current timestamp.
    
    Returns:
        datetime: Current datetime
    """
    return datetime.utcnow()
