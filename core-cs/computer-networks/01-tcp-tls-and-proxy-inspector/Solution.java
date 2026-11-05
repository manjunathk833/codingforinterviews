/**
 * Networks Lab 01: TCP/TLS Handshakes, SYN Backlogs & SASE Proxy Inspector (Java 17).
 */
public class Solution {

    public record NetworkReport(
            double totalLatencyMs,
            double handshakeOverheadMs,
            boolean synBacklogOverflow,
            int droppedConnections
    ) {}

    public NetworkReport evaluateNetworkProfile(
            double rttMs,
            int numRequests,
            String tlsVersion,
            boolean keepAlive,
            int concurrentBurst,
            int serverBacklog
    ) {
        int tcpRtts = 1;
        int tlsRtts = "1.3".equals(tlsVersion) ? 1 : 2;
        double handshakeMs = (tcpRtts + tlsRtts) * rttMs;
        double requestMs = rttMs;

        double totalLatencyMs;
        double totalHandshakeMs;
        if (keepAlive) {
            totalLatencyMs = handshakeMs + (numRequests * requestMs);
            totalHandshakeMs = handshakeMs;
        } else {
            totalLatencyMs = numRequests * (handshakeMs + requestMs);
            totalHandshakeMs = numRequests * handshakeMs;
        }

        int dropped = Math.max(0, concurrentBurst - serverBacklog);
        boolean overflow = dropped > 0;

        return new NetworkReport(
                Math.round(totalLatencyMs * 100.0) / 100.0,
                Math.round(totalHandshakeMs * 100.0) / 100.0,
                overflow,
                dropped
        );
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Case 1: Unpooled TLS 1.2
        NetworkReport r1 = sol.evaluateNetworkProfile(50.0, 10, "1.2", false, 1, 128);
        assert r1.totalLatencyMs() == 2000.0 : "Expected 2000.0ms, got " + r1;

        // Case 2: Pooled TLS 1.3
        NetworkReport r2 = sol.evaluateNetworkProfile(50.0, 10, "1.3", true, 1, 128);
        assert r2.totalLatencyMs() == 600.0 : "Expected 600.0ms, got " + r2;

        // Case 3: Linux SYN Backlog Overflow (32 burst vs backlog=5)
        NetworkReport r3 = sol.evaluateNetworkProfile(10.0, 32, "1.3", true, 32, 5);
        assert r3.synBacklogOverflow() && r3.droppedConnections() == 27 : "Expected 27 drops, got " + r3;

        System.out.println("All 3 Java Computer Networks TCP/TLS & Backlog test cases passed!");
    }
}

