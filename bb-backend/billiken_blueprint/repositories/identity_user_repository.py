from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from billiken_blueprint.identity import IdentityUser


class IdentityUserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.async_session = session

    async def get_by_id(self, user_id: int) -> Optional[IdentityUser]:
        async with self.async_session() as session:
            stmt = select(IdentityUser).where(IdentityUser.id == user_id).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_email(self, username: str) -> Optional[IdentityUser]:
        async with self.async_session() as session:
            stmt = select(IdentityUser).where(IdentityUser.email == username).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def save(self, user: IdentityUser) -> IdentityUser:
        """
        Save or update an IdentityUser and return the user with the database-generated ID.
        """
        insert_stmt = insert(IdentityUser).values(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            student_id=user.student_id,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[IdentityUser.id],
            set_=dict(
                name=insert_stmt.excluded.name,
                email=insert_stmt.excluded.email,
                password_hash=insert_stmt.excluded.password_hash,
                student_id=insert_stmt.excluded.student_id,
            ),
        ).returning(IdentityUser)

        async with self.async_session() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            return result.scalar_one()  # type: ignore
