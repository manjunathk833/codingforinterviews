package pages;

import core.PlaywrightDriverFactory.MockPage;

public class LoginPage {
    private final MockPage page;

    public static final String USERNAME_INPUT = "#username";
    public static final String PASSWORD_INPUT = "#password";
    public static final String LOGIN_BUTTON = "#login-btn";

    public LoginPage(MockPage page) {
        this.page = page;
    }

    public LoginPage enterUsername(String username) {
        page.fill(USERNAME_INPUT, username);
        return this;
    }

    public LoginPage enterPassword(String password) {
        page.fill(PASSWORD_INPUT, password);
        return this;
    }

    public void clickSubmit() {
        page.click(LOGIN_BUTTON);
    }
}
