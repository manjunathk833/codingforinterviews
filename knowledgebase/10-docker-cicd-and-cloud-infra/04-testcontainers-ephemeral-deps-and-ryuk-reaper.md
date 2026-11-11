---
slug: "infra-04-testcontainers-ephemeral-deps-and-ryuk-reaper"
course_id: "10-docker-cicd-and-cloud-infra"
track: "system-design"
volume: "10. Docker, Kubernetes, CI/CD & Quality Infrastructure"
module_number: 1
module_title: "Module 1: Container Internals, Multi-Stage BuildKit, Compose DAGs & Hermetic Testcontainers"
chapter_number: 4
level_tag: "Absolute Zero → Senior/Staff"
title: "Testcontainers: Programmatic Ephemeral Dependencies, Dynamic Ports & the Moby Ryuk Reaper"
summary: "Upgrade to AeroPipe v0.4: manage PostgreSQL, Redis, and Kafka containers directly from Python pytest fixtures and Java JUnit 5 @Testcontainers, prevent CI port collisions with dynamic random host-port mapping, and guarantee zombie-free cleanup after SIGKILL via the Moby Ryuk reaper sidecar."
reading_time_minutes: 15
visualizer_id: "infra-docker-layer-testcontainers"
lab_path: "frameworks/cicd-infra/01-container-and-sharding-orchestrator"
tags: ["testcontainers", "ryuk", "pytest", "junit5", "hermetic-testing", "ephemeral-containers"]
prerequisites: ["infra-03-docker-compose-networks-volumes-and-healthcheck-dags"]
primary_sources: ["https://testcontainers.com/guides/introducing-testcontainers/", "https://testcontainers.com/guides/testing-spring-boot-rest-api-using-testcontainers/", "https://java.testcontainers.org/features/networking/"]
---

# Testcontainers: Programmatic Ephemeral Dependencies, Dynamic Ports & the Moby Ryuk Reaper

```json continuity
{
  "previously": "In Chapter 03, we orchestrated multi-service stacks in `AeroPipe v0.3` using Docker Compose healthcheck DAGs and Bridge DNS.",
  "painPoint": "While Docker Compose works for full-stack E2E tests, running `pytest` or `mvn test` in an IDE required developers to manually boot external Compose files first. Worse, when a developer hit `Ctrl+C` or Jenkins sent `SIGKILL (-9)` to a timed-out test job, Python `finally:` and Java `Runtime.addShutdownHook()` never ran—leaving 40 zombie Postgres containers eating 100% of our CI runner RAM!",
  "unlock": "Evolve to AeroPipe v0.4: embed programmatic `Testcontainers` directly inside `pytest` (`scope='session'`) and JUnit 5 (`@ServiceConnection`), map ephemeral random host ports (`get_exposed_port(5432)` / `getMappedPort(5432)`), and rely on the out-of-process **Moby Ryuk Reaper** container to garbage-collect orphaned containers even after a hard `SIGKILL`."
}
```

