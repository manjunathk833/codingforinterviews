public class Solution {

    public int numIslands(char[][] grid) {
        // TODO: Implement your solution here
        return 0;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        char[][] grid1 = {
            { '1', '1', '1', '1', '0' },
            { '1', '1', '0', '1', '0' },
            { '1', '1', '0', '0', '0' },
            { '0', '0', '0', '0', '0' }
        };
        assert sol.numIslands(grid1) == 1 : "Test 1 Failed";

        char[][] grid2 = {
            { '1', '1', '0', '0', '0' },
            { '1', '1', '0', '0', '0' },
            { '0', '0', '1', '0', '0' },
            { '0', '0', '0', '1', '1' }
        };
        assert sol.numIslands(grid2) == 3 : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
