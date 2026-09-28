package pages;

import core.WebDriverFactory.MockDriver;

public class DashboardPage {
    private final MockDriver driver;

    public static final String METRIC_CARD = "#total-tests-metric";
    public static final String STATUS_BADGE = ".status-pass";

    public DashboardPage(MockDriver driver) {
        this.driver = driver;
    }

    public String getMetricText() {
        return driver.getText(METRIC_CARD);
    }
}
