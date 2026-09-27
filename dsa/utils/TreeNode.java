package utils;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

public class TreeNode {
    public int val;
    public TreeNode left;
    public TreeNode right;

    public TreeNode() {}

    public TreeNode(int val) {
        this.val = val;
    }

    public TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }

    public static TreeNode fromLevelOrder(Integer[] values) {
        if (values == null || values.length == 0 || values[0] == null) return null;
        TreeNode root = new TreeNode(values[0]);
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        int i = 1;
        while (!queue.isEmpty() && i < values.length) {
            TreeNode curr = queue.poll();
            if (i < values.length && values[i] != null) {
                curr.left = new TreeNode(values[i]);
                queue.add(curr.left);
            }
            i++;
            if (i < values.length && values[i] != null) {
                curr.right = new TreeNode(values[i]);
                queue.add(curr.right);
            }
            i++;
        }
        return root;
    }

    public static List<Integer> toLevelOrder(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            TreeNode curr = queue.poll();
            if (curr != null) {
                result.add(curr.val);
                queue.add(curr.left);
                queue.add(curr.right);
            } else {
                result.add(null);
            }
        }
        // Trim trailing nulls
        int last = result.size() - 1;
        while (last >= 0 && result.get(last) == null) {
            result.remove(last);
            last--;
        }
        return result;
    }
}
