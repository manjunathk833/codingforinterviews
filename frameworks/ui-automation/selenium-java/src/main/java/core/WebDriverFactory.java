package core;

import java.util.HashMap;
import java.util.Map;

/**
 * ThreadLocal driver manager demonstrating thread-safe parallel browser execution.
 */
public class WebDriverFactory {

    public interface MockDriver {
        void get(String url);
        void click(String selector);
        void sendKeys(String selector, String text);
        String getText(String selector);
        void quit();
    }

    public static class SimpleDriver implements MockDriver {
        private final Map<String, String> elements = new HashMap<>();

        @Override public void get(String url) {}
        @Override public void click(String selector) {}
        @Override public void sendKeys(String selector, String text) { elements.put(selector, text); }
        @Override public String getText(String selector) { return elements.getOrDefault(selector, ""); }
        @Override public void quit() { elements.clear(); }
    }

    private static final ThreadLocal<MockDriver> driverThread = new ThreadLocal<>();

    public static MockDriver getDriver() {
        if (driverThread.get() == null) {
            driverThread.set(new SimpleDriver());
        }
        return driverThread.get();
    }

    public static void quitDriver() {
        if (driverThread.get() != null) {
            driverThread.get().quit();
            driverThread.remove(); // Prevent thread pool memory leak
        }
    }
}
