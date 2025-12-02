# Testing RMP Reviews Feature

## Quick Test Steps

### 1. **Check Database Setup**
```bash
# Check if migration ran
docker compose exec backend alembic current

# Check if reviews table exists
docker compose exec backend python -c "import sqlite3; conn = sqlite3.connect('/app/data/data.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"rmp_reviews\"'); print('Table exists:', cursor.fetchone() is not None)"

# Check review count
docker compose exec backend python -c "import sqlite3; conn = sqlite3.connect('/app/data/data.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM rmp_reviews'); print('Total reviews:', cursor.fetchone()[0])"
```

### 2. **Test API Endpoint**
```bash
# Get reviews for instructor ID 6 (Michael Liljegren)
curl http://localhost:8000/api/instructors/6/reviews | python3 -m json.tool

# Should return an array of review objects with:
# - id, instructorId, course, quality, difficulty, comment
# - wouldTakeAgain, grade, attendance, tags, reviewDate
```

### 3. **Test in Browser**

1. **Open the app**: Go to `http://localhost:4200/courses`

2. **Navigate to a course with instructors**:
   - Click on any course group (e.g., "Intro to CS")
   - Click on a course card (e.g., "CSCI 1300")
   - Click the "Instructors" section to expand it

3. **Click on an instructor**:
   - Click on an instructor name (e.g., "Michael Liljegren")
   - OR click the "View reviews" button
   - A modal should open showing all RMP reviews for that instructor

4. **Verify the modal shows**:
   - ✅ Instructor name in header
   - ✅ Individual review cards
   - ✅ Each review shows: rating, comment, course (if available)
   - ✅ Difficulty, grade, attendance, "would take again" status
   - ✅ Tags (if any)
   - ✅ Review date (if available)

### 4. **Check Browser Console**
- Open DevTools (F12)
- Go to Network tab
- Click on an instructor
- Look for: `GET /api/instructors/{id}/reviews`
- Should return 200 with JSON array of reviews

### 5. **Common Issues**

**No reviews showing:**
- Check if reviews were imported: `docker compose exec backend python -c "import sqlite3; conn = sqlite3.connect('/app/data/data.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM rmp_reviews'); print(cursor.fetchone()[0])"`
- Run import manually: `docker compose exec backend python /app/import_rmp_ratings.py`

**Modal doesn't open:**
- Check browser console for errors
- Verify instructor has an ID (check Network tab for `/api/instructors` call)
- Make sure instructor name matches between course page and backend

**API returns 404:**
- Check backend logs: `docker compose logs backend | tail -20`
- Verify endpoint exists: `curl http://localhost:8000/api/instructors/6/reviews`

**Migration issues:**
- Check current migration: `docker compose exec backend alembic current`
- Run migrations: `docker compose exec backend alembic upgrade head`

## Expected Behavior

✅ **Working correctly when:**
- Clicking instructor name opens modal
- Modal displays all reviews for that instructor
- Each review shows complete information
- Reviews are scrollable if there are many
- Modal closes when clicking outside or X button
- "View reviews" button appears for instructors with reviews

❌ **Not working if:**
- Clicking does nothing
- Modal opens but is empty
- API returns 404 or 500
- Browser console shows errors

