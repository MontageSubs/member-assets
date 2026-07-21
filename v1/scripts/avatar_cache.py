import json

from profile_common import ROOT

CACHE_DIR = ROOT / "cache" / "members"


def path_for(member_id):
    return CACHE_DIR / f"{member_id}.json"


def load(member_id):
    file = path_for(member_id)
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}


def save(member_id, hashes):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path_for(member_id).write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def delete(member_id):
    path_for(member_id).unlink(missing_ok=True)
