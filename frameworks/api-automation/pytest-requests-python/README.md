# Pytest + Python API Automation Framework

Enterprise-grade API automation framework pattern using standard Python, connection pooling, dynamic authentication, and schema validation.

---

## 🏛️ Architecture & Features

- **Centralized Client (`api_client.py`)**: Uses Python's standard `urllib.request` / `http.client` (zero third-party dependencies required out of the box, with seamless upgrade path to `requests` or `httpx`).
- **Standardized Response Model**: Captures `status_code`, `body_json`, `headers`, and `latency_ms`.
- **Pre-request & Post-request Interceptors**: Auth headers injection, logging, and error categorization.

---

## 🏃 Execution

Run the suite directly:
```bash
python3 test_api.py
```
Or via unittest:
```bash
python3 -m unittest test_api.py
```
