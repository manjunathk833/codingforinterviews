import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * AI Lab 02: Weighted Multi-Signal Self-Healing UI Locator Engine (Java 17).
 */
public class Solution {

    private static final Set<String> DESTRUCTIVE = Set.of("delete", "cancel", "remove", "destroy", "revoke");

    public record DomElement(
            String id,
            String tag,
            String role,
            String text,
            String ariaLabel,
            String parentContext
    ) {}

    public record HealResult(
            boolean healed,
            double confidence,
            String matchedId,
            String suggestedAstLocator
    ) {}

    private boolean isDestructive(DomElement el) {
        String combined = (el.text() + " " + el.ariaLabel()).toLowerCase();
        for (String kw : DESTRUCTIVE) {
            if (combined.contains(kw)) {
                return true;
            }
        }
        return false;
    }

    private double tokenJaccard(String a, String b) {
        Set<String> sa = new HashSet<>(Arrays.asList(a.toLowerCase().split("[\\s\\-_]+")));
        Set<String> sb = new HashSet<>(Arrays.asList(b.toLowerCase().split("[\\s\\-_]+")));
        sa.remove("");
        sb.remove("");
        if (sa.isEmpty() || sb.isEmpty()) {
            return 0.0;
        }
        Set<String> inter = new HashSet<>(sa);
        inter.retainAll(sb);
        Set<String> union = new HashSet<>(sa);
        union.addAll(sb);
        return inter.size() / (double) union.size();
    }

    public HealResult healBrokenLocator(
            DomElement baseline,
            List<DomElement> candidates,
            double threshold
    ) {
        boolean baseDestructive = isDestructive(baseline);
        DomElement best = null;
        double bestScore = 0.0;

        for (DomElement cand : candidates) {
            if (isDestructive(cand) != baseDestructive) {
                continue;
            }
            double score = 0.0;
            if (cand.role().equals(baseline.role()) && cand.tag().equals(baseline.tag())) {
                score += 0.25;
            }
            score += 0.35 * tokenJaccard(baseline.ariaLabel(), cand.ariaLabel());
            score += 0.25 * tokenJaccard(baseline.text(), cand.text());
            if (cand.parentContext().equals(baseline.parentContext())) {
                score += 0.15;
            }
            score = Math.round(score * 1000.0) / 1000.0;
            if (score > bestScore) {
                bestScore = score;
                best = cand;
            }
        }

        if (best != null && bestScore >= threshold) {
            String astLocator = "page.getByRole(\"" + best.role() + "\", name=\"" + best.text() + "\")";
            return new HealResult(true, bestScore, best.id(), astLocator);
        }
        return new HealResult(false, bestScore, null, null);
    }

    public static void main(String[] args) {
        Solution sol = new Solution();
        DomElement baseline = new DomElement(
                "btn-book-legacy", "button", "button",
                "Confirm Flight Booking", "Confirm Flight Booking", "checkout-form"
        );
        DomElement cancelBtn = new DomElement(
                "btn-cancel-danger", "button", "button",
                "Cancel Flight Booking", "Cancel Flight Booking", "checkout-form"
        );
        DomElement renamedBtn = new DomElement(
                "confirm-booking-cta-v2", "button", "button",
                "Confirm Flight Booking", "Confirm Flight Booking Now", "checkout-form"
        );

        HealResult r1 = sol.healBrokenLocator(baseline, List.of(cancelBtn, renamedBtn), 0.75);
        assert r1.healed() && "confirm-booking-cta-v2".equals(r1.matchedId()) : "Expected heal: " + r1;

        HealResult r2 = sol.healBrokenLocator(baseline, List.of(cancelBtn), 0.75);
        assert !r2.healed() : "Must never heal onto destructive cancel button!";

        System.out.println("All 2 Java Self-Healing UI Locator & AST Safety Gate test cases passed!");
    }
}

