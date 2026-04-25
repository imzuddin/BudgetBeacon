import bcrypt
import hmac

from config.settings import settings

def _pepper_password(password: str) -> bytes:
    return hmac.digest(
        settings.pepper_string.encode("utf-8"),
        password.encode("utf-8"),
        "sha256",
    )

def hash_password(password: str) -> str:
    peppered_password = _pepper_password(password)
    return bcrypt.hashpw(peppered_password, bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> str:
    _pepper_password = _pepper_password(password)
    return bcrypt.checkpw(_pepper_password, password_hash.encode("utf-8"))