```json walkthrough
[
  {
    "time": "0:00",
    "badge": "Why Mocks Lie",
    "title": "In-Memory H2/SQLite Mocks vs. Real Ephemeral Containers",
    "caption": "Mocks and in-memory SQLite/H2 databases pass tests that later crash in production on Postgres JSONB operators, Redis Lua scripts, or Kafka partitioning. Testcontainers boots the real Docker image directly from your test code.",
    "nodes": ["pytest / JUnit 5", "Testcontainers SDK", "Docker Socket (/var/run/docker.sock)", "Real Postgres 17 + Redis 7"],
    "activeIndex": 1,
    "code": "with PostgresContainer(\"postgres:17-alpine\") as pg:\n    engine = create_engine(pg.get_connection_url())\n    # Runs against genuine PostgreSQL 17!"
  },
  {
    "time": "0:25",
    "badge": "Dynamic Port Mapping",
    "title": "Why Testcontainers Never Binds Fixed Host Port `5432:5432`",
    "caption": "Binding fixed host port 5432 causes `Address already in use` when 8 parallel test workers run on the same machine. Testcontainers asks the Linux kernel for a random free ephemeral host port (e.g., `32789 -> 5432`) and queries it dynamically.",
    "nodes": ["Container Port 5432", "Docker Ephemeral NAT", "Host Port 49182 (Worker 1)", "Host Port 49183 (Worker 2)"],
    "activeIndex": 2,
    "code": "# Python: host_port = pg.get_exposed_port(5432)\n# Java:   int hostPort = pg.getMappedPort(5432);\n# Zero port collisions across 16 parallel CI workers!"
  },
  {
    "time": "0:50",
    "badge": "The Ryuk Reaper",
    "title": "How Moby Ryuk Cleans Up Containers After `SIGKILL (-9)`",
    "caption": "If a test runner process is killed with `SIGKILL (-9)`, in-process teardown hooks (`atexit`, `finally`, JVM shutdown hooks) CANNOT execute! Testcontainers spawns a tiny sidecar container (`testcontainers/ryuk`) linked via a TCP heartbeat socket; when the test process dies, the TCP socket closes and Ryuk reaps all labeled containers after a 10s grace period.",
    "nodes": ["Test Process (SIGKILL -9!)", "TCP Heartbeat Closes", "Moby Ryuk Sidecar", "Prunes org.testcontainers.sessionId"],
    "activeIndex": 2,
    "code": "# Ryuk filter registered over TCP on startup:\nlabel=org.testcontainers=true&label=org.testcontainers.sessionId=8f92a1..."
  },
  {
    "time": "1:15",
    "badge": "Singleton Lifecycle",
    "title": "300 Containers (`scope='function'`) vs. 1 Container + TRUNCATE (`scope='session'`)",
    "caption": "Starting a new Postgres container before every single test function (`@BeforeEach`) adds 2s * 300 tests = 10 minutes of overhead! Boot the container once per test worker (`scope='session'` / static singleton) and isolate tests via rolled-back transactions or fast `TRUNCATE`.",
    "nodes": ["1 Container per Worker (2.0s)", "Run 300 Tests (5ms Reset)", "Total Suite: 4.5s!", "Ryuk Reaps on Exit"],
    "activeIndex": 1,
    "code": "@pytest.fixture(scope=\"session\")\ndef postgres_container():\n    with PostgresContainer(\"postgres:17-alpine\") as pg:\n        yield pg"
  }
]
```

```json pretraining
[
  {
    "term": "Programmatic Testcontainers Lifecycle",
    "formula": "Test Code -> Docker Engine API -> Readiness WaitStrategy -> Dynamic DSN -> Auto-Teardown",
    "meaning": "A library for Python (`testcontainers-python`) and Java (`org.testcontainers`) that boots, health-checks, and destroys real Docker containers directly inside `pytest` fixtures or JUnit 5 lifecycles."
  },
  {
    "term": "Dynamic Ephemeral Host-Port Mapping",
    "formula": "Container Fixed Port (5432) <-> Random Host Ephemeral Port (32768–60999)",
    "meaning": "Docker assigns an unused high port on the host automatically (`-P`), and test code retrieves it at runtime via `get_exposed_port(5432)` (Python) or `getMappedPort(5432)` (Java) so parallel workers never collide."
  },
  {
    "term": "Moby Ryuk Resource Reaper (`testcontainers/ryuk`)",
    "formula": "TCP Socket EOF (Test Runner Died) -> Wait 10s -> docker rm -f <session_labels>",
    "meaning": "An out-of-process watchdog container started by Testcontainers that monitors a TCP connection to the test runner; if the runner crashes or receives `SIGKILL (-9)`, the kernel closes the socket and Ryuk deletes all containers matching that session's Docker labels."
  },
  {
    "term": "`WaitStrategy` (`Wait.forListeningPort()` / `Wait.forLogMessage()`)",
    "formula": "Container Started -> Readiness Probe Loop -> Yield to Test",
    "meaning": "Built-in Testcontainers readiness checks (log regex, TCP port handshake, HTTP status `200`, or `DockerHealthcheckWaitStrategy`) that block fixture return until the service inside the container is ready."
  }
]
```

## 🌱 Step 1: Plain-English Mental Model — Self-Cleaning Pop-Up Kitchens & The Dead-Man's Switch

With `Docker Compose` in Chapter 03, someone still had to run `docker compose up` outside the test runner before running tests in PyCharm, VS Code, or IntelliJ. Worse, if two test suites tried to use port `5432` on the same machine, they crashed into each other; and if a CI build timed out and was killed with `kill -9`, half-dead containers littered the server like abandoned rental cars.

