"""
Migration 004 — Remove specialties_title from member frontmatters.

specialties_title was originally intended to let members customise the
section heading, but the feature was reverted: the heading is now a
fixed string ("特长") and the field is no longer written or read by
any script.  This migration strips the leftover key from every existing
profile so the frontmatter stays tidy.
"""

import os
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(os.environ.get("DATA_ROOT", Path(__file__).resolve().parent.parent.parent))
MEMBERS_DIR = ROOT / "members"
FRONTMATTER_PATTERN = re.compile(r"(<!-- profile:meta\n)(.*?)(\n-->)", re.S)


def migrate_profile(readme_path: Path) -> bool:
    text = readme_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.search(text)
    if not match:
        print(f"  skip (no frontmatter): {readme_path}")
        return False

    frontmatter = yaml.safe_load(match.group(2)) or {}
    if "specialties_title" not in frontmatter:
        return False

    del frontmatter["specialties_title"]
    new_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    new_text = FRONTMATTER_PATTERN.sub(
        lambda m: m.group(1) + new_yaml.rstrip("\n") + m.group(3),
        text,
    )
    readme_path.write_text(new_text, encoding="utf-8")
    print(f"  migrated: {readme_path.parent.name}")
    return True


def main():
    if not MEMBERS_DIR.exists():
        print("No members directory found, nothing to do.")
        return

    changed = []
    for member_dir in sorted(MEMBERS_DIR.iterdir()):
        readme = member_dir / "README.md"
        if readme.exists() and migrate_profile(readme):
            changed.append(member_dir.name)

    if changed:
        print(f"\nDone. Migrated {len(changed)} profile(s): {', '.join(changed)}")
    else:
        print("No profiles needed migration.")


if __name__ == "__main__":
    main()
