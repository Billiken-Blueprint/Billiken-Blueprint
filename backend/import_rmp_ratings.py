"""Import RateMyProfessor ratings and reviews from JSON file and match with instructors."""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.domain.rmp_review import RmpReview


async def import_rmp_ratings():
    """Import RMP ratings and reviews from JSON file and update instructors."""
    # Load RMP data - try multiple possible locations, prioritize file with reviews
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir / "cs_professors_with_reviews.json",  # File with individual reviews
        script_dir / "cs_professors.json",  # File with just aggregated ratings
        script_dir.parent / "RateMyProfessor.com-Web-Scraper" / "cs_professors_with_reviews.json",
        script_dir.parent / "RateMyProfessor.com-Web-Scraper" / "cs_professors.json",
        Path("/app/cs_professors_with_reviews.json"),  # Absolute path in container
        Path("/app/cs_professors.json"),  # Absolute path in container
    ]
    
    rmp_file = None
    for path in possible_paths:
        if path.exists():
            rmp_file = path
            break
    
    if not rmp_file or not rmp_file.exists():
        print(f"RMP file not found in any of the expected locations")
        return
    
    print(f"Loading RMP data from: {rmp_file}")
    with open(rmp_file, 'r') as f:
        rmp_data = json.load(f)
    
    print(f"Loaded {len(rmp_data)} RMP professor records")
    
    # Get all existing instructors
    existing_instructors = await services.instructor_repository.get_all()
    instructor_by_name = {instructor.name.lower(): instructor for instructor in existing_instructors}
    
    matched = 0
    not_matched = []
    total_reviews = 0
    
    for rmp_prof in rmp_data:
        name = rmp_prof.get('name', '').strip()
        if not name:
            continue
        
        # Try exact match first
        instructor = instructor_by_name.get(name.lower())
        
        # If no exact match, try partial matches (handle variations like "Dr. Name" vs "Name")
        if not instructor:
            # Try matching by last name or removing middle names/initials
            rmp_name_parts = name.lower().split()
            for existing_name, existing_instructor in instructor_by_name.items():
                existing_parts = existing_name.split()
                # Match if last names match or if one name contains the other
                if (rmp_name_parts and existing_parts and 
                    rmp_name_parts[-1] == existing_parts[-1]):  # Last name match
                    instructor = existing_instructor
                    # Update name if RMP has a better version (e.g., "Tae-Hyuk (Ted) Ahn" -> "Ted Ahn")
                    if "ted" in name.lower() and "ted" not in existing_name.lower():
                        # Update to use Ted if RMP has it
                        updated_instructor = Professor(
                            id=existing_instructor.id,
                            name="Ted Ahn" if "ahn" in name.lower() else existing_instructor.name,
                            rmp_rating=rmp_prof.get('overall_rating'),
                            rmp_num_ratings=rmp_prof.get('num_ratings'),
                            rmp_url=rmp_prof.get('profile_url'),
                        )
                        await services.instructor_repository.save(updated_instructor)
                    break
                # Also try substring matching
                if name.lower() in existing_name or existing_name in name.lower():
                    instructor = existing_instructor
                    break
        
        if instructor:
            # Update instructor with RMP aggregated data
            updated_instructor = Professor(
                id=instructor.id,
                name=instructor.name,
                rmp_rating=rmp_prof.get('overall_rating'),
                rmp_num_ratings=rmp_prof.get('num_ratings'),
                rmp_url=rmp_prof.get('profile_url'),
            )
            await services.instructor_repository.save(updated_instructor)
            matched += 1
            
            # Import individual reviews if available (skip if table doesn't exist)
            reviews = rmp_prof.get('reviews', [])
            if reviews:
                try:
                    rmp_reviews = []
                    for review_data in reviews:
                        # Parse date if available
                        review_date = None
                        if review_data.get('date'):
                            try:
                                # Try to parse date string if it's in a standard format
                                review_date = datetime.fromisoformat(str(review_data['date']).replace('Z', '+00:00'))
                            except (ValueError, TypeError):
                                pass
                        
                        rmp_review = RmpReview(
                            id=None,  # Auto-increment
                            instructor_id=instructor.id,
                            course=review_data.get('course'),
                            quality=review_data.get('quality', 0.0),
                            difficulty=review_data.get('difficulty'),
                            comment=review_data.get('comment', ''),
                            would_take_again=review_data.get('would_take_again'),
                            grade=review_data.get('grade'),
                            attendance=review_data.get('attendance'),
                            tags=review_data.get('tags', []) or [],
                            review_date=review_date,
                        )
                        rmp_reviews.append(rmp_review)
                    
                    # Delete existing reviews for this instructor and save new ones
                    await services.rmp_review_repository.delete_by_instructor_id(instructor.id)
                    if rmp_reviews:
                        await services.rmp_review_repository.save_many(rmp_reviews)
                        total_reviews += len(rmp_reviews)
                        print(f"  → Imported {len(rmp_reviews)} reviews for {instructor.name}")
                except Exception as e:
                    # Skip reviews import if table doesn't exist or other error
                    print(f"  → Skipped reviews import for {instructor.name} (table may not exist)")
            
            print(f"✓ Matched: {name} -> {instructor.name} (Rating: {rmp_prof.get('overall_rating')})")
        else:
            not_matched.append(name)
            print(f"✗ No match found for: {name}")
    
    print(f"\nSummary:")
    print(f"  Matched instructors: {matched}/{len(rmp_data)}")
    print(f"  Total reviews imported: {total_reviews}")
    print(f"  Not matched: {len(not_matched)}")
    if not_matched:
        print(f"\nUnmatched professors:")
        for name in not_matched[:10]:  # Show first 10
            print(f"  - {name}")


if __name__ == "__main__":
    asyncio.run(import_rmp_ratings())
