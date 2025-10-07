import jwt
import datetime
from helpers.token_utils import get_random_hex

SECRET_KEY = get_random_hex(300)  

password = "replicanx"+get_random_hex()

def create_token(payload: dict, expires_in: int = 3600) -> str:
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
