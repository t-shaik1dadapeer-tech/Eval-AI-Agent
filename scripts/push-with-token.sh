#!/usr/bin/env bash
# Push Evil-Ai to GitHub using a Personal Access Token (no gh/brew needed).
# Usage:
#   GITHUB_TOKEN=ghp_xxxx bash scripts/push-with-token.sh
set -euo pipefail

REPO="https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent.git"
BRANCH="${BRANCH:-main}"

cd "$(dirname "$0")/.."

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Missing GITHUB_TOKEN."
  echo ""
  echo "1. Open https://github.com/settings/tokens (logged in as t-shaik1dadapeer-tech)"
  echo "2. Generate new token (classic) with 'repo' scope"
  echo "3. Run:"
  echo "   GITHUB_TOKEN=ghp_YOUR_TOKEN bash scripts/push-with-token.sh"
  exit 1
fi

git remote set-url origin "$REPO"

# Token embedded only for this push command (not stored in git config)
AUTH_URL="https://t-shaik1dadapeer-tech:${GITHUB_TOKEN}@github.com/t-shaik1dadapeer-tech/Eval-AI-Agent.git"

echo "Pushing $(git rev-list --count HEAD) commits to Eval-AI-Agent ($BRANCH)..."
git push "$AUTH_URL" "$BRANCH:refs/heads/$BRANCH" --force

git remote set-url origin "$REPO"
git branch --set-upstream-to="origin/$BRANCH" "$BRANCH" 2>/dev/null || true

echo ""
echo "Done: https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent"
