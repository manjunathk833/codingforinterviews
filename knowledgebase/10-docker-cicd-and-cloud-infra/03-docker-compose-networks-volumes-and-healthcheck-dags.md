---
slug: "infra-03-docker-compose-networks-volumes-and-healthcheck-dags"
course_id: "10-docker-cicd-and-cloud-infra"
track: "system-design"
volume: "10. Docker, Kubernetes, CI/CD & Quality Infrastructure"
module_number: 1
module_title: "Module 1: Container Internals, Multi-Stage BuildKit, Compose DAGs & Hermetic Testcontainers"
chapter_number: 3
level_tag: "Absolute Zero → Senior/Staff"
title: "Docker Compose Topologies: Bridge DNS, Anonymous Volumes & Healthcheck Startup DAGs"
summary: "Build AeroPipe v0.3: wire multi-container stacks (PostgreSQL 17, Redis, AeroCart API, Playwright Runner), understand why plain depends_on causes Connection Refused races, enforce condition: service_healthy startup DAGs, and resolve 127.0.0.1 vs Bridge DNS traps."
reading_time_minutes: 15
visualizer_id: "infra-docker-layer-testcontainers"
lab_path: "frameworks/cicd-infra/01-container-and-sharding-orchestrator"
tags: ["docker-compose", "healthcheck", "depends-on", "bridge-dns", "volumes", "ci-stacks"]
prerequisites: ["infra-02-multistage-dockerfiles-layer-caching-and-buildkit"]
primary_sources: ["https://docs.docker.com/compose/how-tos/startup-order/", "https://docs.docker.com/compose/how-tos/networking/", "https://docs.docker.com/reference/compose-file/services/"]
---

# Docker Compose Topologies: Bridge DNS, Anonymous Volumes & Healthcheck Startup DAGs

```json continuity
{
  "previously": "In Chapter 02, we built `AeroPipe v0.2` using multi-stage BuildKit `Dockerfile`s, lockfile-first caching, and non-root runtime images.",
  "painPoint": "When we wired `AeroCart API`, `PostgreSQL 17`, and our `Playwright/Pytest` test container together in `docker-compose.yml` using `depends_on: [postgres]`, 40% of CI runs failed immediately with `psycopg.OperationalError: connection to server at '127.0.0.1' port 5432 failed: Connection refused`!",
  "unlock": "Evolve to AeroPipe v0.3: replace host loopback (`127.0.0.1`) with Docker Bridge DNS service discovery (`postgres:5432`), upgrade `depends_on` from process-start to `condition: service_healthy` startup DAGs with `pg_isready`, and teardown ephemeral volumes cleanly with `docker compose down -v`."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "The 127.0.0.1 Trap",
    "title": "Why `127.0.0.1:5432` Inside a Container Never Reaches Neighboring Containers",
    "caption": "Every container has its own Linux `net` namespace! Inside the `aerocart-api` container, `127.0.0.1` points back to `aerocart-api` itself—not the `postgres` container.",
    "nodes": ["aerocart-api (net ns A)", "127.0.0.1 -> Self! (Refused)", "Bridge DNS (127.0.0.11)", "postgres:5432 (net ns B)"],
    "activeIndex": 2,
    "code": "# ❌ Broken inside container:\nDATABASE_URL=postgresql://aero:pass@127.0.0.1:5432/aerodb\n# ✅ Correct (Docker embedded DNS resolves service name 'postgres'):\nDATABASE_URL=postgresql://aero:pass@postgres:5432/aerodb"
  },
  {
    "time": "0:25",
    "badge": "The depends_on Lie",
    "title": "Why Plain `depends_on: [postgres]` Still Throws `Connection Refused`",
    "caption": "By default, `depends_on` only waits until the Postgres container's Linux PID is created (~50ms). Postgres still needs 1.5–3.0 seconds to initialize `initdb`, replay WAL, and bind TCP port 5432!",
    "nodes": ["T=0.05s: Postgres PID Started", "T=0.06s: API Starts & Crashes!", "T=2.10s: Port 5432 Actually Ready", "Race Condition!"],
    "activeIndex": 1,
    "code": "# ❌ Plain depends_on only waits for container_started, NOT port readiness!\ndepends_on:\n  - postgres"
  },
  {
    "time": "0:50",
    "badge": "Healthcheck DAG",
    "title": "Enforcing a True Readiness DAG with `healthcheck` + `condition: service_healthy`",
    "caption": "Pair a service `healthcheck` (`pg_isready` or HTTP `/healthz`) with `depends_on: condition: service_healthy` so downstream containers wait deterministically until upstream ports accept traffic.",
    "nodes": ["postgres: pg_isready (Healthy)", "migrations: service_completed_successfully", "aerocart-api: /healthz (Healthy)", "e2e-tests: Runs with 0 Flakes!"],
    "activeIndex": 3,
    "code": "depends_on:\n  postgres:\n    condition: service_healthy\n  migrations:\n    condition: service_completed_successfully"
  },
  {
    "time": "1:15",
    "badge": "Volume Hygiene",
    "title": "Named Volumes vs. `tmpfs` & Why `docker compose down` Without `-v` Leaks State",
    "caption": "`docker compose down` stops containers and removes networks, but keeps named volumes on disk! In CI, always pass `down -v --remove-orphans` (or mount test DBs on `tmpfs`) so stale rows never pollute the next test run.",
    "nodes": ["tmpfs (/var/lib/postgresql/data)", "RAM-Speed In-Memory DB", "docker compose down -v", "100% Clean CI Slate"],
    "activeIndex": 2,
    "code": "docker compose -p aeropipe-ci-${BUILD_ID} up --build --abort-on-container-exit --exit-code-from e2e-tests\ndocker compose -p aeropipe-ci-${BUILD_ID} down -v --remove-orphans"
  }
]
```

