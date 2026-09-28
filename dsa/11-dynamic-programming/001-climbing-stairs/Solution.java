public class Solution {

    public int climbStairs(int n) {
        if (n <= 2) return n;
        int one = 1, two = 2;
        for (int i = 3; i <= n; i++) {
            int temp = one + two;
            one = two;
            two = temp;
        }
        return two;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        assert sol.climbStairs(2) == 2 : "Test 1 Failed";
        assert sol.climbStairs(3) == 3 : "Test 2 Failed";
        assert sol.climbStairs(5) == 8 : "Test 3 Failed";

        System.out.println("All 3 Java test cases passed!");
    }
}
