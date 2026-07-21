import os
import sys
import uuid
from datetime import datetime, timezone

import yaml

import avatar_pipeline
import releases
from profile_common import MEMBERS_DIR, existing_profiles, render_readme


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_github(raw):
    raw = raw.strip().rstrip("/")
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        raw = raw.split("github.com/")[-1]
    return raw.split("/")[0].split("?")[0]


def ensure_github_unique(github, profiles):
    if not github:
        return
    target = github.lower()
    for profile in profiles:
        if (profile.get("github") or "").lower() == target:
            sys.exit(f"GitHub 用户名已被成员 {profile.get('id')} 占用：{github}")


def generate_id(profiles):
    taken = {profile.get("id") for profile in profiles}
    while True:
        candidate = uuid.uuid4().hex[-12:]
        if candidate not in taken and not (MEMBERS_DIR / candidate).exists():
            return candidate


def avatar_cell(member_id, display_name, github):
    size = avatar_pipeline.PROFILE_AVATAR_SIZE
    asset_name = f"circle-{size}.png"
    image_tag = f'<img src="{releases.asset_url(member_id, asset_name)}" width="{size}" alt="Avatar of {display_name}">'
    if github:
        return f'<a href="https://github.com/{github}" title="GitHub profile">{image_tag}</a>'
    return image_tag


def github_cell(github):
    if not github:
        return "—"
    return f'<a href="https://github.com/{github}" title="GitHub profile"><b>GitHub</b></a>'


def write_profile(member_id, display_name, github, created_at):
    member_dir = MEMBERS_DIR / member_id
    member_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "id": member_id,
        "display_name": display_name,
        "github": github,
        "avatar_source": "",
        "avatar_local": False,
        "type": "member",
        "created_at": created_at,
    }
    content = (
        "<!--\n"
        "WARNING: do not remove or reorder the marked sections below.\n"
        "Automation depends on these markers to detect and update the\n"
        "display name and GitHub link. Editing content inside a marker\n"
        "is fine; removing the markers themselves breaks automation.\n"
        "-->\n\n"
        "<table>\n<tr>\n<td valign=\"top\">\n\n"
        f"{avatar_cell(member_id, display_name, github)}\n\n"
        '</td>\n<td valign="top" style="padding-left:20px;">\n\n'
        "<!-- profile:display_name:start -->\n"
        f"# {display_name}\n"
        "<!-- profile:display_name:end -->\n\n"
        "**简介：** （在此填写自我介绍）\n\n"
        "**特长：** \n\n"
        "<table>\n<tr>\n"
        '<th align="center">GitHub</th>\n'
        '<th align="center">头像 Release</th>\n'
        '<th align="center">社区成员ID</th>\n'
        "</tr>\n<tr>\n"
        '<td align="center">\n'
        "<!-- profile:github:start -->\n"
        f"{github_cell(github)}\n"
        "<!-- profile:github:end -->\n"
        "</td>\n"
        f'<td align="center"><a href="{releases.page_url(member_id)}" title="Avatar release page"><b>查看</b></a></td>\n'
        f'<td align="center"><code>{member_id}</code></td>\n'
        "</tr>\n</table>\n\n"
        "</td>\n</tr>\n</table>\n\n"
        "<!-- profile:community_contributions:start -->\n"
        "## 社区贡献\n\n"
        "| 项目 | 角色 | 说明 |\n"
        "| :--- | :--- | :--- |\n"
        "<!-- profile:community_contributions:end -->\n\n"
        "<!-- profile:external_contributions:start -->\n"
        "## 外部贡献\n\n"
        "- \n"
        "<!-- profile:external_contributions:end -->\n\n"
        "<!-- profile:honors:start -->\n"
        "## 荣誉\n\n"
        "（暂无）\n"
        "<!-- profile:honors:end -->\n\n"
        "---\n\n"
        '<div align="center">\n\n'
        "**蒙太奇字幕社区 (MontageSubs)**  \n"
        '"用爱发电 ❤️ Powered by Love"\n\n'
        "</div>\n\n"
        "<!-- profile:meta\n"
        + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
        + "-->\n"
    )
    (member_dir / "README.md").write_text(content, encoding="utf-8")


def main():
    display_name = os.environ.get("INPUT_DISPLAY_NAME", "").strip()
    github = normalize_github(os.environ.get("INPUT_GITHUB", ""))
    if not display_name:
        sys.exit("昵称不能为空")

    profiles = existing_profiles()
    ensure_github_unique(github, profiles)
    member_id = generate_id(profiles)
    created_at = now_iso()

    write_profile(member_id, display_name, github, created_at)
    profiles.append({"id": member_id, "display_name": display_name, "github": github, "created_at": created_at})
    render_readme(profiles)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"member_id={member_id}\n")


if __name__ == "__main__":
    main()
