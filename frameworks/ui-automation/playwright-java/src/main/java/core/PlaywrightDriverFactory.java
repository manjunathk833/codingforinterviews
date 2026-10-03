package core;

import java.util.HashMap;
import java.util.Map;

/**
 * Thread-safe driver factory managing Page instances per worker thread.
 */
public class PlaywrightDriverFactory {

    public interface MockPage {
        void navigate(String url);
        void click(String selector);
        void fill(String selector, String text);
        String textContent(String selector);
        boolean isVisible(String selector);
    }

    public static class SimplePage implements MockPage {
        private final Map<String, String> elements = new HashMap<>();
        private String currentUrl;

        @Override
        public void navigate(String url) { this.currentUrl = url; }
        @Override
        public void click(String selector) {}
        @Override
        public void fill(String selector, String text) { elements.put(selector, text); }
        @Override
        public String textContent(String selector) { return elements.getOrDefault(selector, ""); }
        @Override
        public boolean isVisible(String selector) { return true; }

        public String getFieldValue(String selector) { return elements.get(selector); }
    }

    private static final ThreadLocal<MockPage> pageThread = new ThreadLocal<>();

    public static MockPage getPage() {
        if (pageThread.get() == null) {
            pageThread.set(new SimplePage());
        }
        return pageThread.get();
    }

    public static void cleanUp() {
        pageThread.remove();
    }
}
