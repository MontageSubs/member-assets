import os
import subprocess


def repo():
    return os.environ.get("GITHUB_REPOSITORY", "MontageSubs/member-assets")


def tag(member_id):
    return f"v1-{member_id}"


def asset_url(member_id, asset_name):
    return f"https://github.com/{repo()}/releases/download/{tag(member_id)}/{asset_name}"


def page_url(member_id):
    return f"https://github.com/{repo()}/releases/tag/{tag(member_id)}"


def profile_url(member_id):
    return f"https://github.com/{repo()}/tree/v1/members/{member_id}"


def avatar_upload_url(member_id):
    return f"https://github.com/{repo()}/upload/v1/members/{member_id}/avatar"


def avatar_tree_url(member_id):
    return f"https://github.com/{repo()}/tree/v1/members/{member_id}/avatar"


def sizes_for(shape, asset_names):
    return sorted(int(name[len(shape) + 1 : -4]) for name in asset_names if name.startswith(f"{shape}-"))


def notes_body(member_id, asset_names):
    header = "| Size | URL |\n| :--- | :--- |"

    def rows(shape):
        return "\n".join(
            f"| {size} | `{asset_url(member_id, f'{shape}-{size}.png')}` |"
            for size in sizes_for(shape, asset_names)
        )

    return (
        "MontageSubs member avatar assets\n"
        f"Profile: [members/{member_id}]({profile_url(member_id)})\n\n"
        f"**Square**\n\n{header}\n{rows('square')}\n\n"
        f"**Circle**\n\n{header}\n{rows('circle')}\n"
    )


def ensure_release(member_id, asset_names):
    release_tag = tag(member_id)
    check = subprocess.run(["gh", "release", "view", release_tag, "--repo", repo()], capture_output=True)
    if check.returncode == 0:
        return False
    subprocess.run(
        [
            "gh", "release", "create", release_tag,
            "--repo", repo(),
            "--title", release_tag,
            "--notes", notes_body(member_id, asset_names),
        ],
        check=True,
    )
    return True


def upload_assets(member_id, local_paths):
    subprocess.run(
        ["gh", "release", "upload", tag(member_id), *[str(p) for p in local_paths], "--repo", repo(), "--clobber"],
        check=True,
    )


def sync_notes(member_id, asset_names):
    subprocess.run(
        ["gh", "release", "edit", tag(member_id), "--repo", repo(), "--notes", notes_body(member_id, asset_names)],
        check=True,
    )


def delete_release(member_id):
    subprocess.run(
        ["gh", "release", "delete", tag(member_id), "--repo", repo(), "--yes", "--cleanup-tag"],
        check=False,
    )
