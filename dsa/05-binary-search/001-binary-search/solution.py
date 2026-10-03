from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> int:
        # TODO: Implement your solution here
        return -1


if __name__ == "__main__":
    sol = Solution()

    assert sol.search([-1, 0, 3, 5, 9, 12], 9) == 4, "Test 1 Failed"
    assert sol.search([-1, 0, 3, 5, 9, 12], 2) == -1, "Test 2 Failed"
    assert sol.search([5], 5) == 0, "Test 3 Failed"

    print("All 3 Python test cases passed!")
