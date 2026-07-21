import os
import re
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("DATA_ROOT", Path(__file__).resolve().parent.parent))
MEMBERS_DIR = ROOT / "members"
README_PATH = ROOT / "README.md"
INDEX_START = "<!-- members:start -->"
INDEX_END = "<!-- members:end -->"
WARNING_START = "<!-- profile:warning:start -->"
WARNING_END = "<!-- profile:warning:end -->"

FRONTMATTER_PATTERN = re.compile(r"<!-- profile:meta\n(.*?)\n-->", re.S)


def load_frontmatter(profile_path):
    text = profile_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.search(text)
    return yaml.safe_load(match.group(1)) or {} if match else {}


def existing_profiles():
    if not MEMBERS_DIR.exists():
        return []
    return [
        frontmatter
        for path in MEMBERS_DIR.glob("*/README.md")
        if (frontmatter := load_frontmatter(path))
    ]


def default_readme():
    return (
        "# 蒙太奇字幕社区 成员档案\n\n"
        "本仓库维护蒙太奇字幕社区成员的公开档案信息，供各字幕仓库及未来官网调用。\n\n"
        f"{INDEX_START}\n{INDEX_END}\n\n"
        "---\n\n"
        '<div align="center">\n\n'
        "**蒙太奇字幕社区 (MontageSubs)**  \n"
        '"用爱发电 ❤️ Powered by Love"\n\n'
        "</div>\n"
    )


def render_readme(profiles):
    from releases import asset_url

    import avatar_cache

    ordered = sorted(profiles, key=lambda p: p.get("created_at", ""))
    rows = []
    for profile in ordered:
        member_id = profile["id"]
        display_name = profile.get("display_name") or "（未命名）"
        github = profile.get("github") or ""
        
        cache = avatar_cache.load(member_id)
        best_size = next((s for s in (96, 48, 32) if f"circle-{s}.png" in cache), 32)
        
        img_tag = f'<img src="{asset_url(member_id, f"circle-{best_size}.png")}" width="32" alt="">'
        release_url = f"https://github.com/MontageSubs/member-assets/releases/tag/v1-{member_id}"
        avatar_link = f"[{img_tag}]({release_url})"
        
        profile_cell = f"[查看](members/{member_id})"
        github_cell = f"[{github}](https://github.com/{github})" if github else "—"
        id_cell = f"`{member_id}`"
        rows.append(f"| {avatar_link} | {display_name} | {id_cell} | {profile_cell} | {github_cell} |")
    table = (
        "\n".join(["| | 昵称 | 成员 ID | 个人档案 | GitHub |", "| :---: | :--- | :--- | :--- | :--- |", *rows])
        if rows
        else "*暂无成员*"
    )
    readme_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else default_readme()
    pattern = re.compile(re.escape(INDEX_START) + r".*?" + re.escape(INDEX_END), re.S)
    replacement = f"{INDEX_START}\n{table}\n{INDEX_END}"
    readme_text = (
        pattern.sub(replacement, readme_text)
        if pattern.search(readme_text)
        else readme_text.rstrip() + "\n\n" + replacement + "\n"
    )
    README_PATH.write_text(readme_text, encoding="utf-8")


def write_warning(readme_path, error_detail):
    text = readme_path.read_text(encoding="utf-8")
    block = (
        f"{WARNING_START}\n"
        "> [!CAUTION]\n"
        f"> 此档案的标记结构已损坏，自动化流程无法解析。错误：`{error_detail}`\n"
        ">\n"
        "> **修复步骤：** 确认 `<!-- profile:display_name:start/end -->`、`<!-- profile:github:start/end -->`、`<!-- profile:meta ... -->` 标记完整无缺，然后在 Actions 页面手动触发 **v1 - Watch Profile**，成功运行后此警告自动消除。\n\n"
        "> [!CAUTION]\n"
        f"> The marker structure of this profile is corrupted and cannot be parsed by automation. Error: `{error_detail}`\n"
        ">\n"
        "> **How to Fix:** Ensure `<!-- profile:display_name:start/end -->`, `<!-- profile:github:start/end -->`, and `<!-- profile:meta ... -->` markers are intact, then manually trigger **v1 - Watch Profile** in Actions. This warning clears automatically on success.\n"
        f"{WARNING_END}\n\n"
    )
    pattern = re.compile(re.escape(WARNING_START) + r".*?" + re.escape(WARNING_END) + r"\n\n", re.S)
    readme_path.write_text(
        pattern.sub(block, text) if pattern.search(text) else block + text,
        encoding="utf-8",
    )


def clear_warning(readme_path):
    text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(WARNING_START) + r".*?" + re.escape(WARNING_END) + r"\n\n", re.S)
    if pattern.search(text):
        readme_path.write_text(pattern.sub("", text), encoding="utf-8")
