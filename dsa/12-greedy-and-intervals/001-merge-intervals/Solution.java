import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Solution {

    public int[][] merge(int[][] intervals) {
        // TODO: Implement your solution here
        return new int[][] {};
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        int[][] intervals1 = { { 1, 3 }, { 2, 6 }, { 8, 10 }, { 15, 18 } };
        int[][] res1 = sol.merge(intervals1);
        int[][] exp1 = { { 1, 6 }, { 8, 10 }, { 15, 18 } };
        assert Arrays.deepEquals(res1, exp1) : "Test 1 Failed";

        int[][] intervals2 = { { 1, 4 }, { 4, 5 } };
        int[][] res2 = sol.merge(intervals2);
        int[][] exp2 = { { 1, 5 } };
        assert Arrays.deepEquals(res2, exp2) : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