**Testcontainers** turns infrastructure into **ordinary test variables** with three superpowers:
1. **Self-Service Pop-Up Appliances**: When you hit the green "Run Test" arrow in your IDE, your Python `pytest` fixture or Java JUnit 5 class talks directly to the Docker daemon and spins up a fresh `postgres:17-alpine` container automatically.
2. **Dynamic Room Numbers (Random Host Ports)**: Instead of fighting over Room `#5432`, every container gets a random unused room number from the OS (like `#49182` or `#51044`) and hands the exact room key to your test client via `get_exposed_port(5432)` / `getMappedPort(5432)`.
3. **The Dead-Man's Switch (`Moby Ryuk` Reaper)**: Why can't a normal `try / finally` block clean up containers? Because when the OS sends **`SIGKILL (-9)`** to a hung test process, the process is vaporized instantly—**zero lines of `finally` or JVM shutdown hook code are allowed to run**! Testcontainers solves this by starting a tiny watchdog container called **`Ryuk`**. Your test runner holds an open TCP phone line to `Ryuk`. The millisecond your test process dies (even from `kill -9`), the Linux kernel hangs up the TCP phone line, and `Ryuk` automatically sweeps away every container tagged with your test session ID:

```mermaid
flowchart LR
    Test["pytest / JUnit 5 Runner"] -->|"1. Hold TCP Heartbeat"| Ryuk["Moby Ryuk Reaper Container"]
    Test -->|"2. Spawn + Label sessionId"| PG["Postgres 17 (Port 49182->5432)"]
    Kill["SIGKILL (-9) / CI Abort"] -.->|"3. TCP EOF Detected!"| Ryuk
    Ryuk -->|"4. docker rm -f by Label"| PG
```

---

## 🔨 Step 2: Zero-to-Running Starter & CLI — Wiring `AeroPipe v0.4`

In a terminal with Docker running, installing and running Testcontainers takes two commands:

```bash
# 1. Install Testcontainers for Python (or declare org.testcontainers:postgresql in Maven/Gradle)
pip install "testcontainers[postgres,redis]>=4.8.0" pytest

# 2. Run pytest — watch Ryuk and Postgres 17 spin up on random ports and vanish on exit!
pytest tests/integration/ -v
```

Let's build a runnable Python 3 and Java 17 **Testcontainers Ephemeral Port Allocator & Ryuk Dead-Man's-Switch Simulator** using standard library sockets so you can see the exact TCP heartbeat and label-reaping protocol in action:

```python
from __future__ import annotations
import socket
from dataclasses import dataclass, field


# Subgoal 1: Allocate a guaranteed-free ephemeral host port from the OS kernel (bind port 0)
def allocate_ephemeral_host_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


# Subgoal 2: Model a labeled Testcontainer with dynamic host-port mapping
@dataclass
class SimulatedTestContainer:
    image: str
    session_id: str
    exposed_container_port: int = 5432
    mapped_host_port: int = field(default_factory=allocate_ephemeral_host_port)
    running: bool = True

    @property
    def labels(self) -> dict[str, str]:
        return {
            "org.testcontainers": "true",
            "org.testcontainers.sessionId": self.session_id,
        }

    def get_exposed_port(self, container_port: int) -> int:
        if container_port != self.exposed_container_port:
            raise KeyError(f"Port {container_port} not exposed")
        return self.mapped_host_port

    def get_connection_url(self) -> str:
        return f"postgresql://aero:pass@127.0.0.1:{self.get_exposed_port(5432)}/aerodb"


# Subgoal 3: Model Moby Ryuk reaping all containers matching sessionId when TCP heartbeat closes
class MobyRyukReaper:
    def __init__(self) -> None:
        self.active_containers: list[SimulatedTestContainer] = []

    def register(self, container: SimulatedTestContainer) -> None:
        self.active_containers.append(container)

    def on_tcp_heartbeat_eof(self, dead_session_id: str) -> int:
        reaped = 0
        for c in self.active_containers:
            if c.running and c.labels.get("org.testcontainers.sessionId") == dead_session_id:
                c.running = False
                reaped += 1
        return reaped


ryuk = MobyRyukReaper()
pg_worker_1 = SimulatedTestContainer("postgres:17-alpine", session_id="sess-w1")
pg_worker_2 = SimulatedTestContainer("postgres:17-alpine", session_id="sess-w2")
ryuk.register(pg_worker_1)
ryuk.register(pg_worker_2)

# Verify dynamic random host ports prevent collisions across parallel workers
assert pg_worker_1.get_exposed_port(5432) >= 1024
assert pg_worker_1.get_connection_url().startswith("postgresql://aero:pass@127.0.0.1:")

# Simulate Worker 1 receiving SIGKILL (-9): Ryuk reaps Worker 1's containers while leaving Worker 2 untouched!
reaped_count = ryuk.on_tcp_heartbeat_eof("sess-w1")
assert reaped_count == 1
assert not pg_worker_1.running and pg_worker_2.running
print(f"AeroPipe v0.4 verified: dynamic URL={pg_worker_1.get_connection_url()}, Ryuk reaped {reaped_count} orphan.")
```

