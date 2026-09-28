"""Problem: Group Anagrams (LeetCode #49)
Pattern: Arrays & Hashing
Difficulty: Medium
"""
from collections import defaultdict
from typing import List


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        # TODO: Implement your solution here
        return []


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    res1 = sol.groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert len(res1) == 3, f"Test 1 Failed: Expected 3 groups, got {len(res1)}"

    # Test 2
    res2 = sol.groupAnagrams([""])
    assert res2 == [[""]], f"Test 2 Failed: Expected [['']], got {res2}"

    # Test 3
    res3 = sol.groupAnagrams(["a"])
    assert res3 == [["a"]], f"Test 3 Failed: Expected [['a']], got {res3}"

    print("All 3 Python test cases passed!")
