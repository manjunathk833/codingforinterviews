"""SDET Challenge: Fluent Test Data Factory with Deep Clone Mutator"""
import copy
from typing import List


class TestUser:
    def __init__(self, user_id: str, name: str, email: str, permissions: List[str]):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.permissions = list(permissions)


class TestUserFactory:
    def __init__(self):
        self._user_id = "USR-1001"
        self._name = "Default Candidate"
        self._email = "candidate@maang.com"
        self._permissions = ["READ", "WRITE"]

    @classmethod
    def a_default_user(cls) -> "TestUserFactory":
        return cls()

    def with_name(self, name: str) -> "TestUserFactory":
        self._name = name
        return self

    def with_email(self, email: str) -> "TestUserFactory":
        self._email = email
        return self

    def with_permissions(self, *perms: str) -> "TestUserFactory":
        self._permissions = list(perms)
        return self

    def build(self) -> TestUser:
        return TestUser(
            user_id=self._user_id,
            name=self._name,
            email=self._email,
            permissions=copy.deepcopy(self._permissions),
        )


if __name__ == "__main__":
    # Test 1: Standard baseline
    user1 = TestUserFactory.a_default_user().build()
    assert user1.name == "Default Candidate", "Test 1 Failed"
    assert "READ" in user1.permissions, "Test 1 Failed"

    # Test 2: Overrides do not affect other instances
    user2 = (
        TestUserFactory.a_default_user()
        .with_name("Admin Manjunath")
        .with_permissions("ADMIN", "READ", "WRITE", "DELETE")
        .build()
    )

    assert user2.name == "Admin Manjunath", "Test 2 Failed"
    assert len(user2.permissions) == 4, "Test 2 Failed"
    assert len(user1.permissions) == 2, "Test 2 Failed: user1 was mutated!"

    print("All 2 Python Test Data Factory test cases passed!")
