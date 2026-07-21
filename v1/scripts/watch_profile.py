import os
import re

import yaml

from profile_common import (
    FRONTMATTER_PATTERN,
    MEMBERS_DIR,
    WARNING_START,
    clear_warning,
    write_warning,
    existing_profiles,
    render_readme,
)

DISPLAY_NAME_PATTERN = re.compile(
    r"<!-- profile:display_name:start -->\s*#\s*(.+?)\s*<!-- profile:display_name:end -->", re.S
)
GITHUB_MARKER_PATTERN = re.compile(
    r"<!-- profile:github:start -->(.*?)<!-- profile:github:end -->", re.S
)
GITHUB_HREF_PATTERN = re.compile(r'href="https://github\.com/([^"/]+)"')


def live_display_name(text, fallback):
    match = DISPLAY_NAME_PATTERN.search(text)
    return match.group(1).strip() if match else fallback


def live_github(text, fallback):
    match = GITHUB_MARKER_PATTERN.search(text)
    if not match:
        return fallback
    href_match = GITHUB_HREF_PATTERN.search(match.group(1))
    return href_match.group(1) if href_match else ""


def reconcile_member(member_dir):
    readme_path = member_dir / "README.md"
    if not readme_path.exists():
        return False
    text = readme_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.search(text)
    if not match:
        write_warning(readme_path, "profile:meta block missing or malformed")
        return True

    had_warning = WARNING_START in text
    clear_warning(readme_path)
    text = readme_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.search(text)

    frontmatter = yaml.safe_load(match.group(1)) or {}
    display_name = live_display_name(text, frontmatter.get("display_name", ""))
    github = live_github(text, frontmatter.get("github", ""))

    if frontmatter.get("display_name") == display_name and frontmatter.get("github") == github:
        return had_warning

    frontmatter["display_name"] = display_name
    frontmatter["github"] = github
    new_block = "<!-- profile:meta\n" + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False) + "-->"
    readme_path.write_text(text[: match.start()] + new_block + text[match.end() :], encoding="utf-8")
    return True


def target_members():
    raw = os.environ.get("INPUT_MEMBER_ID", "").strip()
    if not raw:
        return sorted(path for path in MEMBERS_DIR.iterdir() if path.is_dir())
    return [MEMBERS_DIR / member_id.strip() for member_id in raw.split(",") if member_id.strip()]


def main():
    changed = [member_dir.name for member_dir in target_members() if reconcile_member(member_dir)]
    if changed:
        print(f"reconciled: {', '.join(changed)}")
        render_readme(existing_profiles())
    else:
        print("no changes detected")


if __name__ == "__main__":
    main()
