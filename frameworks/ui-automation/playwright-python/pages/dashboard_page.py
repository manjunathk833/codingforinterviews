"""Dashboard Page Object encapsulating post-login metrics and user controls."""
from .base_page import BasePage


class DashboardPage(BasePage):
    WELCOME_HEADER = "h1.welcome-title, [data-testid='welcome-header']"
    LOGOUT_BUTTON = "button#logout, [data-testid='logout-btn']"
    PROFILE_BADGE = ".user-profile, [data-testid='profile-badge']"

    def get_welcome_text(self) -> str:
        return self.get_text(self.WELCOME_HEADER)

    def logout(self) -> None:
        self.click(self.LOGOUT_BUTTON)
