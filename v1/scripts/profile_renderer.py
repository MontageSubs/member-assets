import yaml
import os
from pathlib import Path

import releases

TEMPLATE_VERSION = "2"
PROFILE_AVATAR_SIZE = 96
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "profile.md"


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


def build_readme(frontmatter, bio="", specialties="", community_contributions="", external_contributions="", honors_body="（暂无）"):
    member_id = frontmatter["id"]
    display_name = frontmatter.get("display_name", "")
    github = frontmatter.get("github", "")
    frontmatter["template_version"] = TEMPLATE_VERSION

    if not community_contributions:
        community_contributions = "| 项目 | 角色 | 说明 |\n| :--- | :--- | :--- |"
    
    if not external_contributions:
        external_contributions = "-"

    if honors_body == "（暂无）" or not honors_body.strip():
        honors_body = "-"

    bio_line = bio.strip() if bio.strip() else "No bio yet · 暂无简介"
    avatar_html = avatar_cell(member_id, display_name, github)
    github_html = github_cell(github)
    view_url = releases.page_url(member_id)
    frontmatter_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)

    template_str = TEMPLATE_PATH.read_text(encoding="utf-8")

    return template_str.format(
        display_name=display_name,
        github=github,
        bio=bio,
        specialties=specialties,
        avatar_html=avatar_html,
        bio_line=bio_line,
        github_html=github_html,
        view_url=view_url,
        member_id=member_id,
        community_contributions=community_contributions,
        external_contributions=external_contributions,
        honors_body=honors_body,
        frontmatter_yaml=frontmatter_yaml
    )
