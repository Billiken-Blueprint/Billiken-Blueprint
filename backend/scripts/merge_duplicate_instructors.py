"""Merge duplicate instructors (e.g., Ted Ahn and Tae Ahn)."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor


def normalize_name_for_matching(name: str) -> str:
    """Normalize name for matching (e.g., Ted Ahn variations)."""
    name_lower = name.lower()
    # Normalize Ted Ahn variations
    if "ahn" in name_lower and ("ted" in name_lower or "tae" in name_lower):
        return "ted ahn"
    return name_lower.strip()


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
    for normalized, instructors in duplicates.items():
        print(f"\n  Normalized: '{normalized}'")
        for inst in instructors:
            print(f"    - ID {inst.id}: '{inst.name}' (dept: {inst.department}, rmp_rating: {inst.rmp_rating})")
    
    print("\n" + "=" * 60)
    print("To merge duplicates, you would need to:")
    print("1. Choose the 'canonical' instructor (usually the one with RMP data)")
    print("2. Update all references (sections, ratings) to point to the canonical one")
    print("3. Delete the duplicate entries")
    print("\nThis is a destructive operation - run manually after reviewing duplicates.")


if __name__ == "__main__":
    asyncio.run(merge_duplicate_instructors())

