from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    res1 = sorted(sol.topKFrequent([1, 1, 1, 2, 2, 3], 2))
    assert res1 == [1, 2], f"Test 1 Failed: {res1}"

    res2 = sol.topKFrequent([1], 1)
    assert res2 == [1], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
