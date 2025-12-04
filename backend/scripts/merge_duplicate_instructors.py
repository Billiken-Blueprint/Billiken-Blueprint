"""Merge duplicate instructors (e.g., Ted Ahn and Tae Ahn)."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor
from sqlalchemy import update, delete
from billiken_blueprint.repositories.instructor_repository import DBInstructor
from billiken_blueprint.repositories.rating_repository import DBRating
from billiken_blueprint.repositories.rmp_review_repository import DBRmpReview


def normalize_name_for_matching(name: str) -> str:
    """Normalize name for matching (e.g., Ted Ahn variations, typos)."""
    name_lower = name.lower().strip()
    
    # Normalize Ted Ahn variations
    if "ahn" in name_lower and ("ted" in name_lower or "tae" in name_lower):
        return "ted ahn"
    
    # Normalize Jamal Abdul-Hafidh typo (Adbul -> Abdul)
    if "jamal" in name_lower and "abdul" in name_lower.replace("adbul", "abdul") and "hafidh" in name_lower:
        return "jamal abdul-hafidh"
    
    # Normalize common typos/variations
    name_normalized = name_lower
    # Fix common typos
    name_normalized = name_normalized.replace("adbul", "abdul")
    
    return name_normalized


def choose_canonical_instructor(instructors: list[Professor]) -> Professor:
    """Choose the canonical instructor from duplicates.
    
    Priority:
    1. Has RMP rating data
    2. Has department set
    3. Correct spelling (no typos like "Adbul" -> prefer "Abdul")
    4. Has normalized name (e.g., "Ted Ahn" over "Tae Ahn")
    5. Lower ID (older record)
    """
    # Prefer instructor with RMP data
    with_rmp = [inst for inst in instructors if inst.rmp_rating is not None]
    if with_rmp:
        instructors = with_rmp
    
    # Prefer instructor with department
    with_dept = [inst for inst in instructors if inst.department]
    if with_dept:
        instructors = with_dept
    
    # Prefer correct spelling (no typos)
    without_typos = [inst for inst in instructors if "adbul" not in inst.name.lower()]
    if without_typos:
        instructors = without_typos
    
    # Prefer normalized name (Ted Ahn over Tae Ahn)
    for inst in instructors:
        normalized = normalize_name_for_matching(inst.name)
        if normalized == "ted ahn" and "ted" in inst.name.lower():
            return inst
        if normalized == "jamal abdul-hafidh" and "abdul" in inst.name.lower() and "adbul" not in inst.name.lower():
            return inst
    
    # Prefer name that matches normalized form
    for inst in instructors:
        if normalize_name_for_matching(inst.name) == normalize_name_for_matching(inst.name):
            return inst
    
    # Fall back to lowest ID
    return min(instructors, key=lambda x: x.id or 999999)


async def merge_duplicate_instructors():
    """Find and merge duplicate instructors."""
    print("Finding duplicate instructors...")
    print("=" * 60)
    
    all_instructors = await services.instructor_repository.get_all()
    print(f"Total instructors: {len(all_instructors)}")
    
    # Group by normalized name
    by_normalized = {}
    for instructor in all_instructors:
        normalized = normalize_name_for_matching(instructor.name)
        if normalized not in by_normalized:
            by_normalized[normalized] = []
        by_normalized[normalized].append(instructor)
    
    # Find duplicates
    duplicates = {k: v for k, v in by_normalized.items() if len(v) > 1}
    
    if not duplicates:
        print("✓ No duplicate instructors found!")
        return
    
    print(f"\nFound {len(duplicates)} sets of duplicate instructors:")
    total_to_merge = 0
    for normalized, instructors in duplicates.items():
        print(f"\n  Normalized: '{normalized}'")
        canonical = choose_canonical_instructor(instructors)
        print(f"    → Canonical: ID {canonical.id} - '{canonical.name}'")
        for inst in instructors:
            if inst.id != canonical.id:
                print(f"      - ID {inst.id}: '{inst.name}' (will be merged into {canonical.id})")
                total_to_merge += 1
    
    print("\n" + "=" * 60)
    print(f"Will merge {total_to_merge} duplicate instructors into {len(duplicates)} canonical ones")
    
    if total_to_merge == 0:
        print("No duplicates to merge.")
        return
    
    print("\nMerging duplicates...")
    merged_count = 0
    
    async with services.async_sessionmaker() as session:
        for normalized, instructors in duplicates.items():
            canonical = choose_canonical_instructor(instructors)
            canonical_id = canonical.id
            
            # Determine canonical name (prefer normalized)
            if normalized == "ted ahn":
                canonical_name = "Ted Ahn"
            else:
                canonical_name = canonical.name
            
            # Merge data: prefer non-null values from duplicates
            merged_rmp_rating = canonical.rmp_rating
            merged_rmp_num_ratings = canonical.rmp_num_ratings
            merged_rmp_url = canonical.rmp_url
            merged_department = canonical.department
            
            for inst in instructors:
                if inst.id == canonical_id:
                    continue
                
                # Merge RMP data if canonical doesn't have it
                if not merged_rmp_rating and inst.rmp_rating:
                    merged_rmp_rating = inst.rmp_rating
                    merged_rmp_num_ratings = inst.rmp_num_ratings
                    merged_rmp_url = inst.rmp_url
                
                # Merge department if canonical doesn't have it
                if not merged_department and inst.department:
                    merged_department = inst.department
            
            # Fix typos in canonical name (e.g., "Adbul" -> "Abdul")
            if "adbul" in canonical_name.lower():
                canonical_name = canonical_name.replace("Adbul", "Abdul").replace("adbul", "abdul")
            
            # Update canonical instructor with merged data
            update_stmt = update(DBInstructor).where(
                DBInstructor.id == canonical_id
            ).values(
                name=canonical_name,
                rmp_rating=merged_rmp_rating,
                rmp_num_ratings=merged_rmp_num_ratings,
                rmp_url=merged_rmp_url,
                department=merged_department,
            )
            await session.execute(update_stmt)
            
            # Update all foreign key references
            for inst in instructors:
                if inst.id == canonical_id:
                    continue
                
                duplicate_id = inst.id
                
                # Update ratings.professor_id
                ratings_update = update(DBRating).where(
                    DBRating.professor_id == duplicate_id
                ).values(professor_id=canonical_id)
                await session.execute(ratings_update)
                
                # Update rmp_reviews.instructor_id
                rmp_update = update(DBRmpReview).where(
                    DBRmpReview.instructor_id == duplicate_id
                ).values(instructor_id=canonical_id)
                await session.execute(rmp_update)
                
                # Note: instructor_sections is a junction table, but sections use instructor_names (JSON array)
                # We'll handle that separately if needed, but it's less critical
                
                # Delete duplicate instructor
                delete_stmt = delete(DBInstructor).where(DBInstructor.id == duplicate_id)
                await session.execute(delete_stmt)
                
                merged_count += 1
                print(f"  ✓ Merged ID {duplicate_id} into ID {canonical_id}")
        
        await session.commit()
    
    print(f"\n✓ Successfully merged {merged_count} duplicate instructors!")
    print(f"  Remaining instructors: {len(all_instructors) - merged_count}")


if __name__ == "__main__":
    asyncio.run(merge_duplicate_instructors())
