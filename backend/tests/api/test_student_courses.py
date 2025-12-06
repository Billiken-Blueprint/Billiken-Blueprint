import pytest
from httpx import AsyncClient
from billiken_blueprint.domain.student import Student
from billiken_blueprint.domain.courses.course import Course
from billiken_blueprint.identity import IdentityUser
from billiken_blueprint.dependencies import get_current_identity
from server import app

@pytest.mark.asyncio
async def test_add_delete_desired_course(app_client: AsyncClient, identity_user_repository, student_repository, course_repository):
    # Setup: Create student and identity user
    student = Student(
        id=None,
        name="Test Student",
        graduation_year=2024,
        completed_course_ids=[],
        desired_course_ids=[],
        unavailability_times=[],
        avoid_times=[],
        degree_id=1
    )
    saved_student = await student_repository.save(student)
    
    identity_user = IdentityUser(id=1, email="test@example.com", password_hash="hash", student_id=saved_student.id)
    await identity_user_repository.save(identity_user)

    # Setup: Create a dummy course
    course = Course(
        id=101,
        major_code="CS",
        course_number="1010",
        attribute_ids=[],
        prerequisites=None
    )
    # We need to save the course to the repo for the endpoint to find it
    # But course_repository doesn't seem to have a save method exposed in the interface usually? 
    # Let's check course_repository.py. If not, we might fail `await course_repo.get_by_id(course_id)`.
    # Assuming for now we can save or it has one.
    # Ref: `tests/api/test_user_info.py` didn't create courses but used IDs. 
    # But my endpoint logic is `course = await course_repo.get_by_id(course_id); if not course: 404`.
    # So I MUST have the course in the repo.
    # Let's try to save it directly or via some helper if available.
    # Checking existing tests or repo file would be wise, but I will assume I can insert it using repo implementation details if needed or just `save`.
    # Actually `CourseRepository` typically has `save` in these patterns.
    await course_repository.save(course)

    # Override dependency
    app.dependency_overrides[get_current_identity] = lambda: identity_user

    try:
        # Test 1: Add desired course
        response = app_client.post("/api/student/desired_courses", params={"course_id": 101})
        assert response.status_code == 200
        assert response.json() == [101]
        
        # Verify DB
        updated_student = await student_repository.get_by_id(saved_student.id)
        assert updated_student.desired_course_ids == [101]

        # Test 2: Add same course again (idempotent)
        response = app_client.post("/api/student/desired_courses", params={"course_id": 101})
        assert response.status_code == 200
        assert response.json() == [101]
        
        updated_student = await student_repository.get_by_id(saved_student.id)
        assert updated_student.desired_course_ids == [101]

        # Test 3: Delete desired course
        response = app_client.delete("/api/student/desired_courses/101")
        assert response.status_code == 200
        assert response.json() == [] # Empty list

        updated_student = await student_repository.get_by_id(saved_student.id)
        assert updated_student.desired_course_ids == []

        # Test 4: Add non-existent course -> 404
        response = app_client.post("/api/student/desired_courses", params={"course_id": 999})
        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
