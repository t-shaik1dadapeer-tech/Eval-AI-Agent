# Push Evil-Ai to GitHub

**Target repo:** [t-shaik1dadapeer-tech/Dadapeer-evil-ai](https://github.com/t-shaik1dadapeer-tech/Dadapeer-evil-ai)

Remote is configured as SSH:

```text
git@github.com:t-shaik1dadapeer-tech/Dadapeer-evil-ai.git
```

---

## Option A — GitHub CLI (`gh`)

```bash
# Install (fix brew permissions first if needed)
brew install gh

# Login
gh auth login

# From Evil-Ai repo root — push full history
cd /Users/shaikdadapeer/Evil-Ai
git push -u origin main --force
```

Clone on another machine:

```bash
gh repo clone t-shaik1dadapeer-tech/Dadapeer-evil-ai
```

---

## Option B — SSH (recommended)

### 1. Generate key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519 -N ""
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### 2. Add public key to GitHub

Copy `~/.ssh/id_ed25519.pub` → GitHub → **Settings → SSH and GPG keys → New SSH key**

### 3. If port 22 is blocked, add to `~/.ssh/config`

```sshconfig
Host github.com
  HostName ssh.github.com
  Port 443
  User git
```

### 4. Test and push

```bash
ssh -T git@github.com
cd /Users/shaikdadapeer/Evil-Ai
git remote set-url origin git@github.com:t-shaik1dadapeer-tech/Dadapeer-evil-ai.git
git push -u origin main --force
```

Clone:

```bash
git clone git@github.com:t-shaik1dadapeer-tech/Dadapeer-evil-ai.git
```

---

## Option C — Helper script

```bash
cd /Users/shaikdadapeer/Evil-Ai
bash scripts/push-to-github.sh
```

---

## Why `--force`?

The GitHub repo currently has only a placeholder README. Your local repo has the full 24-task history (B1–D6 commits). Force push replaces the remote with the complete Evil-Ai portfolio.

---

## After push — verify

```bash
make setup
make eval-api    # http://127.0.0.1:8788
```

See also: [`JIRA_TASK_MAP.md`](JIRA_TASK_MAP.md) for PM4-6626 subtask mapping.
