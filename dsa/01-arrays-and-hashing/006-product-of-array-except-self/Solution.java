import java.util.Arrays;

public class Solution {

    public int[] productExceptSelf(int[] nums) {
        // TODO: Implement your solution here
        return new int[] {};
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        int[] res1 = sol.productExceptSelf(new int[] { 1, 2, 3, 4 });
        assert Arrays.equals(res1, new int[] { 24, 12, 8, 6 }) : "Test 1 Failed";

        int[] res2 = sol.productExceptSelf(new int[] { -1, 1, 0, -3, 3 });
        assert Arrays.equals(res2, new int[] { 0, 0, 9, 0, 0 }) : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
