import os
import shutil
import sys

import avatar_cache
import releases
from profile_common import MEMBERS_DIR, existing_profiles, render_readme


def expected_confirmation(member_id):
    return f"DELETE {member_id}"


def main():
    member_id = os.environ.get("INPUT_MEMBER_ID", "").strip()
    confirmation = os.environ.get("INPUT_CONFIRMATION", "").strip()

    if not member_id:
        sys.exit("Community member ID is required / 社区成员ID 不能为空")

    member_dir = MEMBERS_DIR / member_id
    if not member_dir.is_dir():
        sys.exit(f"Member not found / 未找到该社区成员：{member_id}")

    expected = expected_confirmation(member_id)
    if confirmation != expected:
        sys.exit(f'Confirmation text must be exactly / 确认文本应精确输入："{expected}"')

    shutil.rmtree(member_dir)
    avatar_cache.delete(member_id)
    releases.delete_release(member_id)
    render_readme(existing_profiles())


if __name__ == "__main__":
    main()
