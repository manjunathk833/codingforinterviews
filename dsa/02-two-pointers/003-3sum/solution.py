from typing import List


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.threeSum([-1, 0, 1, 2, -1, -4])
    assert len(res1) == 2, f"Test 1 Failed: {res1}"

    res2 = sol.threeSum([0, 1, 1])
    assert res2 == [], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
