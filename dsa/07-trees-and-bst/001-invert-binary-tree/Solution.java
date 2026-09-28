import java.util.Arrays;
import java.util.List;
import utils.TreeNode;

public class Solution {

    public TreeNode invertTree(TreeNode root) {
        if (root == null) return null;

        TreeNode left = invertTree(root.left);
        TreeNode right = invertTree(root.right);

        root.left = right;
        root.right = left;

        return root;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: [4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1]
        TreeNode root1 = TreeNode.fromLevelOrder(new Integer[] { 4, 2, 7, 1, 3, 6, 9 });
        TreeNode inv1 = sol.invertTree(root1);
        List<Integer> res1 = TreeNode.toLevelOrder(inv1);
        assert res1.equals(Arrays.asList(4, 7, 2, 9, 6, 3, 1)) : "Test 1 Failed: " + res1;

        // Test 2: [2,1,3] -> [2,3,1]
        TreeNode root2 = TreeNode.fromLevelOrder(new Integer[] { 2, 1, 3 });
        TreeNode inv2 = sol.invertTree(root2);
        List<Integer> res2 = TreeNode.toLevelOrder(inv2);
        assert res2.equals(Arrays.asList(2, 3, 1)) : "Test 2 Failed";

        // Test 3: empty
        assert sol.invertTree(null) == null : "Test 3 Failed";

        System.out.println("All 3 Java test cases passed!");
    }
}
