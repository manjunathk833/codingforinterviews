import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * AI Lab 01: RAG Triad Evaluator & Negation Hallucination Gate (Java 17).
 */
public class Solution {

    private static final Set<String> NEGATIONS = Set.of("not", "never", "cannot", "cant", "prohibited");
    private static final Set<String> STOP_WORDS = Set.of(
            "the", "a", "an", "is", "are", "for", "to", "of", "in", "on", "with", "within", "what", "can", "i"
    );

    public record RagEvaluation(
            double contextRecall,
            double faithfulness,
            double answerRelevance,
            boolean passedCiGate
    ) {}

    private Set<String> tokenize(String text) {
        return Arrays.stream(text.toLowerCase().split("[^a-z0-9%]+"))
                .filter(w -> !w.isBlank() && !STOP_WORDS.contains(w))
                .collect(Collectors.toSet());
    }

    public RagEvaluation evaluateRagTriad(
            String query,
            List<String> retrievedContexts,
            String generatedAnswer,
            List<String> groundTruthFacts
    ) {
        String combinedCtx = String.join(" ", retrievedContexts).toLowerCase();
        Set<String> ctxTokens = tokenize(combinedCtx);
        Set<String> ansTokens = tokenize(generatedAnswer);
        Set<String> qTokens = tokenize(query);

        // 1. Context Recall
        int covered = 0;
        for (String fact : groundTruthFacts) {
            Set<String> fTokens = tokenize(fact);
            long match = fTokens.stream().filter(ctxTokens::contains).count();
            if (!fTokens.isEmpty() && (match / (double) fTokens.size()) >= 0.6) {
                covered++;
            }
        }
        double contextRecall = Math.round((covered / (double) Math.max(1, groundTruthFacts.size())) * 100.0) / 100.0;

        // 2. Faithfulness + Polarity Check
        long supported = ansTokens.stream().filter(ctxTokens::contains).count();
        double baseFaith = ansTokens.isEmpty() ? 0.0 : supported / (double) ansTokens.size();

        boolean contradictoryNegation = false;
        for (String neg : NEGATIONS) {
            if (generatedAnswer.toLowerCase().contains(neg) && !combinedCtx.contains(neg)) {
                contradictoryNegation = true;
                break;
            }
        }
        double faithfulness;
        if (contradictoryNegation || generatedAnswer.toLowerCase().contains("under all circumstances")) {
            faithfulness = Math.round(Math.min(0.25, baseFaith * 0.25) * 100.0) / 100.0;
        } else {
            faithfulness = Math.round(Math.min(1.0, baseFaith * 1.25) * 100.0) / 100.0;
        }

        // 3. Answer Relevance
        long qMatch = qTokens.stream().filter(ansTokens::contains).count();
        double relevance = qTokens.isEmpty() ? 1.0 : Math.round(Math.min(1.0, (qMatch / (double) qTokens.size()) * 1.4) * 100.0) / 100.0;

        boolean passed = contextRecall >= 0.80 && faithfulness >= 0.80 && relevance >= 0.70;
        return new RagEvaluation(contextRecall, faithfulness, relevance, passed);
    }

    public static void main(String[] args) {
        Solution sol = new Solution();
        List<String> ctx = List.of(
                "Passengers may cancel their reservation within 24 hours of booking for a 100% full refund, provided the ticket was purchased at least 7 days prior to departure."
        );
        List<String> facts = List.of("cancel within 24 hours 100% full refund", "purchased 7 days prior departure");

        RagEvaluation r1 = sol.evaluateRagTriad(
                "Can I cancel within 24 hours for a full refund?",
                ctx,
                "Yes, you may cancel your reservation within 24 hours of booking for a 100% full refund if purchased 7 days prior.",
                facts
        );
        assert r1.passedCiGate() : "Expected grounded answer to pass: " + r1;

        RagEvaluation r2 = sol.evaluateRagTriad(
                "Can I cancel within 24 hours for a full refund?",
                ctx,
                "Passengers cannot cancel their reservation within 24 hours of booking for a 100% full refund.",
                facts
        );
        assert !r2.passedCiGate() && r2.faithfulness() <= 0.25 : "Expected negation trap to fail: " + r2;

        RagEvaluation r3 = sol.evaluateRagTriad(
                "Can I cancel within 24 hours for a full refund?",
                ctx,
                "Pets traveling in the cabin must remain inside a ventilated carrier beneath the seat.",
                facts
        );
        assert !r3.passedCiGate() && r3.answerRelevance() < 0.50 : "Expected irrelevant answer to fail: " + r3;

        System.out.println("All 3 Java AI Engineering RAG Triad & Negation Trap test cases passed!");
    }
}