```json pretraining
[
  {
    "term": "Docker Bridge DNS (`127.0.0.11`)",
    "formula": "Service Name (`postgres`) -> Container Virtual IP (`172.18.0.2`)",
    "meaning": "An embedded DNS server mounted inside every user-defined Compose network that automatically resolves each service's YAML name (`postgres`, `redis`, `aerocart-api`) to its container IP address."
  },
  {
    "term": "`condition: service_started` vs. `condition: service_healthy`",
    "formula": "Process PID Spawned (50ms) != Application Port Ready (2,000ms)",
    "meaning": "Default `depends_on` (`service_started`) fires the instant the container's OS process spawns; `service_healthy` waits until the container's `healthcheck` command exits `0`."
  },
  {
    "term": "`condition: service_completed_successfully`",
    "formula": "One-Shot Init / Migration Job Exit Code == 0",
    "meaning": "A Compose dependency condition designed for Flyway/Alembic schema migration or test-seed containers that must run to completion and exit `0` before the API or test runner starts."
  },
  {
    "term": "Named Volumes vs. Bind Mounts vs. `tmpfs`",
    "formula": "Named = Docker-Managed Disk · Bind = Host Path · tmpfs = Ephemeral RAM",
    "meaning": "Named volumes persist across `docker compose down` unless `-v` is passed; `tmpfs` mounts store database files in host RAM and vanish automatically the instant the container stops."
  }
]
```

## 🌱 Step 1: Plain-English Mental Model — Private Apartment Intercoms & Waiting for the Kitchen to Warm Up

In Chapter 01, we learned that every container lives inside its own soundproofed apartment (**Linux `net` namespace**). Now suppose you launch two containers: `aerocart-api` in Apartment A and `postgres` in Apartment B.

1. **Why `127.0.0.1` Fails (The Mirror Trap)**: In networking, `127.0.0.1` (`localhost`) means *"this very apartment."* When `aerocart-api` dials `127.0.0.1:5432`, it is knocking on its **own closet door** inside Apartment A, where no database lives! To call Apartment B, it must dial the building's **Bridge DNS intercom** using the service name: `postgres:5432`.
2. **Why Default `depends_on` Fails (Unlocking the Door $\neq$ Oven Preheated)**: Imagine a restaurant where the waiter (`aerocart-api`) starts taking food orders the millisecond the chef (`postgres`) walks through the back door, before the chef has even turned on the stove! That is what plain `depends_on: [postgres]` does: it waits `50ms` for the container process to exist, not `2,000ms` for PostgreSQL to finish booting and open port `5432`.

By adding a **`healthcheck` probe** (`pg_isready`) and **`condition: service_healthy`**, `AeroPipe v0.3` turns a race condition into a deterministic **Startup Directed Acyclic Graph (DAG)**:

```mermaid
flowchart LR
    PG["1. postgres (pg_isready == 0)"] -->|"service_healthy"| Mig["2. db-migrate (Exit 0)"]
    Mig -->|"service_completed_successfully"| API["3. aerocart-api (/healthz == 200)"]
    API -->|"service_healthy"| Tests["4. e2e-tests (Pytest / Playwright)"]
```

