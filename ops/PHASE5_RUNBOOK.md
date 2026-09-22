# Phase 5 — end-to-end test runbook

The publisher cannot be installed from the Claude VM: `~/Library/LaunchAgents` is on macOS,
which the VM cannot reach (no `launchctl`, no Keychain, different kernel). One command in
macOS Terminal installs it; after that the loop needs no manual step.

## Step 1 — install the publisher (once)

```bash
bash "/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/watch/install_publisher.sh"
```

It refuses to install if `gh` is missing or unauthenticated. It never reads or prints a token.

**This immediately proves the publication half**: a commit and a handoff are already staged, so
within ~5 minutes the agent should push commit `5da6dcc` and post a comment on issue #2, then
advance `watch/state.json`. Check with:

```bash
tail "/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/watch/publish.log"
```

## Step 2 — prove the detection half

Post the issue in `watch/TEST_MANDATE.md`, then either wait for the 3-hourly poll or fire it
from a Claude conversation. Expected chain: poll reports `NEW WORK` → Claude makes the trivial
file change and commits → publisher pushes and comments → state advances → next poll reports
`NOTHING NEW` and the mandate is not executed twice.

## Step 3 — cleanup

Remove `ops/test/automation_loop_test.txt` in a separate commit titled
`[automation test] cleanup`. Leave the issue and its comment in place as evidence.
