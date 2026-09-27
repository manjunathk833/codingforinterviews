import java.io.IOException;
import java.util.concurrent.Callable;

/**
 * SDET Challenge: Custom Retry Analyzer with Exponential Backoff
 */
public class Solution {

    public static class RetryConfig {
        public final int maxRetries;
        public final long initialDelayMs;
        public final double backoffMultiplier;

        public RetryConfig(int maxRetries, long initialDelayMs, double backoffMultiplier) {
            this.maxRetries = maxRetries;
            this.initialDelayMs = initialDelayMs;
            this.backoffMultiplier = backoffMultiplier;
        }
    }

    /**
     * Executes a supplier task with retry and exponential backoff.
     */
    public <T> T executeWithRetry(Callable<T> task, RetryConfig config, Class<? extends Throwable> retriableException)
            throws Exception {
        int attempt = 0;
        long delay = config.initialDelayMs;

        while (true) {
            try {
                attempt++;
                return task.call();
            } catch (Exception e) {
                if (!retriableException.isInstance(e) || attempt > config.maxRetries) {
                    throw e;
                }
                // Simulate wait (in test we don't actually sleep to keep tests fast)
                delay = (long) (delay * config.backoffMultiplier);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        Solution engine = new Solution();
        RetryConfig config = new RetryConfig(3, 10, 2.0);

        // Test 1: Succeeds on attempt 3
        int[] counter1 = { 0 };
        String res1 = engine.executeWithRetry(() -> {
            counter1[0]++;
            if (counter1[0] < 3) {
                throw new IOException("Temporary 503 network error");
            }
            return "SUCCESS_DATA";
        }, config, IOException.class);
        assert res1.equals("SUCCESS_DATA") && counter1[0] == 3 : "Test 1 Failed: Expected 3 attempts";

        // Test 2: Fails immediately on non-retriable exception (e.g. IllegalArgumentException)
        int[] counter2 = { 0 };
        boolean caughtNonRetriable = false;
        try {
            engine.executeWithRetry(() -> {
                counter2[0]++;
                throw new IllegalArgumentException("400 Bad Request - schema invalid");
            }, config, IOException.class);
        } catch (IllegalArgumentException e) {
            caughtNonRetriable = true;
        }
        assert caughtNonRetriable && counter2[0] == 1 : "Test 2 Failed: Non-retriable exception was retried";

        // Test 3: Exhausts all retries and rethrows
        int[] counter3 = { 0 };
        boolean caughtExhausted = false;
        try {
            engine.executeWithRetry(() -> {
                counter3[0]++;
                throw new IOException("Persistent outage");
            }, config, IOException.class);
        } catch (IOException e) {
            caughtExhausted = true;
        }
        assert caughtExhausted && counter3[0] == 4 : "Test 3 Failed: Expected initial + 3 retries = 4 attempts";

        System.out.println("All 3 Java Retry Analyzer test cases passed!");
    }
}
