"""Problem: Two Sum (LeetCode #1)
Pattern: Arrays & Hashing
Difficulty: Easy
"""
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """Find indices of the two numbers such that they add up to target.

        Time Complexity: O(N)
        Space Complexity: O(N)
        """
        prev_map = {}  # val -> index

        for i, n in enumerate(nums):
            diff = target - n
            if diff in prev_map:
                return [prev_map[diff], i]
            prev_map[n] = i

        return []


if __name__ == "__main__":
    sol = Solution()

    # Test Case 1
    res1 = sorted(sol.twoSum([2, 7, 11, 15], 9))
    assert res1 == [0, 1], f"Test 1 Failed: Expected [0, 1], got {res1}"

    # Test Case 2
    res2 = sorted(sol.twoSum([3, 2, 4], 6))
    assert res2 == [1, 2], f"Test 2 Failed: Expected [1, 2], got {res2}"

    # Test Case 3
    res3 = sorted(sol.twoSum([3, 3], 6))
    assert res3 == [0, 1], f"Test 3 Failed: Expected [0, 1], got {res3}"

    # Test Case 4: Negative numbers
    res4 = sorted(sol.twoSum([-1, -2, -3, -4, -5], -8))
    assert res4 == [2, 4], f"Test 4 Failed: Expected [2, 4], got {res4}"

    print("All 4 Python test cases passed!")
