from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        # TODO: Implement your solution here
        return 0


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
