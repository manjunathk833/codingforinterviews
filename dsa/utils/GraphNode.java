package utils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

public class GraphNode {
    public int val;
    public List<GraphNode> neighbors;

    public GraphNode() {
        this.val = 0;
        this.neighbors = new ArrayList<>();
    }

    public GraphNode(int val) {
        this.val = val;
        this.neighbors = new ArrayList<>();
    }

    public GraphNode(int val, List<GraphNode> neighbors) {
        this.val = val;
        this.neighbors = neighbors != null ? neighbors : new ArrayList<>();
    }

    public static GraphNode fromAdjList(List<List<Integer>> adj) {
        if (adj == null || adj.isEmpty()) return null;
        List<GraphNode> nodes = new ArrayList<>();
        for (int i = 0; i < adj.size(); i++) {
            nodes.add(new GraphNode(i + 1));
        }
        for (int i = 0; i < adj.size(); i++) {
            for (Integer nb : adj.get(i)) {
                if (nb != null && nb >= 1 && nb <= nodes.size()) {
                    nodes.get(i).neighbors.add(nodes.get(nb - 1));
                }
            }
        }
        return nodes.get(0);
    }

    public static List<List<Integer>> toAdjList(GraphNode start) {
        List<List<Integer>> res = new ArrayList<>();
        if (start == null) return res;
        Map<Integer, GraphNode> seen = new HashMap<>();
        Queue<GraphNode> q = new LinkedList<>();
        seen.put(start.val, start);
        q.add(start);
        int maxVal = start.val;
        while (!q.isEmpty()) {
            GraphNode curr = q.poll();
            maxVal = Math.max(maxVal, curr.val);
            for (GraphNode nb : curr.neighbors) {
                if (!seen.containsKey(nb.val)) {
                    seen.put(nb.val, nb);
                    q.add(nb);
                }
            }
        }
        for (int i = 1; i <= maxVal; i++) {
            List<Integer> row = new ArrayList<>();
            GraphNode n = seen.get(i);
            if (n != null) {
                for (GraphNode nb : n.neighbors) {
                    row.add(nb.val);
                }
                Collections.sort(row);
            }
            res.add(row);
        }
        return res;
    }
}
