# Push Evil-Ai to GitHub

**Target repo:** [t-shaik1dadapeer-tech/Eval-AI-Agent](https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent)

Remote URLs:

```text
SSH:  git@github.com:t-shaik1dadapeer-tech/Eval-AI-Agent.git
HTTPS: https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent.git
```

---

## Quick push (after auth)

```bash
cd /Users/shaikdadapeer/Evil-Ai

# Option A — GitHub CLI
gh auth login
git push -u origin main --force

# Option B — SSH
git remote set-url origin git@github.com:t-shaik1dadapeer-tech/Eval-AI-Agent.git
ssh -T git@github.com
git push -u origin main --force
```

Clone on another machine:

```bash
gh repo clone t-shaik1dadapeer-tech/Eval-AI-Agent
# or
git clone git@github.com:t-shaik1dadapeer-tech/Eval-AI-Agent.git
```

---

## Token push (office laptop)

```bash
cd /Users/shaikdadapeer/Evil-Ai
GITHUB_TOKEN=ghp_YOUR_TOKEN bash scripts/push-with-token.sh
```

**Classic token scopes required:** `repo` + **`workflow`** (this repo has `.github/workflows/`).

**Fine-grained token permissions:** Contents **Read and write** + Workflows **Read and write**.

If you see `403 Permission denied`, the token is missing **workflow** / write permissions — create a new token with the scopes above.

**Do not paste tokens in chat.** Revoke after push: https://github.com/settings/tokens

---

Add to `~/.ssh/config`:

```sshconfig
Host github.com
  HostName ssh.github.com
  Port 443
  User git
```

Generate and add key to GitHub → Settings → SSH keys:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

---

## What gets pushed (39 commits)

| Track | Commits |
|-------|---------|
| Beginner B1–B6 | dc959ba .. 09bd86f |
| Intermediate I1–I6 | 21d4eab .. e0936a0 |
| Advanced A1–A6 | 9565fdb .. 95b009f |
| DevOps D1–D6 | 568a96c .. 0045be1 |
| Framework docs | 2afec22, dd0630a, 3d6f9e6 |

`--force` is needed because the remote only has a placeholder README.

---

## After push

```bash
make setup
make eval-api    # http://127.0.0.1:8788
```

See: [`JIRA_TASK_MAP.md`](JIRA_TASK_MAP.md) for PM4-6626 subtask mapping.
