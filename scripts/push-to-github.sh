#!/usr/bin/env bash
# Push Evil-Ai complete repo to Dadapeer-evil-ai GitHub.
# Run from repo root after GitHub auth is configured.
set -euo pipefail

# SSH (recommended) or HTTPS:
REPO_URL="${1:-git@github.com:t-shaik1dadapeer-tech/Dadapeer-evil-ai.git}"
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
echo "24 task commits in history:"
git log --oneline | rg '^[a-f0-9]+ (B[1-6]|I[1-6]|A[1-6]|D[1-6]):' || true

echo ""
echo "Auth options:"
echo "  SSH:  ssh -T git@github.com   (or git@ssh.github.com port 443 if port 22 blocked)"
echo "  gh:   gh auth login && gh repo clone t-shaik1dadapeer-tech/Dadapeer-evil-ai"
echo ""
read -r -p "Force-push to origin/$BRANCH? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  git push -u origin "$BRANCH" --force
  echo "Done: https://github.com/t-shaik1dadapeer-tech/Dadapeer-evil-ai/tree/$BRANCH"
else
  echo "Aborted."
fi
