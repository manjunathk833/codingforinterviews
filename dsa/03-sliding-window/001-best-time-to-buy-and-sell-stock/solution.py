"""Problem: Best Time to Buy and Sell Stock (LeetCode #121)
Pattern: Sliding Window / Two Pointers
Difficulty: Easy
"""
from typing import List


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """Calculates max profit using one-pass sliding minimum.

        Time Complexity: O(N)
        Space Complexity: O(1)
        """
        min_price = float("inf")
        max_profit = 0

        for price in prices:
            if price < min_price:
                min_price = price
            elif price - min_price > max_profit:
                max_profit = price - min_price

        return max_profit


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    assert sol.maxProfit([7, 1, 5, 3, 6, 4]) == 5, "Test 1 Failed"

    # Test 2
    assert sol.maxProfit([7, 6, 4, 3, 1]) == 0, "Test 2 Failed"

    # Test 3
    assert sol.maxProfit([2, 2, 2, 2]) == 0, "Test 3 Failed"

    # Test 4
    assert sol.maxProfit([5]) == 0, "Test 4 Failed"

    print("All 4 Python test cases passed!")
