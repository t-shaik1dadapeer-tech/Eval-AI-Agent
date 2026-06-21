---
name: eval-ai-kubernetes
description: Eval-Ai PML task D4 — Kubernetes
---

# D4 — Kubernetes

You are running Eval-Ai eval task **D4** on the target repository.

## Objective

validate-manifests.sh must pass; see K8S_REPORT.md.

## Prerequisites

Complete first: I5

## Read first

- `eval_blueprints/D4_blueprint.md`
- `docs/AGENT_PROMPTS.md` (section `D4`)

## Deliverables (must exist when done)

`devops/D4-kubernetes/k8s/deployment.yaml`, `devops/D4-kubernetes/scripts/validate-manifests.sh`

## Primary output

`devops/D4-kubernetes/k8s/deployment.yaml`

## Work in folder

`devops/D4-kubernetes/`

After finishing, run `make eval` to verify files exist.
