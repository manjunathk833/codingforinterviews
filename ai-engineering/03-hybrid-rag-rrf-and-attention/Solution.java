import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI Engineering Lab 03: Causal Scaled Dot-Product Self-Attention & Hybrid RRF (Java 17).
 */
public class Solution {

    static double[][] causalAttentionWeights(double[][] Q, double[][] K) {
        int seqLen = Q.length;
        int dk = Q[0].length;
        double scale = Math.sqrt(dk);
        double[][] weights = new double[seqLen][seqLen];

        for (int i = 0; i < seqLen; i++) {
            double maxLogit = Double.NEGATIVE_INFINITY;
            double[] logits = new double[seqLen];
            for (int j = 0; j < seqLen; j++) {
                if (j > i) {
                    logits[j] = Double.NEGATIVE_INFINITY;
                } else {
                    double dot = 0.0;
                    for (int m = 0; m < dk; m++) {
                        dot += Q[i][m] * K[j][m];
                    }
                    logits[j] = dot / scale;
                    maxLogit = Math.max(maxLogit, logits[j]);
                }
            }
            double denom = 0.0;
            for (int j = 0; j < seqLen; j++) {
                weights[i][j] = Double.isInfinite(logits[j]) ? 0.0 : Math.exp(logits[j] - maxLogit);
                denom += weights[i][j];
            }
            for (int j = 0; j < seqLen; j++) {
                weights[i][j] /= denom;
            }
        }
        return weights;
    }

    static List<String> reciprocalRankFusion(List<List<String>> lists, int k) {
        Map<String, Double> scores = new HashMap<>();
        for (List<String> ranked : lists) {
            for (int i = 0; i < ranked.size(); i++) {
                String doc = ranked.get(i);
                scores.put(doc, scores.getOrDefault(doc, 0.0) + 1.0 / (k + i + 1));
            }
        }
        List<String> docs = new ArrayList<>(scores.keySet());
        docs.sort(Comparator.<String>comparingDouble(scores::get).reversed().thenComparing(s -> s));
        return docs;
    }

    public static void main(String[] args) {
        double[][] Q = {{1.0, 0.0}, {0.5, 0.5}, {0.0, 1.0}};
        double[][] K = {{1.0, 0.0}, {0.5, 0.5}, {0.0, 1.0}};
        double[][] w = causalAttentionWeights(Q, K);

        assert Math.abs(w[0][0] - 1.0) < 1e-9;
        assert w[0][1] == 0.0 && w[0][2] == 0.0;

        List<String> fused = reciprocalRankFusion(
            List.of(
                List.of("doc_err_409", "doc_retry_guide", "doc_general_faq"),
                List.of("doc_concurrency_overview", "doc_err_409", "doc_retry_guide")
            ),
            60
        );
        assert "doc_err_409".equals(fused.get(0)) : "Expected doc_err_409 first, got " + fused;

        System.out.println("All 2 Java Causal Self-Attention & Hybrid RRF Retrieval test cases passed!");
    }
}