---

## 🔨 Step 2: Zero-to-Running Starter & CLI — Orchestrating `AeroPipe v0.3`

Here is the exact CLI workflow to run a hermetic multi-container E2E test stack in CI, stream the test runner's exit code back to the pipeline, and guarantee zero leaked volumes or orphan containers:

```bash
# 1. Start the Compose DAG, block until e2e-tests finishes, and return e2e-tests' exit code
docker compose -p aeropipe-pr-42 up \
  --build \
  --abort-on-container-exit \
  --exit-code-from e2e-tests

# 2. Always run in an 'always()' CI post-step: destroy containers, networks, AND named volumes (-v)
docker compose -p aeropipe-pr-42 down -v --remove-orphans
```

Let's build a runnable Python 3 and Java 17 **Compose Healthcheck DAG & Bridge DNS Resolver Simulator** that models why plain `depends_on` (`service_started`) crashes at `t=50ms` while `service_healthy` + `service_completed_successfully` sequences the 4-stage pipeline with zero race conditions:

```python
from __future__ import annotations
from dataclasses import dataclass


# Subgoal 1: Model each Compose service's process spawn time, readiness time, and dependency rules
@dataclass(frozen=True)
class ComposeService:
    name: str
    pid_spawn_ms: int
    ready_or_complete_ms: int
    depends_on: dict[str, str]  # {upstream_service: "service_started" | "service_healthy" | "service_completed_successfully"}


# Subgoal 2: Compute exact startup timestamp for each service and check for premature connection races
def simulate_compose_dag(services: dict[str, ComposeService]) -> tuple[dict[str, int], list[str]]:
    start_times: dict[str, int] = {}
    ready_times: dict[str, int] = {}
    errors: list[str] = []

    for name, svc in services.items():
        wait_until_ms = 0
        for dep_name, condition in svc.depends_on.items():
            dep = services[dep_name]
            if condition == "service_started":
                wait_until_ms = max(wait_until_ms, start_times[dep_name] + dep.pid_spawn_ms)
            elif condition in ("service_healthy", "service_completed_successfully"):
                wait_until_ms = max(wait_until_ms, ready_times[dep_name])
            else:
                raise ValueError(f"Unknown condition: {condition}")

        start_times[name] = wait_until_ms
        ready_times[name] = wait_until_ms + svc.ready_or_complete_ms

        # Check if any upstream dependency is not actually ready when this service starts!
        for dep_name in svc.depends_on:
            if start_times[name] < ready_times[dep_name]:
                errors.append(
                    f"{name} started at {start_times[name]}ms before {dep_name} was ready at {ready_times[dep_name]}ms!"
                )
    return start_times, errors


# Subgoal 3: Contrast Naive service_started (Connection Refused!) vs Staff service_healthy DAG
naive_stack = {
    "postgres": ComposeService("postgres", pid_spawn_ms=50, ready_or_complete_ms=2000, depends_on={}),
    "aerocart-api": ComposeService("aerocart-api", pid_spawn_ms=40, ready_or_complete_ms=800, depends_on={"postgres": "service_started"}),
}
_, naive_errs = simulate_compose_dag(naive_stack)
assert len(naive_errs) == 1 and "50ms before postgres was ready at 2000ms" in naive_errs[0]

staff_stack = {
    "postgres": ComposeService("postgres", pid_spawn_ms=50, ready_or_complete_ms=2000, depends_on={}),
    "migrations": ComposeService("migrations", pid_spawn_ms=30, ready_or_complete_ms=500, depends_on={"postgres": "service_healthy"}),
    "aerocart-api": ComposeService(
        "aerocart-api",
        pid_spawn_ms=40,
        ready_or_complete_ms=800,
        depends_on={"postgres": "service_healthy", "migrations": "service_completed_successfully"},
    ),
    "e2e-tests": ComposeService("e2e-tests", pid_spawn_ms=30, ready_or_complete_ms=4000, depends_on={"aerocart-api": "service_healthy"}),
}
starts, staff_errs = simulate_compose_dag(staff_stack)
assert not staff_errs
assert starts == {"postgres": 0, "migrations": 2000, "aerocart-api": 2500, "e2e-tests": 3300}
print(f"AeroPipe v0.3 DAG verified: zero race errors, timeline (ms) = {starts}")
```

### Java 17 Equivalent

