# 💻 Core Computer Science Mastery (`core-cs/`)

Welcome to the **Core CS Pillar** of the Antigravity Learning Hub.
Every Staff/Lead SDET and Systems Engineer must understand what happens *beneath* high-level test scripts—inside the OS kernel, virtual memory manager, TCP/IP network stack, and database storage engine.

---

## 📊 Core CS Curriculum & Lab Tracker

| # | Domain | Lab / Module | Key Concepts Covered | Java | Python | Visualizer ID | Status |
| :-: | :--- | :--- | :--- | :-: | :-: | :--- | :---: |
| **1** | **Operating Systems** | [`01-memory-and-handle-leak-detector`](operating-systems/01-memory-and-handle-leak-detector/) | Virtual Memory vs. RSS, Post-GC Floor Slope ($\Delta\text{RSS}/\Delta t$), File Descriptor (`lsof`) Leaks, macOS `EndpointSecurity` vs. Windows Minifilters | [x] | [x] | `cs-os-leak-detector` | `Completed` |
| **2** | **Computer Networks** | [`01-tcp-tls-and-proxy-inspector`](computer-networks/01-tcp-tls-and-proxy-inspector/) | TCP 3-Way Handshake, Linux `listen()` SYN Backlog (`128`), TLS 1.2 (2-RTT) vs. TLS 1.3 (1-RTT), HTTP/2 Multiplexing, SASE mTLS Proxy Inspection | [x] | [x] | `cs-tcp-tls-handshake` | `Completed` |
| **3** | **Database Internals** | [`01-wal-and-isolation-anomalies`](databases/01-wal-and-isolation-anomalies/) | B-Tree vs. LSM Tree, Write-Ahead Logging (SQLite/Postgres WAL), FIFO Bounded Ring-Buffer, ACID Isolation & Optimistic Concurrency Control (CAS) | [x] | [x] | `arch-endpoint-cloud-sync` | `Completed` |

---

## 🚀 How to Run Core CS Labs

Every Core CS lab adheres to the **Dual-Language Self-Contained Runner** standard and can be executed via `./run.sh test` or directly from the Web UI (`http://127.0.0.1:8090`):

```bash
# Test Operating Systems Leak Detector (Java 17 & Python 3)
./run.sh test 01-memory-and-handle-leak-detector

# Test Computer Networks TCP/TLS & Proxy Inspector (Java 17 & Python 3)
./run.sh test 01-tcp-tls-and-proxy-inspector

# Test Database WAL & Optimistic Concurrency Engine (Java 17 & Python 3)
./run.sh test 01-wal-and-isolation-anomalies
```

