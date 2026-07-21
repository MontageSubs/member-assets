import os
import sys
import uuid
from datetime import datetime, timezone

from profile_common import MEMBERS_DIR, existing_profiles, render_readme
from profile_renderer import build_readme, normalize_github


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def write_profile(member_id, display_name, github, created_at):
    member_dir = MEMBERS_DIR / member_id
    member_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "id": member_id,
        "display_name": display_name,
        "github": github,
        "bio": "",
        "specialties": "",
        "avatar_source": "",
        "avatar_local": False,
        "type": "member",
        "created_at": created_at,
    }
    (member_dir / "README.md").write_text(build_readme(frontmatter), encoding="utf-8")


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
