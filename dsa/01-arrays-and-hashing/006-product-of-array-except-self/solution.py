from typing import List


class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.productExceptSelf([1, 2, 3, 4])
    assert res1 == [24, 12, 8, 6], f"Test 1 Failed: {res1}"

    res2 = sol.productExceptSelf([-1, 1, 0, -3, 3])
    assert res2 == [0, 0, 9, 0, 0], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
