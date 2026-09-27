"""UI Automation Test Suite testing Page Object interactions and locator assertions."""
import unittest
from pages.login_page import LoginPage


class MockPageDriver:
    """Simulates Playwright Page object for offline unit testing of POM logic."""

    def __init__(self):
        self.elements = {}
        self.current_url = ""

    def goto(self, url: str):
        self.current_url = url

    def fill(self, selector: str, text: str):
        self.elements[selector] = text

    def click(self, selector: str):
        self.last_clicked = selector

    def inner_text(self, selector: str) -> str:
        return self.elements.get(selector, "")

    def is_visible(self, selector: str) -> bool:
        return True


class TestLoginFlow(unittest.TestCase):
    def setUp(self):
        self.mock_driver = MockPageDriver()
        self.login_page = LoginPage(self.mock_driver)

    def test_login_field_population_and_submit(self):
        self.login_page.login("test_user@example.com", "SecretPass123!")

        self.assertEqual(
            self.mock_driver.elements[LoginPage.USERNAME_INPUT],
            "test_user@example.com",
        )
        self.assertEqual(
            self.mock_driver.elements[LoginPage.PASSWORD_INPUT],
            "SecretPass123!",
        )
        self.assertEqual(self.mock_driver.last_clicked, LoginPage.LOGIN_BUTTON)
        self.assertTrue(self.login_page.is_login_successful())


if __name__ == "__main__":
    unittest.main()
