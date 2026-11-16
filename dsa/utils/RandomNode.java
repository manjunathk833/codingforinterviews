package utils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RandomNode {
    public int val;
    public RandomNode next;
    public RandomNode random;

    public RandomNode(int val) {
        this.val = val;
    }

    public static RandomNode fromPairs(List<List<Integer>> pairs) {
        if (pairs == null || pairs.isEmpty()) return null;
        List<RandomNode> nodes = new ArrayList<>();
        for (List<Integer> p : pairs) {
            nodes.add(new RandomNode(p.get(0)));
        }
        for (int i = 0; i < nodes.size(); i++) {
            if (i + 1 < nodes.size()) {
                nodes.get(i).next = nodes.get(i + 1);
            }
            Integer rIdx = pairs.get(i).get(1);
            if (rIdx != null && rIdx >= 0 && rIdx < nodes.size()) {
                nodes.get(i).random = nodes.get(rIdx);
            }
        }
        return nodes.get(0);
    }

    public static List<List<Integer>> toPairs(RandomNode head) {
        List<List<Integer>> res = new ArrayList<>();
        if (head == null) return res;
        List<RandomNode> order = new ArrayList<>();
        Map<RandomNode, Integer> idxMap = new HashMap<>();
        RandomNode curr = head;
        int idx = 0;
        while (curr != null && !idxMap.containsKey(curr)) {
            idxMap.put(curr, idx++);
            order.add(curr);
            curr = curr.next;
        }
        for (RandomNode node : order) {
            List<Integer> pair = new ArrayList<>(2);
            pair.add(node.val);
            pair.add(node.random != null ? idxMap.get(node.random) : null);
            res.add(pair);
        }
        return res;
    }
}
