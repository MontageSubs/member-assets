import yaml

import releases

PROFILE_AVATAR_SIZE = 96


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


def input_block(display_name="", github="", bio="", specialties=""):
    return (
        "<!-- profile:input\n"
        "Edit the info below and save — it auto-renders into your profile card · 编辑下方信息并保存，将自动渲染进你的档案卡片\n"
        "\n"
        "-----\n"
        "Nickname · 昵称\n"
        "-----\n"
        f"{display_name}\n"
        "\n"
        "-----\n"
        "GitHub — link, username, or leave empty · GitHub 用户名——可填链接、用户名，或留空\n"
        "-----\n"
        f"{github}\n"
        "\n"
        "-----\n"
        "Bio · 简介\n"
        "-----\n"
        f"{bio}\n"
        "\n"
        "-----\n"
        "Specialties · 特长（自定义字段，可自行修改标题 · customizable title）\n"
        "-----\n"
        f"{specialties}\n"
        "\n"
        "-->"
    )


def rendered_card(member_id, display_name, github, bio):
    bio_line = bio.strip() if bio.strip() else "No bio yet · 暂无简介"
    return (
        '<table>\n<tr>\n<td valign="top">\n\n'
        f"{avatar_cell(member_id, display_name, github)}\n\n"
        '</td>\n<td valign="top" style="padding-left:20px;">\n\n'
        f"# {display_name}\n\n"
        f"{bio_line}\n\n"
        "<table>\n<tr>\n"
        '<th align="center">GitHub</th>\n'
        '<th align="center">Avatar Release · 头像</th>\n'
        '<th align="center">Member ID · 用户ID</th>\n'
        "</tr>\n<tr>\n"
        f'<td align="center">{github_cell(github)}</td>\n'
        f'<td align="center"><a href="{releases.page_url(member_id)}" title="Avatar release page"><b>View · 查看</b></a></td>\n'
        f'<td align="center"><code>{member_id}</code></td>\n'
        "</tr>\n</table>\n\n"
        "</td>\n</tr>\n</table>"
    )


def build_readme(frontmatter, bio="", specialties="", contributions_block="", honors_body="（暂无）"):
    member_id = frontmatter["id"]
    display_name = frontmatter.get("display_name", "")
    github = frontmatter.get("github", "")

    if not contributions_block:
        contributions_block = (
            "<!-- profile:community_contributions:start -->\n"
            "## 社区贡献\n\n"
            "| 项目 | 角色 | 说明 |\n"
            "| :--- | :--- | :--- |\n"
            "<!-- profile:community_contributions:end -->\n\n"
            "<!-- profile:external_contributions:start -->\n"
            "## 外部贡献\n\n"
            "- \n"
            "<!-- profile:external_contributions:end -->"
        )

    return (
        f"{input_block(display_name, github, bio, specialties)}\n\n"
        f"{rendered_card(member_id, display_name, github, bio)}\n\n"
        f"{contributions_block}\n\n"
        "<!-- profile:honors:start -->\n"
        "Maintained by the community team, not by yourself · 由社区管理团队维护，无需自行编辑\n\n"
        "## Honors · 荣誉\n\n"
        f"{honors_body}\n"
        "<!-- profile:honors:end -->\n\n"
        "---\n\n"
        '<div align="center">\n\n'
        "**蒙太奇字幕社区 (MontageSubs)**  \n"
        '"用爱发电 ❤️ Powered by Love"\n\n'
        "</div>\n\n"
        "<!-- profile:meta\n"
        + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
        + "-->"
    )
