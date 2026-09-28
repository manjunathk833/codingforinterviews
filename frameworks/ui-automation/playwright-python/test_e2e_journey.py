"""End-to-End User Journey test simulating Playwright Page interactions."""
import unittest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


class MockPlaywrightPage:
    def __init__(self):
        self.elements = {
            DashboardPage.WELCOME_HEADER: "Welcome back, Manjunath!",
            DashboardPage.PROFILE_BADGE: "Senior SDET",
        }
        self.clicked_history = []

    def goto(self, url: str):
        pass

    def fill(self, selector: str, text: str):
        self.elements[selector] = text

    def click(self, selector: str):
        self.clicked_history.append(selector)

    def inner_text(self, selector: str) -> str:
        return self.elements.get(selector, "")

    def is_visible(self, selector: str) -> bool:
        return selector in self.elements


class TestEndToEndJourney(unittest.TestCase):
    def setUp(self):
        self.page = MockPlaywrightPage()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_full_login_to_dashboard_journey(self):
        self.login_page.login("candidate@maang.com", "Password@2026")
        self.assertIn(LoginPage.LOGIN_BUTTON, self.page.clicked_history)

        welcome_text = self.dashboard_page.get_welcome_text()
        self.assertEqual(welcome_text, "Welcome back, Manjunath!")

        self.dashboard_page.logout()
        self.assertIn(DashboardPage.LOGOUT_BUTTON, self.page.clicked_history)


if __name__ == "__main__":
    unittest.main()
