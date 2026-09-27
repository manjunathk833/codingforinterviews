"""Problem: Valid Anagram (LeetCode #242)
Pattern: Arrays & Hashing
Difficulty: Easy
"""


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        """Checks if string t is an anagram of string s.

        Time Complexity: O(N)
        Space Complexity: O(1) (26-character alphabet)
        """
        if len(s) != len(t):
            return False

        count = [0] * 26
        for char_s, char_t in zip(s, t):
            count[ord(char_s) - ord('a')] += 1
            count[ord(char_t) - ord('a')] -= 1

        return all(c == 0 for c in count)


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    assert sol.isAnagram("anagram", "nagaram") is True, "Test 1 Failed"

    # Test 2
    assert sol.isAnagram("rat", "car") is False, "Test 2 Failed"

    # Test 3
    assert sol.isAnagram("a", "ab") is False, "Test 3 Failed"

    # Test 4
    assert sol.isAnagram("z", "z") is True, "Test 4 Failed"

    print("All 4 Python test cases passed!")
