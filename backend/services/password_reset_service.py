import hashlib
import secrets


def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def verify_otp(
    otp: str,
    stored_hash: str
) -> bool:

    calculated_hash = hash_otp(otp)

    return secrets.compare_digest(
        calculated_hash,
        stored_hash
    )