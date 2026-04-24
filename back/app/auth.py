from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, List
from app.config import settings
import logging
import hashlib
import hmac
import secrets
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session


def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 260_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iter_s, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iter_s)
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return verify_token(token)


def create_access_token(
    data: dict, role: str = "viewer", expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    to_encode.update({"role": role})
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    try:
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        logging.info("Token created successfully.")
        return token
    except Exception as e:
        logging.error(f"Error creating token: {e}")
        raise


def require_permission(permission: str):
    _ROLE_PERMISSIONS = {
        "admin": {"view_reports", "manage_users", "manage_routes", "manage_inventory"},
        "manager": {"view_reports", "manage_routes", "manage_inventory"},
        "viewer": {"view_reports"},
        "user": set(),
    }

    def permission_checker(user: dict = Depends(get_current_user)):
        role = user.get("role", "user")
        if permission not in _ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return Depends(permission_checker)


def require_role(required_roles: List[str]):
    def role_checker(token: str = Depends(oauth2_scheme)):
        user = verify_token(token)
        user_role = user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=403, detail=f"Access forbidden for role: {user_role}"
            )

    return role_checker


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("Token has expired.")
            raise JWTError("Token has expired.")
        logger.info("Token verified successfully.")
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise JWTError("Token is invalid.")
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise


def get_user_role(token: str):
    try:
        payload = verify_token(token)
        return payload.get("role", "user")
    except Exception as e:
        logger.error(f"Error extracting user role: {e}")
        return "user"


def token_about_to_expire(token: str, buffer_minutes: int = 1):
    try:
        payload = verify_token(token)
        exp = payload.get("exp")
        if exp and (exp - datetime.utcnow().timestamp()) < buffer_minutes * 60:
            logger.warning("Token is about to expire.")
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking token expiry: {e}")
        return False


def is_admin(token: str):
    payload = verify_token(token)
    role = payload.get("role", "user")
    return role == "admin"
