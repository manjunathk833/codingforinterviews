"""API Automation Suite Tests demonstrating contract validation, status checks, and latency benchmarking."""
import unittest
from conftest import get_api_client
from models.user_contract import UserContract


class TestUserApi(unittest.TestCase):
    def setUp(self):
        self.client = get_api_client()

    def test_get_user_success_and_contract(self):
        resp = self.client.request("GET", "users/1")
        self.assertTrue(resp.is_success)
        self.assertEqual(resp.status_code, 200)

        # Validate schema contract
        user = UserContract.from_dict(resp.body)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.name, "Manjunath H K")
        self.assertEqual(user.role, "SENIOR_SDET")
        self.assertLess(resp.latency_ms, 500, "Latency benchmark violated (>500ms)")

    def test_create_user_contract(self):
        payload = {"name": "Priya", "email": "priya@example.com", "role": "QA_LEAD"}
        resp = self.client.request("POST", "users", payload=payload)
        self.assertEqual(resp.status_code, 201)

        created_user = UserContract.from_dict(resp.body)
        self.assertEqual(created_user.id, 102)
        self.assertEqual(created_user.name, "Priya")

    def test_user_not_found(self):
        resp = self.client.request("GET", "users/9999")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
