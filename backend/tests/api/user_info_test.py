from pickletools import pystring
import re
from fastapi.testclient import TestClient
from httpx import get
import pytest
from billiken_blueprint.domain.student import Student
from billiken_blueprint.identity.identity_user import IdentityUser


@pytest.fixture(scope="function")
def registered_user(app_client):
    """Fixture to register a user and return the response."""
    register_response = app_client.post(
        "/identity/register",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "email": "testemail@example.com",
            "password": "Abc123!@#",
        },
    )
    assert register_response.is_success == True
    return register_response


@pytest.mark.asyncio
async def test_user_info_endpoint_saves_data(
    app_client: TestClient,
    registered_user,
):
    token = registered_user.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    user_info_payload = dict(
        name="Test User",
        degree_ids=[1, 2],
        major="Computer Science",
        minor=None,
        graduation_year=2025,
        completed_course_ids=[101, 102, 103],
    )

    post_response = app_client.post(
        "user_info/", json=user_info_payload, headers=auth_headers
    )

    assert post_response.is_success
    get_response = app_client.get("user_info/", headers=auth_headers)
    assert get_response.is_success
    data = get_response.json()
    assert data["name"] == "Test User"
    assert set(data["degreeIds"]) == {1, 2}
    assert set(data["completedCourseIds"]) == {101, 102, 103}


@pytest.mark.asyncio
async def test_user_info_get_404_for_no_student(
    app_client: TestClient,
    registered_user,
):
    token = registered_user.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    get_response = app_client.get("user_info/", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_user_info_upsert_updates_existing_data(
    app_client: TestClient,
    registered_user,
):
    """Test that posting user info twice updates the existing data (upsert)."""
    token = registered_user.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Initial user info
    initial_payload = dict(
        name="Test User",
        degree_ids=[1, 2],
        major="Computer Science",
        minor=None,
        graduation_year=2025,
        completed_course_ids=[101, 102, 103],
    )

    post_response = app_client.post(
        "user_info/", json=initial_payload, headers=auth_headers
    )
    assert post_response.is_success

    # Updated user info
    updated_payload = dict(
        name="Test User Updated",
        degree_ids=[3, 4, 5],
        major="Mathematics",
        minor="Statistics",
        graduation_year=2026,
        completed_course_ids=[201, 202],
    )

    upsert_response = app_client.post(
        "user_info/", json=updated_payload, headers=auth_headers
    )
    assert upsert_response.is_success

    # Verify the data was updated
    get_response = app_client.get("user_info/", headers=auth_headers)
    assert get_response.is_success
    data = get_response.json()
    assert data["name"] == "Test User Updated"
    assert set(data["degreeIds"]) == {3, 4, 5}
    assert set(data["completedCourseIds"]) == {201, 202}
