from typing import List


class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        """Calculates product of array except self in O(N) time and O(1) extra space."""
        n = len(nums)
        res = [1] * n

        prefix = 1
        for i in range(n):
            res[i] = prefix
            prefix *= nums[i]

        postfix = 1
        for i in range(n - 1, -1, -1):
            res[i] *= postfix
            postfix *= nums[i]

        return res


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.productExceptSelf([1, 2, 3, 4])
    assert res1 == [24, 12, 8, 6], f"Test 1 Failed: {res1}"

    res2 = sol.productExceptSelf([-1, 1, 0, -3, 3])
    assert res2 == [0, 0, 9, 0, 0], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
