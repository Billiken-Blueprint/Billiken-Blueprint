from datetime import timedelta, datetime, timezone
from typing import Optional

import jwt
from pydantic import BaseModel

from src.variables import JWT_PRIVATE_KEY

SECRET_KEY = "27e7a5811fabc16a334ba2aaca332a8d3319506e8dcc0e9724cf7c28109065c6"


class Token(BaseModel):
    access_token: str
    token_type: str

    @staticmethod
    def create(data: dict, expires_delta: Optional[timedelta] = None) -> "Token":
        to_encode = data.copy()
        if not expires_delta:
            expires_delta = timedelta(minutes=15)
        exire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": exire})
        encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm="EdDSA")
        return Token(access_token=encoded_jwt, token_type="Bearer")
