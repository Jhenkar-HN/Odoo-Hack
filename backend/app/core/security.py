from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import base64, hashlib, hmac, json, os
from backend.app.core.config import settings

try:
    from jose import jwt as jose_jwt
except ImportError:
    jose_jwt = None
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None

def _fallback_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return "pbkdf2_sha256$310000$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

def _fallback_verify(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt_b64, digest_b64 = encoded.split("$", 3)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2_sha256$"):
        return _fallback_verify(plain_password, hashed_password)
    if pwd_context is None:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password) if pwd_context is not None else _fallback_hash(password)

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _fallback_encode(payload: dict) -> str:
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header}.{body}".encode()
    sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    return f"{header}.{body}.{_b64url(sig)}"

def _fallback_decode(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    header, body, signature = parts
    expected = _b64url(hmac.new(settings.SECRET_KEY.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid signature")
    padded = body + "=" * (-len(body) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded).decode())
    if "exp" in payload and datetime.now(timezone.utc).timestamp() > float(payload["exp"]):
        raise ValueError("Token expired")
    return payload

def create_access_token(subject: Union[str, Any], role: str, employee_id: Optional[int] = None, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"exp": expire.timestamp(), "sub": str(subject), "role": role, "employee_id": employee_id, "type": "access"}
    if jose_jwt is not None:
        return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return _fallback_encode(payload)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        if jose_jwt is not None:
            return jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return _fallback_decode(token)
    except Exception:
        return None
