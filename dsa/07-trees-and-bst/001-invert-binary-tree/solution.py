from typing import Optional
from utils.dsa_helpers import TreeNode


class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        # TODO: Implement your solution here
        return None


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    root1 = TreeNode.from_list([4, 2, 7, 1, 3, 6, 9])
    inv1 = sol.invertTree(root1)
    assert inv1.to_list() == [4, 7, 2, 9, 6, 3, 1], f"Test 1 Failed: {inv1.to_list()}"

    # Test 2
    root2 = TreeNode.from_list([2, 1, 3])
    inv2 = sol.invertTree(root2)
    assert inv2.to_list() == [2, 3, 1], f"Test 2 Failed: {inv2.to_list()}"

    # Test 3
    assert sol.invertTree(None) is None, "Test 3 Failed"

    print("All 3 Python test cases passed!")
