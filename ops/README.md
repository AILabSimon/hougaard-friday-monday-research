# Research-loop automation

```
ChatGPT posts a mandate on GitHub
      ↓
Claude scheduled task polls every 3h  (watch/github_poll.sh — GitHub metadata only)
      ↓
Claude runs the research locally and COMMITS; writes watch/HANDOFF_PENDING.md
      ↓
macOS publisher agent (every 5 min)   (watch/publish.sh via LaunchAgent)
      ↓  push  →  gh issue comment  →  mark_processed.sh
ChatGPT reviews on GitHub → next mandate
```

## Why the split

The Claude scheduled session runs in an **isolated Linux VM** inside the Cowork desktop app
(`uname` → Linux aarch64, host `claude`), not in macOS. It has no `gh`, no `security`/Keychain,
no SSH keys, and no GitHub token in its environment. Its network goes through a session proxy
that injects a **read-scoped** credential for the attached repository: `git ls-remote` and
GitHub API GETs succeed, while `git push` fails with *"could not read Username"* and API writes
return HTTP 401. That is the whole of the failure — not token scope, not remote configuration,
not a credential helper, and not a difference between scheduled and interactive sessions
(neither has write access).

Rather than placing a long-lived token inside the VM or the connected folder, publication is
done on the Mac, where the account's normal `gh`/git authentication already works. **No new
credential is created, stored, or read by any of this.**

## Components

| file | runs on | purpose |
|---|---|---|
| `github_poll.sh` | Claude VM | metadata-only poll; prints `NOTHING NEW` or `NEW WORK`; ~1 s |
| `mark_processed.sh` | either | advances `watch/state.json` (last issue, comment id, commit) |
| `publish.sh` | **macOS** | push → comment → *then* advance state |
| `com.ailab.hougaard-publish.plist` | macOS | LaunchAgent, every 300 s |
| `install_publisher.sh` | macOS | one-time install; refuses if `gh` is missing or unauthenticated |

## Safety properties (each verified by a stubbed test harness)

1. Nothing to publish → silent exit 0, no state change.
2. **Push fails → handoff retained, state NOT advanced**, non-zero exit, retried next run.
3. **Comment fails → handoff retained, state NOT advanced**, retried next run.
4. Handoff without a valid `<!-- HANDOFF-ISSUE: N -->` marker → rejected, nothing posted.
5. Marker containing shell metacharacters → rejected; the issue number must match `^[0-9]+$`.
   The comment body is passed to `gh --body-file` and is never interpolated into a command, so
   issue or comment text cannot become shell code.
6. Full success → comment posted, handoff archived to `watch/handoffs/`, state advanced exactly
   once.

## Operational notes

- The Claude task must **not** push and must **not** call `mark_processed.sh` after doing
  research — otherwise a failed publication could be recorded as complete. Its prompt says so.
- `watch/state.json`, `publish.log` and the handoff archive stay local; the `.json` caches and
  logs are gitignored.
- Only the `TM Research` folder is attached to the polling task. The market `Data` folder is
  deliberately not attached, and was not attached to solve authentication.
