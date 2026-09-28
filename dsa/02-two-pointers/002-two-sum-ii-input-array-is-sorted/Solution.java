import java.util.Arrays;

public class Solution {

    public int[] twoSum(int[] numbers, int target) {
        // TODO: Implement your solution here
        return new int[] {};
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        int[] res1 = sol.twoSum(new int[] { 2, 7, 11, 15 }, 9);
        assert Arrays.equals(res1, new int[] { 1, 2 }) : "Test 1 Failed";

        int[] res2 = sol.twoSum(new int[] { 2, 3, 4 }, 6);
        assert Arrays.equals(res2, new int[] { 1, 3 }) : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
