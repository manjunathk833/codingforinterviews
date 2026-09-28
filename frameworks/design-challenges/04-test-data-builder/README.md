# CH-04: Fluent Test Data Factory & Deep Clone Mutator

- **Target Level**: Senior SDET / Data Quality Engineer (Meta, Google, Uber)
- **Domain**: Dynamic Test Data Management for Microservices

---

## Interview Problem Statement
In microservice testing, hardcoded test data leads to brittle tests and data collisions. Tests require generating valid base entities while fluently overriding specific fields (e.g. creating an inactive user, an admin user, or a user with invalid email) without mutating the baseline prototype.

Your task is to implement a **Fluent Test Data Factory** that:
1. Holds a baseline default entity prototype.
2. Supports chaining field overrides (`withName()`, `withEmail()`, `withStatus()`).
3. Produces a deep-copied, independent instance upon `.build()`, guaranteeing that mutating one generated instance never alters other tests or the baseline template.

---

## Target Complexities
- **Time Complexity**: $O(K)$ per entity generated where $K$ is number of fields
- **Space Complexity**: $O(K)$ per instance
