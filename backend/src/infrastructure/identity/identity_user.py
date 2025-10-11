from pwdlib import PasswordHash
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.base import Base

password_hash = PasswordHash.recommended()


class IdentityUser(Base):
    __tablename__ = "identity_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]

    def verify_password(self, password: str) -> bool:
        return password_hash.verify(password, self.password_hash)
