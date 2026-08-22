import hashlib
import os
import secrets
from typing import Optional, Dict, Any


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using PBKDF2 with SHA-256 and salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pwd_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, 100000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against stored salt$hash."""
    try:
        salt, key_hex = hashed.split("$")
        test_hash = hash_password(password, salt)
        return test_hash == hashed
    except Exception:
        return False
