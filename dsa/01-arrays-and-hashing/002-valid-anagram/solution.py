"""Problem: Valid Anagram (LeetCode #242)
Pattern: Arrays & Hashing
Difficulty: Easy
"""


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        count = [0] * 26

        if len(s) != len(t):
            return False
        for i in range(len(s)):
            count[ord(s[i]) - ord('a')] +=1
            count[ord(t[i]) - ord('a')] -=1
        for i in range(len(count)):
            if count[i] != 0:
                return False
        return True


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
