"""Import RateMyProfessor ratings from JSON file and match with instructors."""
import asyncio
import json
from pathlib import Path
from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor


async def import_rmp_ratings():
    """Import RMP ratings from JSON file and update instructors."""
    # Load RMP data - try multiple possible locations
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir / "cs_professors.json",  # Same directory as script
        script_dir.parent / "RateMyProfessor.com-Web-Scraper" / "cs_professors.json",  # Project root
        Path("/app/cs_professors.json"),  # Absolute path in container
    ]
    
    rmp_file = None
    for path in possible_paths:
        if path.exists():
            rmp_file = path
            break
    
    if not rmp_file.exists():
        print(f"RMP file not found: {rmp_file}")
        return
    
    with open(rmp_file, 'r') as f:
        rmp_data = json.load(f)
    
    print(f"Loaded {len(rmp_data)} RMP professor records")
    
    # Get all existing instructors
    existing_instructors = await services.instructor_repository.get_all()
    instructor_by_name = {instructor.name.lower(): instructor for instructor in existing_instructors}
    
    matched = 0
    not_matched = []
    
    for rmp_prof in rmp_data:
        name = rmp_prof.get('name', '').strip()
        if not name:
            continue
        
        # Try exact match first
        instructor = instructor_by_name.get(name.lower())
        
        # If no exact match, try partial matches (handle variations like "Dr. Name" vs "Name")
        if not instructor:
            for existing_name, existing_instructor in instructor_by_name.items():
                if name.lower() in existing_name or existing_name in name.lower():
                    instructor = existing_instructor
                    break
        
        if instructor:
            # Update instructor with RMP data
            updated_instructor = Professor(
                id=instructor.id,
                name=instructor.name,
                rmp_rating=rmp_prof.get('overall_rating'),
                rmp_num_ratings=rmp_prof.get('num_ratings'),
                rmp_url=rmp_prof.get('profile_url'),
            )
            await services.instructor_repository.save(updated_instructor)
            matched += 1
            print(f"✓ Matched: {name} -> {instructor.name} (Rating: {rmp_prof.get('overall_rating')})")
        else:
            not_matched.append(name)
            print(f"✗ No match found for: {name}")
    
    print(f"\nSummary:")
    print(f"  Matched: {matched}/{len(rmp_data)}")
    print(f"  Not matched: {len(not_matched)}")
    if not_matched:
        print(f"\nUnmatched professors:")
        for name in not_matched[:10]:  # Show first 10
            print(f"  - {name}")


if __name__ == "__main__":
    asyncio.run(import_rmp_ratings())

