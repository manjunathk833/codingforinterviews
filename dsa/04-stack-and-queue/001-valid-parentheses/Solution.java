import java.util.Stack;

public class Solution {

    public boolean isValid(String s) {
        Stack<Character> stack = new Stack<>();
        for (char c : s.toCharArray()) {
            if (c == '(') stack.push(')');
            else if (c == '{') stack.push('}');
            else if (c == '[') stack.push(']');
            else if (stack.isEmpty() || stack.pop() != c) return false;
        }
        return stack.isEmpty();
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
