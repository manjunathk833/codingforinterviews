from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.merge([[1, 3], [2, 6], [8, 10], [15, 18]])
    assert res1 == [[1, 6], [8, 10], [15, 18]], f"Test 1 Failed: {res1}"

    res2 = sol.merge([[1, 4], [4, 5]])
    assert res2 == [[1, 5]], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
