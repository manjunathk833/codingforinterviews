# 🌐 Networks Lab 01: TCP/TLS Handshakes, SYN Backlogs & SASE Proxy Inspection

**Domain:** Computer Networks & Security Protocols  
**Target Role:** Senior / Staff SDET (Cloud Networking, SASE/SWG Proxies, High-Throughput APIs)  
**Interactive Visualizer:** `cs-tcp-tls-handshake` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

Every API or UI request traverses multiple network protocol layers before a single byte of application JSON is processed:
1. **TCP 3-Way Handshake (`1 RTT`)**:
   - `Client ──SYN──► Server`
   - `Client ◄──SYN-ACK── Server`
   - `Client ──ACK──► Server`
   - **The Linux `listen()` SYN Backlog Trap**: When a server binds a socket, the OS maintains a **SYN Queue** and **Accept Queue** capped by `listen(backlog)` (in Python's `HTTPServer`, default `request_queue_size = 5`). If 32 worker threads fire `SYN` packets simultaneously against a backlog of `5`, the Linux kernel drops/resets connections `#6..#32` with `ConnectionResetError: [Errno 104] Connection reset by peer`!
2. **TLS 1.2 (`2 RTT`) vs. TLS 1.3 (`1 RTT` / `0-RTT`)**:
   - **TLS 1.2**: Requires 2 full roundtrips after TCP (`ClientHello` $\to$ `ServerHello/Cert` $\to$ `KeyExchange/CipherSpec` $\to$ `Finished`). Total cold connection latency = $1\text{ (TCP)} + 2\text{ (TLS 1.2)} + 1\text{ (HTTP)} = \mathbf{4 \times \text{RTT}}$.
   - **TLS 1.3**: Combines key share into the initial `ClientHello`, completing in **1 RTT** (Total cold latency = $\mathbf{3 \times \text{RTT}}$), or **0-RTT** on session resumption!
3. **HTTP/1.1 Keep-Alive vs. HTTP/2 Multiplexing**:
   - **HTTP/1.1 without pooling**: Pays the TCP + TLS handshake tax on *every* request.
   - **HTTP/2 over persistent mTLS**: Amortizes the handshake across thousands of multiplexed streams over a single TCP connection without head-of-line blocking at the application layer.
4. **SASE Forward Proxy TLS Inspection (MITM)**:
   - Enterprise agents (like Netskope) steer traffic through a cloud Secure Web Gateway (SWG) that terminates the client's TLS session using an enterprise Root CA and opens a second TLS session to the origin server.

---

## 🔬 2. What We Compute in This Lab

Given network parameters (`rtt_ms`, `tls_version`, `keep_alive`, `num_requests`, `concurrent_burst`, `server_backlog`):
1. Calculate total latency across `num_requests`.
2. Detect whether the burst will trigger **TCP SYN Backlog Drops (`ConnectionResetError`)** (`concurrent_burst > server_backlog`).
3. Quantify the exact latency savings of HTTP/2 connection pooling + TLS 1.3 over unpooled HTTP/1.1 + TLS 1.2.

---

## 🧪 3. Running Verification

```bash
./run.sh test 01-tcp-tls-and-proxy-inspector
```

