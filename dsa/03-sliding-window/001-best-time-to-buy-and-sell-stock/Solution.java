/**
 * Problem: Best Time to Buy and Sell Stock (LeetCode #121)
 * Pattern: Sliding Window / Two Pointers
 * Difficulty: Easy
 */
public class Solution {

    /**
     * Calculates the maximum profit achievable from a single buy and sell.
     *
     * @param prices Array of daily stock prices
     * @return Maximum profit, or 0 if none
     */
    public int maxProfit(int[] prices) {
        // TODO: Implement your solution here
        int minPrice = Integer.MAX_VALUE;
        int maxProfit = 0;

        for (int price : prices) {
            if (price < minPrice) {
                minPrice = price;
            } else if (price - minPrice > maxProfit) {
                maxProfit = price - minPrice;
            }
        }

        return maxProfit;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: Standard case
        assert sol.maxProfit(new int[] { 7, 1, 5, 3, 6, 4 }) == 5 : "Test 1 Failed: Expected 5";

        // Test 2: Descending prices (no profit)
        assert sol.maxProfit(new int[] { 7, 6, 4, 3, 1 }) == 0 : "Test 2 Failed: Expected 0";

        // Test 3: Flat prices
        assert sol.maxProfit(new int[] { 2, 2, 2, 2 }) == 0 : "Test 3 Failed: Expected 0";

        // Test 4: Single element
        assert sol.maxProfit(new int[] { 5 }) == 0 : "Test 4 Failed: Expected 0";

        System.out.println("All 4 Java test cases passed!");
    }
}
