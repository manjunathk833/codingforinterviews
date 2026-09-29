import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Problem: Two Sum (LeetCode #1)
 * Pattern: Arrays & Hashing
 * Difficulty: Easy
 */
public class Solution {

    /**
     * Finds indices of the two numbers such that they add up to target.
     *
     * @param nums   Array of integers
     * @param target Target sum
     * @return Indices [i, j]
     */
    public int[] twoSum(int[] nums, int target) {
        // TODO: Implement your solution here
        if (nums == null || nums.length < 2) 
            throw new IllegalArgumentException("invalid input");
        Map<Integer, Integer> complement= new HashMap<>();
        for(int i = 0; i < nums.length ; i++){
            if (complement.containsKey(target - nums[i])){
                return new int[] {(complement.get(target-nums[i])), i};
            }
            else {
                complement.put(nums[i], i);
            }
        }
        throw new IllegalArgumentException("no two sum solution found for given imput");
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test Case 1
        int[] res1 = sol.twoSum(new int[] { 2, 7, 11, 15 }, 9);
        Arrays.sort(res1);
        assert Arrays.equals(res1, new int[] { 0, 1 }) : "Test 1 Failed: Expected [0, 1], got " + Arrays.toString(res1);

        // Test Case 2
        int[] res2 = sol.twoSum(new int[] { 3, 2, 4 }, 6);
        Arrays.sort(res2);
        assert Arrays.equals(res2, new int[] { 1, 2 }) : "Test 2 Failed: Expected [1, 2], got " + Arrays.toString(res2);

        // Test Case 3
        int[] res3 = sol.twoSum(new int[] { 3, 3 }, 6);
        Arrays.sort(res3);
        assert Arrays.equals(res3, new int[] { 0, 1 }) : "Test 3 Failed: Expected [0, 1], got " + Arrays.toString(res3);

        // Test Case 4: Negative numbers
        int[] res4 = sol.twoSum(new int[] { -1, -2, -3, -4, -5 }, -8);
        Arrays.sort(res4);
        assert Arrays.equals(res4, new int[] { 2, 4 }) : "Test 4 Failed: Expected [2, 4], got " + Arrays.toString(res4);

        System.out.println("All 4 Java test cases passed!");
    }
}
