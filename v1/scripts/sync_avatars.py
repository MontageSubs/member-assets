import hashlib
import os
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import avatar_cache
import releases
from avatar_pipeline import render_variants
from profile_common import MEMBERS_DIR, load_frontmatter

MAX_WORKERS = min(os.cpu_count() or 1, 6)


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def process_member(member_dir):
    member_id = member_dir.name
    result = {"member_id": member_id, "hashes": {}, "queue": [], "usable": set(), "previous": set()}
    try:
        frontmatter = load_frontmatter(member_dir / "README.md")
        output_dir = Path(tempfile.mkdtemp(prefix=f"avatar-{member_id}-"))
        variants = render_variants(member_dir, frontmatter, output_dir)
        cache = avatar_cache.load(member_id)
        result["usable"] = set(variants)
        result["previous"] = set(cache)
        for asset_name, local_path in variants.items():
            digest = sha256_of(local_path)
            if cache.get(asset_name) == digest:
                result["hashes"][asset_name] = digest
            else:
                result["queue"].append((local_path, asset_name, digest))
    except Exception as error:
        print(f"member {member_id} skipped: {error}", file=sys.stderr)
    return result


def upload_and_finalize(results):
    for result in results:
        member_id = result["member_id"]
        if not result["usable"]:
            continue
        created = releases.ensure_release(member_id, result["usable"])
        if result["queue"]:
            local_paths = [item[0] for item in result["queue"]]
            try:
                releases.upload_assets(member_id, local_paths)
                for _, asset_name, digest in result["queue"]:
                    result["hashes"][asset_name] = digest
            except Exception as error:
                print(f"upload failed {member_id}: {error}", file=sys.stderr)
        avatar_cache.save(member_id, result["hashes"])
        if not created and (result["queue"] or result["previous"] != result["usable"]):
            releases.sync_notes(member_id, result["usable"])


def target_members():
    raw = os.environ.get("INPUT_MEMBER_ID", "").strip()
    if not raw:
        return sorted(path for path in MEMBERS_DIR.iterdir() if path.is_dir())
    return [MEMBERS_DIR / member_id.strip() for member_id in raw.split(",") if member_id.strip()]


def main():
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_member, member_dir) for member_dir in target_members()]
        results = [future.result() for future in as_completed(futures)]
    upload_and_finalize(results)


if __name__ == "__main__":
    main()
