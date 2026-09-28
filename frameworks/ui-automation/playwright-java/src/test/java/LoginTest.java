package test;

import core.PlaywrightDriverFactory;
import pages.LoginPage;

public class LoginTest {

    public void testLoginSequence() {
        PlaywrightDriverFactory.SimplePage page = (PlaywrightDriverFactory.SimplePage) PlaywrightDriverFactory.getPage();
        LoginPage loginPage = new LoginPage(page);

        loginPage.enterUsername("sdet_candidate")
                 .enterPassword("Pass1234!")
                 .clickSubmit();

        assert page.getFieldValue(LoginPage.USERNAME_INPUT).equals("sdet_candidate") : "Username incorrect";
        assert page.getFieldValue(LoginPage.PASSWORD_INPUT).equals("Pass1234!") : "Password incorrect";

        PlaywrightDriverFactory.cleanUp();
    }

    public static void main(String[] args) {
        LoginTest test = new LoginTest();
        test.testLoginSequence();
        System.out.println("Playwright Java LoginTest passed successfully!");
    }
}
