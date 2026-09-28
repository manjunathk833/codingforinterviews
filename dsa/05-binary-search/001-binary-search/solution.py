from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> int:
        """Searches target in sorted nums with O(log N) time."""
        left, right = 0, len(nums) - 1

        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return -1


if __name__ == "__main__":
    sol = Solution()

    assert sol.search([-1, 0, 3, 5, 9, 12], 9) == 4, "Test 1 Failed"
    assert sol.search([-1, 0, 3, 5, 9, 12], 2) == -1, "Test 2 Failed"
    assert sol.search([5], 5) == 0, "Test 3 Failed"

    print("All 3 Python test cases passed!")