### Java 17 Equivalent

```java
import java.io.IOException;
import java.net.ServerSocket;
import java.util.*;

public class AeroPipeCh04Starter {
    // Subgoal 1: Allocate dynamic host port via OS ephemeral range (port 0)
    public static int allocateEphemeralPort() {
        try (ServerSocket socket = new ServerSocket(0)) {
            return socket.getLocalPort();
        } catch (IOException e) {
            throw new IllegalStateException("Failed to allocate ephemeral port", e);
        }
    }

    // Subgoal 2: Model Java Testcontainers getMappedPort(5432) and Ryuk session label cleanup
    public static final class EphemeralContainer {
        private final String sessionId;
        private final int mappedPort = allocateEphemeralPort();
        private boolean running = true;

        public EphemeralContainer(String sessionId) {
            this.sessionId = sessionId;
        }

        public int getMappedPort(int containerPort) {
            if (containerPort != 5432) throw new IllegalArgumentException("Unmapped port: " + containerPort);
            return mappedPort;
        }

        public String getJdbcUrl() {
            return "jdbc:postgresql://127.0.0.1:" + getMappedPort(5432) + "/aerodb";
        }
    }

    public static void main(String[] args) {
        EphemeralContainer c1 = new EphemeralContainer("session-junit-1");
        assert c1.getMappedPort(5432) > 1024;
        assert c1.getJdbcUrl().contains(String.valueOf(c1.getMappedPort(5432)));

        // Subgoal 3: Simulate Ryuk reaping containers by sessionId on TCP disconnect
        List<EphemeralContainer> fleet = List.of(c1, new EphemeralContainer("session-junit-2"));
        long reaped = fleet.stream()
                .filter(c -> "session-junit-1".equals(c.sessionId))
                .peek(c -> c.running = false)
                .count();
        assert reaped == 1 && !c1.running;
    }
}
```

---

## 🛠️ Step 3: Everyday Practitioner Workflows & Where Naive Code Breaks

In day-to-day Python (`pytest`) and Java (`JUnit 5` + `Spring Boot 3.1+`) repositories, **fixture scope** determines whether your integration suite runs in `6 seconds` or `12 minutes`:
- **Python `pytest` (`conftest.py`)**: Declare `@pytest.fixture(scope="session")` for `PostgresContainer("postgres:17-alpine")` so the container boots **once per `pytest-xdist` worker process**, apply migrations once, and wrap each test function in a rolled-back database transaction (or fast `TRUNCATE TABLE ... RESTART IDENTITY CASCADE`).
- **Java `JUnit 5` & `Spring Boot 3.1+`**: Avoid putting `@Container` on an instance field (which restarts the container before every single `@Test` method!). Declare `static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:17-alpine");` (or use the Singleton Container Pattern + `@ServiceConnection` in Spring Boot 3.1+, which automatically wires `spring.datasource.url`, `username`, and `password` without boilerplate `@DynamicPropertySource`).

```json contrast
{
  "title": "Per-Test Container Thrashing vs. Session/Singleton Lifecycle + Fast Reset",
  "leftLabel": "❌ Naive Scope (300 Tests x 2.2s Boot = 11 Minutes!)",
  "leftCode": "# Python: function scope boots a brand-new container per test!\n@pytest.fixture(scope=\"function\")\ndef db():\n    with PostgresContainer(\"postgres:17-alpine\") as pg:\n        yield pg\n\n// Java JUnit 5: non-static @Container restarts per @Test!\n@Testcontainers\nclass CheckoutIT {\n    @Container // Instance field = 300 container restarts!\n    PostgreSQLContainer<?> pg = new PostgreSQLContainer<>(\"postgres:17-alpine\");\n}",
  "rightLabel": "✅ Staff Scope (1 Container per Worker + 2ms Savepoint Reset)",
  "rightCode": "# Python: session scope boots ONCE per xdist worker!\n@pytest.fixture(scope=\"session\")\ndef pg_engine():\n    with PostgresContainer(\"postgres:17-alpine\") as pg:\n        engine = create_engine(pg.get_connection_url())\n        Base.metadata.create_all(engine)\n        yield engine\n\n// Java Spring Boot 3.1+: static @Container + @ServiceConnection\n@Testcontainers\nclass CheckoutIT {\n    @Container @ServiceConnection\n    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>(\"postgres:17-alpine\");\n}"
}
```

