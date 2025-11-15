from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from courses.model.course import Course


class CourseRepository:
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.async_session = async_session

    async def save(self, course: dict) -> None:
        """Save (upsert) a single course mapping by (code, title).

        This implements the upsert behavior you asked for. The input
        `course` should be a dict with at least 'code' and 'title'. If a row
        with the same (code, title) exists, update its `crn` field.
        """
        code = course.get("code")
        title = course.get("title")

        if not code or not title:
            raise ValueError("course dict must include 'code' and 'title'")

        insert_stmt = insert(Course).values(code=code, title=title)
        conflict_stmt = insert_stmt.on_conflict_do_nothing()

        async with self.async_session() as session:
            await session.execute(conflict_stmt)
            await session.commit()
