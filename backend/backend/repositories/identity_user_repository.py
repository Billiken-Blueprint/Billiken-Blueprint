from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from identity.identity_user import IdentityUser


class IdentityUserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.async_session = session

    async def get_by_email(self, username: str) -> Optional[IdentityUser]:
        async with self.async_session() as session:
            stmt = select(IdentityUser).where(IdentityUser.email == username).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def save(self, user: IdentityUser) -> None:
        insert_stmt = insert(IdentityUser).values(
            email=user.email, password_hash=user.password_hash
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[IdentityUser.id],
            set_=dict(
                email=insert_stmt.excluded.email,
                password_hash=insert_stmt.excluded.password_hash,
            ),
        )
        async with self.async_session() as session:
            await session.execute(conflict_stmt)
            await session.commit()
