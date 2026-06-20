#!/usr/bin/env python3
"""Generate Evil-Ai 24-task quick reference PDF."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "EVIL_AI_TASK_NOTES.pdf"


class NotesPDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Evil-Ai / Eval AI Agent - 24 Task Reference", align="R")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def title_page(self) -> None:
        self.add_page()
        self.ln(40)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(30, 60, 120)
        self.cell(0, 14, "Evil-Ai", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "Eval AI Agent - 24 Task Quick Reference", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(12)
        self.set_font("Helvetica", "", 11)
        self.set_x(self.l_margin)
        self.multi_cell(
            self.epw,
            7,
            "Hands-on exercises for evaluating AI coding agents.\n"
            "Covers beginner, intermediate, advanced, and DevOps tracks.",
            align="C",
        )
        self.ln(20)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Key constants", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font("Helvetica", "", 10)
        constants = [
            "Eval API URL:  http://127.0.0.1:8788",
            "Start server:  make eval-api",
            "Dashboard:     http://127.0.0.1:8788/",
            "Task guide:    GET /api/agent/guide/{ID}",
            "Submit work:   POST /api/agent/submit",
            "Verdicts:      ok | partial | mismatch",
            "Task IDs:      B1-B6, I1-I6, A1-A6, D1-D6",
        ]
        for line in constants:
            self.cell(0, 7, line, align="C", new_x="LMARGIN", new_y="NEXT")

    def section(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(self.epw, 5, text)
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(self.epw, 5, f"- {text}")

    def task_block(
        self,
        task_id: str,
        name: str,
        purpose: str,
        output: str,
        verify: str,
        depends: str = "",
        api_note: str = "",
    ) -> None:
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(20, 20, 20)
        self.cell(0, 6, f"{task_id} - {name}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 5, f"Purpose: {purpose}")
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 5, f"Output:  {output}")
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 5, f"Check:   {verify}")
        if depends:
            self.set_x(self.l_margin)
            self.multi_cell(self.epw, 5, f"Needs:   {depends}")
        if api_note:
            self.set_x(self.l_margin)
            self.multi_cell(self.epw, 5, f"API:     {api_note}")
        self.ln(2)


TASKS = {
    "Beginner (B1-B6)": [
        ("B1", "Repo Inventory", "Scan repo and list files by category", "REPORT.md, inventory.csv", "Match paths/counts in CSV", "", ""),
        ("B2", "API Map", "Find all HTTP routes in the project", "API_MAP.md, endpoints.csv", "25 routes across 6 services", "B1", ""),
        ("B3", "Test Discovery", "Find all tests and run them", "TEST_REPORT.md", "make test", "", ""),
        ("B4", "FastAPI Service", "Build transaction REST API in Python", "app/main.py, tests", "pytest (port 8000)", "", "GET/POST /transactions, GET /balance, GET /health"),
        ("B5", "Node API", "Same transaction API in Express", "src/app.js, tests", "npm test (port 3001)", "B4", "Same routes as B4 (no get-by-id)"),
        ("B6", "Rust CLI", "Log analyzer command-line tool", "src/main.rs, tests", "cargo test", "", "No HTTP - CLI only"),
    ],
    "Intermediate (I1-I6)": [
        ("I1", "ER Diagram", "Draw database entities and relationships", "ER_REPORT.md, er-diagram.mmd", "Match B4/D2/A3 models", "B1", ""),
        ("I2", "End-to-End Trace", "Trace request flow through system", "FLOW_TRACE.md, sequence-diagram.mmd", "Follow steps in trace doc", "B2", ""),
        ("I3", "Safe Change", "Plan a small code change with risk report", "CHANGE_REPORT.md, risk-assessment.md", "Risk scope matches report", "B3", ""),
        ("I4", "FastAPI + Node Pair", "Currency API + Node client", "fastapi main.py, node cli.js", "pytest + npm test (port 8000)", "B4, B5", "POST /convert, GET /health"),
        ("I5", "Dockerize", "Put a service in a Docker container", "Dockerfile, DOCKER_REPORT.md", "verify-docker.sh", "", ""),
        ("I6", "Bug Diagnosis", "Find root cause and document fix", "BUG_REPORT.md, ROOT_CAUSE_ANALYSIS.md", "Match RCA structure", "I2", ""),
    ],
    "Advanced (A1-A6)": [
        ("A1", "Parallel Planning", "Plan work for multiple agents/branches", "PARALLEL_EXECUTION_PLAN.md, agent-prompts.md", "Lane prompts match plan", "", ""),
        ("A2", "Parallel Worktrees", "Use git worktrees for parallel dev", "WORKTREE_EXECUTION_REPORT.md, merge-log.md", "Worktree workflow in report", "A1", ""),
        ("A3", "Polyglot System", "FastAPI -> queue -> Node worker -> Rust", "Python + Node + Rust services", "integration-test.sh (port 8000)", "B4, B5, B6, I4", "POST /transactions returns 202"),
        ("A4", "Modernization", "Find what to upgrade in codebase", "MODERNIZATION_REPORT.md, PRIORITIZATION_MATRIX.md", "Priority matrix is reference", "B1, B3", ""),
        ("A5", "Agent Review", "Review code/agent output with findings", "REVIEW_REPORT.md, FINDINGS_MATRIX.md", "Findings categorized like matrix", "", ""),
        ("A6", "Performance", "Benchmark and optimize code", "PERFORMANCE_REPORT.md, run-benchmark.sh", "Run benchmark script", "", ""),
    ],
    "DevOps (D1-D6)": [
        ("D1", "Terraform", "AWS infra as code (Lambda, etc.)", "main.tf, lambda/index.py", "terraform validate", "", ""),
        ("D2", "Docker Compose", "Multi-service stack (API + Postgres)", "docker-compose.yml, e2e_test.sh", "API on port 8200", "I5", "GET/POST /transactions, GET /health"),
        ("D3", "CI Pipeline", "Local CI (lint, test, build)", "PIPELINE_REPORT.md, run-pipeline-local.sh", "Run local pipeline script", "B3, I5", ""),
        ("D4", "Kubernetes", "K8s deployment manifests", "k8s/deployment.yaml, validate-manifests.sh", "Manifest validation passes", "I5", ""),
        ("D5", "Dev Environment", "One-command setup for whole repo", "README.md, bootstrap docs", "make bootstrap / make test", "B3", ""),
        ("D6", "Observability", "Logs + Prometheus + Grafana", "docker-compose.yml, service main.py", "GET /metrics (port 8000/18080)", "I5", "B4 routes + GET /metrics"),
    ],
}

ONE_LINERS = [
    ("B1", "List everything in the repo"),
    ("B2", "Map all API endpoints"),
    ("B3", "Find and run all tests"),
    ("B4", "Build FastAPI transaction API"),
    ("B5", "Build same API in Node.js"),
    ("B6", "Build Rust log analyzer CLI"),
    ("I1", "Draw ER diagram for data model"),
    ("I2", "Trace request flow end-to-end"),
    ("I3", "Plan a safe code change"),
    ("I4", "Currency API + Node client"),
    ("I5", "Dockerize a service"),
    ("I6", "Diagnose and document a bug"),
    ("A1", "Plan parallel agent work"),
    ("A2", "Use git worktrees in parallel"),
    ("A3", "Connect Python + Node + Rust system"),
    ("A4", "Plan codebase modernization"),
    ("A5", "Review agent/code quality"),
    ("A6", "Benchmark and optimize performance"),
    ("D1", "Terraform AWS infra"),
    ("D2", "Docker Compose multi-service stack"),
    ("D3", "CI pipeline (lint/test/build)"),
    ("D4", "Kubernetes manifests"),
    ("D5", "Reproducible dev environment setup"),
    ("D6", "Monitoring (metrics + Grafana)"),
]

PIPELINE = "B1 -> B2 -> B3 -> B4 -> B5 -> B6 -> I1 -> I2 -> I3 -> I4 -> I5 -> I6 -> A1 -> A2 -> A3 -> A4 -> A5 -> A6 -> D1 -> D2 -> D3 -> D4 -> D5 -> D6"


def build_pdf() -> None:
    pdf = NotesPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.title_page()

    pdf.add_page()
    pdf.section("How to Use the Eval API")
    pdf.body(
        "1. Clone repo and run: make setup && make eval-api\n"
        "2. Open dashboard: http://127.0.0.1:8788\n"
        "3. Get task instructions: curl http://127.0.0.1:8788/api/agent/guide/B4\n"
        "4. Do work in the task folder (e.g. beginner/B4-fastapi-service/)\n"
        "5. Submit: POST /api/agent/submit with task_id and output_path\n"
        "6. Check verdict on dashboard or GET /api/portfolio"
    )
    pdf.subsection("Main API Endpoints")
    endpoints = [
        "GET  /              Live dashboard (browser)",
        "GET  /api/health     Server health check",
        "GET  /api/docs       Full API list",
        "GET  /api/tasks      All 24 tasks",
        "GET  /api/tasks/{id} One task status",
        "GET  /api/agent/guide/{id}  Task instructions (read first)",
        "POST /api/agent/submit      Submit your work for checking",
        "GET  /api/portfolio         All tasks + results (JSON)",
        "POST /api/portfolio/refresh Re-scan repo files",
    ]
    for ep in endpoints:
        pdf.bullet(ep)

    pdf.subsection("Submit Example")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Courier", "", 8)
    pdf.multi_cell(
        pdf.epw,
        4,
        'curl -X POST http://127.0.0.1:8788/api/agent/submit \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"task_id":"B2","output_path":"beginner/B2-api-endpoint-map/API_MAP.md"}\'',
    )
    pdf.ln(4)

    for section_title, tasks in TASKS.items():
        pdf.add_page()
        pdf.section(section_title)
        for task in tasks:
            pdf.task_block(*task)

    pdf.add_page()
    pdf.section("One-Line Summary (All 24)")
    for task_id, summary in ONE_LINERS:
        pdf.bullet(f"{task_id}: {summary}")

    pdf.ln(4)
    pdf.section("Suggested Pipeline Order")
    pdf.body(PIPELINE)

    pdf.ln(4)
    pdf.section("Task Types")
    pdf.bullet("analysis - B1, B2, B3 (read repo, write reports)")
    pdf.bullet("code - B4, B5, B6, I4, A3, A6 (write and run code)")
    pdf.bullet("report - I1, I2, I3, I6, A1, A2, A4, A5 (docs and diagrams)")
    pdf.bullet("infra - I5, D1-D6 (Docker, Terraform, CI, K8s)")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
