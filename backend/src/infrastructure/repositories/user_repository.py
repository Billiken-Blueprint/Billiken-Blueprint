from sqlalchemy.dialects.sqlite import insert, JSON
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.user import User
from src.infrastructure.base import Base


class UserDbEntity(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    majors: Mapped[list[str]] = mapped_column(JSON)
    minors: Mapped[list[str]] = mapped_column(JSON)


class UserRepository:
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.async_session = async_session

    async def save(self, user: User):
        insert_stmt = insert(UserDbEntity).values(
            id=user.id, majors=user.majors, minors=user.minors
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[User.id],
            set_=dict(
                majors=insert_stmt.excluded.majors, minors=insert_stmt.excluded.minors
            ),
        )
        async with self.async_session() as session:
            await session.execute(conflict_stmt)
