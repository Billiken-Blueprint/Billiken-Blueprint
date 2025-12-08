# How Instructor Ratings Work in Autogenerate Schedule

## Current Implementation Flow

### Step 1: Data Collection (in `autogenerate_schedule` endpoint)

When you call `/api/degree-requirements/autogenerate-schedule`:

1. **Fetch All Instructors**
   ```python
   all_instructors = await instructor_repo.get_all()
   ```

2. **Create Rating Map - Two Sources:**

   **Source A: RMP Ratings (CSCI & MATH only)**
   ```python
   for instructor in all_instructors:
       if instructor.rmp_rating is not None:
           # Add to map with both original and lowercase keys
           instructor_ratings_map[instructor.name] = instructor.rmp_rating
           instructor_ratings_map[instructor.name.lower()] = instructor.rmp_rating
   ```

   **Source B: User-Submitted Ratings (All departments)**
   ```python
   all_user_ratings = await rating_repo.get_all()
   # Group by instructor_id
   # Calculate average for each instructor
   # Add to map ONLY if instructor doesn't have RMP rating
   ```

### Step 2: Rating Map Structure

The `instructor_ratings_map` looks like:
```python
{
    "Michael Goldwasser": 4.2,        # RMP rating (CSCI)
    "michael goldwasser": 4.2,        # lowercase version
    "John Smith": 4.67,               # User rating average (ENGL)
    "john smith": 4.67,               # lowercase version
    "Jane Doe": 3.5,                  # User rating average (HIST)
    "jane doe": 3.5,                  # lowercase version
}
```

### Step 3: Scoring Sections (in `get_section_score`)

For each section in the schedule:

1. **Get Section's Instructor Names**
   ```python
   section.instructor_names  # e.g., ["Michael Goldwasser"]
   ```

2. **Look Up Ratings**
   ```python
   for name in section.instructor_names:
       rating = instructor_ratings_map.get(name) or instructor_ratings_map.get(name.lower())
       if rating:
           instructor_ratings.append(rating)
   ```

3. **Calculate Average**
   ```python
   if instructor_ratings:
       avg_rating = sum(instructor_ratings) / len(instructor_ratings)
       score += avg_rating  # Add to section score
   ```

### Step 4: Section Ranking

Sections are sorted by their total score:
- **Base score** (from course requirements/prerequisites)
- **+ Average instructor rating** (if available)
- **- 10 points** (if overlaps with avoid_times)

Higher total score = Higher priority in schedule

## Example Flow

### Example 1: CSCI Course with RMP Rating

**Section:** CSCI 1000, Instructor: "Michael Goldwasser"
1. Base course score: 5.0
2. Look up "Michael Goldwasser" → Found RMP rating: 4.2
3. Total score: 5.0 + 4.2 = **9.2**

### Example 2: ENGL Course with User Ratings

**Section:** ENGL 1900, Instructor: "John Smith"
1. Base course score: 3.0
2. Look up "John Smith" → Found user rating average: 4.67
3. Total score: 3.0 + 4.67 = **7.67**

### Example 3: HIST Course with No Ratings

**Section:** HIST 1000, Instructor: "Jane Doe"
1. Base course score: 2.0
2. Look up "Jane Doe" → Not found (no ratings)
3. Total score: 2.0 (no bonus, but not penalized)

### Example 4: Multiple Instructors

**Section:** CSCI 2000, Instructors: ["Michael Goldwasser", "Assistant Prof"]
1. Base course score: 6.0
2. Look up "Michael Goldwasser" → 4.2
3. Look up "Assistant Prof" → Not found
4. Average rating: 4.2 / 1 = 4.2 (only count instructors with ratings)
5. Total score: 6.0 + 4.2 = **10.2**

## Key Features

✅ **Dual Source System**
- RMP ratings (external, CSCI/MATH)
- User ratings (internal, all departments)

✅ **Priority System**
- RMP ratings take precedence
- User ratings used as fallback

✅ **Case-Insensitive Matching**
- Handles "Michael Goldwasser" vs "michael goldwasser"

✅ **Multiple Instructors**
- Averages ratings if section has multiple instructors
- Only counts instructors with ratings

✅ **Graceful Degradation**
- Sections without ratings still work
- No penalty for missing ratings

## Current Status

**What's Working:**
- ✅ RMP ratings from CSCI/MATH are used
- ✅ User-submitted ratings are aggregated and used
- ✅ Ratings are added to section scores
- ✅ Sections with better instructors rank higher

**What's Not Working (if any):**
- ⚠️ If no user ratings exist yet, only CSCI/MATH get rating bonuses
- ⚠️ Single user ratings are used (could be biased)
- ⚠️ No minimum threshold for user ratings

## Data Flow Diagram

```
┌─────────────────────────────────────────┐
│  autogenerate_schedule endpoint          │
├─────────────────────────────────────────┤
│  1. Fetch all instructors                │
│  2. Fetch all user ratings              │
│  3. Build instructor_ratings_map:       │
│     - RMP ratings (CSCI/MATH)            │
│     - User rating averages (all depts)   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  get_schedule() function                 │
├─────────────────────────────────────────┤
│  Calls get_recommended_sections()        │
│  Passes instructor_ratings_map           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  get_recommended_sections()              │
├─────────────────────────────────────────┤
│  For each section:                      │
│  1. Calculate base course score          │
│  2. Look up instructor ratings           │
│  3. Add average rating to score          │
│  4. Sort by total score                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Returned Schedule (ranked by score)    │
│  - Higher-rated instructors first       │
│  - Better course matches prioritized    │
└─────────────────────────────────────────┘
```

## Testing

To verify it's working:

1. **Check the rating map is populated:**
   - Add logging: `print(f"Instructor ratings map: {len(instructor_ratings_map)} entries")`
   - Should show entries for CSCI/MATH (RMP) + any instructors with user ratings

2. **Check section scoring:**
   - Add logging in `get_section_score`: `print(f"Section {section.course_code} score: {score}, instructors: {section.instructor_names}")`
   - Should show higher scores for sections with rated instructors

3. **Verify ranking:**
   - Generate schedule
   - Check that sections with higher-rated instructors appear first
   - Compare sections of the same course with different instructors


