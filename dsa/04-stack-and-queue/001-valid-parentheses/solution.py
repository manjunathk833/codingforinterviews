class Solution:
    def isValid(self, s: str) -> bool:
        """Determines if string has valid matching parentheses."""
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}

        for char in s:
            if char in mapping:
                top = stack.pop() if stack else "#"
                if mapping[char] != top:
                    return False
            else:
                stack.append(char)

        return not stack


if __name__ == "__main__":
    sol = Solution()

    assert sol.isValid("()") is True, "Test 1 Failed"
    assert sol.isValid("()[]{}") is True, "Test 2 Failed"
    assert sol.isValid("(]") is False, "Test 3 Failed"
    assert sol.isValid("([)]") is False, "Test 4 Failed"
    assert sol.isValid("{[]}") is True, "Test 5 Failed"

    print("All 5 Python test cases passed!")
