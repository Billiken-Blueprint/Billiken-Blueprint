# Testing Instructor Ratings on the Website

## Step-by-Step Guide

### 1. Start the Application
```bash
# Make sure both backend and frontend are running
docker compose up
# Or separately:
# Terminal 1: docker compose up backend
# Terminal 2: docker compose up web
```

### 2. Navigate to the Scheduling Page

1. **Open your browser** and go to: `http://localhost:4200`

2. **Login** (if not already logged in):
   - Go to `/login` or `/register`
   - Complete authentication

3. **Navigate to the Scheduling Page**:
   - Click on "Schedule" in the navigation menu
   - Or go directly to: `http://localhost:4200/schedule`

### 3. Generate a Schedule

1. On the scheduling page, you'll see:
   - **Degree Requirements** section (collapsible)
   - **Your Spring 2026 Schedule** section (collapsible)

2. **Click "Autogenerate Schedule"** button
   - This will call the backend API that now includes instructor ratings in scoring

3. **Wait for the schedule to load**
   - You'll see a weekly calendar grid with courses
   - Below that, you'll see a "Recommended Sections" list

### 4. Verify Instructor Ratings Are Working

#### Method 1: Check the Schedule Grid
- Look at the courses displayed in the weekly calendar
- Each course block shows:
  - Course code (e.g., "CSCI 1000")
  - Course title
  - **Instructor name** (first instructor if multiple)
  - Meeting times

#### Method 2: Check the Recommended Sections List
- Scroll down to see the "Recommended Sections" panel
- Sections are listed in order of priority (highest first)
- Sections with higher-rated instructors should appear earlier

#### Method 3: Compare Sections of the Same Course
To verify ratings are affecting the order:

1. **Check which instructors have ratings:**
   - Go to: `http://localhost:4200/ratings` or check the instructors page
   - Note which instructors have high ratings (4.0+) vs low ratings (2.0-)

2. **Look for courses with multiple sections:**
   - If a course appears multiple times in the recommended sections
   - The section with the higher-rated instructor should appear first

3. **Example verification:**
   - If "CSCI 1000" has two sections:
     - Section 1: Instructor "Michael Goldwasser" (rating: 4.2)
     - Section 2: Instructor "Low Rated Prof" (rating: 1.5)
   - Section 1 should appear before Section 2 in the list

### 5. What to Look For

✅ **Signs it's working:**
- Sections with instructors rated 4.0+ appear early in the list
- When comparing sections of the same course, higher-rated instructors are prioritized
- The schedule grid shows instructor names

❌ **If it's not working:**
- All sections appear in random order (not sorted by instructor rating)
- Sections with low-rated instructors appear before high-rated ones
- No instructor names are displayed

### 6. Debugging Tips

#### Check Browser Console
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for any errors when clicking "Autogenerate Schedule"

#### Check Network Tab
1. Open Developer Tools (F12)
2. Go to Network tab
3. Click "Autogenerate Schedule"
4. Find the request to `/api/degree-requirements/autogenerate-schedule`
5. Check the Response - verify sections include `instructorNames`

#### Verify Instructors Have Ratings
1. Check the instructors endpoint:
   ```bash
   curl http://localhost:8000/api/instructors | jq '.[] | select(.rmpRating != null) | {name, rmpRating}'
   ```
2. Or check in the browser: `http://localhost:4200/instructors` (if that route exists)

### 7. Visual Verification

The schedule page shows:
- **Weekly Calendar Grid**: Courses displayed with instructor names
- **Recommended Sections List**: Ordered list showing which sections were selected

**Key indicators:**
- Instructor names are visible in the course blocks
- The order of sections reflects instructor quality (higher-rated = higher priority)
- Multiple sections of the same course are ordered by instructor rating

### 8. Expected Behavior

When instructor ratings are working correctly:

1. **First section selected** for a course should have the highest-rated instructor
2. **If two courses have equal requirement scores**, the one with better instructors ranks higher
3. **Sections with no instructors** or **instructors without ratings** are not penalized (they just don't get the bonus)

### Quick Test Scenario

1. Find a course that has multiple sections with different instructors
2. Note which instructor has a higher RMP rating
3. Generate the schedule
4. Verify the section with the higher-rated instructor appears first in the recommended sections list

---

## Alternative: Check via Browser DevTools

You can also verify the API response directly:

1. Open DevTools (F12) → Network tab
2. Click "Autogenerate Schedule"
3. Find the `autogenerate-schedule` request
4. Click on it → Response tab
5. Check the `sections` array - they should be ordered with higher-rated instructors first


