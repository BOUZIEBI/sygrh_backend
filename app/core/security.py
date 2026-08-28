from pwdlib import PasswordHash
import hashlib
import re
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str)->str:
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    bcrypt_hash = pwd_context.hash(sha256_hash)
    return bcrypt_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = hashlib.sha256(plain_password.encode()).hexdigest() 
    return pwd_context.verify(password_bytes, hashed_password) 


def validate_password_strength(password: str) -> bool:
    if len(password) < 6:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

