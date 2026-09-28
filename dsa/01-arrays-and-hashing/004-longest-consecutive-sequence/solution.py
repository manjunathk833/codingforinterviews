"""Problem: Longest Consecutive Sequence (LeetCode #128)
Pattern: Arrays & Hashing
Difficulty: Medium
"""
from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        """Finds length of longest consecutive elements sequence in O(N) time."""
        num_set = set(nums)
        longest = 0

        for num in num_set:
            # Only start counting if num is the beginning of a sequence
            if num - 1 not in num_set:
                current_num = num
                streak = 1
                while current_num + 1 in num_set:
                    current_num += 1
                    streak += 1
                longest = max(longest, streak)

        return longest


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    assert sol.longestConsecutive([100, 4, 200, 1, 3, 2]) == 4, "Test 1 Failed"

    # Test 2
    assert sol.longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9, "Test 2 Failed"

    # Test 3: Empty list
    assert sol.longestConsecutive([]) == 0, "Test 3 Failed"

    # Test 4: Single element
    assert sol.longestConsecutive([10]) == 1, "Test 4 Failed"

    print("All 4 Python test cases passed!")
