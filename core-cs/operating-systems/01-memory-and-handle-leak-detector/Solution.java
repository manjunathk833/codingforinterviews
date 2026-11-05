import java.util.ArrayList;
import java.util.List;

/**
 * OS Lab 01: Desktop Daemon Memory & File-Descriptor Leak Detector (Java 17).
 */
public class Solution {

    public record Snapshot(double timestampMin, double rssMb, boolean gcTriggered, int openFds) {}

    public record SoakReport(
            String verdict,
            double postGcSlopeMbPerHr,
            double peakFdUtilization,
            boolean memoryLeak,
            boolean fdLeak
    ) {}

    public SoakReport analyzeSoakTelemetry(
            List<Snapshot> snapshots,
            int maxFdLimit,
            double leakSlopeThresholdMbPerHr
    ) {
        if (snapshots == null || snapshots.isEmpty()) {
            return new SoakReport("HEALTHY", 0.0, 0.0, false, false);
        }

        List<Snapshot> gcPoints = new ArrayList<>();
        int peakFds = 0;
        for (Snapshot s : snapshots) {
            if (s.gcTriggered()) {
                gcPoints.add(s);
            }
            if (s.openFds() > peakFds) {
                peakFds = s.openFds();
            }
        }
        if (gcPoints.size() < 2) {
            gcPoints.clear();
            gcPoints.add(snapshots.get(0));
            gcPoints.add(snapshots.get(snapshots.size() - 1));
        }

        Snapshot firstGc = gcPoints.get(0);
        Snapshot lastGc = gcPoints.get(gcPoints.size() - 1);
        double deltaHours = (lastGc.timestampMin() - firstGc.timestampMin()) / 60.0;

        double slopeMbPerHr = 0.0;
        if (deltaHours > 0) {
            slopeMbPerHr = Math.round(((lastGc.rssMb() - firstGc.rssMb()) / deltaHours) * 100.0) / 100.0;
        }
        boolean memoryLeak = slopeMbPerHr > leakSlopeThresholdMbPerHr;

        double peakFdUtil = Math.round((peakFds / (double) maxFdLimit) * 10000.0) / 10000.0;
        boolean monotonicFdGrowth = gcPoints.size() >= 3;
        if (monotonicFdGrowth) {
            for (int i = 0; i < gcPoints.size() - 1; i++) {
                if (gcPoints.get(i).openFds() >= gcPoints.get(i + 1).openFds()) {
                    monotonicFdGrowth = false;
                    break;
                }
            }
            if (lastGc.openFds() - firstGc.openFds() < 50) {
                monotonicFdGrowth = false;
            }
        }

        boolean fdLeak = (peakFdUtil >= 0.80) || monotonicFdGrowth;

        String verdict;
        if (memoryLeak && fdLeak) {
            verdict = "CRITICAL_DUAL_LEAK";
        } else if (memoryLeak) {
            verdict = "MEMORY_LEAK";
        } else if (fdLeak) {
            verdict = "FD_LEAK";
        } else {
            verdict = "HEALTHY";
        }

        return new SoakReport(verdict, slopeMbPerHr, peakFdUtil, memoryLeak, fdLeak);
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Case 1: Benign GC Sawtooth
        List<Snapshot> sawtooth = List.of(
                new Snapshot(0, 48.0, true, 64),
                new Snapshot(30, 135.0, false, 72),
                new Snapshot(60, 48.5, true, 65),
                new Snapshot(90, 142.0, false, 70),
                new Snapshot(120, 49.0, true, 64)
        );
        SoakReport r1 = sol.analyzeSoakTelemetry(sawtooth, 1024, 5.0);
        assert "HEALTHY".equals(r1.verdict()) : "Expected HEALTHY, got " + r1;

        // Case 2: True Post-GC Heap Leak
        List<Snapshot> heapLeak = List.of(
                new Snapshot(0, 50.0, true, 60),
                new Snapshot(60, 86.0, true, 62),
                new Snapshot(120, 122.0, true, 61)
        );
        SoakReport r2 = sol.analyzeSoakTelemetry(heapLeak, 1024, 5.0);
        assert "MEMORY_LEAK".equals(r2.verdict()) : "Expected MEMORY_LEAK, got " + r2;

        // Case 3: Silent Socket / File Descriptor Leak
        List<Snapshot> fdLeak = List.of(
                new Snapshot(0, 50.0, true, 80),
                new Snapshot(60, 50.2, true, 340),
                new Snapshot(120, 50.4, true, 890)
        );
        SoakReport r3 = sol.analyzeSoakTelemetry(fdLeak, 1024, 5.0);
        assert "FD_LEAK".equals(r3.verdict()) : "Expected FD_LEAK, got " + r3;

        System.out.println("All 3 Java OS Memory & File-Descriptor Leak Detector test cases passed!");
    }
}

