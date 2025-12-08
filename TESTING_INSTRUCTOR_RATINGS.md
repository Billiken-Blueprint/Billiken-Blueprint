# Testing Instructor Ratings in Schedule Endpoint

## Overview
The schedule endpoint now includes instructor ratings in the scoring algorithm. Sections with higher-rated instructors will be prioritized in schedule recommendations.

## Manual Testing via API

### 1. Start the Backend Server
```bash
cd backend
docker compose up backend
# Or if running locally:
uv run fastapi dev server.py
```

### 2. Get an Auth Token
First, you need to authenticate:

```bash
# Login (replace with your credentials)
curl -X POST "http://localhost:8000/api/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_email@example.com&password=your_password"
```

This will return a token like:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Check Available Instructors with Ratings
```bash
curl -X GET "http://localhost:8000/api/instructors" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Look for instructors with `rmpRating` values (e.g., 4.5, 3.2, etc.)

### 4. Test the Schedule Endpoint
```bash
curl -X GET "http://localhost:8000/api/degree-requirements/autogenerate-schedule?semester=202501" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Verify Instructor Ratings Are Affecting Scores

To verify that instructor ratings are being used:

1. **Find sections with different instructors:**
   - Look at the returned sections
   - Note which instructors are assigned to each section

2. **Check instructor ratings:**
   - Use the `/api/instructors` endpoint to see ratings
   - Sections with higher-rated instructors should appear earlier in the results

3. **Compare two sections of the same course:**
   - If a course has multiple sections with different instructors
   - The section with the higher-rated instructor should be ranked higher

## Unit Testing

### Add a Test Case

Add this test to `backend/tests/domain/test_schedule.py`:

```python
def test_get_schedule_prioritizes_high_rated_instructors(self):
    """Test that sections with higher-rated instructors are prioritized."""
    # Setup courses
    c1 = CourseWithAttributes(
        id=1, major_code="CSCI", course_number="1000", 
        attribute_ids=[], prerequisites=None, attributes=[]
    )
    all_courses = [c1]

    # Setup sections: Two sections for the same course, different instructors
    mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
    mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
    
    s1 = Section(
        id=1, crn="1", instructor_names=["Michael Goldwasser"], 
        campus_code="STL", description="", title="S1",
        course_code="CSCI 1000", semester="Fall", meeting_times=[mt1]
    )
    s2 = Section(
        id=2, crn="2", instructor_names=["Low Rated Instructor"], 
        campus_code="STL", description="", title="S2",
        course_code="CSCI 1000", semester="Fall", meeting_times=[mt2]
    )
    
    all_sections = [s1, s2]

    # Setup Degree
    req = DegreeRequirement(
        label="Req", needed=1,
        course_rules=CourseRule(
            courses=[CourseWithCode("CSCI", "1000")],
            exclude=[]
        )
    )
    degree = Degree(
        id=1, name="CS", degree_works_major_code="CS", 
        degree_works_degree_type="BS",
        degree_works_college_code="ENGI", requirements=[req]
    )

    # Create instructor ratings map
    # Michael Goldwasser has a high rating (4.2)
    # Low Rated Instructor has a low rating (1.5)
    instructor_ratings_map = {
        "Michael Goldwasser": 4.2,
        "michael goldwasser": 4.2,  # lowercase for case-insensitive matching
        "Low Rated Instructor": 1.5,
        "low rated instructor": 1.5,
    }

    schedule = get_schedule(
        degree=degree,
        student=Student(
            id=1, name="Test", degree_id=1, graduation_year=2025,
            completed_course_ids=[], desired_course_ids=[],
            unavailability_times=[], avoid_times=[]
        ),
        taken_courses=[],
        all_courses=all_courses,
        all_sections=all_sections,
        course_equivalencies=[],
        instructor_ratings_map=instructor_ratings_map,
    )
    
    # Should pick the section with the higher-rated instructor
    assert len(schedule) == 1
    assert schedule[0].section.crn == "1"  # Michael Goldwasser's section
    assert schedule[0].section.instructor_names == ["Michael Goldwasser"]
```

### Run the Tests
```bash
cd backend
uv run pytest tests/domain/test_schedule.py::TestSchedule::test_get_schedule_prioritizes_high_rated_instructors -v
```

## Verification Checklist

- [ ] Backend server starts without errors
- [ ] `/api/instructors` endpoint returns instructors with `rmpRating` values
- [ ] `/api/degree-requirements/autogenerate-schedule` endpoint returns sections
- [ ] Sections include `instructorNames` field
- [ ] When comparing sections of the same course, higher-rated instructors appear first
- [ ] Unit test passes

## Debugging Tips

1. **Check if instructors have ratings:**
   ```bash
   curl "http://localhost:8000/api/instructors" | jq '.[] | select(.rmpRating != null) | {name, rmpRating}'
   ```

2. **Check section instructor names match database:**
   - Compare section `instructorNames` with instructor names in database
   - Note: Matching is case-insensitive

3. **Verify the scoring:**
   - Add debug prints in `get_section_score` function
   - Check that `instructor_ratings_map` is populated
   - Verify average rating calculation

4. **Test edge cases:**
   - Sections with no instructors
   - Sections with instructors that don't have ratings
   - Sections with multiple instructors (should average ratings)


