# Course 12 Lab: `AeroShield` BOLA/IDOR, JWT RFC 8725, SSRF Socket Guard & LLM Prompt-Injection Gate

Deterministic local verification harness for **Course 12 (`12-app-api-and-ai-security`)**.

## Invariants Verified
1. **OWASP API1:2023 Broken Object Level Authorization (`BOLA` / `IDOR`)**: Enforces composite `(resource_id, caller_tenant_id)` predicates on every object access.
2. **RFC 8725 JWT Hardening**: Rejects `alg: none`, unpinned algorithms (`RS256 -> HS256` confusion), invalid `iss`/`aud`, and expired tokens using constant-time `hmac.compare_digest`.
3. **OWASP API7:2023 Server-Side Request Forgery (`SSRF`)**: Validates resolved IP addresses pre-connect against AWS/GCP IMDSv2 (`169.254.169.254`), loopback (`127.0.0.0/8`), and RFC 1918 private networks.
4. **Stripe-Style Webhook HMAC & Replay Window**: Binds timestamp + payload bytes into HMAC-SHA256 and enforces a bounded 300-second replay window.
5. **OWASP LLM01 / LLM06 Agentic Tool Policy Gate**: Blocks indirect prompt injections embedded in untrusted RAG documents and enforces caller-scoped, human-gated tool execution.

## Run Locally
```bash
python3 frameworks/security-testing/01-bola-jwt-and-prompt-shield/reference_solution.py
```
