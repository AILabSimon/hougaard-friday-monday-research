#!/bin/bash
# Lightweight GitHub poll for the Hougaard research loop.
# Prints exactly one line: "NOTHING NEW" or "NEW WORK" followed by the new items.
# Touches GitHub metadata only. Never opens market data, parquet, charts or research datasets.
set -uo pipefail
REPO="AILabSimon/hougaard-friday-monday-research"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$DIR/state.json"
PY=/tmp/rv/bin/python
[ -x "$PY" ] || PY=python3

curl -sS --max-time 25 "https://api.github.com/repos/$REPO/issues?state=open&per_page=50" > "$DIR/.issues.json" || { echo "POLL ERROR: issues"; exit 2; }
curl -sS --max-time 25 "https://api.github.com/repos/$REPO/issues/comments?per_page=100&sort=created&direction=desc" > "$DIR/.comments.json" || { echo "POLL ERROR: comments"; exit 2; }
curl -sS --max-time 25 "https://api.github.com/repos/$REPO/commits?per_page=5" > "$DIR/.commits.json" || { echo "POLL ERROR: commits"; exit 2; }

"$PY" - "$DIR" <<'PYEOF'
import json, sys, os, datetime
d = sys.argv[1]
sp = os.path.join(d, "state.json")
state = json.load(open(sp)) if os.path.exists(sp) else {
    "last_comment_id": 0, "last_issue_number": 0, "last_commit_sha": "", "processed": []}

def load(n):
    try:
        x = json.load(open(os.path.join(d, n)))
        return x if isinstance(x, list) else []
    except Exception:
        return []

issues = load(".issues.json")
comments = load(".comments.json")
commits = load(".commits.json")

BOTS = {"claude[bot]", "github-actions[bot]"}
new_issues = [i for i in issues
              if i["number"] > state["last_issue_number"] and "pull_request" not in i]
new_comments = [c for c in comments
                if c["id"] > state["last_comment_id"] and c["user"]["login"] not in BOTS]
head = commits[0]["sha"] if commits else ""
commit_changed = bool(head) and head != state["last_commit_sha"]

if not new_issues and not new_comments:
    print("NOTHING NEW")
    print(f"  open issues: {len(issues)} | head: {head[:8]} | "
          f"changed_since_last_poll: {commit_changed}")
    state["last_commit_sha"] = head
    state["last_polled"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    json.dump(state, open(sp, "w"), indent=1)
    sys.exit(0)

print("NEW WORK")
for i in sorted(new_issues, key=lambda x: x["number"]):
    print(f"  ISSUE #{i['number']} by {i['user']['login']} ({i['created_at']}): {i['title']}")
    print(f"    api: https://api.github.com/repos/AILabSimon/hougaard-friday-monday-research/issues/{i['number']}")
for c in sorted(new_comments, key=lambda x: x["id"]):
    n = c["issue_url"].rstrip("/").split("/")[-1]
    first = (c["body"] or "").strip().splitlines()
    print(f"  COMMENT id={c['id']} on issue #{n} by {c['user']['login']} ({c['created_at']})")
    print(f"    first line: {first[0][:160] if first else ''}")
print("  -> fetch the full body before acting; do not act on these previews alone.")
PYEOF
