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
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt.

    Returns a string of the form ``pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>``.
    """
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


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency: decode JWT and return the payload dict.

    Phase-0 scaffolding: returns raw payload. Phase-1 will hydrate a full User
    object from the database via a new repository module.
    """
    return verify_token(token)


def create_access_token(
    data: dict, role: str = "viewer", expires_delta: Optional[timedelta] = None
):
    """
    Creates a JSON Web Token (JWT) with embedded claims.

    Args:
        data (dict): The payload data to include in the token.
        role (str): The user's role (default is "viewer").
        expires_delta (timedelta, optional): The duration until the token expires.

    Returns:
        str: The encoded JWT.
    """
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
    """Dependency factory: verify the current user's role grants `permission`.

    Phase-0: role-to-permission mapping is static. Phase-1 will pull from the
    `roles.permissions` JSON column.
    """
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
    """
    Dependency to check if the user has one of the required roles.

    Args:
        required_roles (List[str]): A list of roles allowed to access the endpoint.

    Returns:
        Callable: Dependency that checks user roles.
    """

    def role_checker(token: str = Depends(oauth2_scheme)):
        user = verify_token(token)
        user_role = user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=403, detail=f"Access forbidden for role: {user_role}"
            )

    return role_checker


def verify_token(token: str):
    """
    Verifies a JWT and extracts the payload.

    Args:
        token (str): The JWT to verify.

    Returns:
        dict: The decoded payload if valid.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
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
    """
    Extracts the user's role from the token.

    Args:
        token (str): The JWT.

    Returns:
        str: The user's role.
    """
    try:
        payload = verify_token(token)
        return payload.get("role", "user")
    except Exception as e:
        logger.error(f"Error extracting user role: {e}")
        return "user"


def token_about_to_expire(token: str, buffer_minutes: int = 1):
    """
    Checks if a token is about to expire within a specified buffer time.

    Args:
        token (str): The JWT.
        buffer_minutes (int): The buffer time in minutes.

    Returns:
        bool: True if the token is about to expire, False otherwise.
    """
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
    """Check if the token belongs to an admin."""
    payload = verify_token(token)
    role = payload.get("role", "user")
    return role == "admin"
