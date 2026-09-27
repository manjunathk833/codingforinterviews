# REST Assured API Automation Framework (Java 17)

Enterprise-grade Java API automation framework pattern utilizing REST Assured, TestNG, RequestSpecBuilder, Filter chaining, and POJO mapping.

---

## 🏛️ Architecture & Best Practices

1. **Request & Response Specification Builders**:
   - Centralizes base URIs, common query params, and authentication headers (`Authorization: Bearer <token>`).
   - Standardizes response assertions (e.g. content-type `application/json`, status code assertions).
2. **Custom Allure / Logging Filters**:
   - Intercepts requests and responses to attach cURL commands and payloads into reports.
3. **Data Transfer Objects (DTOs / POJOs)**:
   - Uses Jackson / Gson annotations for clean serialization and deserialization.
   - Eliminates fragile hardcoded JSON strings.
4. **Environment & Secrets Configuration**:
   - Type-safe config using `Owner` library or system environment properties.
