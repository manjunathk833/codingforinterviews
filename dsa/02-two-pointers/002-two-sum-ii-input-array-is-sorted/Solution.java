import java.util.Arrays;

public class Solution {

    public int[] twoSum(int[] numbers, int target) {
        int left = 0, right = numbers.length - 1;

        while (left < right) {
            int sum = numbers[left] + numbers[right];
            if (sum == target) {
                return new int[] { left + 1, right + 1 };
            } else if (sum < target) {
                left++;
            } else {
                right--;
            }
        }
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
