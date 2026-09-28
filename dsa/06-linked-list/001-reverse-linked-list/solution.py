from typing import Optional
from utils.dsa_helpers import ListNode


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """Reverses a singly linked list in O(N) time and O(1) space."""
        prev = None
        curr = head

        while curr:
            next_temp = curr.next
            curr.next = prev
            prev = curr
            curr = next_temp

        return prev


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    head1 = ListNode.from_list([1, 2, 3, 4, 5])
    rev1 = sol.reverseList(head1)
    assert rev1.to_list() == [5, 4, 3, 2, 1], f"Test 1 Failed: {rev1}"

    # Test 2
    head2 = ListNode.from_list([1, 2])
    rev2 = sol.reverseList(head2)
    assert rev2.to_list() == [2, 1], f"Test 2 Failed: {rev2}"

    # Test 3: empty
    assert sol.reverseList(None) is None, "Test 3 Failed"

    print("All 3 Python test cases passed!")
