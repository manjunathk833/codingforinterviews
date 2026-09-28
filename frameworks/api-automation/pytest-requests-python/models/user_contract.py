"""Data Contract Schema validation models for User API."""
from typing import Optional, Dict, Any


class UserContract:
    def __init__(self, id: int, name: str, email: str, role: str, active: bool = True):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.active = active

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserContract":
        required_keys = {"id", "name", "email", "role"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(f"Schema Contract Violation: Missing fields {missing}")

        if not isinstance(data["id"], int) or data["id"] <= 0:
            raise ValueError(f"Invalid id: {data['id']}")
        if not isinstance(data["name"], str) or len(data["name"]) == 0:
            raise ValueError(f"Invalid name: {data['name']}")
        if "@" not in data.get("email", ""):
            raise ValueError(f"Invalid email: {data['email']}")

        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            role=data["role"],
            active=data.get("active", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
        }
