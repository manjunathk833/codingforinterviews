"""Problem: Group Anagrams (LeetCode #49)
Pattern: Arrays & Hashing
Difficulty: Medium

Time Complexity: O(M * N) where M is the number of strings and N is the max string length.
Space Complexity: O(M * N) to store the grouped anagram lists and hash table keys.
"""
from collections import defaultdict
from typing import List


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        """Groups anagrams together from the input list of strings.

        Uses a 26-element character count tuple as the dictionary key to achieve
        O(M * N) linear time complexity without sorting overhead.
        """
        if not strs:
            return []

        anagram_map = defaultdict(list)

        for s in strs:
            count = [0] * 26
            for char in s:
                count[ord(char) - ord("a")] += 1
            # Tuple of counts is hashable and serves as the dictionary key
            anagram_map[tuple(count)].append(s)

        return list(anagram_map.values())


if __name__ == "__main__":
    sol = Solution()

    # Test 1: Multiple anagram groups
    res1 = sol.groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert len(res1) == 3, f"Test 1 Failed: Expected 3 groups, got {len(res1)}"

    # Test 2: Empty string
    res2 = sol.groupAnagrams([""])
    assert res2 == [[""]], f"Test 2 Failed: Expected [['']], got {res2}"

    # Test 3: Single char
    res3 = sol.groupAnagrams(["a"])
    assert res3 == [["a"]], f"Test 3 Failed: Expected [['a']], got {res3}"

    # Test 4: All strings are anagrams of each other
    res4 = sol.groupAnagrams(["abc", "bca", "cab", "cba"])
    assert len(res4) == 1 and len(res4[0]) == 4, f"Test 4 Failed: Expected 1 group of 4 items, got {res4}"

    # Test 5: No anagrams present
    res5 = sol.groupAnagrams(["a", "b", "c"])
    assert len(res5) == 3, f"Test 5 Failed: Expected 3 groups, got {len(res5)}"

    # Test 6: Empty input array
    res6 = sol.groupAnagrams([])
    assert res6 == [], f"Test 6 Failed: Expected [], got {res6}"

    print("All 6 Python test cases passed!")
