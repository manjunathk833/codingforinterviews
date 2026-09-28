class Solution:
    def climbStairs(self, n: int) -> int:
        """Calculates distinct ways to climb stairs in O(N) time and O(1) space."""
        if n <= 2:
            return n

        one, two = 1, 2
        for _ in range(3, n + 1):
            one, two = two, one + two

        return two


if __name__ == "__main__":
    sol = Solution()

    assert sol.climbStairs(2) == 2, "Test 1 Failed"
    assert sol.climbStairs(3) == 3, "Test 2 Failed"
    assert sol.climbStairs(5) == 8, "Test 3 Failed"

    print("All 3 Python test cases passed!")
