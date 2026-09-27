"""Login Page Object encapsulating elements and actions on Login screen."""
from .base_page import BasePage


class LoginPage(BasePage):
    # Resilient Locators
    USERNAME_INPUT = "#username, [data-testid='username-field']"
    PASSWORD_INPUT = "#password, [data-testid='password-field']"
    LOGIN_BUTTON = "button[type='submit'], [data-testid='login-btn']"
    ERROR_MESSAGE = ".alert-danger, [data-testid='error-msg']"
    SUCCESS_BANNER = ".dashboard-welcome, [data-testid='welcome-banner']"

    def login(self, username: str, password: str) -> "LoginPage":
        """Performs full login sequence."""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_successful(self) -> bool:
        return self.is_visible(self.SUCCESS_BANNER)
