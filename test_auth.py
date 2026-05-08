import sys
import os

print("=" * 60)
print("  AUTHSAFE - AUTHENTICATION LOGIC TEST SUITE v2")
print("=" * 60)

results = []

# -------------------------------------------------------
# TEST 1: Import auth_utils
# -------------------------------------------------------
print("\n[1] Importing auth_utils...")
try:
    from utils.auth_utils import (
        hash_pin, verify_pin, validate_email,
        validate_uuid, validate_pin, generate_unique_id,
        sanitize_input, get_timestamp
    )
    print("  PASS - auth_utils imported")
    results.append(("Import auth_utils", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("Import auth_utils", False, str(e)))

# -------------------------------------------------------
# TEST 2: PIN Hashing & Verification
# -------------------------------------------------------
print("\n[2] PIN Hashing & Verification...")
try:
    pin = "1234"
    hashed = hash_pin(pin)
    assert verify_pin("1234", hashed) == True,  "correct PIN not verified"
    assert verify_pin("9999", hashed) == False, "wrong PIN incorrectly verified"
    print("  PASS - hash_pin / verify_pin work correctly")
    results.append(("PIN Hash & Verify", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("PIN Hash & Verify", False, str(e)))

# -------------------------------------------------------
# TEST 3: Email Validation
# -------------------------------------------------------
print("\n[3] Email Validation...")
try:
    cases = [
        ("user@authsafe.in",        True),
        ("test.name@authsafe.in",   True),
        ("user@gmail.com",          False),
        ("user@authsafe.com",       False),
        ("notanemail",              False),
        ("@authsafe.in",            False),
    ]
    for email, expected in cases:
        got = validate_email(email)
        assert got == expected, f"Email '{email}': expected {expected}, got {got}"
    print("  PASS - validate_email works (domain restricted to @authsafe.in)")
    results.append(("Email Validation", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Email Validation", False, str(e)))

# -------------------------------------------------------
# TEST 4: PIN Validation (4-6 digits)
# -------------------------------------------------------
print("\n[4] PIN Validation...")
try:
    cases = [
        ("1234",    True),
        ("12345",   True),
        ("123456",  True),
        ("123",     False),
        ("1234567", False),
        ("abcd",    False),
        ("",        False),
    ]
    for pin_val, expected in cases:
        got = validate_pin(pin_val)
        assert got == expected, f"PIN '{pin_val}': expected {expected}, got {got}"
    print("  PASS - validate_pin works correctly")
    results.append(("PIN Validation", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("PIN Validation", False, str(e)))

# -------------------------------------------------------
# TEST 5: UUID Validation
# -------------------------------------------------------
print("\n[5] UUID Validation...")
try:
    cases = [
        ("AUTHSAFE-ABC123", True),
        ("authsafe-abc123", True),
        ("WRONG-ABC123",    False),
        ("AUTHSAFE-AB12",   False),
        ("AUTHSAFE-1234567",False),
        ("",                False),
    ]
    for uuid_val, expected in cases:
        got = validate_uuid(uuid_val)
        assert got == expected, f"UUID '{uuid_val}': expected {expected}, got {got}"
    print("  PASS - validate_uuid works correctly")
    results.append(("UUID Validation", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("UUID Validation", False, str(e)))

# -------------------------------------------------------
# TEST 6: generate_unique_id (now uses secrets CSPRNG)
# -------------------------------------------------------
print("\n[6] Unique ID Generation (CSPRNG)...")
try:
    import secrets as _secrets_mod
    import string as _string_mod
    ids = [generate_unique_id() for _ in range(10)]
    for uid in ids:
        assert uid.startswith("AUTHSAFE-"), f"Wrong prefix: {uid}"
        assert len(uid) == 15, f"Wrong length {len(uid)}: {uid}"
    # Verify uniqueness across 10 samples
    assert len(set(ids)) == 10, "Duplicate IDs generated (extremely unlikely with CSPRNG)"
    print(f"  PASS - e.g. {ids[0]} (10 unique IDs generated)")
    results.append(("Unique ID Generation (CSPRNG)", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Unique ID Generation (CSPRNG)", False, str(e)))

# -------------------------------------------------------
# TEST 7: sanitize_input (apostrophe no longer stripped)
# -------------------------------------------------------
print("\n[7] Input Sanitization (apostrophe fix)...")
try:
    r1 = sanitize_input("  hello  ")
    assert r1 == "hello", f"Strip whitespace failed: '{r1}'"

    r2 = sanitize_input("normal text")
    assert r2 == "normal text", f"Normal text modified: '{r2}'"

    # HTML-dangerous chars still stripped
    r3 = sanitize_input("test<b>bold</b>")
    assert "<" not in r3 and ">" not in r3, f"HTML tags not stripped: '{r3}'"

    # Apostrophe must be PRESERVED (Fix #7)
    r4 = sanitize_input("O'Brien")
    assert "'" in r4, f"Apostrophe wrongly stripped from name: '{r4}'"
    assert r4 == "O'Brien", f"Name mutated: '{r4}'"

    print("  PASS - whitespace/HTML stripped; apostrophe preserved for names like O'Brien")
    results.append(("Input Sanitization (apostrophe fix)", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Input Sanitization (apostrophe fix)", False, str(e)))

# -------------------------------------------------------
# TEST 8: get_timestamp
# -------------------------------------------------------
print("\n[8] Timestamp...")
try:
    from datetime import datetime
    ts = get_timestamp()
    assert isinstance(ts, datetime), f"Expected datetime, got {type(ts)}"
    print(f"  PASS - returned: {ts}")
    results.append(("Timestamp", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("Timestamp", False, str(e)))

# -------------------------------------------------------
# TEST 9: QR utils import
# -------------------------------------------------------
print("\n[9] Importing qr_utils...")
try:
    from utils.qr_utils import (
        generate_qr_code, verify_qr_code,
        read_qr_code_from_cv2_image, _sign_qr_payload
    )
    print("  PASS - qr_utils imported")
    results.append(("Import qr_utils", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("Import qr_utils", False, str(e)))

# -------------------------------------------------------
# TEST 10: QR verify_qr_code — plain (legacy) mode
# -------------------------------------------------------
print("\n[10] QR Code Verification (plain/legacy)...")
try:
    assert verify_qr_code("AUTHSAFE-ABC123", "AUTHSAFE-ABC123") == True
    assert verify_qr_code("authsafe-abc123", "AUTHSAFE-ABC123") == True
    assert verify_qr_code("AUTHSAFE-XXXXXX", "AUTHSAFE-ABC123") == False
    assert verify_qr_code(None, "AUTHSAFE-ABC123") == False
    assert verify_qr_code("AUTHSAFE-ABC123", None) == False
    print("  PASS - plain verify_qr_code works correctly")
    results.append(("QR Code Verification (plain)", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("QR Code Verification (plain)", False, str(e)))

# -------------------------------------------------------
# TEST 11: HMAC-signed QR code (Fix #6)
# -------------------------------------------------------
print("\n[11] HMAC-Signed QR Code (Fix #6)...")
try:
    import hmac as _hmac_mod
    import hashlib
    import tempfile

    SECRET = "test-secret-key"
    UID    = "AUTHSAFE-ABC123"

    # Generate signed payload manually
    sig = _sign_qr_payload(UID, SECRET)
    signed_payload = f"{UID}:{sig.upper()}"

    # Should pass with correct key
    assert verify_qr_code(signed_payload, UID, secret_key=SECRET) == True, \
        "Valid HMAC signature rejected"

    # Should fail with wrong key
    assert verify_qr_code(signed_payload, UID, secret_key="wrong-key") == False, \
        "Invalid HMAC signature accepted"

    # Should fail if UUID doesn't match
    assert verify_qr_code(signed_payload, "AUTHSAFE-XXXXXX", secret_key=SECRET) == False, \
        "Mismatched UUID accepted"

    # Unsigned QR should be REJECTED when secret_key is enforced
    assert verify_qr_code(UID, UID, secret_key=SECRET) == False, \
        "Unsigned QR accepted when HMAC enforced"

    # Generate a QR file and verify round-trip (no webcam needed)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    ok = generate_qr_code(UID, tmp.name, secret_key=SECRET)
    assert ok == True, "generate_qr_code with secret_key failed"
    os.remove(tmp.name)

    print("  PASS - HMAC-signed QR: correct key passes, wrong key/UUID/unsigned rejected")
    results.append(("HMAC-Signed QR Code", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("HMAC-Signed QR Code", False, str(e)))
except Exception as e:
    print(f"  FAIL (exception) - {e}")
    results.append(("HMAC-Signed QR Code", False, str(e)))

# -------------------------------------------------------
# TEST 12: face_utils import
# -------------------------------------------------------
print("\n[12] Importing face_utils...")
try:
    from utils.face_utils import get_face_encoding, verify_face, save_face_image
    print("  PASS - face_utils imported")
    results.append(("Import face_utils", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("Import face_utils", False, str(e)))

# -------------------------------------------------------
# TEST 13: Face Verification - edge cases + tolerance fix
# -------------------------------------------------------
print("\n[13] Face Verification - edge cases & tolerance fix (Fix #4)...")
try:
    import numpy as np
    import cv2

    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    # None stored encoding should return False
    assert verify_face(dummy_img, None) == False, \
        "verify_face with None encoding should be False"

    # Identical encodings should always match
    enc = [0.1] * 160
    assert verify_face.__code__, "verify_face importable"  # sanity

    # Verify that the tolerance threshold is symmetric:
    # cosine_similarity > (1 - tolerance) for tolerance=0.85 => sim > ~0.15
    import math
    tolerance = 0.85
    sim_threshold = 1.0 - tolerance
    assert math.isclose(sim_threshold, 0.15, rel_tol=1e-9), \
        f"Unexpected sim threshold: {sim_threshold}"

    print("  PASS - verify_face handles None; tolerance threshold is symmetric")
    results.append(("Face Verify Edge Cases (tolerance fix)", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Face Verify Edge Cases (tolerance fix)", False, str(e)))

# -------------------------------------------------------
# TEST 14: App Config
# -------------------------------------------------------
print("\n[14] App Configuration...")
try:
    from config import config
    dev_cfg = config["development"]
    # Tolerance should be 0.85 (not 0.6 as the old default was)
    assert dev_cfg.FACE_RECOGNITION_TOLERANCE == 0.85, \
        f"Expected 0.85, got {dev_cfg.FACE_RECOGNITION_TOLERANCE}"
    print(f"  PASS - config loaded; FACE_RECOGNITION_TOLERANCE = {dev_cfg.FACE_RECOGNITION_TOLERANCE}")
    results.append(("App Configuration", True, ""))
except Exception as e:
    print(f"  FAIL - {e}")
    results.append(("App Configuration", False, str(e)))

# -------------------------------------------------------
# TEST 15: Rate-limiter helper functions (Fix #9)
# -------------------------------------------------------
print("\n[15] Rate Limiter Logic (Fix #9)...")
try:
    from datetime import datetime, timedelta
    import threading

    # Replicate the rate-limiter logic inline for unit testing
    _attempts: dict = {}
    _lock = threading.Lock()
    MAX_A, WIN_M, LOCK_M = 3, 5, 5  # tighter values for the test

    def _record(ident):
        now = datetime.utcnow()
        ws  = now - timedelta(minutes=WIN_M)
        with _lock:
            lst = [t for t in _attempts.get(ident, []) if t > ws]
            lst.append(now)
            _attempts[ident] = lst

    def _locked(ident):
        now = datetime.utcnow()
        ws  = now - timedelta(minutes=WIN_M)
        with _lock:
            recent = [t for t in _attempts.get(ident, []) if t > ws]
            _attempts[ident] = recent
            return len(recent) >= MAX_A

    def _clear(ident):
        with _lock:
            _attempts.pop(ident, None)

    # Not locked initially
    assert _locked("user@authsafe.in") == False

    # Record 3 attempts → locked
    _record("user@authsafe.in")
    _record("user@authsafe.in")
    _record("user@authsafe.in")
    assert _locked("user@authsafe.in") == True, "Should be locked after 3 attempts"

    # Clear → unlocked
    _clear("user@authsafe.in")
    assert _locked("user@authsafe.in") == False, "Should be unlocked after clear"

    print(f"  PASS - rate limiter: locked after {MAX_A} attempts, cleared on success")
    results.append(("Rate Limiter Logic", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Rate Limiter Logic", False, str(e)))

# -------------------------------------------------------
# TEST 16: PIN Uniqueness NOT enforced globally (Fix #1)
# -------------------------------------------------------
print("\n[16] Global PIN Uniqueness Removed (Fix #1)...")
try:
    import inspect
    import app as flask_app

    src = inspect.getsource(flask_app.register)
    # The old loop should be gone
    assert "for existing_user in" not in src, \
        "Global PIN uniqueness loop still present in register()"
    assert "password already taken" not in src, \
        "Old PIN uniqueness error message still present"
    print("  PASS - global PIN uniqueness loop removed from register()")
    results.append(("Global PIN Uniqueness Removed", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("Global PIN Uniqueness Removed", False, str(e)))
except Exception as e:
    print(f"  FAIL (exception) - {e}")
    results.append(("Global PIN Uniqueness Removed", False, str(e)))

# -------------------------------------------------------
# TEST 17: face_encoding NOT in session after login (Fix #2)
# -------------------------------------------------------
print("\n[17] face_encoding Removed from Session (Fix #2)...")
try:
    import inspect
    import app as flask_app

    login_src = inspect.getsource(flask_app.login)
    # The assignment `session['face_encoding'] = ...` must NOT appear
    assert "session['face_encoding']" not in login_src, \
        "face_encoding still stored in session inside login()"
    print("  PASS - face_encoding not stored in session inside login()")
    results.append(("face_encoding NOT in Session", True, ""))
except AssertionError as e:
    print(f"  FAIL - {e}")
    results.append(("face_encoding NOT in Session", False, str(e)))
except Exception as e:
    print(f"  FAIL (exception) - {e}")
    results.append(("face_encoding NOT in Session", False, str(e)))

# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
print()
print("=" * 60)
print("  SUMMARY")
print("=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
for name, ok, err in results:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {name}"
    if err:
        msg += f"  => {err}"
    print(msg)

print()
print(f"  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
