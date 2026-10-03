# Secret Scanner Patterns & False Positive Filters

This reference documents the security rules enforced by `secret_scanner.py` and `safety_check.sh`.

---

## 1. High-Confidence Secret Signatures

| Pattern Label | Regex Definition | Target Credentials |
| :--- | :--- | :--- |
| **GitHub Classic PAT** | `\bghp_[a-zA-Z0-9]{36}\b` | Personal access tokens |
| **GitHub Fine-Grained Token** | `\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}\b` | Scoped GitHub tokens |
| **GitHub App / OAuth Token** | `\bgh[oas]_[a-zA-Z0-9]{36}\b` | OAuth/server tokens |
| **Anthropic API Key** | `\bsk-ant-(?:api03\|oat01\|admin01)-[0-9A-Za-z_\-]{93}AA\b` | Claude API keys |
| **OpenAI API Key** | `\bsk-(?:live\|test\|proj\|svcacct)?-[a-zA-Z0-9_\-]{40,}\b` | GPT API keys |
| **AWS Access Key ID** | `\bAKIA[0-9A-Z]{16}\b` | IAM access keys |
| **AWS Secret Access Key** | `(?i)aws_secret_access_key\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]` | IAM secret keys |
| **Google Cloud API Key** | `\bAIza[0-9A-Za-z_\-]{35}\b` | GCP API credentials |
| **Slack Token & Webhooks** | `\bxox[baprs]-[0-9]{10,13}...` & `hooks.slack.com...` | Slack integrations |
| **Private Keys** | `-----BEGIN ((EC\|PGP\|DSA\|RSA\|OPENSSH) )?PRIVATE KEY...` | Cryptographic keys |
| **Database Connection URI** | `(postgres\|mysql\|mongodb(\+srv)?):\/\/[^\s:@]+:[^\s:@]+@[^\s\/:]+` | DB strings with passwords |

---

## 2. Prohibited Extensions and Files

- **Binary / Bytecode**: `.class`, `.pyc`, `.pyo`, `.jar`, `.war`, `.ear`
- **Keys & Certificates**: `.pem`, `.key`, `.p12`, `.pfx`, `.keystore`
- **Personal Files**: `singlepageresume.json`, `*resume*`, `*.pdf`
- **Environment**: `.env`, `.env.local`, `.env.production`
- **System**: `.DS_Store`, `Thumbs.db`

---

## 3. Allowed Test Patterns (False Positive Filters)

The scanner ignores patterns containing words like `dummy`, `example`, `sample`, `your_jwt`, `test_token`, `SecretPass123!`, `Password@2026`, or `TokenBucketRateLimiter` to allow realistic test payloads in automation suites.