```json poe
{
  "question": "Before running the simulator: a developer sets `TESTCONTAINERS_RYUK_DISABLED=true` in CI to shave 400ms off startup. Halfway through the pipeline, a developer pushes a new commit to the same PR, and GitHub Actions cancels the running job (`SIGKILL`). What happens on the self-hosted CI runner?",
  "options": [
    "Python's `with PostgresContainer(...) as pg:` `__exit__` block still runs and stops the container",
    "Because `SIGKILL (-9)` cannot be caught by Python `__exit__` or JVM shutdown hooks and Ryuk was disabled, the PostgreSQL and Kafka containers remain running indefinitely as zombie orphans—leaking RAM and disk until the CI host crashes",
    "Docker Engine automatically stops any container after 60 seconds of inactivity",
    "The container ports revert to 5432"
  ],
  "answerIndex": 1,
  "explanation": "`SIGKILL` terminates the user-space test runner immediately in the kernel, preventing `__exit__`, `atexit`, or JVM shutdown hooks from executing. Without the out-of-process `Moby Ryuk` sidecar container watching the TCP socket, those containers become permanent orphans on the runner!"
}
```

---

## 🏢 Step 4: How Big Tech Runs It at Scale, Staff Math & Production Blueprint

### 🏢 In the Wild: Spotify & AtomicJar Hermetic Integration Harnesses

At **Spotify** (over 2,000 backend services) and **AtomicJar** (creators of Testcontainers), hermetic integration testing replaced shared staging databases:
1. **Container Reuse in Local Dev (`withReuse(true)`) vs. Ephemeral in CI**: Locally, developers enable `.withReuse(true)` (with `testcontainers.reuse.enable=true` in `~/.testcontainers.properties`) so Testcontainers hashes the container configuration and keeps the container warm between IDE runs—dropping local startup time to **`0.08 seconds`**. In CI, reuse is disabled and `Ryuk` stays strictly enabled for 100% hermetic teardown.
2. **WaitStrategy Precision**: Instead of sleeping or checking only TCP port opening (since Postgres restarts its socket once during `initdb`), Testcontainers' `PostgresContainer` waits for the log message `".*database system is ready to accept connections.*"` **twice** (or runs a JDBC/SQL query wait strategy) before handing the connection URL to the test.

### Staff Lifecycle Amortization & Port Collision Math

If a suite of $N$ integration tests runs across $W$ parallel workers, where booting a container costs $T_{\text{boot}}$ (`2.2s`), running one test costs $T_{\text{test}}$ (`0.03s`), and resetting state via transaction rollback or `TRUNCATE` costs $T_{\text{reset}}$ (`0.002s`), total wall-clock time per worker for Naive Per-Test booting vs. Staff Session-Scoped reuse is:

$$T_{\text{naive}}(N) = \frac{N}{W}\left(T_{\text{boot}} + T_{\text{test}}\right), \qquad T_{\text{session}}(N) = T_{\text{boot}} + \frac{N}{W}\left(T_{\text{reset}} + T_{\text{test}}\right)$$

For $N = 400$ tests across $W = 4$ workers ($100$ tests/worker):
- **Naive Per-Test Container**: $100 \times (2.2 + 0.03) = \mathbf{223.0\text{ seconds}}$ (`3m 43s`).
- **Staff Session Singleton + Rollback**: $2.2 + 100 \times (0.002 + 0.03) = \mathbf{5.4\text{ seconds}}$ (**a $41.3\times$ speedup**)!

