# Instructor Ratings and Sections Overview

## How Ratings Are Stored

### Database Structure
Ratings are stored in the `instructors` table with the following fields:
- `id`: Primary key
- `name`: Instructor name (string)
- `rmp_rating`: Overall RMP rating (float, nullable) - **This is what we use for scoring**
- `rmp_num_ratings`: Number of ratings (int, nullable)
- `rmp_url`: RMP profile URL (string, nullable)
- `department`: Department code (string, nullable) - e.g., "CSCI", "MATH"

### Data Sources
Ratings come from JSON files in `backend/data_dumps/`:
- **CSCI Department:**
  - `cs_professors_with_reviews.json` (preferred - has reviews)
  - `cs_professors.json` (fallback - aggregated data only)
  
- **MATH Department:**
  - `math_professors_with_reviews.json` (preferred - has reviews)
  - `math_professors.json` (fallback - aggregated data only)

**Important:** Currently, **only CSCI and MATH departments have RMP ratings**. Other departments will not have ratings in the system.

### Rating Data Format
From the JSON files, each professor has:
```json
{
  "name": "Michael Liljegren",
  "overall_rating": 4.4,
  "num_ratings": 7,
  "profile_url": "https://www.ratemyprofessors.com/professor/2999302",
  "department": null,  // Added as "CSCI" or "MATH" during import
  "department_id": 11
}
```

The `overall_rating` field becomes `rmp_rating` in the database.

## How Sections Are Structured

### Section Domain Model
Sections have the following structure:
```python
Section(
    id: int | None,
    crn: str,                    # Course Registration Number
    instructor_names: list[str], # List of instructor names (e.g., ["Michael Goldwasser"])
    campus_code: str,            # e.g., "North Campus (Main Campus)"
    description: str,
    title: str,
    course_code: str,            # e.g., "CSCI 1000"
    semester: str,                # e.g., "202620"
    meeting_times: list[MeetingTime]
)
```

### Key Field: `instructor_names`
- **Type:** `list[str]` - A list of instructor name strings
- **Example:** `["Michael Goldwasser"]` or `["Instructor A", "Instructor B"]`
- **Multiple Instructors:** If a section has multiple instructors, they're all in the list
- **Empty List:** Some sections may have `[]` if no instructor is assigned

### Database Storage
In the `sections` table:
- `instructor_names` is stored as JSON: `["Michael Goldwasser"]`
- This is converted to/from the domain model automatically

## How Ratings Are Used in Schedule Scoring

### Current Implementation
1. **Fetch all instructors** from the database via `InstructorRepository.get_all()`
2. **Create a mapping** of instructor name → RMP rating:
   ```python
   instructor_ratings_map = {
       "Michael Goldwasser": 4.2,
       "michael goldwasser": 4.2,  # lowercase for case-insensitive matching
       "Low Rated Prof": 1.5,
       "low rated prof": 1.5
   }
   ```
3. **For each section**, calculate average instructor rating:
   - Get `section.instructor_names` (e.g., `["Michael Goldwasser"]`)
   - Look up each instructor's rating in the map
   - Calculate average: `sum(ratings) / len(ratings)`
   - Add average to section score

### Example Scoring
```python
# Section 1: CSCI 1000 with Michael Goldwasser (rating: 4.2)
section1.instructor_names = ["Michael Goldwasser"]
avg_rating = 4.2
score = course_score + 4.2  # Instructor rating added

# Section 2: CSCI 1000 with Low Rated Prof (rating: 1.5)
section2.instructor_names = ["Low Rated Prof"]
avg_rating = 1.5
score = course_score + 1.5  # Lower score, so ranked lower

# Section 3: CSCI 2000 with no instructor
section3.instructor_names = []
avg_rating = None  # No rating to add
score = course_score  # No bonus, but not penalized
```

## Limitations

### Department Coverage
- **Only CSCI and MATH** departments have ratings
- Instructors from other departments will have `rmp_rating = None`
- Sections with instructors from other departments won't get rating bonuses

### Name Matching
- Matching is **case-insensitive** (handled in the implementation)
- Names must match exactly (after normalization)
- Variations like "Greg" vs "Gregory" are handled in `update_instructor_rmp_data.py`

### Missing Data Handling
- Sections with **no instructors** (`instructor_names = []`) → No rating bonus
- Sections with **instructors without ratings** (`rmp_rating = None`) → No rating bonus
- These sections are **not penalized**, they just don't get the bonus

## Verification

### Check Which Instructors Have Ratings
```bash
# Via API
curl http://localhost:8000/api/instructors | jq '.[] | select(.rmpRating != null) | {name, rmpRating, department}'

# Via database (if you have access)
sqlite3 backend/data/data.db "SELECT name, rmp_rating, department FROM instructors WHERE rmp_rating IS NOT NULL;"
```

### Check Section Instructor Names
```bash
# Via database
sqlite3 backend/data/data.db "SELECT course_code, instructor_names FROM sections WHERE instructor_names != '[]' LIMIT 10;"
```

## Summary

✅ **What we have:**
- RMP ratings for CSCI and MATH instructors
- Ratings stored in `instructors.rmp_rating` field
- Sections have `instructor_names` list
- Implementation adds average instructor rating to section scores

⚠️ **Limitations:**
- Only CSCI and MATH departments have ratings
- Other departments won't benefit from instructor rating scoring
- Name matching must be exact (with normalization)

🔧 **Current Implementation:**
- Fetches all instructors and creates name→rating map
- Matches section instructor names to ratings (case-insensitive)
- Averages ratings for sections with multiple instructors
- Adds average rating to section score in `get_section_score()`


