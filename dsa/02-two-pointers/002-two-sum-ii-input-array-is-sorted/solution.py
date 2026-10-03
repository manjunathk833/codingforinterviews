from typing import List


class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.twoSum([2, 7, 11, 15], 9)
    assert res1 == [1, 2], f"Test 1 Failed: {res1}"

    res2 = sol.twoSum([2, 3, 4], 6)
    assert res2 == [1, 3], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