| Test Dependency Strategy | Production Fidelity | Parallel Worker Safety | Teardown on `SIGKILL` | When to Use / When NOT to Use |
| :--- | :--- | :--- | :--- | :--- |
| **Session-Scoped `Testcontainers` + `Ryuk`** | **100% Real Engine** (Postgres 17, Redis 7, Kafka) | **100% Safe** (Random ephemeral host ports) | **Guaranteed via `Moby Ryuk` TCP EOF** | **Default for all DB, Cache, Queue & S3 (`MinIO`/`LocalStack`) integration tests**. |
| **Per-Function `Testcontainers`** | 100% Real Engine | Safe, but exhausts ephemeral ports & CPU | Guaranteed via `Ryuk` | **Use ONLY if a test intentionally corrupts cluster-level filesystem/WAL state**. |
| **In-Memory Mock DB (`H2` / `SQLite` for Postgres)** | **Low** (Misses dialects, `JSONB`, locking, extensions) | Safe | In-process memory | **Use only for ultra-fast unit tests** or when explicitly testing SQLite. Never as a blind substitute for Postgres features! |
| **Shared Remote Dev/QA Database** | High | **0% Safe** (Workers overwrite each other's rows!) | Requires manual cron cleanup | **NEVER use for automated CI tests!** |

### Production Blueprint: `AeroPipe v0.4` Session-Scoped Testcontainers & Ryuk Orchestrator

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ContainerInstance:
    container_id: str
    image: str
    internal_port: int
    host_port: int
    labels: dict[str, str]
    healthy: bool = True
    stopped: bool = False


@dataclass(frozen=True)
class SuiteExecutionMetrics:
    containers_spawned: int
    wall_clock_sec: float
    orphans_remaining_after_sigkill: int


class AeroPipeTestcontainersHarness:
    """Simulates session-scoped vs function-scoped Testcontainers with dynamic ports and Moby Ryuk reaping."""

    def __init__(self, session_id: str, ryuk_enabled: bool = True) -> None:
        self.session_id = session_id
        self.ryuk_enabled = ryuk_enabled
        self._next_ephemeral_port = 49152
        self.containers: list[ContainerInstance] = []

    def spawn_container(self, image: str, internal_port: int = 5432) -> ContainerInstance:
        host_port = self._next_ephemeral_port
        self._next_ephemeral_port += 1
        inst = ContainerInstance(
            container_id=f"tc-{len(self.containers) + 1}",
            image=image,
            internal_port=internal_port,
            host_port=host_port,
            labels={
                "org.testcontainers": "true",
                "org.testcontainers.sessionId": self.session_id,
            },
        )
        self.containers.append(inst)
        return inst

    def simulate_sigkill_and_ryuk_sweep(self) -> int:
        # Normal finally blocks cannot run on SIGKILL; only Ryuk can reap labeled containers!
        if self.ryuk_enabled:
            for c in self.containers:
                if c.labels.get("org.testcontainers.sessionId") == self.session_id:
                    c.stopped = True
        return sum(1 for c in self.containers if not c.stopped)

    @classmethod
    def benchmark_lifecycle(
        cls,
        num_tests: int,
        workers: int,
        scope: str,
        boot_sec: float = 2.2,
        test_sec: float = 0.03,
        reset_sec: float = 0.002,
        ryuk_enabled: bool = True,
    ) -> SuiteExecutionMetrics:
        tests_per_worker = num_tests // workers
        harness = cls(session_id="aeropipe-ci-sess", ryuk_enabled=ryuk_enabled)

        if scope == "function":
            for _ in range(num_tests):
                harness.spawn_container("postgres:17-alpine")
            wall_sec = tests_per_worker * (boot_sec + test_sec)
        elif scope == "session":
            for _ in range(workers):
                harness.spawn_container("postgres:17-alpine")
            wall_sec = boot_sec + tests_per_worker * (reset_sec + test_sec)
        else:
            raise ValueError(f"Unsupported scope: {scope}")

        orphans = harness.simulate_sigkill_and_ryuk_sweep()
        return SuiteExecutionMetrics(
            containers_spawned=len(harness.containers),
            wall_clock_sec=round(wall_sec, 2),
            orphans_remaining_after_sigkill=orphans,
        )


if __name__ == "__main__":
    naive = AeroPipeTestcontainersHarness.benchmark_lifecycle(
        num_tests=400, workers=4, scope="function", ryuk_enabled=False
    )
    staff = AeroPipeTestcontainersHarness.benchmark_lifecycle(
        num_tests=400, workers=4, scope="session", ryuk_enabled=True
    )
    assert naive.containers_spawned == 400 and naive.wall_clock_sec == 223.0
    assert naive.orphans_remaining_after_sigkill == 400
    assert staff.containers_spawned == 4 and staff.wall_clock_sec == 5.4
    assert staff.orphans_remaining_after_sigkill == 0
```

### Java 17 Equivalent

```java
import java.util.*;

public final class AeroPipeCh04Blueprint {
    public record BenchmarkResult(int containersSpawned, double wallClockSec, int leakedOrphansOnSigkill) {}

    public static BenchmarkResult evaluateLifecycle(
            int totalTests,
            int workers,
            boolean singletonScope,
            boolean ryukEnabled) {
        int testsPerWorker = totalTests / workers;
        double bootSec = 2.2;
        double testSec = 0.03;
        double resetSec = 0.002;

        int spawned = singletonScope ? workers : totalTests;
        double wallSec = singletonScope
                ? bootSec + testsPerWorker * (resetSec + testSec)
                : testsPerWorker * (bootSec + testSec);
        int orphans = ryukEnabled ? 0 : spawned;
        return new BenchmarkResult(spawned, Math.round(wallSec * 100.0) / 100.0, orphans);
    }

    public static void main(String[] args) {
        BenchmarkResult singleton = evaluateLifecycle(400, 4, true, true);
        BenchmarkResult perMethodNoRyuk = evaluateLifecycle(400, 4, false, false);
        assert singleton.containersSpawned() == 4;
        assert singleton.wallClockSec() == 5.4;
        assert singleton.leakedOrphansOnSigkill() == 0;
        assert perMethodNoRyuk.leakedOrphansOnSigkill() == 400;
    }
}
```

> [!WARNING]
> **Hiring Bar-Raiser Gotcha — Container-to-Container Networking vs. Host-to-Container Port Mapping!**
> When your `pytest` or `JUnit 5` test runs **on the host** and connects to a `PostgresContainer`, it MUST use `pg.get_connection_url()` (`localhost:<getMappedPort(5432)>`, e.g., `localhost:49182`). However, if you ALSO launch a second `Testcontainer` (such as a `KafkaConnect` or `Debezium` container) on the same `Network.newNetwork()` that needs to talk to that `PostgresContainer`, the second container MUST connect to `.withNetworkAliases("postgres")` on internal port **`postgres:5432`**—NOT `localhost:49182`! Host-mapped ports (`getMappedPort`) are for host-to-container traffic; network aliases + internal ports (`5432`) are for container-to-container traffic.

*Up Next in Chapter 05*: With Module 1 complete (`Containers -> Multi-Stage BuildKit -> Compose DAGs -> Hermetic Testcontainers`), we enter **Module 2: Kubernetes & Incident Triage**. We will deploy `AeroCart` onto a Kubernetes cluster (`AeroPipe v0.5`) and see why copying the same health endpoint into `startupProbe`, `readinessProbe`, and `livenessProbe` triggers a catastrophic production restart storm!

```json quiz
[
  {
    "id": "infra04-q1",
    "question": "Why does Testcontainers start a separate `testcontainers/ryuk` sidecar container instead of relying solely on Python `atexit` / `finally` or Java `Runtime.getRuntime().addShutdownHook()`?",
    "options": [
      "Because Python and Java cannot communicate with `/var/run/docker.sock` directly",
      "Because if the test runner process crashes or is terminated with `SIGKILL (-9)` by CI timeout/cancellation, in-process shutdown hooks and `finally` blocks never execute; the out-of-process Ryuk container detects the closed TCP heartbeat socket and reaps all containers matching the session's Docker labels",
      "Because Ryuk compresses container logs into JUnit XML",
      "Because Ryuk assigns static IP addresses to every container"
    ],
    "answerIndex": 1,
    "explanation": "A hard `SIGKILL` (`kill -9`) or JVM segfault immediately terminates the process in the OS kernel without running user-space cleanup hooks. When the process dies, the kernel closes its TCP socket to Ryuk, triggering Ryuk to delete all resources labeled with that `org.testcontainers.sessionId`."
  },
  {
    "id": "infra04-q2",
    "question": "How does Testcontainers prevent port collisions when 8 parallel `pytest-xdist` or JUnit 5 workers each start a `PostgresContainer` on the same CI host?",
    "options": [
      "It increments ports sequentially from 5432 to 5439 using a shared lockfile in `/tmp`",
      "It publishes container port 5432 to an OS-assigned random ephemeral host port (`0.0.0.0:0 -> 5432`) and exposes `get_exposed_port(5432)` / `getMappedPort(5432)` so each test worker discovers its unique port at runtime",
      "It shares a single PostgreSQL process across all 8 containers",
      "It blocks workers 2–8 until worker 1 finishes the entire test suite"
    ],
    "answerIndex": 1,
    "explanation": "Never bind fixed host ports in Testcontainers. Docker maps container port 5432 to a random free ephemeral host port (e.g., `49182`), which the test queries via `get_exposed_port(5432)` or `getMappedPort(5432)`."
  },
  {
    "id": "infra04-q3",
    "question": "In JUnit 5 with `@Testcontainers`, a test class has 50 `@Test` methods and declares `@Container PostgreSQLContainer<?> pg = new PostgreSQLContainer<>(\"postgres:17-alpine\");` WITHOUT the `static` keyword. What happens?",
    "options": [
      "JUnit 5 throws a compilation error",
      "Testcontainers boots and destroys a brand-new PostgreSQL container 50 times (once before every `@Test` method), adding ~100 seconds of container startup overhead",
      "The container is shared across all 50 methods automatically",
      "Ryuk deletes the container before the first `@Test` runs"
    ],
    "answerIndex": 1,
    "explanation": "In `@Testcontainers`, an instance field annotated with `@Container` is tied to the per-method lifecycle (`@BeforeEach` / `@AfterEach`), restarting the container for every test method. Making the field `static` (or using the Singleton Container pattern) ties it to the class/JVM lifecycle."
  }
]
```

---

## 📋 Step 5: Master Cheat-Sheet, 60-Second Interview Pitch & Verified Sources

| Capability | Python (`testcontainers-python` + `pytest`) | Java 17 (`org.testcontainers` + `JUnit 5` / `Spring Boot 3.1+`) | Staff Engineering Rule |
| :--- | :--- | :--- | :--- |
| **Start Ephemeral Postgres** | `with PostgresContainer("postgres:17-alpine") as pg:` | `new PostgreSQLContainer<>("postgres:17-alpine")` | Pin explicit image tag (`17-alpine`), never `:latest` |
| **Query Dynamic Host Port** | `pg.get_exposed_port(5432)` / `pg.get_connection_url()` | `pg.getMappedPort(5432)` / `pg.getJdbcUrl()` | Never hardcode `5432` on the host side |
| **Fast Worker-Scoped Reuse** | `@pytest.fixture(scope="session")` + per-test rollback | `static @Container @ServiceConnection` (or Singleton pattern) | Amortizes 2.2s container boot across hundreds of tests |
| **Container-to-Container DNS** | `with Network() as net:` + `.with_network_aliases("pg")` | `Network.newNetwork()` + `.withNetworkAliases("pg")` | Sibling containers connect via `pg:5432`, not `getMappedPort` |
| **Orphan Zombie Protection** | Automatic via `testcontainers/ryuk` sidecar | Automatic via `testcontainers/ryuk` sidecar | Never set `TESTCONTAINERS_RYUK_DISABLED=true` in CI! |

### 🎙️ 60-Second Interview Soundbite

> *"For database, Redis, and Kafka integration tests, I replace brittle mocks and shared staging databases with **Testcontainers**. Three mechanics make Testcontainers production-grade in CI: first, every container maps its internal port (like `5432`) to an OS-assigned random ephemeral host port queried via `get_exposed_port(5432)` or `getMappedPort(5432)`, so 16 parallel test workers on the same runner never collide. Second, instead of spinning up a new container per test function—which turns 300 tests into a 10-minute wait—I scope containers to the worker session (`@pytest.fixture(scope='session')` or `static @Container` with Spring Boot `@ServiceConnection`) and isolate individual tests in 2 milliseconds using transaction rollbacks or `TRUNCATE`. Finally, I rely on the **Moby Ryuk** reaper sidecar container, which holds a TCP heartbeat to the test runner and automatically garbage-collects all session-labeled containers even if a CI job is abruptly killed with `SIGKILL (-9)`."*

### 📚 Verified Primary Sources
- [Testcontainers Official Guide — Introducing Testcontainers & Ephemeral Dependency Lifecycle](https://testcontainers.com/guides/introducing-testcontainers/)
- [Testcontainers Official Guide — Testing Spring Boot REST APIs Using `@Testcontainers` & `@ServiceConnection`](https://testcontainers.com/guides/testing-spring-boot-rest-api-using-testcontainers/)
- [Testcontainers for Java Official Docs — Networking, `getMappedPort`, & Custom Bridge Networks](https://java.testcontainers.org/features/networking/)
