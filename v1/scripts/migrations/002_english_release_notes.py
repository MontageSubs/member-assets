import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from profile_common import MEMBERS_DIR, existing_profiles
from releases import repo, tag, sync_notes


def _asset_names_from_release(member_id):
    result = subprocess.run(
        ["gh", "release", "view", tag(member_id), "--repo", repo(), "--json", "assets", "--jq", ".assets[].name"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _current_notes(member_id):
    result = subprocess.run(
        ["gh", "release", "view", tag(member_id), "--repo", repo(), "--json", "body", "--jq", ".body"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def migrate_release(member_id):
    current = _current_notes(member_id)
    if not current or not current.startswith("蒙太奇"):
        return False
    asset_names = _asset_names_from_release(member_id)
    if not asset_names:
        return False
    sync_notes(member_id, asset_names)
    return True


def main():
    profiles = existing_profiles()
    migrated = [p["id"] for p in profiles if migrate_release(p["id"])]
    print(f"migrated: {', '.join(migrated)}" if migrated else "nothing to migrate")


if __name__ == "__main__":
    main()