```java
import java.util.*;

public class AeroPipeCh03Starter {
    // Subgoal 1: Represent Compose service timing and dependency condition
    public record ServiceSpec(String name, int pidSpawnMs, int readyMs, Map<String, String> dependsOn) {}

    // Subgoal 2: Calculate deterministic startup schedule across the Compose DAG
    public static Map<String, Integer> scheduleDag(List<ServiceSpec> orderedSpecs) {
        Map<String, Integer> startMs = new LinkedHashMap<>();
        Map<String, Integer> readyMs = new HashMap<>();
        Map<String, ServiceSpec> byName = new HashMap<>();

        for (ServiceSpec spec : orderedSpecs) {
            byName.put(spec.name(), spec);
            int waitUntil = 0;
            for (var entry : spec.dependsOn().entrySet()) {
                String dep = entry.getKey();
                String cond = entry.getValue();
                if ("service_started".equals(cond)) {
                    waitUntil = Math.max(waitUntil, startMs.get(dep) + byName.get(dep).pidSpawnMs());
                } else {
                    waitUntil = Math.max(waitUntil, readyMs.get(dep));
                }
            }
            startMs.put(spec.name(), waitUntil);
            readyMs.put(spec.name(), waitUntil + spec.readyMs());
        }
        return startMs;
    }

    public static void main(String[] args) {
        List<ServiceSpec> stack = List.of(
                new ServiceSpec("postgres", 50, 2000, Map.of()),
                new ServiceSpec("migrations", 30, 500, Map.of("postgres", "service_healthy")),
                new ServiceSpec("aerocart-api", 40, 800, Map.of("migrations", "service_completed_successfully")),
                new ServiceSpec("e2e-tests", 30, 4000, Map.of("aerocart-api", "service_healthy"))
        );
        Map<String, Integer> timeline = scheduleDag(stack);
        assert timeline.get("migrations") == 2000;
        assert timeline.get("aerocart-api") == 2500;
        assert timeline.get("e2e-tests") == 3300;
    }
}
```

---

## 🛠️ Step 3: Everyday Practitioner Workflows & Where Naive Code Breaks

When authoring `compose.yaml` files for local dev and CI pipelines, pay close attention to four production details:
1. **`start_period` vs. `interval` in `healthcheck`**: During `start_period: 10s`, failed health probe checks **do not count** toward `retries`. This lets slow-starting services (like JVM apps or database WAL recovery) warm up without prematurely tripping a failure.
2. **Host Port Publishing (`ports: ["5432:5432"]`) Breaks Parallel CI**: If two CI jobs run on the same Jenkins/GitHub self-hosted runner and both bind host port `5432:5432`, the second job fails instantly with `Bind for 0.0.0.0:5432 failed: port is already allocated`! Inside a Compose network, containers talk over the internal bridge network (`postgres:5432`) **without publishing any `ports:` to the host**.
3. **Project Namespace Isolation (`-p aeropipe-${GITHUB_RUN_ID}`)**: By default, Docker Compose names networks and volumes after the folder name. Always pass `-p <unique_id>` (or `COMPOSE_PROJECT_NAME`) so concurrent CI runs never collide.

```json contrast
{
  "title": "Flaky `docker-compose.yml` vs. Deterministic `AeroPipe v0.3` DAG",
  "leftLabel": "❌ Naive Compose (Host Port Collisions + Race Condition)",
  "leftCode": "services:\n  postgres:\n    image: postgres:17\n    ports:\n      - \"5432:5432\" # Fails when 2 CI jobs run on same host!\n    environment:\n      POSTGRES_PASSWORD: pass\n  aerocart-api:\n    build: .\n    depends_on:\n      - postgres # Only waits for PID start (50ms)!\n    environment:\n      # Breaks: 127.0.0.1 is the API container itself!\n      DB_URL: postgresql://postgres:pass@127.0.0.1:5432/db",
  "rightLabel": "✅ Staff Compose (`service_healthy` + `tmpfs` + Bridge DNS)",
  "rightCode": "services:\n  postgres:\n    image: postgres:17-alpine\n    tmpfs: [\"/var/lib/postgresql/data\"] # RAM disk, 0 I/O wait!\n    environment:\n      POSTGRES_USER: aero\n      POSTGRES_PASSWORD: pass\n      POSTGRES_DB: aerodb\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U aero -d aerodb\"]\n      interval: 2s\n      timeout: 2s\n      retries: 10\n      start_period: 5s\n  aerocart-api:\n    build: { context: ., target: runtime }\n    depends_on:\n      postgres: { condition: service_healthy }\n    environment:\n      DB_URL: postgresql://aero:pass@postgres:5432/aerodb"
}
```

