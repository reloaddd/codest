import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings


def hashed(password):
    bytes=password.encode("utf-8")
    salt=bcrypt.gensalt()
    hashed_pass=bcrypt.hashpw(bytes,salt)

    return hashed_pass.decode("utf-8")

def verify(plain_pass, hashed_pass):

    print(f"\n[DEBUG] Attempting to log in...")
    print(f"[DEBUG] Plain text from user: '{plain_pass}'")
    print(f"[DEBUG] Hash from database: '{hashed_pass}'\n")


    bytes_enc=plain_pass.encode("utf-8")
    hashed_pass_enc=hashed_pass.encode("utf-8")

    return bcrypt.checkpw(bytes_enc, hashed_pass_enc)



ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_jwt_token(data):

    to_encode=data.copy()

    expire=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})

    signature=jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

    return signature


