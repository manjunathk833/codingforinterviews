from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        """Counts number of connected islands using DFS flood fill."""
        if not grid:
            return 0

        m, n = len(grid), len(grid[0])
        islands = 0

        def dfs(r, c):
            if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] != "1":
                return
            grid[r][c] = "0"
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        for r in range(m):
            for c in range(n):
                if grid[r][c] == "1":
                    islands += 1
                    dfs(r, c)

        return islands


if __name__ == "__main__":
    sol = Solution()

    grid1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    assert sol.numIslands(grid1) == 1, "Test 1 Failed"

    grid2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    assert sol.numIslands(grid2) == 3, "Test 2 Failed"

    print("All 2 Python test cases passed!")
