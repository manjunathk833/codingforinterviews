from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        """Finds top k frequent elements in O(N) time using bucket sort."""
        count = Counter(nums)
        bucket = [[] for _ in range(len(nums) + 1)]

        for num, freq in count.items():
            bucket[freq].append(num)

        res = []
        for i in range(len(bucket) - 1, 0, -1):
            for num in bucket[i]:
                res.append(num)
                if len(res) == k:
                    return res
        return res


if __name__ == "__main__":
    sol = Solution()

    res1 = sorted(sol.topKFrequent([1, 1, 1, 2, 2, 3], 2))
    assert res1 == [1, 2], f"Test 1 Failed: {res1}"

    res2 = sol.topKFrequent([1], 1)
    assert res2 == [1], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
