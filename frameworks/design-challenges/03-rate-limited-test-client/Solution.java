/**
 * SDET Challenge: Thread-Safe Rate-Limited Test Client (Token Bucket Algorithm)
 */
public class Solution {

    public static class TokenBucketRateLimiter {
        private final long capacity;
        private final double refillRatePerMs;
        private double availableTokens;
        private long lastRefillTimestamp;

        public TokenBucketRateLimiter(long capacity, double refillTokensPerSecond) {
            this.capacity = capacity;
            this.refillRatePerMs = refillTokensPerSecond / 1000.0;
            this.availableTokens = capacity;
            this.lastRefillTimestamp = System.currentTimeMillis();
        }

        public synchronized boolean tryAcquire(int tokens) {
            refill();
            if (availableTokens >= tokens) {
                availableTokens -= tokens;
                return true;
            }
            return false;
        }

        private void refill() {
            long now = System.currentTimeMillis();
            long elapsed = now - lastRefillTimestamp;
            if (elapsed > 0) {
                double tokensToAdd = elapsed * refillRatePerMs;
                availableTokens = Math.min(capacity, availableTokens + tokensToAdd);
                lastRefillTimestamp = now;
            }
        }

        public synchronized double getAvailableTokens() {
            refill();
            return availableTokens;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        // Capacity 5, refill rate 10 tokens/sec
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(5, 10.0);

        // Test 1: Immediate burst should consume all 5 tokens
        for (int i = 0; i < 5; i++) {
            assert limiter.tryAcquire(1) : "Test 1 Failed: Token " + i + " should be acquired";
        }

        // Test 2: 6th request immediately should fail (burst exhausted)
        assert !limiter.tryAcquire(1) : "Test 2 Failed: Burst should be exhausted";

        // Test 3: Wait 250ms -> should refill ~2.5 tokens, so acquiring 2 should succeed
        Thread.sleep(250);
        assert limiter.tryAcquire(2) : "Test 3 Failed: Tokens should have replenished";

        System.out.println("All 3 Java Token Bucket Rate Limiter test cases passed!");
    }
}
