#!/bin/bash
# Hougaard research publisher.
#
# RUNS ON macOS (as Simon), NOT in the Claude VM. That is the whole point: the Claude VM has no
# GitHub write credential, whereas this account's normal git/gh auth already works. No new
# secret is created, stored or read by this script.
#
# It publishes work that the Claude research session has already committed locally:
#   1. push any unpushed commits on main
#   2. if watch/HANDOFF_PENDING.md exists, post it as a comment on the issue it names
#   3. only if BOTH succeeded, advance the processed state and archive the handoff
# If either step fails, the handoff is left in place, the processed state is NOT advanced, and
# the failure is logged so the next run retries it.
set -uo pipefail

REPO_DIR="/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/repo"
WATCH_DIR="/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/watch"
GH_REPO="AILabSimon/hougaard-friday-monday-research"
PENDING="$WATCH_DIR/HANDOFF_PENDING.md"
LOG="$WATCH_DIR/publish.log"
LOCK="$WATCH_DIR/.publish.lock"

log() { printf '%s  %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"; }

# single instance
exec 9>"$LOCK" || exit 0
flock -n 9 2>/dev/null || { command -v flock >/dev/null || true; }

cd "$REPO_DIR" 2>/dev/null || { log "FATAL repo dir missing"; exit 1; }

UNPUSHED=$(git log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')
[ -f "$PENDING" ] && HAVE_PENDING=1 || HAVE_PENDING=0
if [ "$UNPUSHED" = "0" ] && [ "$HAVE_PENDING" = "0" ]; then
  exit 0                                   # nothing to publish; stay silent and cheap
fi

log "work found: unpushed=$UNPUSHED pending_handoff=$HAVE_PENDING"

# ---------- 1. push ----------
PUSHED_OK=1
if [ "$UNPUSHED" != "0" ]; then
  if ! git push origin main >>"$LOG" 2>&1; then
    log "PUSH FAILED - leaving everything pending, will retry"
    exit 1
  fi
  log "pushed -> $(git rev-parse HEAD)"
fi

# ---------- 2. handoff comment ----------
if [ "$HAVE_PENDING" = "1" ]; then
  # The issue number is read from a strict marker line and must be digits only.
  # The body is passed to gh via --body-file and is NEVER interpolated into a shell command,
  # so issue/comment text can never become code.
  ISSUE=$(grep -m1 -E '^<!-- HANDOFF-ISSUE: [0-9]+ -->$' "$PENDING" | grep -oE '[0-9]+' | head -1)
  if ! printf '%s' "${ISSUE:-}" | grep -qE '^[0-9]+$'; then
    log "HANDOFF REJECTED: no valid '<!-- HANDOFF-ISSUE: N -->' marker - not posting"
    exit 1
  fi
  BODY="$WATCH_DIR/.handoff_body.md"
  grep -v -E '^<!-- HANDOFF-ISSUE: [0-9]+ -->$' "$PENDING" > "$BODY"
  if ! gh issue comment "$ISSUE" --repo "$GH_REPO" --body-file "$BODY" >>"$LOG" 2>&1; then
    log "HANDOFF COMMENT FAILED on issue #$ISSUE - state NOT advanced, will retry"
    rm -f "$BODY"
    exit 1
  fi
  rm -f "$BODY"
  log "handoff posted to issue #$ISSUE"
  mkdir -p "$WATCH_DIR/handoffs"
  mv "$PENDING" "$WATCH_DIR/handoffs/handoff_$(date -u +%Y%m%dT%H%M%SZ)_issue${ISSUE}.md"
fi

# ---------- 3. advance processed state, only now ----------
if bash "$WATCH_DIR/mark_processed.sh" "auto-published by publish.sh" >>"$LOG" 2>&1; then
  log "processed state advanced"
else
  log "WARNING mark_processed failed (published, but state not advanced)"
  exit 1
fi
log "publish complete"
