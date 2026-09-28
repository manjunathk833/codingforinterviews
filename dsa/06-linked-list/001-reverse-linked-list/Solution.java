import java.util.Arrays;
import utils.ListNode;

public class Solution {

    public ListNode reverseList(ListNode head) {
        // TODO: Implement your solution here
        return null;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: [1,2,3,4,5] -> [5,4,3,2,1]
        ListNode head1 = ListNode.fromArray(new int[] { 1, 2, 3, 4, 5 });
        ListNode rev1 = sol.reverseList(head1);
        assert Arrays.equals(ListNode.toArray(rev1), new int[] { 5, 4, 3, 2, 1 }) : "Test 1 Failed";

        // Test 2: [1,2] -> [2,1]
        ListNode head2 = ListNode.fromArray(new int[] { 1, 2 });
        ListNode rev2 = sol.reverseList(head2);
        assert Arrays.equals(ListNode.toArray(rev2), new int[] { 2, 1 }) : "Test 2 Failed";

        // Test 3: empty
        assert sol.reverseList(null) == null : "Test 3 Failed";

        System.out.println("All 3 Java test cases passed!");
    }
}
