from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        """Merges overlapping intervals in O(N log N) time."""
        if not intervals:
            return []

        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]

        for start, end in intervals[1:]:
            prev_start, prev_end = merged[-1]
            if start <= prev_end:
                merged[-1][1] = max(prev_end, end)
            else:
                merged.append([start, end])

        return merged


if __name__ == "__main__":
    sol = Solution()

    res1 = sol.merge([[1, 3], [2, 6], [8, 10], [15, 18]])
    assert res1 == [[1, 6], [8, 10], [15, 18]], f"Test 1 Failed: {res1}"

    res2 = sol.merge([[1, 4], [4, 5]])
    assert res2 == [[1, 5]], f"Test 2 Failed: {res2}"

    print("All 2 Python test cases passed!")
