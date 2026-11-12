#!/usr/bin/env bash
# Build the site, then check it:
#   1. HTML and CSS validity, with the W3C Nu Html Checker (vnu)
#   2. Links and images that point to pages or files that don't exist
# Exits non-zero if any check finds an error.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

VNU_VERSION="26.11.9"
TOOLS_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/benja-at-tools"
VNU_JAR="$TOOLS_DIR/node_modules/vnu-jar/build/dist/vnu.jar"

.claude/scripts/build.sh

for tool in java npm; do
  if ! command -v "$tool" >/dev/null; then
    echo "error: '$tool' is not installed, so HTML/CSS validation can't run." >&2
    exit 2
  fi
done

if [ ! -f "$VNU_JAR" ] || ! grep -q "\"version\": \"$VNU_VERSION\"" "$TOOLS_DIR/node_modules/vnu-jar/package.json" 2>/dev/null; then
  echo "Installing the HTML/CSS validator (vnu-jar $VNU_VERSION)..."
  npm install --prefix "$TOOLS_DIR" --no-audit --no-fund --silent "vnu-jar@$VNU_VERSION"
fi

status=0

echo "Validating HTML and CSS..."
# The filtered message is about markup Jekyll's Markdown converter generates
# (<img ... />), which we can't change.
vnu_output="$(java -jar "$VNU_JAR" --skip-non-html --also-check-css \
  --filterpattern '.*Trailing slash on void elements.*' _site 2>&1)" || status=1
# Drop Java's proxy notice and shorten file paths to "_site/...".
printf '%s\n' "$vnu_output" | grep -v '^Picked up JAVA_TOOL_OPTIONS' \
  | sed -E 's#^"file:[^"]*/(_site/[^"]*)"#\1#' || true

echo "Checking links and images..."
python3 .claude/scripts/sitetools.py links || status=1

if [ "$status" -eq 0 ]; then
  echo "All checks passed."
else
  echo "Some checks failed (see above)."
fi
exit "$status"
