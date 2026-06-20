# D4 — Kubernetes

## What to do

validate-manifests.sh must pass; see K8S_REPORT.md.

## Depends on

I5

## Required deliverables

- `devops/D4-kubernetes/k8s/deployment.yaml`
- `devops/D4-kubernetes/scripts/validate-manifests.sh`

## Reference files (golden examples in this repo)

- `devops/D4-kubernetes/README.md`
- `devops/D4-kubernetes/docs/K8S_REPORT.md`
- `devops/D4-kubernetes/k8s/deployment.yaml`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## D4 —**

Or run slash command: `/evil-ai-kubernetes`

## Verify (optional)

```bash
bash devops/D4-kubernetes/scripts/validate-manifests.sh
```
