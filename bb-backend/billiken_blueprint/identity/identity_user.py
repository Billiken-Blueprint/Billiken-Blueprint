from dataclasses import dataclass
from typing import Optional

from pwdlib import PasswordHash

from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column

password_hash = PasswordHash.recommended()


class IdentityUser(Base):
    __tablename__ = "identity_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    student_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    def verify_password(self, password: str) -> bool:
        return password_hash.verify(password, self.password_hash)

    @staticmethod
    def create(name: str, email: str, password: str) -> "IdentityUser":
        hashed_password = password_hash.hash(password)
        return IdentityUser(name=name, email=email, password_hash=hashed_password)
