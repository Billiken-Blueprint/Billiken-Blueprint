from dataclasses import dataclass


@dataclass
class TokenPayload:
    sub: str
    email: str
