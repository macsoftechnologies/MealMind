from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext


load_dotenv()


# ------------------------------------------------------------
# PASSWORD HASHING
# ------------------------------------------------------------

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Convert a plain password into a secure bcrypt hash.
    """
    return password_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Check whether the entered password matches the stored hash.
    """
    return password_context.verify(
        plain_password,
        hashed_password
    )


# ------------------------------------------------------------
# JWT CONFIGURATION
# ------------------------------------------------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing from the .env file"
    )


# ------------------------------------------------------------
# CREATE ACCESS TOKEN
# ------------------------------------------------------------

def create_access_token(
    user_id: int,
    email: str
) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ------------------------------------------------------------
# DECODE ACCESS TOKEN
# ------------------------------------------------------------

def decode_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None