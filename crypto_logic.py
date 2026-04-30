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
