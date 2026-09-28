import java.util.Stack;

public class Solution {

    public boolean isValid(String s) {
        // TODO: Implement your solution here
        return false;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        assert sol.isValid("()") : "Test 1 Failed";
        assert sol.isValid("()[]{}") : "Test 2 Failed";
        assert !sol.isValid("(]") : "Test 3 Failed";
        assert !sol.isValid("([)]") : "Test 4 Failed";
        assert sol.isValid("{[]}") : "Test 5 Failed";

        System.out.println("All 5 Java test cases passed!");
    }
}
