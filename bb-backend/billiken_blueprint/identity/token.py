from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, timezone
from typing import Optional
import jwt

from billiken_blueprint.identity.token_payload import TokenPayload

with open("dev-certs/jwt.pem", "r") as f:
    SECRET_KEY = f.read()

ALGORITHM = "EdDSA"


@dataclass
class Token:
    access_token: str
    token_type: str

    @staticmethod
    def create(
        payload: TokenPayload, expires_delta: Optional[timedelta] = None
    ) -> "Token":
        to_encode = payload.__dict__.copy()
        if not expires_delta:
            expires_delta = timedelta(minutes=15)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return Token(access_token=encoded_jwt, token_type="Bearer")
