#!/usr/bin/env python3
"""
Deterministic Source-Grounded Pedagogy, 5-Step Hiring Mastery & Continuity Linter
(`.agents/rules/03-true-zero-pedagogy-and-continuity.md`)

Enforces:
1. Antigravity `always_on` rule size & token budget (< 24 KB per file, < 20,000 tokens total).
2. Law 1 (Udemy Continuity): Non-empty ```json continuity``` (`previously`, `painPoint`, `unlock`).
3. Law 2 (4-Pillar Source Grounding for v2 Courses):
   - Valid `COURSE_MANIFEST.json` (officialSources, canonicalReferences, bigTechCaseStudies, chapters)
   - Acyclic prerequisite DAG across all chapters in the course
   - Per-chapter YAML frontmatter `prerequisites` & `primary_sources`
4. Law 3 (Progressive Chain of Information):
   - Legacy v1 chapters: Sequential `Step 1..4`
   - Hiring-Grade v2 chapters: Sequential `Step 1..5`
     * Step 1: ZERO `$$` display math and ZERO >20-line code blocks.
     * Step 2: `python` + `java` starter code (+ `bash` CLI block & `# Subgoal` labels in v2).
     * Step 3: `contrast` Naive-vs-Staff card.
     * Step 4: `> [!WARNING]` Bar-Raiser Gotcha, `>= 3` `quiz` items (+ `🏢` Big Tech case study in v2).
     * Step 5 (v2): Cheat-Sheet lookup table, `🎙️` 60-Second Interview Soundbite, and verified `https://` sources.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
KB_ROOT = REPO_ROOT / "knowledgebase"

# Courses enforcing full v2 4-Pillar COURSE_MANIFEST.json + 5-Step Hiring-Grade Mastery Chain
REQUIRED_V2_SOURCED_COURSES: tuple[str, ...] = (
    "09-sql-and-data-engineering",
)

REQUIRED_TRUE_ZERO_RELPATHS: tuple[str, ...] = (
    # Course 01: Zero to Staff SDET (12/12 chapters)
    "01-zero-to-staff-sdet/01-determinism-and-flakiness-math.md",
    "01-zero-to-staff-sdet/02-test-design-bva-and-pairwise.md",
    "01-zero-to-staff-sdet/03-test-pyramid-and-seam-economics.md",
    "01-zero-to-staff-sdet/04-hermetic-environments-and-ephemeral-containers.md",
    "01-zero-to-staff-sdet/05-parallel-tenant-isolation.md",
    "01-zero-to-staff-sdet/06-async-event-driven-and-saga-testing.md",
    "01-zero-to-staff-sdet/07-ci-sharding-and-bin-packing.md",
    "01-zero-to-staff-sdet/08-test-impact-analysis-and-ast-graphs.md",
    "01-zero-to-staff-sdet/09-statistical-flake-quarantine-governance.md",
    "01-zero-to-staff-sdet/10-opentelemetry-traceparent-triage.md",
    "01-zero-to-staff-sdet/11-shift-right-canaries-and-chaos.md",
    "01-zero-to-staff-sdet/12-staff-sdet-rfcs-and-dora-metrics.md",
    # Course 02: Building Testing Frameworks (10/10 chapters)
    "02-building-testing-frameworks/01-runner-lifecycles-and-ast-discovery.md",
    "02-building-testing-frameworks/02-di-fixtures-and-lifo-teardown.md",
    "02-building-testing-frameworks/03-pom-components-app-actions-screenplay.md",
    "02-building-testing-frameworks/04-fluent-immutable-data-builders.md",
    "02-building-testing-frameworks/05-recursive-payload-and-ast-diff-engines.md",
    "02-building-testing-frameworks/06-parallel-worker-process-and-thread-isolation.md",
    "02-building-testing-frameworks/07-smart-retries-and-rate-limited-clients.md",
    "02-building-testing-frameworks/08-stateful-in-memory-mock-servers.md",
    "02-building-testing-frameworks/09-structured-artifacts-allure-and-otel-reporters.md",
    "02-building-testing-frameworks/10-multi-env-config-secrets-and-sdk-packaging.md",
    # Course 03: UI Automation — Playwright (10/10 chapters)
    "03-ui-automation-playwright/01-webdriver-http-vs-cdp-and-bidi-pipes.md",
    "03-ui-automation-playwright/02-browser-processes-vs-browser-context-memory.md",
    "03-ui-automation-playwright/03-dom-shadow-dom-iframes-and-hydration-races.md",
    "03-ui-automation-playwright/04-accessibility-tree-locators-and-strict-mode.md",
    "03-ui-automation-playwright/05-five-actionability-gates-and-web-first-assertions.md",
    "03-ui-automation-playwright/06-zero-ui-auth-storage-state-and-personas.md",
    "03-ui-automation-playwright/07-network-interception-route-and-har-replay.md",
    "03-ui-automation-playwright/08-clock-virtualization-websockets-and-aerocart.md",
    "03-ui-automation-playwright/09-trace-viewer-forensics-a11y-and-visual-diffing.md",
    "03-ui-automation-playwright/10-containerized-sharding-and-blob-reports.md",
    # Course 04: API & API Automation (10/10 chapters)
    "04-api-and-api-automation/01-tcp-tls13-and-http2-connection-pooling.md",
    "04-api-and-api-automation/02-rest-idempotency-caching-and-pagination.md",
    "04-api-and-api-automation/03-auth-internals-jwt-oauth2-pkce-and-mtls.md",
    "04-api-and-api-automation/04-production-api-clients-pydantic-and-rest-assured.md",
    "04-api-and-api-automation/05-rate-limiting-token-buckets-and-timeouts.md",
    "04-api-and-api-automation/06-graphql-ast-n-plus-one-and-error-envelopes.md",
    "04-api-and-api-automation/07-grpc-protobuf-framing-and-deadlines.md",
    "04-api-and-api-automation/08-async-saga-and-webhook-verification.md",
    "04-api-and-api-automation/09-openapi-schema-governance-and-fuzzing.md",
    "04-api-and-api-automation/10-pact-consumer-driven-contract-testing.md",
    # Course 05: AI Engineering (12/12 chapters)
    "05-ai-engineering/01-supervised-learning-loss-and-gradient-descent.md",
    "05-ai-engineering/02-classification-metrics-calibration-and-drift.md",
    "05-ai-engineering/03-bpe-tokenization-and-embedding-geometry.md",
    "05-ai-engineering/04-scaled-dot-product-attention-and-causal-masking.md",
    "05-ai-engineering/05-modern-transformers-rope-swiglu-gqa-and-moe.md",
    "05-ai-engineering/06-inference-mechanics-kv-cache-pagedattention-quantization.md",
    "05-ai-engineering/07-sampling-physics-and-constrained-structured-outputs.md",
    "05-ai-engineering/08-context-architecture-prefix-caching-and-ttft-economics.md",
    "05-ai-engineering/09-hybrid-rag-chunking-hnsw-bm25-and-rrf.md",
    "05-ai-engineering/10-cross-encoder-reranking-and-contextual-retrieval.md",
    "05-ai-engineering/11-rag-vs-fine-tuning-lora-qlora-and-dpo.md",
    "05-ai-engineering/12-agentic-architectures-tool-contracts-and-mcp.md",
    # Course 06: AI Engineering — QA-Focused (10/10 chapters across 06-ai-engineering-qa-focused/ + ai-engineering/)
    "06-ai-engineering-qa-focused/01-testing-nondeterministic-systems-and-metamorphic-qa.md",
    "06-ai-engineering-qa-focused/02-golden-dataset-engineering-and-stratification.md",
    "ai-engineering/01-rag-triad-and-claim-verification.md",
    "06-ai-engineering-qa-focused/04-negation-flips-entity-swaps-and-abstention-qa.md",
    "06-ai-engineering-qa-focused/05-llm-judge-biases-and-pairwise-swap-debiasing.md",
    "06-ai-engineering-qa-focused/06-statistical-judge-calibration-kappa-and-rogan-gladen.md",
    "06-ai-engineering-qa-focused/07-adversarial-red-teaming-prompt-injection-and-pii.md",
    "06-ai-engineering-qa-focused/08-agent-trajectory-qa-and-mock-mcp-sandboxes.md",
    "ai-engineering/02-self-healing-ast-and-dom-confidence.md",
    "06-ai-engineering-qa-focused/10-production-ai-ci-gates-and-shadow-drift-monitoring.md",
    # Course 07: Distributed System Design (5/5 chapters)
    "system-design/01-continuous-sync-and-backpressure.md",
    "system-design/02-consistent-hashing-and-sharding.md",
    "system-design/03-kafka-outbox-and-eventual-consistency.md",
    "system-design/04-distributed-caching-and-singleflight.md",
    "system-design/05-replication-quorums-and-raft-consensus.md",
    # Course 08: Core CS Internals (5/5 chapters)
    "core-cs/01-os-virtual-memory-gc-and-fd-leaks.md",
    "core-cs/02-tcp-tls-http2-and-websocket-framing.md",
    "core-cs/03-lsm-trees-b-trees-and-wal-isolation.md",
    "core-cs/04-concurrency-mutexes-and-lock-free-cas.md",
    "core-cs/05-linux-epoll-cgroups-and-containers.md",
    # Course 09: SQL, PostgreSQL & Data Validation Engineering (10/10 v2 5-Step chapters)
    "09-sql-and-data-engineering/01-day0-relational-schemas-keys-and-crud.md",
    "09-sql-and-data-engineering/02-joins-set-operations-and-fanout-traps.md",
    "09-sql-and-data-engineering/03-aggregations-having-ctes-and-cohort-assertions.md",
    "09-sql-and-data-engineering/04-window-functions-ranking-lag-and-dedup.md",
    "09-sql-and-data-engineering/05-btree-composite-indexes-and-sargability.md",
    "09-sql-and-data-engineering/06-explain-analyze-query-plans-and-join-algorithms.md",
    "09-sql-and-data-engineering/07-acid-mvcc-isolation-and-seat-double-booking.md",
    "09-sql-and-data-engineering/08-zero-downtime-migrations-jsonb-and-constraints.md",
    "09-sql-and-data-engineering/09-synthetic-test-data-seeding-and-db-isolation.md",
    "09-sql-and-data-engineering/10-event-to-warehouse-reconciliation-and-data-qa.md",
)


def _extract_frontmatter_dict(raw: str) -> dict[str, str]:
    if not raw.startswith("---\n"):
        return {}
    end_idx = raw.find("\n---\n", 4)
    if end_idx == -1:
        return {}
    out: dict[str, str] = {}
    for line in raw[4:end_idx].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def is_true_zero_chapter(md_path: pathlib.Path) -> bool:
    rel = md_path.relative_to(KB_ROOT).as_posix()
    if rel in REQUIRED_TRUE_ZERO_RELPATHS:
        return True
    raw = md_path.read_text(encoding="utf-8")
    return bool(
        re.search(r"```json\s+continuity\b", raw)
        or re.search(r"^##\s+.*Step\s+1\b", raw, flags=re.MULTILINE)
    )


def audit_true_zero_chapter(md_path: pathlib.Path) -> list[str]:
    raw = md_path.read_text(encoding="utf-8")
    errors: list[str] = []
    fm = _extract_frontmatter_dict(raw)
    is_v2_course = md_path.parent.name in REQUIRED_V2_SOURCED_COURSES

    # 1. Law 1: Mandatory ```json continuity``` story bridge
    m_cont = re.search(r"```json\s+continuity\s*\n(.*?)```", raw, flags=re.DOTALL)
    if not m_cont:
        errors.append("Missing ```json continuity``` story bridge block")
    else:
        try:
            c_data = json.loads(m_cont.group(1).strip())
            for key in ("previously", "painPoint", "unlock"):
                if not str(c_data.get(key, "")).strip():
                    errors.append(f"Empty continuity.{key}")
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in continuity block: {exc}")

    # 2. Law 3: Progressive Chain (Step 1..4 for v1; Step 1..5 required for v2 courses)
    step_headings = re.findall(r"^##\s+.*Step\s+([1-5])\b.*$", raw, flags=re.MULTILINE)
    is_v2_chapter = is_v2_course or step_headings == ["1", "2", "3", "4", "5"]

    if is_v2_course and step_headings != ["1", "2", "3", "4", "5"]:
        errors.append(f"v2 course chapter requires sequential Step 1..5 headings, found {step_headings}")
    elif step_headings not in (["1", "2", "3", "4"], ["1", "2", "3", "4", "5"]):
        errors.append(f"Expected sequential Step 1..4 (or Step 1..5) headings, found {step_headings}")

    # 2b. Law 2: Per-Chapter YAML Grounding for v2 chapters
    if is_v2_chapter:
        for req_fm in ("prerequisites", "primary_sources"):
            raw_val = fm.get(req_fm, "")
            if not raw_val.startswith("["):
                errors.append(f"Missing or non-JSON-array YAML frontmatter `{req_fm}` in v2 chapter")
            else:
                try:
                    parsed_arr = json.loads(raw_val)
                    if not isinstance(parsed_arr, list):
                        errors.append(f"YAML `{req_fm}` must be a JSON array")
                    elif req_fm == "primary_sources" and len(parsed_arr) < 2:
                        errors.append("YAML `primary_sources` must cite at least 2 verified sources")
                except json.JSONDecodeError as exc:
                    errors.append(f"Invalid JSON in YAML `{req_fm}`: {exc}")

    # 3. Step 1 must NOT ambush beginners with `$$` display math or >20-line code blocks
    m_step1 = re.search(
        r"^##\s+.*Step\s+1\b.*?\n(.*?)(?=^##\s+.*Step\s+2\b)",
        raw,
        flags=re.MULTILINE | re.DOTALL,
    )
    if m_step1:
        step1_text = m_step1.group(1)
        if "$$" in step1_text:
            errors.append("Symbol-shock violation: `$$` display math found inside Step 1 (Plain-English Story)")
        for code_m in re.finditer(r"```(?!mermaid)[^\n]*\n(.*?)```", step1_text, flags=re.DOTALL):
            lines = code_m.group(1).strip().splitlines()
            if len(lines) > 20:
                errors.append(f"Code-wall violation in Step 1: {len(lines)} lines (>20 max)")

    # 4. Step 2 must provide immediate working starter code in Python 3 + Java 17 (+ bash & Subgoal in v2)
    m_step2 = re.search(
        r"^##\s+.*Step\s+2\b.*?\n(.*?)(?=^##\s+.*Step\s+3\b)",
        raw,
        flags=re.MULTILINE | re.DOTALL,
    )
    if m_step2:
        step2_text = m_step2.group(1)
        if "```python" not in step2_text or "```java" not in step2_text:
            errors.append("Step 2 must include both ```python and ```java starter code blocks")
        if is_v2_chapter:
            if "```bash" not in step2_text:
                errors.append("v2 Step 2 must include a ```bash setup/run CLI block")
            if "Subgoal" not in step2_text:
                errors.append("v2 Step 2 starter code must include explicit `Subgoal` comment labels")

    # 5. Step 3 must include a Contrastive Naive-vs-Pro card
    m_step3 = re.search(
        r"^##\s+.*Step\s+3\b.*?\n(.*?)(?=^##\s+.*Step\s+4\b)",
        raw,
        flags=re.MULTILINE | re.DOTALL,
    )
    if m_step3 and not re.search(r"```(?:json\s+)?contrast\b", m_step3.group(1)):
        errors.append("Missing ```json contrast``` card in Step 3")

    # 6. Step 4 must include a Staff Interview Gotcha (`> [!WARNING]`), >=3 Quiz items (+ 🏢 Big Tech case study in v2)
    m_step4 = re.search(
        r"^##\s+.*Step\s+4\b.*?\n(.*?)(?=^##\s+.*Step\s+5\b|\Z)",
        raw,
        flags=re.MULTILINE | re.DOTALL,
    )
    if m_step4:
        step4_text = m_step4.group(1)
        if "[!WARNING]" not in step4_text:
            errors.append("Missing `> [!WARNING]` Staff Interview Gotcha callout in Step 4")
        if is_v2_chapter and "🏢" not in step4_text:
            errors.append("v2 Step 4 must include a `🏢` Big Tech production case study section")
        m_quiz = re.search(r"```json\s+quiz\s*\n(.*?)```", raw[m_step4.start() :], flags=re.DOTALL)
        if not m_quiz:
            errors.append("Missing ```json quiz``` block in Step 4")
        else:
            try:
                q_list = json.loads(m_quiz.group(1).strip())
                if not isinstance(q_list, list) or len(q_list) < 3:
                    errors.append("Step 4 quiz must contain at least 3 questions")
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON in Step 4 quiz: {exc}")

    # 7. Step 5 (v2 Hiring-Grade Reference): Cheat-Sheet table + 🎙️ 60s Interview Soundbite + Verified Sources
    if is_v2_chapter:
        m_step5 = re.search(r"^##\s+.*Step\s+5\b.*?\n(.*)$", raw, flags=re.MULTILINE | re.DOTALL)
        if not m_step5:
            errors.append("Missing Step 5 section in v2 chapter")
        else:
            step5_text = m_step5.group(1)
            if "|---" not in step5_text and "| ---" not in step5_text and "| :---" not in step5_text:
                errors.append("v2 Step 5 must include a Markdown Cheat-Sheet lookup table")
            if "🎙️" not in step5_text:
                errors.append("v2 Step 5 must include a `🎙️` 60-Second Interview Soundbite")
            if len(re.findall(r"https://", step5_text)) < 2:
                errors.append("v2 Step 5 must include at least 2 clickable `https://` primary source links")

    return errors


def audit_v2_course_manifests() -> list[str]:
    """
    Validate 4-Pillar COURSE_MANIFEST.json, acyclic prerequisite DAG, and 1-to-1
    extraction mapping between COURSE_MANIFEST.json and actual chapter Markdown content.
    """
    errors: list[str] = []
    for course_id in REQUIRED_V2_SOURCED_COURSES:
        course_dir = KB_ROOT / course_id
        manifest_path = course_dir / "COURSE_MANIFEST.json"
        if not manifest_path.exists():
            errors.append(f"[{course_id}] Missing COURSE_MANIFEST.json")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"[{course_id}] Invalid JSON in COURSE_MANIFEST.json: {exc}")
            continue

        for req_key in (
            "courseId",
            "projectThread",
            "officialSources",
            "canonicalReferences",
            "bigTechCaseStudies",
            "chapters",
        ):
            if not manifest.get(req_key):
                errors.append(f"[{course_id}] COURSE_MANIFEST.json missing or empty `{req_key}`")

        if manifest.get("courseId") != course_id:
            errors.append(f"[{course_id}] Manifest courseId `{manifest.get('courseId')}` != `{course_id}`")

        chapters = manifest.get("chapters") or []
        slug_set = {ch.get("slug") for ch in chapters if ch.get("slug")}
        prereq_graph: dict[str, list[str]] = {}
        manifest_files: list[str] = []

        for ch in chapters:
            slug = ch.get("slug", "")
            fname = ch.get("file", "")
            ch_num = ch.get("chapterNumber")
            manifest_files.append(fname)
            md_file = course_dir / fname
            if not fname or not md_file.exists():
                errors.append(f"[{course_id}] Manifest chapter file missing on disk: {fname}")
                continue

            prereqs = ch.get("prerequisites") or []
            prereq_graph[slug] = prereqs
            for p_slug in prereqs:
                if p_slug not in slug_set:
                    errors.append(f"[{course_id}] Chapter `{slug}` cites unknown course prerequisite `{p_slug}`")

            # Verify 1-to-1 mapping between Manifest entry and actual Markdown file on disk
            raw_md = md_file.read_text(encoding="utf-8")
            fm = _extract_frontmatter_dict(raw_md)
            fm_slug = fm.get("slug", "").strip('"').strip("'")
            if fm_slug != slug:
                errors.append(f"[{course_id}:{fname}] Manifest slug `{slug}` != frontmatter slug `{fm_slug}`")

            try:
                fm_ch_num = int(fm.get("chapter_number", "0").strip('"').strip("'"))
                if fm_ch_num != ch_num:
                    errors.append(
                        f"[{course_id}:{fname}] Manifest chapterNumber `{ch_num}` != frontmatter `{fm_ch_num}`"
                    )
            except ValueError:
                errors.append(f"[{course_id}:{fname}] Invalid integer chapter_number in frontmatter")

            try:
                fm_prereqs = json.loads(fm.get("prerequisites", "[]"))
                if fm_prereqs != prereqs:
                    errors.append(
                        f"[{course_id}:{fname}] Manifest prerequisites {prereqs} != frontmatter {fm_prereqs}"
                    )
            except json.JSONDecodeError:
                errors.append(f"[{course_id}:{fname}] Invalid JSON prerequisites in frontmatter")

            # Verify every frontmatter `primary_sources` URL is rendered inside Step 5 of the chapter
            try:
                fm_sources = json.loads(fm.get("primary_sources", "[]"))
                m_step5 = re.search(r"^##\s+.*Step\s+5\b.*?\n(.*)$", raw_md, flags=re.MULTILINE | re.DOTALL)
                step5_body = m_step5.group(1) if m_step5 else ""
                for src_url in fm_sources:
                    if src_url not in step5_body:
                        errors.append(
                            f"[{course_id}:{fname}] Frontmatter primary_source `{src_url}` not cited in Step 5"
                        )
            except json.JSONDecodeError:
                pass

            # Verify every Manifest competency is substantively covered in the chapter markdown
            competencies = ch.get("competencies") or []
            if len(competencies) < 3:
                errors.append(f"[{course_id}:{fname}] Manifest must declare >= 3 competencies")
            lower_md = raw_md.lower()
            for comp in competencies:
                comp_tokens = [
                    tok.lower()
                    for tok in re.findall(r"[A-Za-z0-9_]{3,}", comp)
                    if tok.lower() not in {"and", "the", "for", "with", "from", "into", "why", "how", "via"}
                ]
                if comp_tokens and not any(tok in lower_md for tok in comp_tokens):
                    errors.append(
                        f"[{course_id}:{fname}] Manifest competency `{comp}` has zero matching terms in chapter content"
                    )

        actual_md_files = sorted(f.name for f in course_dir.glob("*.md"))
        if sorted(manifest_files) != actual_md_files:
            errors.append(
                f"[{course_id}] Manifest chapters {sorted(manifest_files)} != disk files {actual_md_files}"
            )

        # Cycle check via DFS coloring (0=unvisited, 1=visiting, 2=visited)
        color: dict[str, int] = {s: 0 for s in prereq_graph}

        def _has_cycle(node: str) -> bool:
            color[node] = 1
            for dep in prereq_graph.get(node, []):
                if dep not in color:
                    continue
                if color[dep] == 1 or (color[dep] == 0 and _has_cycle(dep)):
                    return True
            color[node] = 2
            return False

        for s in prereq_graph:
            if color[s] == 0 and _has_cycle(s):
                errors.append(f"[{course_id}] Prerequisite cycle detected involving `{s}`")
                break

    return errors


def audit_rule_budget() -> list[str]:
    errors: list[str] = []
    rule_files = [REPO_ROOT / "GEMINI.md"] + sorted((REPO_ROOT / ".agents" / "rules").glob("*.md"))
    total_bytes = 0
    for rf in rule_files:
        if not rf.exists():
            continue
        size = rf.stat().st_size
        total_bytes += size
        if size > 24000:
            errors.append(f"Rule file {rf.name} exceeds 24,000-byte limit ({size} bytes)")
    est_tokens = total_bytes // 4
    if est_tokens > 20000:
        errors.append(f"Aggregate always_on rules exceed 20,000-token budget (~{est_tokens} tokens)")
    return errors


def audit_all_upgraded_chapters() -> tuple[int, int, dict[str, list[str]]]:
    all_chapters = sorted(KB_ROOT.glob("*/*.md"))
    upgraded_count = 0
    violations: dict[str, list[str]] = {}
    for md_path in all_chapters:
        if is_true_zero_chapter(md_path):
            upgraded_count += 1
            errs = audit_true_zero_chapter(md_path)
            if errs:
                violations[md_path.relative_to(KB_ROOT).as_posix()] = errs
    for m_err in audit_v2_course_manifests():
        violations.setdefault("COURSE_MANIFEST", []).append(m_err)
    return upgraded_count, len(all_chapters), violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Source-Grounded Pedagogy & Udemy Continuity rules.")
    parser.add_argument("--report", action="store_true", help="Print per-course migration & v2 sourcing report.")
    parser.add_argument("--strict", nargs="*", help="Strictly audit specific chapter file path(s).")
    args = parser.parse_args()

    budget_errors = audit_rule_budget()
    if budget_errors:
        for err in budget_errors:
            print(f"[FAIL] Rule budget: {err}", file=sys.stderr)
        return 1

    if args.strict:
        failed = 0
        for raw_target in args.strict:
            target = pathlib.Path(raw_target).resolve()
            errs = audit_true_zero_chapter(target)
            if errs:
                failed += 1
                print(f"[FAIL] {target.relative_to(REPO_ROOT)}: {errs}")
            else:
                print(f"[PASS] {target.relative_to(REPO_ROOT)}: Pedagogy & Continuity Chain verified.")
        return 1 if failed else 0

    upgraded_count, total_count, violations = audit_all_upgraded_chapters()

    if args.report:
        print("=== Source-Grounded Pedagogy & Udemy-Continuity Course Report ===")
        for course_dir in sorted(p for p in KB_ROOT.iterdir() if p.is_dir()):
            ch_files = sorted(course_dir.glob("*.md"))
            tz_files = [f for f in ch_files if is_true_zero_chapter(f)]
            mode_tag = "v2 5-Step Sourced" if course_dir.name in REQUIRED_V2_SOURCED_COURSES else "v1 4-Step Guided"
            print(f"  {course_dir.name:<36} {len(tz_files):>2} / {len(ch_files):<2} chapters ({mode_tag})")
        print(
            f"Total Verified: {upgraded_count} / {total_count} chapters | "
            f"v2 Sourced Courses: {len(REQUIRED_V2_SOURCED_COURSES)} | Violations: {len(violations)}"
        )

    if violations:
        for rel, errs in violations.items():
            print(f"[FAIL] {rel}:", file=sys.stderr)
            for err in errs:
                print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"[PASS] Rule 03 Pedagogy Gate: {upgraded_count}/{total_count} chapters verified "
        f"({len(REQUIRED_V2_SOURCED_COURSES)} v2 Sourced 5-Step courses, 0 violations)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
