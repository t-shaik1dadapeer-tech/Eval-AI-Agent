#!/usr/bin/env bash
# Push Evil-Ai complete repo to Dadapeer-evil-ai GitHub.
# Run from repo root after GitHub auth is configured.
set -euo pipefail

REPO_URL="${1:-https://github.com/t-shaik1dadapeer-tech/Dadapeer-evil-ai.git}"
BRANCH="${2:-main}"

cd "$(dirname "$0")/.."

if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

echo "Remote: $(git remote get-url origin)"
echo "Branch: $BRANCH"
echo "Commits: $(git rev-list --count HEAD)"
echo ""
echo "Task commits (24 + framework):"
git log --oneline --grep='^B[1-6]:' --grep='^I[1-6]:' --grep='^A[1-6]:' --grep='^D[1-6]:' --all-match 2>/dev/null || \
  git log --oneline | rg '^[a-f0-9]+ (B[1-6]|I[1-6]|A[1-6]|D[1-6]):' || true

echo ""
read -r -p "Force-push to origin/$BRANCH? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  git push -u origin "$BRANCH" --force
  echo "Done: $REPO_URL/tree/$BRANCH"
else
  echo "Aborted."
fi
