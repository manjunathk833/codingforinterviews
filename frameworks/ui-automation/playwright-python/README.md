# Playwright UI Automation Framework

Modern UI Automation testing suite using the Page Object Model (POM), intelligent auto-waiting, explicit synchronization guards, and locator resilience.

---

## 🏛️ Architecture Patterns
- **BasePage (`pages/base_page.py`)**: Encapsulates common browser navigation, auto-wait strategies, screenshot capture, and locator resolution.
- **Page Objects (`pages/login_page.py`)**: Decouples UI selector locators from test logic.
- **Structural Tests (`test_ui_patterns.py`)**: Demonstrates clean verification, fluent method chaining, and state validation.

---

## 🏃 Execution

```bash
python3 test_ui_patterns.py
```
