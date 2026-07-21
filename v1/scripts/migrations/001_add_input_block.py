import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profile_common import MEMBERS_DIR, FRONTMATTER_PATTERN
from profile_renderer import build_readme

INPUT_MARKER = "<!-- profile:input"

OLD_DISPLAY_NAME = re.compile(
    r"<!-- profile:display_name:start -->\s*#\s*(.+?)\s*<!-- profile:display_name:end -->", re.S
)
OLD_GITHUB_HREF = re.compile(
    r'<!-- profile:github:start -->.*?href="https://github\.com/([^"/]+)".*?<!-- profile:github:end -->',
    re.S,
)
SECTION_PATTERN = re.compile(r"<!-- profile:(\w+):start -->(.*?)<!-- profile:\1:end -->", re.S)


def _section_body(sections, key, default=""):
    raw = sections.get(key, default)
    lines = raw.strip().splitlines()
    return "\n".join(lines[1:]).strip() if lines and lines[0].startswith("##") else raw.strip()


def migrate(readme_path):
    text = readme_path.read_text(encoding="utf-8")
    if INPUT_MARKER in text:
        return False

    meta_match = FRONTMATTER_PATTERN.search(text)
    if not meta_match:
        return False

    frontmatter = yaml.safe_load(meta_match.group(1)) or {}
    display_name = (
        m.group(1).strip() if (m := OLD_DISPLAY_NAME.search(text)) else frontmatter.get("display_name", "")
    )
    github = (
        m.group(1) if (m := OLD_GITHUB_HREF.search(text)) else frontmatter.get("github", "")
    )

    sections = {m.group(1): m.group(2).strip() for m in SECTION_PATTERN.finditer(text)}

    frontmatter.update({
        "display_name": display_name,
        "github": github,
        "bio": frontmatter.get("bio", ""),
        "specialties": frontmatter.get("specialties", ""),
    })

    new_text = build_readme(
        frontmatter,
        bio=frontmatter["bio"],
        specialties=frontmatter["specialties"],
        community_contributions=_section_body(sections, "community_contributions"),
        external_contributions=_section_body(sections, "external_contributions"),
        achievements_body=_section_body(sections, "honors", "（暂无）"),
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
