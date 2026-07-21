import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profile_common import MEMBERS_DIR, FRONTMATTER_PATTERN
from profile_renderer import build_readme, TEMPLATE_VERSION, DEFAULT_SPECIALTIES_TITLE
from watch_profile import parse_input_block, extract_section_body


def migrate(readme_path):
    text = readme_path.read_text(encoding="utf-8")
    meta_match = FRONTMATTER_PATTERN.search(text)
    if not meta_match:
        return False

    frontmatter = yaml.safe_load(meta_match.group(1)) or {}
    if str(frontmatter.get("template_version", "1")) == TEMPLATE_VERSION:
        return False

    parsed = parse_input_block(text)
    if parsed:
        frontmatter.update(parsed)

    frontmatter["template_version"] = TEMPLATE_VERSION

    old_honors = extract_section_body(text, "honors")
    old_honors_lines = old_honors.splitlines()
    if old_honors_lines and old_honors_lines[0].startswith("##"):
        old_honors = "\n".join(old_honors_lines[1:]).strip()

    new_text = build_readme(
        frontmatter,
        bio=frontmatter.get("bio", ""),
        specialties=frontmatter.get("specialties", ""),
        specialties_title=frontmatter.get("specialties_title", DEFAULT_SPECIALTIES_TITLE),
        community_contributions=extract_section_body(text, "community_contributions"),
        external_contributions=extract_section_body(text, "external_contributions"),
        achievements_body=old_honors or "（暂无）",
    )
    readme_path.write_text(new_text, encoding="utf-8")
    return True


def main():
    if not MEMBERS_DIR.exists():
        return
    migrated = [
        member_dir.name
        for member_dir in sorted(MEMBERS_DIR.iterdir())
        if member_dir.is_dir() and migrate(member_dir / "README.md")
    ]
    print(f"migrated: {', '.join(migrated)}" if migrated else "nothing to migrate")


if __name__ == "__main__":
    main()
