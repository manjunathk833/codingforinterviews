import java.util.*;

public class Solution {

    public List<List<Integer>> threeSum(int[] nums) {
        // TODO: Implement your solution here
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        List<List<Integer>> res1 = sol.threeSum(new int[] { -1, 0, 1, 2, -1, -4 });
        assert res1.size() == 2 : "Test 1 Failed: Expected 2 triplets, got " + res1.size();

        List<List<Integer>> res2 = sol.threeSum(new int[] { 0, 1, 1 });
        assert res2.isEmpty() : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
