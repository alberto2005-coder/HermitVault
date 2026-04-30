import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

ITERATIONS = 480_000

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_data(data: str, key: bytes) -> bytes:
    """Encrypts a string using a Fernet key."""
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """Decrypts bytes back to a string using a Fernet key."""
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

def generate_salt() -> bytes:
    """Generates a random 16-byte salt."""
    return os.urandom(16)

def generate_secure_password(length: int = 16, use_upper: bool = True, use_digits: bool = True, use_symbols: bool = True) -> str:
    """Generates a cryptographically strong random password."""
    import secrets
    import string
    
    alphabet = string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_password_strength(password: str) -> tuple[int, str, str]:
    """
    Checks password strength based on standard requirements.
    Returns (score 0-4, label, color).
    """
    if not password:
        return 0, "Too Short", "#7f8c8d"
    
    if len(password) < 8:
        return 0, "Too Short", "#e74c3c"
    
    # Requirements
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    # Calculate score based on types
    types_count = sum([has_lower, has_upper, has_digit, has_symbol])
    
    score = 0
    if types_count == 1: score = 1
    elif types_count == 2: score = 2
    elif types_count == 3: score = 3
    elif types_count == 4: score = 4
    
    # Boost score for length
    if score > 0 and len(password) >= 14:
        score = min(4, score + 1)

    strengths = {
        0: ("Very Weak", "#e74c3c"),
        1: ("Weak", "#e74c3c"),
        2: ("Fair", "#f39c12"),
        3: ("Good", "#3498db"),
        4: ("Strong", "#2ecc71")
    }
    
    label, color = strengths.get(score, ("Very Weak", "#e74c3c"))
    return score, label, color
