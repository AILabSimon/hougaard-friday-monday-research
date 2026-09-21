#!/bin/bash
# Record that everything currently on GitHub has been processed.
# Run this ONLY after the work for a mandate has been pushed and handed off.
set -uo pipefail
REPO="AILabSimon/hougaard-friday-monday-research"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/tmp/rv/bin/python; [ -x "$PY" ] || PY=python3
NOTE="${1:-}"
curl -sS --max-time 25 "https://api.github.com/repos/$REPO/issues?state=open&per_page=50" > "$DIR/.issues.json"
curl -sS --max-time 25 "https://api.github.com/repos/$REPO/issues/comments?per_page=100&sort=created&direction=desc" > "$DIR/.comments.json"
curl -sS --max-time 25 "https://api.github.com/repos/$REPO/commits?per_page=5" > "$DIR/.commits.json"
"$PY" - "$DIR" "$NOTE" <<'PYEOF'
import json, sys, os, datetime
d, note = sys.argv[1], sys.argv[2]
sp = os.path.join(d, "state.json")
state = json.load(open(sp)) if os.path.exists(sp) else {"processed": []}
def load(n):
    try:
        x = json.load(open(os.path.join(d, n)));  return x if isinstance(x, list) else []
    except Exception:
        return []
issues, comments, commits = load(".issues.json"), load(".comments.json"), load(".commits.json")
state["last_issue_number"] = max([i["number"] for i in issues if "pull_request" not in i] or [state.get("last_issue_number", 0)])
state["last_comment_id"] = max([c["id"] for c in comments] or [state.get("last_comment_id", 0)])
state["last_commit_sha"] = commits[0]["sha"] if commits else state.get("last_commit_sha", "")
state.setdefault("processed", []).append({
    "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "note": note, "issue": state["last_issue_number"],
    "comment_id": state["last_comment_id"], "commit": state["last_commit_sha"][:12]})
json.dump(state, open(sp, "w"), indent=1)
print("marked processed ->", json.dumps({k: v for k, v in state.items() if k != "processed"}))
PYEOF
