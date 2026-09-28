public class Solution {

    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) return 0;

        int islands = 0;
        int m = grid.length, n = grid[0].length;

        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (grid[r][c] == '1') {
                    islands++;
                    dfs(grid, r, c, m, n);
                }
            }
        }
        return islands;
    }

    private void dfs(char[][] grid, int r, int c, int m, int n) {
        if (r < 0 || r >= m || c < 0 || c >= n || grid[r][c] != '1') {
            return;
        }
        grid[r][c] = '0'; // mark visited
        dfs(grid, r + 1, c, m, n);
        dfs(grid, r - 1, c, m, n);
        dfs(grid, r, c + 1, m, n);
        dfs(grid, r, c - 1, m, n);
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
