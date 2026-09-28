import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Solution {

    public int[][] merge(int[][] intervals) {
        if (intervals.length <= 1) return intervals;

        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> merged = new ArrayList<>();

        int[] current = intervals[0];
        merged.add(current);

        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] <= current[1]) {
                current[1] = Math.max(current[1], intervals[i][1]);
            } else {
                current = intervals[i];
                merged.add(current);
            }
        }

        return merged.toArray(new int[merged.size()][]);
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
