class Solution:
    def climbStairs(self, n: int) -> int:
        # TODO: Implement your solution here
        return 0


if __name__ == "__main__":
    sol = Solution()

    assert sol.climbStairs(2) == 2, "Test 1 Failed"
    assert sol.climbStairs(3) == 3, "Test 2 Failed"
    assert sol.climbStairs(5) == 8, "Test 3 Failed"

    print("All 3 Python test cases passed!")
