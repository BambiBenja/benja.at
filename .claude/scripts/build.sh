#!/usr/bin/env bash
# Build the site into _site/, installing the Ruby gems first if needed.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

export BUNDLE_PATH="${BUNDLE_PATH:-vendor/bundle}"
if ! bundle check >/dev/null 2>&1; then
  echo "Installing Ruby gems (first run takes a minute or two)..."
  bundle install --quiet
fi

bundle exec jekyll build --quiet
echo "Built the site into _site/"
