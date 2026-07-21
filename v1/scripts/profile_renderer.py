import re
import yaml
import os
from pathlib import Path

import releases

PROFILE_AVATAR_SIZE = 96
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "profile.md"
VERSION_MARKER = re.compile(r"^<!-- template:version:\s*(\S+)\s*-->\n+")
DEFAULT_SPECIALTIES_TITLE = "特长"


def _load_template():
    raw = TEMPLATE_PATH.read_text(encoding="utf-8")
    match = VERSION_MARKER.match(raw)
    version = match.group(1) if match else "1"
    body = raw[match.end():] if match else raw
    return version, body


TEMPLATE_VERSION, _TEMPLATE_BODY = _load_template()


class SafeDict(dict):
    """Missing template placeholders render as empty string instead of raising KeyError,
    so future template edits don't require matching code changes."""
    def __missing__(self, key):
        return ""


def normalize_github(raw):
    raw = raw.strip().rstrip("/")
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        raw = raw.split("github.com/")[-1]
    return raw.split("/")[0].split("?")[0]


def avatar_cell(member_id, display_name, github):
    asset_name = f"circle-{PROFILE_AVATAR_SIZE}.png"
    image_tag = f'<img src="{releases.asset_url(member_id, asset_name)}" width="{PROFILE_AVATAR_SIZE}" alt="Avatar of {display_name}">'
    if github:
        return f'<a href="https://github.com/{github}" title="GitHub profile">{image_tag}</a>'
    return image_tag


def github_cell(github):
    if not github:
        return "—"
    return f'<a href="https://github.com/{github}" title="GitHub profile"><b>GitHub</b></a>'


def build_readme(frontmatter, bio="", specialties="", specialties_title=DEFAULT_SPECIALTIES_TITLE, community_contributions="", external_contributions="", achievements_body="（暂无）"):
    member_id = frontmatter["id"]
    display_name = frontmatter.get("display_name", "")
    github = frontmatter.get("github", "")
    frontmatter["template_version"] = TEMPLATE_VERSION

    if not community_contributions:
        community_contributions = "| 项目 | 角色 | 说明 |\n| :--- | :--- | :--- |"
    
    if not external_contributions:
        external_contributions = "-"

    if achievements_body == "（暂无）" or not achievements_body.strip():
        achievements_body = "-"

    bio_line = bio.strip() if bio.strip() else "暂无简介"
    specialties_value = specialties.strip()
    title_customized = specialties_title.strip() and specialties_title.strip() != DEFAULT_SPECIALTIES_TITLE

    if not specialties_value and not title_customized:
        specialties_display = "暂无"
    elif title_customized:
        specialties_display = f"{specialties_title.strip()}：{specialties_value or '暂无'}"
    else:
        specialties_display = f"{DEFAULT_SPECIALTIES_TITLE}：{specialties_value}"
    avatar_html = avatar_cell(member_id, display_name, github)
    github_html = github_cell(github)
    view_url = releases.page_url(member_id)
    frontmatter_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    contributions_block = (
        "<!-- profile:community_contributions:start -->\n"
        "## 社区贡献\n\n"
        f"{community_contributions}\n"
        "<!-- profile:community_contributions:end -->\n\n"
        "<!-- profile:external_contributions:start -->\n"
        "## 外部贡献\n\n"
        f"{external_contributions}\n"
        "<!-- profile:external_contributions:end -->"
    )

    template_str = _TEMPLATE_BODY

    return template_str.format_map(SafeDict(
        display_name=display_name,
        github=github,
        bio=bio,
        specialties=specialties,
        specialties_display=specialties_display,
        avatar_html=avatar_html,
        bio_line=bio_line,
        github_html=github_html,
        view_url=view_url,
        member_id=member_id,
        contributions_block=contributions_block,
        achievements_body=achievements_body,
        frontmatter_yaml=frontmatter_yaml,
        add_custom_avatar=releases.avatar_upload_url(member_id),
        view_custom_avatar=releases.avatar_tree_url(member_id),
    ))
