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
from profile_renderer import build_readme, normalize_github

INPUT_PATTERN = re.compile(r"<!-- profile:input\n(.*?)-->", re.S)


def parse_input_block(text):
    match = INPUT_PATTERN.search(text)
    if not match:
        return None
    body = match.group(1)
    segments = re.split(r"\n-----\n", body)
    if len(segments) < 9:
        return None
    def value(seg):
        return seg.strip()
    return {
        "display_name": value(segments[2]),
        "github":       normalize_github(value(segments[4])),
        "bio":          value(segments[6]),
        "specialties":  value(segments[8]),
    }


def extract_section_body(text, key):
    match = re.search(rf"<!-- profile:{key}:start -->\n.*?\n\n(.*?)<!-- profile:{key}:end -->", text, re.S)
    if not match:
        return ""
    return match.group(1).strip()


def reconcile_member(member_dir):
    readme_path = member_dir / "README.md"
    if not readme_path.exists():
        return False
    text = readme_path.read_text(encoding="utf-8")
    meta_match = FRONTMATTER_PATTERN.search(text)
    if not meta_match:
        write_warning(readme_path, "profile:meta block missing or malformed")
        return True

    frontmatter = yaml.safe_load(meta_match.group(1)) or {}
    
    from profile_renderer import TEMPLATE_VERSION
    if str(frontmatter.get("template_version", "1")) != TEMPLATE_VERSION:
        write_warning(readme_path, f"Template version is outdated (current: {frontmatter.get('template_version', '1')}, latest: {TEMPLATE_VERSION}). Please run v1 - Migrate Profiles to upgrade.")
        return True

    had_warning = WARNING_START in text
    clear_warning(readme_path)
    text = readme_path.read_text(encoding="utf-8")
    meta_match = FRONTMATTER_PATTERN.search(text)

    frontmatter = yaml.safe_load(meta_match.group(1)) or {}
    parsed = parse_input_block(text)

    if parsed is None:
        write_warning(readme_path, "profile:input block missing or malformed")
        return True

    changed = any(frontmatter.get(k) != parsed[k] for k in parsed)
    if not changed:
        return had_warning

    frontmatter.update(parsed)
    new_text = build_readme(
        frontmatter,
        bio=frontmatter.get("bio", ""),
        specialties=frontmatter.get("specialties", ""),
        community_contributions=extract_section_body(text, "community_contributions"),
        external_contributions=extract_section_body(text, "external_contributions"),
        honors_body=extract_section_body(text, "honors") or "（暂无）",
    )
    readme_path.write_text(new_text, encoding="utf-8")
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
