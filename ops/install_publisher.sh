#!/bin/bash
# One-time install of the publisher LaunchAgent. Run once in macOS Terminal:
#   bash "/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/watch/install_publisher.sh"
set -e
W="/Users/ailab/Documents/AI Lab/Projects/Trading/TM Research/Hougaard_Friday_Monday/watch"
L="$HOME/Library/LaunchAgents/com.ailab.hougaard-publish.plist"
echo "checking prerequisites..."
command -v gh >/dev/null || { echo "ERROR: gh CLI not found. brew install gh"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERROR: gh not authenticated. Run: gh auth login"; exit 1; }
echo "  gh: OK (this script never reads or prints your token)"
mkdir -p "$HOME/Library/LaunchAgents"
cp "$W/com.ailab.hougaard-publish.plist" "$L"
launchctl unload "$L" 2>/dev/null || true
launchctl load "$L"
echo "installed: com.ailab.hougaard-publish (every 300s)"
echo "logs: $W/publish.log"
echo
echo "to remove later:  launchctl unload \"$L\" && rm \"$L\""
