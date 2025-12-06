import pytest
from httpx import AsyncClient
from billiken_blueprint.domain.student import Student, TimeSlot
from billiken_blueprint.identity import IdentityUser
from billiken_blueprint.dependencies import get_current_identity
from server import app

@pytest.mark.asyncio
async def test_set_user_info(app_client: AsyncClient, identity_user_repository, student_repository):
    # Setup: Create and save a test identity user
    identity_user = IdentityUser(id=1, email="test@example.com", password_hash="hash", student_id=None)
    await identity_user_repository.save(identity_user)

    # Override dependency to return the test user
    app.dependency_overrides[get_current_identity] = lambda: identity_user
    
    try:
        payload = {
            "name": "Test Student",
            "graduation_year": 2025,
            "completed_course_ids": [1, 2, 3],
            "unavailability_times": [
                {"day": 0, "start": "0900", "end": "1000"},
                {"day": 2, "start": "1400", "end": "1530"}
            ],
            "avoid_times": [
                {"day": 4, "start": "0800", "end": "0900"}
            ],
            "degree_id": 1
        }

        # Execute
        response = app_client.post("/api/user_info", json=payload)

        # Verify Response
        assert response.status_code == 200
        assert response.json() is None  # Endpoint returns nothing on success

        # Verify Database
        # The endpoint updates the identity user with the new student ID
        updated_identity = await identity_user_repository.get_by_id(1)
        assert updated_identity.student_id is not None
        
        student = await student_repository.get_by_id(updated_identity.student_id)
        assert student is not None
        assert student.name == "Test Student"
        assert student.graduation_year == 2025
        assert student.completed_course_ids == [1, 2, 3]
        assert student.desired_course_ids == []
        assert student.degree_id == 1
        
        # Verify Time Slots
        assert len(student.unavailability_times) == 2
        assert student.unavailability_times[0] == TimeSlot(day=0, start="0900", end="1000")
        assert student.unavailability_times[1] == TimeSlot(day=2, start="1400", end="1530")
        
        assert len(student.avoid_times) == 1
        assert student.avoid_times[0] == TimeSlot(day=4, start="0800", end="0900")
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_user_info(app_client: AsyncClient, identity_user_repository, student_repository, course_repository):
    # Setup: Create student and identity user
    student = Student(
        id=None,
        name="Existing Student",
        graduation_year=2024,
        completed_course_ids=[101],
        desired_course_ids=[],
        unavailability_times=[TimeSlot(day=1, start="1000", end="1100")],
        avoid_times=[],
        degree_id=2
    )
    saved_student = await student_repository.save(student)
    
    identity_user = IdentityUser(id=2, email="existing@example.com", password_hash="hash", student_id=saved_student.id)
    await identity_user_repository.save(identity_user)

    # Override dependency
    app.dependency_overrides[get_current_identity] = lambda: identity_user

    try:
        # Execute
        response = app_client.get("/api/user_info")

        # Verify
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Existing Student"
        assert data["graduationYear"] == 2024
        assert data["completedCourseIds"] == [101]
        assert data["desiredCourseIds"] == []
        assert data["degreeId"] == 2
        
        assert len(data["unavailabilityTimes"]) == 1
        assert data["unavailabilityTimes"][0] == {"day": 1, "start": "1000", "end": "1100"}
        assert data["avoidTimes"] == []
    finally:
        app.dependency_overrides.clear()