```json poe
{
  "question": "Before running the simulator: in `compose.yaml`, `postgres` has `healthcheck: { test: [\"CMD-SHELL\", \"pg_isready -U aero\"] }` (notice `-d aerodb` is omitted!). Why can `aerocart-api` STILL fail with `FATAL: database \"aerodb\" does not exist` right after `postgres` becomes `healthy`?",
  "options": [
    "`pg_isready` returns exit code 0 even when PostgreSQL is completely stopped",
    "During first-time container initialization (`docker-entrypoint.sh`), PostgreSQL starts a temporary background server to create `POSTGRES_DB=aerodb`; without `-d aerodb -U aero`, `pg_isready` succeeds against the default `postgres` maintenance DB before `aerodb` has been created!",
    "Bridge DNS caches `127.0.0.1` for the first 5 seconds",
    "`CMD-SHELL` does not execute inside the container's `mnt` namespace"
  ],
  "answerIndex": 1,
  "explanation": "The official `postgres` image runs a temporary server on local socket during entrypoint setup before creating `POSTGRES_DB` and restarting on TCP. Always write `pg_isready -U <user> -d <dbname> -h localhost` so the probe only passes once the target database exists and TCP is accepting connections!"
}
```

---

## 🏢 Step 4: How Big Tech Runs It at Scale, Staff Math & Production Blueprint

### 🏢 In the Wild: Spotify & GitLab Ephemeral Compose Stacks in CI

At **Spotify** and **GitLab**, thousands of microservice integration pipelines spin up multi-container Compose stacks on shared CI fleets:
1. **`tmpfs` Backing for Ephemeral Databases (`/var/lib/postgresql/data`)**: Database `fsync()` calls on cloud EBS/PD network disks are the #1 bottleneck during schema migrations and test seeding. Mounting `/var/lib/postgresql/data` on `tmpfs` (alongside `command: postgres -c fsync=off -c full_page_writes=off`) accelerates 150 Flyway migrations from `18 seconds` to `0.6 seconds` and guarantees automatic RAM cleanup on container exit.
2. **Critical-Path DAG Optimization**: Instead of chaining 6 services in a single linear waterfall, independent infrastructure nodes (`postgres`, `redis`, `kafka`, `wiremock`) boot concurrently in Level 0 of the DAG.

### Staff Startup DAG Critical-Path Math

Given a Compose startup Directed Acyclic Graph $G = (V, E)$ where each service $v \in V$ requires readiness duration $d(v)$, total stack readiness time $T_{\text{stack}}$ equals the **longest path (critical path)** through the dependency graph, NOT the sum of all containers:

$$T_{\text{stack}} = \max_{P \in \text{Paths}(G)} \sum_{v \in P} d(v), \qquad \text{Wait}(u) = \max_{(w, u) \in E} \big(\text{Wait}(w) + d(w)\big)$$

Meanwhile, if a healthcheck polls at interval $I$ after a service becomes truly ready at time $t_{\text{ready}}$, the expected polling quantization delay added per DAG hop is $\mathbb{E}[\Delta t_{\text{poll}}] = \frac{I}{2}$. Setting `interval: 2s` instead of the Docker default `interval: 30s` saves up to **$14\text{s}$ per hop** ($42\text{s}$ across a 3-hop DAG)!

| Storage / Network Option | Disk Persistence After `down` | Host Collision Risk | Speed | When to Use / When NOT to Use |
| :--- | :--- | :--- | :--- | :--- |
| **`tmpfs` Mount (`tmpfs: [/var/lib/postgresql/data]`)** | **Zero (Vanishes in RAM)** | **Zero** | **Fastest (RAM speed)** | **Best for ephemeral CI test databases (< 2 GB)**. Never use for production data! |
| **Named Volume (`volumes: [pgdata:/var/lib/...]`)** | **Persists unless `down -v`** | Collides if `-p` project name is shared | Moderate (Host FS) | **Use for local developer state** across reboots. In CI, always clean with `down -v`. |
| **Host Bind Mount (`./data:/var/lib/...`)** | **Persists on host directory** | **High** (Permissions & UID mismatches) | Slow on macOS/Windows VirtioFS | **Use only for live source-code hot-reloading** in local dev. Avoid in CI! |
| **Internal Bridge Network (No `ports:`)** | Ephemeral per `-p` stack | **Zero host port conflicts** | Native Linux `veth` bridge | **Default for all container-to-container CI traffic** (`postgres:5432`). |

### Production Blueprint: `AeroPipe v0.3` Compose Topology & Critical-Path Validator

```python
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ComposeServiceNode:
    name: str
    image: str
    readiness_sec: float
    poll_interval_sec: float
    has_healthcheck: bool
    is_oneshot_job: bool
    published_host_ports: list[str]
    env_urls: list[str]
    depends_on: dict[str, str]


@dataclass(frozen=True)
class ComposeAuditResult:
    is_valid: bool
    critical_path_sec: float
    service_ready_timeline: dict[str, float]
    violations: list[str]


class AeroPipeComposeValidator:
    """Validates Docker Compose startup DAGs, Bridge DNS URLs, host port safety, and critical-path latency."""

    @classmethod
    def validate_stack(cls, nodes: dict[str, ComposeServiceNode]) -> ComposeAuditResult:
        violations: list[str] = []
        ready_at: dict[str, float] = {}

        # Subgoal 1: Check for host port collisions, 127.0.0.1 loopback bugs, and unsafe depends_on
        for name, node in nodes.items():
            if node.published_host_ports:
                violations.append(
                    f"Service '{name}' publishes fixed host ports {node.published_host_ports}; omit 'ports:' in CI to prevent collisions"
                )
            for url in node.env_urls:
                if "127.0.0.1" in url or "localhost" in url:
                    violations.append(
                        f"Service '{name}' uses loopback '{url}'; use Bridge DNS service name (e.g., postgres:5432)"
                    )
            for dep_name, cond in node.depends_on.items():
                dep = nodes[dep_name]
                if cond == "service_started":
                    violations.append(
                        f"Service '{name}' uses unsafe 'service_started' on '{dep_name}'; use 'service_healthy' or 'service_completed_successfully'"
                    )
                if cond == "service_healthy" and not dep.has_healthcheck:
                    violations.append(
                        f"Service '{name}' waits for '{dep_name}' (service_healthy), but '{dep_name}' defines no healthcheck!"
                    )
                if cond == "service_completed_successfully" and not dep.is_oneshot_job:
                    violations.append(
                        f"Service '{name}' waits for completion of long-running daemon '{dep_name}'"
                    )

        # Subgoal 2: Compute topological critical-path readiness timeline including poll interval overhead
        def compute_ready(svc_name: str, visiting: set[str]) -> float:
            if svc_name in ready_at:
                return ready_at[svc_name]
            if svc_name in visiting:
                raise ValueError(f"Cycle detected in Compose depends_on involving {svc_name}")
            visiting.add(svc_name)
            node = nodes[svc_name]
            wait_sec = 0.0
            for dep_name in node.depends_on:
                wait_sec = max(wait_sec, compute_ready(dep_name, visiting))
            visiting.remove(svc_name)
            # Average healthcheck quantization delay = poll_interval / 2
            poll_overhead = (node.poll_interval_sec / 2.0) if node.has_healthcheck else 0.0
            ready_at[svc_name] = round(wait_sec + node.readiness_sec + poll_overhead, 2)
            return ready_at[svc_name]

        for svc_name in nodes:
            compute_ready(svc_name, set())

        crit_sec = max(ready_at.values()) if ready_at else 0.0
        return ComposeAuditResult(
            is_valid=len(violations) == 0,
            critical_path_sec=crit_sec,
            service_ready_timeline=ready_at,
            violations=violations,
        )


if __name__ == "__main__":
    aeropipe_v03 = {
        "postgres": ComposeServiceNode(
            name="postgres",
            image="postgres:17-alpine",
            readiness_sec=2.0,
            poll_interval_sec=2.0,
            has_healthcheck=True,
            is_oneshot_job=False,
            published_host_ports=[],
            env_urls=[],
            depends_on={},
        ),
        "redis": ComposeServiceNode(
            name="redis",
            image="redis:7-alpine",
            readiness_sec=0.5,
            poll_interval_sec=2.0,
            has_healthcheck=True,
            is_oneshot_job=False,
            published_host_ports=[],
            env_urls=[],
            depends_on={},
        ),
        "migrations": ComposeServiceNode(
            name="migrations",
            image="aerocart-migrate:v0.3",
            readiness_sec=1.0,
            poll_interval_sec=0.0,
            has_healthcheck=False,
            is_oneshot_job=True,
            published_host_ports=[],
            env_urls=["postgresql://aero:pass@postgres:5432/aerodb"],
            depends_on={"postgres": "service_healthy"},
        ),
        "aerocart-api": ComposeServiceNode(
            name="aerocart-api",
            image="aerocart-api:v0.3",
            readiness_sec=1.5,
            poll_interval_sec=2.0,
            has_healthcheck=True,
            is_oneshot_job=False,
            published_host_ports=[],
            env_urls=["postgresql://aero:pass@postgres:5432/aerodb", "redis://redis:6379/0"],
            depends_on={
                "postgres": "service_healthy",
                "redis": "service_healthy",
                "migrations": "service_completed_successfully",
            },
        ),
    }
    res = AeroPipeComposeValidator.validate_stack(aeropipe_v03)
    assert res.is_valid, f"Unexpected violations: {res.violations}"
    # postgres (2.0 + 1.0 poll = 3.0s) -> migrations (3.0 + 1.0 = 4.0s) -> aerocart-api (4.0 + 1.5 + 1.0 = 6.5s)
    assert res.critical_path_sec == 6.5
```

### Java 17 Equivalent

```java
import java.util.*;

public final class AeroPipeCh03Blueprint {
    public record ComposeNode(
            String name,
            double readinessSec,
            double pollIntervalSec,
            boolean hasHealthcheck,
            List<String> envUrls,
            Map<String, String> dependsOn) {}

    public static List<String> auditComposeStack(Map<String, ComposeNode> nodes) {
        List<String> violations = new ArrayList<>();
        for (ComposeNode node : nodes.values()) {
            for (String url : node.envUrls()) {
                if (url.contains("127.0.0.1") || url.contains("localhost")) {
                    violations.add(node.name() + " uses loopback URL instead of Bridge DNS: " + url);
                }
            }
            for (var dep : node.dependsOn().entrySet()) {
                if ("service_started".equals(dep.getValue())) {
                    violations.add(node.name() + " uses unsafe service_started on " + dep.getKey());
                }
                ComposeNode target = nodes.get(dep.getKey());
                if ("service_healthy".equals(dep.getValue()) && (target == null || !target.hasHealthcheck())) {
                    violations.add(node.name() + " requires healthcheck on " + dep.getKey());
                }
            }
        }
        return violations;
    }

    public static void main(String[] args) {
        Map<String, ComposeNode> validStack = Map.of(
                "postgres", new ComposeNode("postgres", 2.0, 2.0, true, List.of(), Map.of()),
                "api", new ComposeNode("api", 1.5, 2.0, true,
                        List.of("postgresql://aero:pass@postgres:5432/aerodb"),
                        Map.of("postgres", "service_healthy"))
        );
        assert auditComposeStack(validStack).isEmpty();
    }
}
```

> [!WARNING]
> **Hiring Bar-Raiser Gotcha — The Anonymous `node_modules` Volume Shadowing Bug!**
> A popular local-dev pattern mounts the repository into the container (`volumes: [".:/app", "/app/node_modules"]`) using an **anonymous volume** (`/app/node_modules`) so the host directory doesn't overwrite the container's `node_modules`. Here is the trap: when `package.json` changes and you run `docker compose build && docker compose up`, Docker **reuses the old anonymous volume** from the previous container, shadowing the newly built `node_modules` inside your fresh image! You MUST run `docker compose up --build --renew-anon-volumes` (or `down -v`) whenever dependencies change.

*Up Next in Chapter 04*: `Docker Compose` is great for full-stack system runs, but what when 8 developers and 16 parallel `pytest`/`JUnit 5` workers want to spin up isolated Postgres, Redis, and Kafka instances directly from test fixtures without writing YAML or colliding on ports? Enter `AeroPipe v0.4` with **Testcontainers & the Moby Ryuk Reaper**!

```json quiz
[
  {
    "id": "infra03-q1",
    "question": "Why does configuring `depends_on: [postgres]` (without a `condition:`) in `docker-compose.yml` still allow the `aerocart-api` container to fail with `Connection refused` on port 5432?",
    "options": [
      "`depends_on` is ignored by Docker Compose v2",
      "Default `depends_on` (`condition: service_started`) only waits until the `postgres` container's OS process is created (~50ms), NOT until PostgreSQL finishes WAL initialization and binds TCP port 5432 (~2s)",
      "`depends_on` only works on Swarm overlay networks",
      "PostgreSQL changes its port from 5432 to 5433 inside containers"
    ],
    "answerIndex": 1,
    "explanation": "Process creation (`service_started`) happens milliseconds after container creation, long before the database engine is ready to accept TCP connections. Use a `healthcheck` with `condition: service_healthy`."
  },
  {
    "id": "infra03-q2",
    "question": "Inside a multi-container Docker Compose network, `aerocart-api` tries to connect to `postgresql://user:pass@127.0.0.1:5432/aerodb` and immediately gets `Connection refused`. Why?",
    "options": [
      "PostgreSQL blocks connections from `127.0.0.1` by default",
      "Each container has its own isolated Linux `net` namespace; `127.0.0.1` inside `aerocart-api` loops back to the `aerocart-api` container itself rather than routing across the bridge network to the `postgres` service",
      "Docker Compose disables IPv4 loopback",
      "Port 5432 must be mapped to 8080 first"
    ],
    "answerIndex": 1,
    "explanation": "Loopback (`127.0.0.1`) is local to each container's network namespace. Containers on a user-defined Compose network reach each other via Docker's embedded Bridge DNS using the service name (`postgres:5432`)."
  },
  {
    "id": "infra03-q3",
    "question": "Which `depends_on` condition should an API service use when waiting for a one-shot Flyway/Alembic database migration container that runs `alembic upgrade head` and exits?",
    "options": [
      "`condition: service_healthy`",
      "`condition: service_started`",
      "`condition: service_completed_successfully`",
      "`condition: always_restart`"
    ],
    "answerIndex": 2,
    "explanation": "A one-shot migration container is not a long-running daemon with a healthcheck; it runs to completion and exits `0`. `condition: service_completed_successfully` blocks downstream services until the migration container exits with status code `0`."
  }
]
```

---

## 📋 Step 5: Master Cheat-Sheet, 60-Second Interview Pitch & Verified Sources

| Compose Orchestration Task | Broken / Naive Pattern | Production Standard (`AeroPipe v0.3`) | Operational Guarantee |
| :--- | :--- | :--- | :--- |
| **Service-to-Service URL** | `http://127.0.0.1:5432` or `localhost` | `postgresql://aero:pass@postgres:5432/aerodb` | Resolves via Docker Bridge DNS (`127.0.0.11`) across `net` namespaces |
| **Waiting for DB Readiness** | `depends_on: [postgres]` | `depends_on: { postgres: { condition: service_healthy } }` + `pg_isready -U aero -d aerodb` | Eliminates startup `Connection refused` race conditions |
| **Waiting for Migrations** | `sleep 10` in API entrypoint script | `depends_on: { migrate: { condition: service_completed_successfully } }` | Guarantees schema is migrated before API boots |
| **Fast Ephemeral Test DB** | Default disk volume + `fsync=on` | `tmpfs: ["/var/lib/postgresql/data"]` | Zero disk I/O latency & automatic RAM cleanup |
| **CI Stack Teardown** | `docker compose down` | `docker compose -p ci-${BUILD_ID} down -v --remove-orphans` | Destroys named volumes (`-v`) & prevents cross-build state leaks |

### 🎙️ 60-Second Interview Soundbite

> *"When I orchestrate multi-container integration stacks with Docker Compose, I design the `compose.yaml` as an explicit readiness DAG rather than relying on plain `depends_on`. Because default `depends_on` only waits for container PID creation (`service_started`), I attach fast `2s`-interval `healthcheck` probes—like `pg_isready -U aero -d aerodb` for Postgres and `/healthz` for APIs—and gate downstream services with `condition: service_healthy`, while gating schema migrations with `condition: service_completed_successfully`. I never hardcode `127.0.0.1` between containers since each has its own Linux `net` namespace; everything routes via Docker Bridge DNS service names without publishing static host ports that would collide on shared CI runners. Finally, I back ephemeral test databases with `tmpfs` and tear down stacks using `docker compose -p <run_id> down -v --remove-orphans` so zero state leaks between builds."*

### 📚 Verified Primary Sources
- [Docker Compose Official Guide — Control Startup and Shutdown Order (`service_healthy`, `service_completed_successfully`)](https://docs.docker.com/compose/how-tos/startup-order/)
- [Docker Compose Official Guide — Networking in Compose & Embedded Bridge DNS Discovery](https://docs.docker.com/compose/how-tos/networking/)
- [Docker Compose File Reference — Services (`healthcheck`, `depends_on`, `tmpfs`, `volumes`)](https://docs.docker.com/reference/compose-file/services/)
