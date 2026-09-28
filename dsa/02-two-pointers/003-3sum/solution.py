from typing import List


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        """Finds all unique triplets that sum to 0 in O(N^2) time."""
        nums.sort()
        res = []

        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]:
                continue

            left, right = i + 1, len(nums) - 1
            while left < right:
                three_sum = nums[i] + nums[left] + nums[right]
                if three_sum == 0:
                    res.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1
                    while left < right and nums[right] == nums[right + 1]:
                        right -= 1
                elif three_sum < 0:
                    left += 1
                else:
                    right -= 1

        return res


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.threeSum([-1, 0, 1, 2, -1, -4])
    assert len(res1) == 2, f"Test 1 Failed: {res1}"

    res2 = sol.threeSum([0, 1, 1])
    assert res2 == [], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
