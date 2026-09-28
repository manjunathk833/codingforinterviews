public class Solution {

    public int search(int[] nums, int target) {
        // TODO: Implement your solution here
        return -1;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        assert sol.search(new int[] { -1, 0, 3, 5, 9, 12 }, 9) == 4 : "Test 1 Failed";
        assert sol.search(new int[] { -1, 0, 3, 5, 9, 12 }, 2) == -1 : "Test 2 Failed";
        assert sol.search(new int[] { 5 }, 5) == 0 : "Test 3 Failed";

        System.out.println("All 3 Java test cases passed!");
    }
}
