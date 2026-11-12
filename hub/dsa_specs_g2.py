"""DSA Catalog Specs — Group 2: Problems #35 to #66 (Linked List, Trees & BST, Heaps & Priority Queue)."""

SPECS_G2 = [
    {
        "id": 35, "slug": "reverse-linked-list", "method": "reverseList",
        "argTypes": {"head": "ListNode"}, "returnType": "ListNode",
        "pySig": "def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:",
        "javaSig": "public ListNode reverseList(ListNode head)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(1)", "invariant": "nxt = curr.next; curr.next = prev; prev, curr = curr, nxt",
        "prompt": "Given the `head` of a singly linked list, reverse the list in-place and return the new head.",
        "firstLine": "Set `prev, curr = None, head` and loop `while curr:`.",
        "steps": [
            "Initialize `prev = None` and `curr = head`",
            "Save `nxt = curr.next`, flip `curr.next = prev`",
            "Advance `prev = curr` and `curr = nxt`; return `prev`"
        ],
        "cases": [
            {"input": {"head": [1, 2, 3, 4, 5]}, "expected": [5, 4, 3, 2, 1]},
            {"input": {"head": [1, 2]}, "expected": [2, 1]},
            {"input": {"head": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:\n        prev, curr = None, head\n        while curr:\n            nxt = curr.next\n            curr.next = prev\n            prev, curr = curr, nxt\n        return prev\n",
    },
    {
        "id": 36, "slug": "merge-two-sorted-lists", "method": "mergeTwoLists",
        "argTypes": {"list1": "ListNode", "list2": "ListNode"}, "returnType": "ListNode",
        "pySig": "def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:",
        "javaSig": "public ListNode mergeTwoLists(ListNode list1, ListNode list2)", "javaRet": "return null;",
        "time": "O(N + M)", "space": "O(1)", "invariant": "Dummy sentinel node + tail pointer splicing smaller head",
        "prompt": "Merge two sorted linked lists `list1` and `list2` into one sorted linked list and return its head.",
        "firstLine": "Create `dummy = tail = ListNode(0)` so you never need special-case logic for the head.",
        "steps": [
            "Create `dummy = tail = ListNode(0)`",
            "While `list1 and list2`: attach the smaller node to `tail.next` and advance that list + `tail`",
            "Attach remaining `list1 or list2` to `tail.next` and return `dummy.next`"
        ],
        "cases": [
            {"input": {"list1": [1, 2, 4], "list2": [1, 3, 4]}, "expected": [1, 1, 2, 3, 4, 4]},
            {"input": {"list1": [], "list2": [0]}, "expected": [0]},
            {"input": {"list1": [], "list2": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:\n        dummy = tail = ListNode(0)\n        while list1 and list2:\n            if list1.val <= list2.val:\n                tail.next = list1\n                list1 = list1.next\n            else:\n                tail.next = list2\n                list2 = list2.next\n            tail = tail.next\n        tail.next = list1 or list2\n        return dummy.next\n",
    },
    {
        "id": 37, "slug": "linked-list-cycle", "method": "hasCycle", "execMode": "list_cycle",
        "pySig": "def hasCycle(self, head: Optional[ListNode]) -> bool:",
        "javaSig": "public boolean hasCycle(ListNode head)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(1)", "invariant": "Floyd tortoise & hare: fast moves 2 steps, slow moves 1 step",
        "prompt": "Given `head` of a linked list, return `True` if there is a cycle in the linked list using `O(1)` memory.",
        "firstLine": "Set `slow = fast = head` and loop `while fast and fast.next:`.",
        "steps": [
            "Initialize `slow = head` and `fast = head`",
            "While `fast and fast.next`: advance `slow = slow.next` and `fast = fast.next.next`",
            "If `slow is fast`, return `True`; return `False` when loop exits"
        ],
        "cases": [
            {"input": {"values": [3, 2, 0, -4], "pos": 1}, "expected": True},
            {"input": {"values": [1, 2], "pos": 0}, "expected": True},
            {"input": {"values": [1], "pos": -1}, "expected": False},
        ],
        "refPy": "class Solution:\n    def hasCycle(self, head: Optional[ListNode]) -> bool:\n        slow = fast = head\n        while fast and fast.next:\n            slow = slow.next\n            fast = fast.next.next\n            if slow is fast:\n                return True\n        return False\n",
    },
    {
        "id": 38, "slug": "reorder-list", "method": "reorderList",
        "argTypes": {"head": "ListNode"}, "returnType": "InPlaceHead",
        "pySig": "def reorderList(self, head: Optional[ListNode]) -> None:",
        "javaSig": "public void reorderList(ListNode head)", "javaRet": "",
        "time": "O(N)", "space": "O(1)", "invariant": "1) Find mid with slow/fast 2) Reverse second half 3) Zipper-merge halves",
        "prompt": "Reorder `L0 -> L1 -> ... -> Ln` in-place to `L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...`.",
        "firstLine": "Find the midpoint with `slow, fast = head, head.next`.",
        "steps": [
            "Find middle with `slow, fast = head, head.next`, then split `second = slow.next; slow.next = None`",
            "Reverse the `second` list using `prev = None`",
            "Alternately weave nodes from `first = head` and `prev` until `prev` is exhausted"
        ],
        "cases": [
            {"input": {"head": [1, 2, 3, 4]}, "expected": [1, 4, 2, 3]},
            {"input": {"head": [1, 2, 3, 4, 5]}, "expected": [1, 5, 2, 4, 3]},
        ],
        "refPy": "class Solution:\n    def reorderList(self, head: Optional[ListNode]) -> None:\n        if not head or not head.next:\n            return\n        slow, fast = head, head.next\n        while fast and fast.next:\n            slow = slow.next\n            fast = fast.next.next\n        second = slow.next\n        slow.next = None\n        prev = None\n        while second:\n            nxt = second.next\n            second.next = prev\n            prev, second = second, nxt\n        first, sec = head, prev\n        while sec:\n            t1, t2 = first.next, sec.next\n            first.next = sec\n            sec.next = t1\n            first, sec = t1, t2\n",
    },
    {
        "id": 39, "slug": "remove-nth-node-from-end-of-list", "method": "removeNthFromEnd",
        "argTypes": {"head": "ListNode"}, "returnType": "ListNode",
        "pySig": "def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:",
        "javaSig": "public ListNode removeNthFromEnd(ListNode head, int n)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(1)", "invariant": "Keep n-node gap between left (at dummy) and right",
        "prompt": "Given `head` of a linked list, remove the `n`-th node from the end in one pass and return its head.",
        "firstLine": "Create `dummy = ListNode(0, head)`, set `left = dummy`, `right = head`, and advance `right` by `n` steps.",
        "steps": [
            "Create `dummy = ListNode(0, head)`; advance `right` `n` times from `head`",
            "Advance both `left` (starting at `dummy`) and `right` until `right` is `None`",
            "Bypass target node via `left.next = left.next.next` and return `dummy.next`"
        ],
        "cases": [
            {"input": {"head": [1, 2, 3, 4, 5], "n": 2}, "expected": [1, 2, 3, 5]},
            {"input": {"head": [1], "n": 1}, "expected": []},
            {"input": {"head": [1, 2], "n": 1}, "expected": [1]},
        ],
        "refPy": "class Solution:\n    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:\n        dummy = ListNode(0, head)\n        left, right = dummy, head\n        for _ in range(n):\n            right = right.next\n        while right:\n            left = left.next\n            right = right.next\n        left.next = left.next.next\n        return dummy.next\n",
    },
    {
        "id": 40, "slug": "copy-list-with-random-pointer", "method": "copyRandomList",
        "argTypes": {"head": "RandomNode"}, "returnType": "RandomNode",
        "pySig": "def copyRandomList(self, head: Optional[RandomNode]) -> Optional[RandomNode]:",
        "javaSig": "public ListNode copyRandomList(ListNode head)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(N)", "invariant": "old_to_copy = {None: None} two-pass node clone + pointer wiring",
        "prompt": "Construct a deep copy of a linked list where each `RandomNode` has `val`, `next`, and `random` pointers.",
        "firstLine": "Initialize `old_to_copy = {None: None}` and clone every node in a first pass.",
        "steps": [
            "Create `old_to_copy = {None: None}`; loop `curr` to allocate `RandomNode(curr.val)` for every node",
            "Loop `curr` a second time setting `copy.next = old_to_copy[curr.next]` and `copy.random = old_to_copy[curr.random]`",
            "Return `old_to_copy[head]`"
        ],
        "cases": [
            {"input": {"head": [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]}, "expected": [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]},
            {"input": {"head": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def copyRandomList(self, head: Optional[RandomNode]) -> Optional[RandomNode]:\n        mp = {None: None}\n        cur = head\n        while cur:\n            mp[cur] = RandomNode(cur.val)\n            cur = cur.next\n        cur = head\n        while cur:\n            cp = mp[cur]\n            cp.next = mp[cur.next]\n            cp.random = mp[cur.random]\n            cur = cur.next\n        return mp[head]\n",
    },
    {
        "id": 41, "slug": "add-two-numbers", "method": "addTwoNumbers",
        "argTypes": {"l1": "ListNode", "l2": "ListNode"}, "returnType": "ListNode",
        "pySig": "def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:",
        "javaSig": "public ListNode addTwoNumbers(ListNode l1, ListNode l2)", "javaRet": "return null;",
        "time": "O(max(N, M))", "space": "O(max(N, M))", "invariant": "carry, digit = divmod(v1 + v2 + carry, 10)",
        "prompt": "Add two non-negative integers represented as reverse-order digit linked lists `l1` and `l2`.",
        "firstLine": "Create `dummy = curr = ListNode(0)` and `carry = 0`, looping `while l1 or l2 or carry:`.",
        "steps": [
            "Initialize `dummy = curr = ListNode(0)` and `carry = 0`",
            "While `l1 or l2 or carry`, extract `v1` and `v2`, compute `carry, digit = divmod(v1 + v2 + carry, 10)`",
            "Append `ListNode(digit)` to `curr.next`, advance pointers, and return `dummy.next`"
        ],
        "cases": [
            {"input": {"l1": [2, 4, 3], "l2": [5, 6, 4]}, "expected": [7, 0, 8]},
            {"input": {"l1": [9, 9, 9], "l2": [1]}, "expected": [0, 0, 0, 1]},
        ],
        "refPy": "class Solution:\n    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:\n        dummy = curr = ListNode(0)\n        carry = 0\n        while l1 or l2 or carry:\n            v1 = l1.val if l1 else 0\n            v2 = l2.val if l2 else 0\n            carry, d = divmod(v1 + v2 + carry, 10)\n            curr.next = ListNode(d)\n            curr = curr.next\n            l1 = l1.next if l1 else None\n            l2 = l2.next if l2 else None\n        return dummy.next\n",
    },
    {
        "id": 42, "slug": "lru-cache", "method": "get", "execMode": "class_ops", "className": "LRUCache",
        "pySig": "class LRUCache:\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        return -1\n    def put(self, key: int, value: int) -> None:",
        "javaSig": "public int get(int key)", "javaRet": "return -1;",
        "time": "O(1)", "space": "O(capacity)", "invariant": "Hash map + doubly-linked list (or OrderedDict) keeping MRU at tail, LRU at head",
        "prompt": "Design an `LRUCache(capacity)` supporting `O(1)` `get(key)` and `put(key, value)` with Least-Recently-Used eviction.",
        "firstLine": "Store `self.cap = capacity` and `self.cache = OrderedDict()` (or sentinel `left`/`right` doubly linked nodes).",
        "steps": [
            "Initialize `self.cap = capacity` and `self.cache = OrderedDict()`",
            "In `get(key)`: if absent return `-1`; else call `self.cache.move_to_end(key)` and return value",
            "In `put(key, val)`: update & `move_to_end(key)`; if `len > cap`, evict `self.cache.popitem(last=False)`"
        ],
        "cases": [
            {
                "input": {"ops": ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"], "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]},
                "expected": [None, None, None, 1, None, -1, None, -1, 3, 4],
            }
        ],
        "refPy": "class LRUCache:\n    def __init__(self, capacity: int):\n        self.cap = capacity\n        self.cache = OrderedDict()\n    def get(self, key: int) -> int:\n        if key not in self.cache:\n            return -1\n        self.cache.move_to_end(key)\n        return self.cache[key]\n    def put(self, key: int, value: int) -> None:\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.cap:\n            self.cache.popitem(last=False)\n",
    },
    {
        "id": 43, "slug": "merge-k-sorted-lists", "method": "mergeKLists",
        "argTypes": {"lists": "ListOfListNode"}, "returnType": "ListNode",
        "pySig": "def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:",
        "javaSig": "public ListNode mergeKLists(ListNode[] lists)", "javaRet": "return null;",
        "time": "O(N log K)", "space": "O(K)", "invariant": "Min-heap of size <= K storing (node.val, tie_breaker, node)",
        "prompt": "Given an array of `k` sorted linked lists, merge all of them into one sorted linked list in `O(N log K)` time.",
        "firstLine": "Create `heap = []` and push `(node.val, idx, node)` for each non-empty list head.",
        "steps": [
            "Push `(node.val, i, node)` into min-heap `heap` for each non-null head",
            "Create `dummy = tail = ListNode(0)`",
            "While `heap`: pop smallest node, attach to `tail.next`, and if `node.next`, push `(node.next.val, i, node.next)`"
        ],
        "cases": [
            {"input": {"lists": [[1, 4, 5], [1, 3, 4], [2, 6]]}, "expected": [1, 1, 2, 3, 4, 4, 5, 6]},
            {"input": {"lists": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:\n        heap = []\n        for i, node in enumerate(lists):\n            if node:\n                heapq.heappush(heap, (node.val, i, node))\n        dummy = tail = ListNode(0)\n        while heap:\n            _, i, node = heapq.heappop(heap)\n            tail.next = node\n            tail = tail.next\n            if node.next:\n                heapq.heappush(heap, (node.next.val, i, node.next))\n        return dummy.next\n",
    },
    {
        "id": 44, "slug": "reverse-nodes-in-k-group", "method": "reverseKGroup",
        "argTypes": {"head": "ListNode"}, "returnType": "ListNode",
        "pySig": "def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:",
        "javaSig": "public ListNode reverseKGroup(ListNode head, int k)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(1)", "invariant": "Check kth node exists -> reverse k nodes -> stitch groupPrev",
        "prompt": "Given `head` of a linked list, reverse nodes `k` at a time and leave remaining `< k` tail nodes as-is (`def reverseKGroup`).",
        "firstLine": "Create `dummy = ListNode(0, head)` and `group_prev = dummy`.",
        "steps": [
            "Walk `k` steps from `group_prev` to find `kth`; if `None`, break",
            "Reverse nodes from `group_prev.next` up to `kth.next` (`group_next`)",
            "Reconnect `group_prev.next = kth` and advance `group_prev` to the old group head"
        ],
        "cases": [
            {"input": {"head": [1, 2, 3, 4, 5], "k": 2}, "expected": [2, 1, 4, 3, 5]},
            {"input": {"head": [1, 2, 3, 4, 5], "k": 3}, "expected": [3, 2, 1, 4, 5]},
        ],
        "refPy": "class Solution:\n    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:\n        dummy = ListNode(0, head)\n        gp = dummy\n        while True:\n            kth = gp\n            for _ in range(k):\n                kth = kth.next\n                if not kth:\n                    return dummy.next\n            gn = kth.next\n            prev, curr = gn, gp.next\n            while curr is not gn:\n                nxt = curr.next\n                curr.next = prev\n                prev, curr = curr, nxt\n            tmp = gp.next\n            gp.next = kth\n            gp = tmp\n",
    },
    {
        "id": 45, "slug": "invert-binary-tree", "method": "invertTree",
        "argTypes": {"root": "TreeNode"}, "returnType": "TreeNode",
        "pySig": "def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:",
        "javaSig": "public TreeNode invertTree(TreeNode root)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(H)", "invariant": "root.left, root.right = invert(root.right), invert(root.left)",
        "prompt": "Given the `root` of a binary tree, invert (mirror) the tree and return its root.",
        "firstLine": "Guard `if not root: return None`, then swap `root.left, root.right` recursively.",
        "steps": [
            "Base case: `if not root: return None`",
            "Swap `root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)`",
            "Return `root`"
        ],
        "cases": [
            {"input": {"root": [4, 2, 7, 1, 3, 6, 9]}, "expected": [4, 7, 2, 9, 6, 3, 1]},
            {"input": {"root": [2, 1, 3]}, "expected": [2, 3, 1]},
            {"input": {"root": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:\n        if not root:\n            return None\n        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)\n        return root\n",
    },
    {
        "id": 46, "slug": "maximum-depth-of-binary-tree", "method": "maxDepth",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def maxDepth(self, root: Optional[TreeNode]) -> int:",
        "javaSig": "public int maxDepth(TreeNode root)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(H)", "invariant": "depth(node) = 1 + max(depth(left), depth(right))",
        "prompt": "Given `root` of a binary tree, return its maximum depth (number of nodes along the longest root-to-leaf path).",
        "firstLine": "Base case `if not root: return 0`, else return `1 + max(...)`.",
        "steps": [
            "If `not root`, return `0`",
            "Recursively compute `left_d = self.maxDepth(root.left)` and `right_d = self.maxDepth(root.right)`",
            "Return `1 + max(left_d, right_d)`"
        ],
        "cases": [
            {"input": {"root": [3, 9, 20, None, None, 15, 7]}, "expected": 3},
            {"input": {"root": [1, None, 2]}, "expected": 2},
            {"input": {"root": []}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def maxDepth(self, root: Optional[TreeNode]) -> int:\n        if not root:\n            return 0\n        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))\n",
    },
    {
        "id": 47, "slug": "diameter-of-binary-tree", "method": "diameterOfBinaryTree",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:",
        "javaSig": "public int diameterOfBinaryTree(TreeNode root)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(H)", "invariant": "best = max(best, left_height + right_height); return 1 + max(lh, rh)",
        "prompt": "Return the length (number of edges) of the longest path between any two nodes in a binary tree.",
        "firstLine": "Track `self.best = 0` and write a helper `height(node)` returning subtree height.",
        "steps": [
            "Initialize `best = 0`",
            "In `dfs(node)`: return `0` if `None`; compute `lh = dfs(node.left)` and `rh = dfs(node.right)`",
            "Update `best = max(best, lh + rh)` and return `1 + max(lh, rh)`"
        ],
        "cases": [
            {"input": {"root": [1, 2, 3, 4, 5]}, "expected": 3},
            {"input": {"root": [1, 2]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:\n        best = 0\n        def dfs(n):\n            nonlocal best\n            if not n:\n                return 0\n            lh, rh = dfs(n.left), dfs(n.right)\n            best = max(best, lh + rh)\n            return 1 + max(lh, rh)\n        dfs(root)\n        return best\n",
    },
    {
        "id": 48, "slug": "balanced-binary-tree", "method": "isBalanced",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def isBalanced(self, root: Optional[TreeNode]) -> bool:",
        "javaSig": "public boolean isBalanced(TreeNode root)", "javaRet": "return true;",
        "time": "O(N)", "space": "O(H)", "invariant": "Bottom-up height returns -1 immediately if |lh - rh| > 1",
        "prompt": "Return `True` if a binary tree is height-balanced (every node's left & right subtree heights differ by at most 1).",
        "firstLine": "Write bottom-up `dfs(node)` returning `-1` when unbalanced, else subtree height.",
        "steps": [
            "Define `dfs(node)`: if `not node`, return `0`",
            "Compute `lh = dfs(node.left)` and `rh = dfs(node.right)`; if `lh == -1 or rh == -1 or abs(lh - rh) > 1`, return `-1`",
            "Return `1 + max(lh, rh)` from `dfs`, and `dfs(root) != -1` from `isBalanced`"
        ],
        "cases": [
            {"input": {"root": [3, 9, 20, None, None, 15, 7]}, "expected": True},
            {"input": {"root": [1, 2, 2, 3, 3, None, None, 4, 4]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isBalanced(self, root: Optional[TreeNode]) -> bool:\n        def dfs(n):\n            if not n:\n                return 0\n            lh = dfs(n.left)\n            if lh == -1:\n                return -1\n            rh = dfs(n.right)\n            if rh == -1 or abs(lh - rh) > 1:\n                return -1\n            return 1 + max(lh, rh)\n        return dfs(root) != -1\n",
    },
    {
        "id": 49, "slug": "same-tree", "method": "isSameTree",
        "argTypes": {"p": "TreeNode", "q": "TreeNode"},
        "pySig": "def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:",
        "javaSig": "public boolean isSameTree(TreeNode p, TreeNode q)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(H)", "invariant": "p.val == q.val and same(p.left, q.left) and same(p.right, q.right)",
        "prompt": "Given roots `p` and `q` of two binary trees, return `True` if they are structurally identical with equal node values.",
        "firstLine": "Handle nulls first: `if not p and not q: return True` and `if not p or not q or p.val != q.val: return False`.",
        "steps": [
            "If both `p` and `q` are `None`, return `True`",
            "If only one is `None` or `p.val != q.val`, return `False`",
            "Recurse on `(p.left, q.left)` AND `(p.right, q.right)`"
        ],
        "cases": [
            {"input": {"p": [1, 2, 3], "q": [1, 2, 3]}, "expected": True},
            {"input": {"p": [1, 2], "q": [1, None, 2]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:\n        if not p and not q:\n            return True\n        if not p or not q or p.val != q.val:\n            return False\n        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)\n",
    },
    {
        "id": 50, "slug": "subtree-of-another-tree", "method": "isSubtree",
        "argTypes": {"root": "TreeNode", "subRoot": "TreeNode"},
        "pySig": "def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:",
        "javaSig": "public boolean isSubtree(TreeNode root, TreeNode subRoot)", "javaRet": "return false;",
        "time": "O(N * M)", "space": "O(H)", "invariant": "sameTree(root, subRoot) or isSubtree(left) or isSubtree(right)",
        "prompt": "Return `True` if `root` contains a subtree with the exact same structure and values as `subRoot`.",
        "firstLine": "Write helper `same(a, b)` and check `same(root, subRoot)` at every node of `root`.",
        "steps": [
            "If `not subRoot`, return `True`; if `not root`, return `False`",
            "Write `same(a, b)` checking structural and value equality",
            "Return `same(root, subRoot) or self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)`"
        ],
        "cases": [
            {"input": {"root": [3, 4, 5, 1, 2], "subRoot": [4, 1, 2]}, "expected": True},
            {"input": {"root": [3, 4, 5, 1, 2, None, None, None, None, 0], "subRoot": [4, 1, 2]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:\n        def same(a, b):\n            if not a and not b:\n                return True\n            if not a or not b or a.val != b.val:\n                return False\n            return same(a.left, b.left) and same(a.right, b.right)\n        if not subRoot:\n            return True\n        if not root:\n            return False\n        return same(root, subRoot) or self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)\n",
    },
    {
        "id": 51, "slug": "lowest-common-ancestor-of-a-binary-search-tree", "method": "lowestCommonAncestor",
        "execMode": "bst_lca",
        "pySig": "def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:",
        "javaSig": "public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q)", "javaRet": "return null;",
        "time": "O(H)", "space": "O(1)", "invariant": "Split point where min(p,q) <= curr.val <= max(p,q) is the LCA",
        "prompt": "Given a Binary Search Tree `root` and nodes `p` and `q`, return their Lowest Common Ancestor node.",
        "firstLine": "Set `curr = root` and walk down while both `p.val` and `q.val` lie on the same side of `curr.val`.",
        "steps": [
            "Start `curr = root`",
            "If `p.val < curr.val and q.val < curr.val`, move `curr = curr.left`; elif both `> curr.val`, move `curr = curr.right`",
            "Otherwise `curr` splits `p` and `q` (or equals one of them) — return `curr`"
        ],
        "cases": [
            {"input": {"root": [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], "p": 2, "q": 8}, "expected": 6},
            {"input": {"root": [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], "p": 2, "q": 4}, "expected": 2},
        ],
        "refPy": "class Solution:\n    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:\n        curr = root\n        while curr:\n            if p.val < curr.val and q.val < curr.val:\n                curr = curr.left\n            elif p.val > curr.val and q.val > curr.val:\n                curr = curr.right\n            else:\n                return curr\n        return root\n",
    },
    {
        "id": 52, "slug": "binary-tree-level-order-traversal", "method": "levelOrder",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> levelOrder(TreeNode root)", "javaRet": "return new ArrayList<>();",
        "time": "O(N)", "space": "O(N)", "invariant": "Snapshot len(queue) per level to group nodes cleanly",
        "prompt": "Given `root` of a binary tree, return the level-order traversal of its nodes' values (`List[List[int]]`).",
        "firstLine": "Guard `if not root: return []`, then initialize `q = deque([root])` and `res = []`.",
        "steps": [
            "If `not root`, return `[]`; create `q = deque([root])` and `res = []`",
            "While `q`: snapshot `level_size = len(q)` and pop `level_size` nodes into `level = []`",
            "Enqueue non-null `.left` and `.right` children, append `level` to `res`, and return `res`"
        ],
        "cases": [
            {"input": {"root": [3, 9, 20, None, None, 15, 7]}, "expected": [[3], [9, 20], [15, 7]]},
            {"input": {"root": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:\n        if not root:\n            return []\n        q, res = deque([root]), []\n        while q:\n            lvl = []\n            for _ in range(len(q)):\n                n = q.popleft()\n                lvl.append(n.val)\n                if n.left: q.append(n.left)\n                if n.right: q.append(n.right)\n            res.append(lvl)\n        return res\n",
    },
    {
        "id": 53, "slug": "binary-tree-right-side-view", "method": "rightSideView",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def rightSideView(self, root: Optional[TreeNode]) -> List[int]:",
        "javaSig": "public List<Integer> rightSideView(TreeNode root)", "javaRet": "return new ArrayList<>();",
        "time": "O(N)", "space": "O(N)", "invariant": "Last node popped in each BFS level is visible from the right",
        "prompt": "Imagine standing on the right side of a binary tree; return the values of the nodes you can see ordered top to bottom.",
        "firstLine": "Guard `if not root: return []`, run BFS with `q = deque([root])`, and record the last node of each level.",
        "steps": [
            "If `not root`, return `[]`; initialize `q = deque([root])` and `res = []`",
            "For each level of size `k = len(q)`, pop `k` nodes and push children",
            "Append the `k-1`-th node's `.val` to `res`"
        ],
        "cases": [
            {"input": {"root": [1, 2, 3, None, 5, None, 4]}, "expected": [1, 3, 4]},
            {"input": {"root": [1, 2]}, "expected": [1, 2]},
        ],
        "refPy": "class Solution:\n    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:\n        if not root:\n            return []\n        q, res = deque([root]), []\n        while q:\n            k = len(q)\n            for i in range(k):\n                n = q.popleft()\n                if i == k - 1:\n                    res.append(n.val)\n                if n.left: q.append(n.left)\n                if n.right: q.append(n.right)\n        return res\n",
    },
    {
        "id": 54, "slug": "count-good-nodes-in-binary-tree", "method": "goodNodes",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def goodNodes(self, root: TreeNode) -> int:",
        "javaSig": "public int goodNodes(TreeNode root)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(H)", "invariant": "Node is good iff node.val >= max_val_along_root_path",
        "prompt": "Count 'good' nodes in `root`: a node `X` is good if no node on the path from `root` to `X` has a value strictly greater than `X.val`.",
        "firstLine": "Write `dfs(node, max_so_far)` starting with `dfs(root, root.val)`.",
        "steps": [
            "Define `dfs(node, max_so_far)` returning `0` if `not node`",
            "Count `good = 1 if node.val >= max_so_far else 0` and update `nxt_max = max(max_so_far, node.val)`",
            "Return `good + dfs(node.left, nxt_max) + dfs(node.right, nxt_max)`"
        ],
        "cases": [
            {"input": {"root": [3, 1, 4, 3, None, 1, 5]}, "expected": 4},
            {"input": {"root": [3, 3, None, 4, 2]}, "expected": 3},
        ],
        "refPy": "class Solution:\n    def goodNodes(self, root: TreeNode) -> int:\n        def dfs(n, mx):\n            if not n:\n                return 0\n            g = 1 if n.val >= mx else 0\n            mx = max(mx, n.val)\n            return g + dfs(n.left, mx) + dfs(n.right, mx)\n        return dfs(root, root.val) if root else 0\n",
    },
    {
        "id": 55, "slug": "validate-binary-search-tree", "method": "isValidBST",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def isValidBST(self, root: Optional[TreeNode]) -> bool:",
        "javaSig": "public boolean isValidBST(TreeNode root)", "javaRet": "return true;",
        "time": "O(N)", "space": "O(H)", "invariant": "Every node satisfies strict open interval low < node.val < high",
        "prompt": "Determine whether `root` is a valid Binary Search Tree (strictly `<` on left subtree, strictly `>` on right subtree).",
        "firstLine": "Write `valid(node, low, high)` starting with `(-inf, +inf)`.",
        "steps": [
            "Define `valid(node, low, high)`: return `True` if `not node`",
            "If not `(low < node.val < high)`, return `False`",
            "Return `valid(node.left, low, node.val) and valid(node.right, node.val, high)`"
        ],
        "cases": [
            {"input": {"root": [2, 1, 3]}, "expected": True},
            {"input": {"root": [5, 1, 4, None, None, 3, 6]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isValidBST(self, root: Optional[TreeNode]) -> bool:\n        def ok(n, lo, hi):\n            if not n:\n                return True\n            if not (lo < n.val < hi):\n                return False\n            return ok(n.left, lo, n.val) and ok(n.right, n.val, hi)\n        return ok(root, float('-inf'), float('inf'))\n",
    },
    {
        "id": 56, "slug": "kth-smallest-element-in-a-bst", "method": "kthSmallest",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:",
        "javaSig": "public int kthSmallest(TreeNode root, int k)", "javaRet": "return 0;",
        "time": "O(H + K)", "space": "O(H)", "invariant": "Iterative inorder traversal visits BST values in sorted order",
        "prompt": "Given `root` of a BST and `1`-indexed `k`, return the `k`-th smallest value in the tree.",
        "firstLine": "Use iterative inorder stack `stack = []`, `curr = root`.",
        "steps": [
            "Initialize `stack = []` and `curr = root`",
            "While `curr or stack`: push all left children `while curr: stack.append(curr); curr = curr.left`",
            "Pop `curr = stack.pop()`, decrement `k -= 1` (return `curr.val` when `k == 0`), then set `curr = curr.right`"
        ],
        "cases": [
            {"input": {"root": [3, 1, 4, None, 2], "k": 1}, "expected": 1},
            {"input": {"root": [5, 3, 6, 2, 4, None, None, 1], "k": 3}, "expected": 3},
        ],
        "refPy": "class Solution:\n    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:\n        stack, curr = [], root\n        while curr or stack:\n            while curr:\n                stack.append(curr)\n                curr = curr.left\n            curr = stack.pop()\n            k -= 1\n            if k == 0:\n                return curr.val\n            curr = curr.right\n        return -1\n",
    },
    {
        "id": 57, "slug": "construct-binary-tree-from-preorder-and-inorder-traversal", "method": "buildTree",
        "returnType": "TreeNode",
        "pySig": "def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:",
        "javaSig": "public TreeNode buildTree(int[] preorder, int[] inorder)", "javaRet": "return null;",
        "time": "O(N)", "space": "O(N)", "invariant": "preorder[pre_idx] is root; inorder_index_map splits left & right subtrees in O(1)",
        "prompt": "Given `preorder` and `inorder` traversal arrays of unique values, reconstruct and return the binary tree.",
        "firstLine": "Pre-index `idx_map = {val: i for i, val in enumerate(inorder)}` and track `pre_idx = 0`.",
        "steps": [
            "Map `val -> index` from `inorder` for O(1) root splitting and set `pre_idx = 0`",
            "In `helper(in_left, in_right)`: return `None` if `in_left > in_right`; take `root_val = preorder[pre_idx]` and increment `pre_idx`",
            "Build `root.left = helper(in_left, mid - 1)` then `root.right = helper(mid + 1, in_right)`"
        ],
        "cases": [
            {"input": {"preorder": [3, 9, 20, 15, 7], "inorder": [9, 3, 15, 20, 7]}, "expected": [3, 9, 20, None, None, 15, 7]},
            {"input": {"preorder": [-1], "inorder": [-1]}, "expected": [-1]},
        ],
        "refPy": "class Solution:\n    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:\n        mp = {v: i for i, v in enumerate(inorder)}\n        pre_i = 0\n        def build(l, r):\n            nonlocal pre_i\n            if l > r:\n                return None\n            rv = preorder[pre_i]\n            pre_i += 1\n            node = TreeNode(rv)\n            mid = mp[rv]\n            node.left = build(l, mid - 1)\n            node.right = build(mid + 1, r)\n            return node\n        return build(0, len(inorder) - 1)\n",
    },
    {
        "id": 58, "slug": "binary-tree-maximum-path-sum", "method": "maxPathSum",
        "argTypes": {"root": "TreeNode"},
        "pySig": "def maxPathSum(self, root: Optional[TreeNode]) -> int:",
        "javaSig": "public int maxPathSum(TreeNode root)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(H)", "invariant": "best = max(best, val + left_gain + right_gain); return val + max(left_gain, right_gain)",
        "prompt": "Return the maximum sum of any non-empty path in a binary tree (path does not need to pass through root).",
        "firstLine": "Track `best = root.val` and compute clamped downward gains `lg = max(0, dfs(node.left))`.",
        "steps": [
            "Initialize `best = float('-inf')`",
            "In `dfs(node)`: compute `lg = max(0, dfs(node.left))` and `rg = max(0, dfs(node.right))`",
            "Update `best = max(best, node.val + lg + rg)` (split arch) and return `node.val + max(lg, rg)` (single arm)"
        ],
        "cases": [
            {"input": {"root": [1, 2, 3]}, "expected": 6},
            {"input": {"root": [-10, 9, 20, None, None, 15, 7]}, "expected": 42},
        ],
        "refPy": "class Solution:\n    def maxPathSum(self, root: Optional[TreeNode]) -> int:\n        best = float('-inf')\n        def dfs(n):\n            nonlocal best\n            if not n:\n                return 0\n            lg = max(0, dfs(n.left))\n            rg = max(0, dfs(n.right))\n            best = max(best, n.val + lg + rg)\n            return n.val + max(lg, rg)\n        dfs(root)\n        return best\n",
    },
    {
        "id": 59, "slug": "serialize-and-deserialize-binary-tree", "method": "serialize", "execMode": "codec_tree", "className": "Codec",
        "pySig": "class Codec:\n    def serialize(self, root: Optional[TreeNode]) -> str:\n        return ''\n    def deserialize(self, data: str) -> Optional[TreeNode]:",
        "javaSig": "public String serialize(TreeNode root)", "javaRet": "return \"\";",
        "time": "O(N)", "space": "O(N)", "invariant": "Preorder DFS with '#' sentinel tokens reconstructs uniquely in one pass",
        "prompt": "Design `Codec` with `serialize(root)` and `deserialize(data)` to convert a binary tree to a string and back.",
        "firstLine": "Use preorder DFS emitting `'#'` for `None` and comma-joined values; consume tokens with an index pointer on `deserialize`.",
        "steps": [
            "In `serialize(root)`: preorder traverse appending `'#'` for `None` and `str(node.val)` otherwise",
            "Join tokens with `','`",
            "In `deserialize(data)`: split by `','`, advance index `i`; if `'#'` return `None`, else build `TreeNode` + left + right"
        ],
        "cases": [
            {"input": {"root": [1, 2, 3, None, None, 4, 5]}, "expected": [1, 2, 3, None, None, 4, 5]},
            {"input": {"root": []}, "expected": []},
        ],
        "refPy": "class Codec:\n    def serialize(self, root: Optional[TreeNode]) -> str:\n        vals = []\n        def dfs(n):\n            if not n:\n                vals.append('#')\n                return\n            vals.append(str(n.val))\n            dfs(n.left)\n            dfs(n.right)\n        dfs(root)\n        return ','.join(vals)\n    def deserialize(self, data: str) -> Optional[TreeNode]:\n        toks = iter(data.split(','))\n        def build():\n            t = next(toks)\n            if t == '#':\n                return None\n            n = TreeNode(int(t))\n            n.left = build()\n            n.right = build()\n            return n\n        return build()\n",
    },
    {
        "id": 60, "slug": "kth-largest-element-in-a-stream", "method": "add", "execMode": "class_ops", "className": "KthLargest",
        "pySig": "class KthLargest:\n    def __init__(self, k: int, nums: List[int]):\n        pass\n    def add(self, val: int) -> int:",
        "javaSig": "public int add(int val)", "javaRet": "return 0;",
        "time": "O(log K)", "space": "O(K)", "invariant": "Min-heap of size K -> heap[0] is always the K-th largest",
        "prompt": "Design `KthLargest(k, nums)` whose `add(val)` appends `val` to the stream and returns the `k`-th largest element.",
        "firstLine": "Store `self.k = k`, `self.heap = nums[:]`, `heapq.heapify(self.heap)`, and pop while `len(self.heap) > k`.",
        "steps": [
            "Heapify `nums` into `self.heap` and `heappop` until `len(self.heap) <= k`",
            "On `add(val)`: `heappush(self.heap, val)`; if `len(self.heap) > self.k`, `heappop(self.heap)`",
            "Return `self.heap[0]`"
        ],
        "cases": [
            {
                "input": {"ops": ["KthLargest", "add", "add", "add", "add", "add"], "args": [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]]},
                "expected": [None, 4, 5, 5, 8, 8],
            }
        ],
        "refPy": "class KthLargest:\n    def __init__(self, k: int, nums: List[int]):\n        self.k = k\n        self.heap = list(nums)\n        heapq.heapify(self.heap)\n        while len(self.heap) > k:\n            heapq.heappop(self.heap)\n    def add(self, val: int) -> int:\n        heapq.heappush(self.heap, val)\n        if len(self.heap) > self.k:\n            heapq.heappop(self.heap)\n        return self.heap[0]\n",
    },
    {
        "id": 61, "slug": "last-stone-weight", "method": "lastStoneWeight",
        "pySig": "def lastStoneWeight(self, stones: List[int]) -> int:",
        "javaSig": "public int lastStoneWeight(int[] stones)", "javaRet": "return 0;",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Max-heap via negated weights [-s for s in stones]",
        "prompt": "Repeatedly smash the two heaviest stones `y >= x` (leaving `y - x` if unequal); return the last remaining weight or `0`.",
        "firstLine": "Build max-heap `heap = [-s for s in stones]; heapq.heapify(heap)`.",
        "steps": [
            "Negate `stones` and call `heapq.heapify(heap)` to simulate a max-heap",
            "While `len(heap) > 1`, pop `first = -heappop(heap)` and `second = -heappop(heap)`",
            "If `first > second`, push `-(first - second)`; return `-heap[0]` if non-empty else `0`"
        ],
        "cases": [
            {"input": {"stones": [2, 7, 4, 1, 8, 1]}, "expected": 1},
            {"input": {"stones": [1]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def lastStoneWeight(self, stones: List[int]) -> int:\n        h = [-s for s in stones]\n        heapq.heapify(h)\n        while len(h) > 1:\n            y, x = -heapq.heappop(h), -heapq.heappop(h)\n            if y > x:\n                heapq.heappush(h, -(y - x))\n        return -h[0] if h else 0\n",
    },
    {
        "id": 62, "slug": "k-closest-points-to-origin", "method": "kClosest", "compareMode": "unordered",
        "pySig": "def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:",
        "javaSig": "public int[][] kClosest(int[][] points, int k)", "javaRet": "return new int[][]{};",
        "time": "O(N log K)", "space": "O(K)", "invariant": "Max-heap of size K storing (-dist_sq, x, y)",
        "prompt": "Given `points[i] = [x, y]`, return the `k` closest points to `(0, 0)` using Euclidean distance.",
        "firstLine": "Maintain a bounded max-heap `heap = []` of `(-(x*x + y*y), x, y)` up to size `k`.",
        "steps": [
            "Create `heap = []`",
            "For `x, y` in `points`, push `(-(x*x + y*y), x, y)` and `heappop` if `len(heap) > k`",
            "Return `[[x, y] for _, x, y in heap]`"
        ],
        "cases": [
            {"input": {"points": [[1, 3], [-2, 2]], "k": 1}, "expected": [[-2, 2]]},
            {"input": {"points": [[3, 3], [5, -1], [-2, 4]], "k": 2}, "expected": [[3, 3], [-2, 4]]},
        ],
        "refPy": "class Solution:\n    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:\n        h = []\n        for x, y in points:\n            heapq.heappush(h, (-(x * x + y * y), x, y))\n            if len(h) > k:\n                heapq.heappop(h)\n        return [[x, y] for _, x, y in h]\n",
    },
    {
        "id": 63, "slug": "kth-largest-element-in-an-array", "method": "findKthLargest",
        "pySig": "def findKthLargest(self, nums: List[int], k: int) -> int:",
        "javaSig": "public int findKthLargest(int[] nums, int k)", "javaRet": "return 0;",
        "time": "O(N log K)", "space": "O(K)", "invariant": "Min-heap of top K elements -> heap[0] is K-th largest",
        "prompt": "Given integer array `nums` and `k`, return the `k`-th largest element without sorting the entire array.",
        "firstLine": "Maintain a min-heap `heap = []` of size `k`.",
        "steps": [
            "Initialize `heap = []`",
            "For `x` in `nums`: `heappush(heap, x)` and if `len(heap) > k`, `heappop(heap)`",
            "Return `heap[0]`"
        ],
        "cases": [
            {"input": {"nums": [3, 2, 1, 5, 6, 4], "k": 2}, "expected": 5},
            {"input": {"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4}, "expected": 4},
        ],
        "refPy": "class Solution:\n    def findKthLargest(self, nums: List[int], k: int) -> int:\n        h = []\n        for x in nums:\n            heapq.heappush(h, x)\n            if len(h) > k:\n                heapq.heappop(h)\n        return h[0]\n",
    },
    {
        "id": 64, "slug": "task-scheduler", "method": "leastInterval",
        "pySig": "def leastInterval(self, tasks: List[str], n: int) -> int:",
        "javaSig": "public int leastInterval(char[] tasks, int n)", "javaRet": "return 0;",
        "time": "O(T)", "space": "O(1)", "invariant": "Max-heap of remaining counts + cooldown queue of (rem_cnt, ready_time)",
        "prompt": "Given CPU `tasks` and cooldown `n` between identical tasks, return the minimum CPU intervals required to finish all tasks.",
        "firstLine": "Build max-heap `heap = [-c for c in Counter(tasks).values()]` and cooldown `q = deque()`.",
        "steps": [
            "Heapify negative counts in `heap` and initialize `q = deque()`, `time = 0`",
            "Each tick `time += 1`: if `heap`, pop `-cnt` and if `cnt - 1 > 0`, append `(-(cnt - 1), time + n)` to `q`",
            "If `q` head has `ready_time == time`, push its count back into `heap`; return `time` when both empty"
        ],
        "cases": [
            {"input": {"tasks": ["A", "A", "A", "B", "B", "B"], "n": 2}, "expected": 8},
            {"input": {"tasks": ["A", "A", "A", "B", "B", "B"], "n": 0}, "expected": 6},
        ],
        "refPy": "class Solution:\n    def leastInterval(self, tasks: List[str], n: int) -> int:\n        h = [-c for c in Counter(tasks).values()]\n        heapq.heapify(h)\n        q = deque()\n        t = 0\n        while h or q:\n            t += 1\n            if h:\n                cnt = 1 + heapq.heappop(h)\n                if cnt != 0:\n                    q.append((cnt, t + n))\n            if q and q[0][1] == t:\n                heapq.heappush(h, q.popleft()[0])\n        return t\n",
    },
    {
        "id": 65, "slug": "design-twitter", "method": "getNewsFeed", "execMode": "class_ops", "className": "Twitter",
        "pySig": "class Twitter:\n    def __init__(self):\n        pass\n    def postTweet(self, userId: int, tweetId: int) -> None:\n        pass\n    def getNewsFeed(self, userId: int) -> List[int]:\n        return []\n    def follow(self, followerId: int, followeeId: int) -> None:\n        pass\n    def unfollow(self, followerId: int, followeeId: int) -> None:",
        "javaSig": "public List<Integer> getNewsFeed(int userId)", "javaRet": "return new ArrayList<>();",
        "time": "O(F log F)", "space": "O(U + T)", "invariant": "Merge k-sorted tweet feeds via max-heap keyed by monotonic timestamp",
        "prompt": "Design `Twitter` supporting `postTweet`, `getNewsFeed` (10 most recent tweets from self + followees), `follow`, and `unfollow`.",
        "firstLine": "Store `self.time = 0`, `self.tweets = defaultdict(list)`, and `self.follows = defaultdict(set)`.",
        "steps": [
            "Decrement `self.time -= 1` on each `postTweet` so smaller timestamp = newer in a min-heap",
            "Ensure `userId` is included in their own feed targets (`self.follows[userId] | {userId}`)",
            "Use k-way heap merge across each followee's tweet list to pop up to 10 most recent tweetIds"
        ],
        "cases": [
            {
                "input": {"ops": ["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed", "unfollow", "getNewsFeed"], "args": [[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]]},
                "expected": [None, None, [5], None, None, [6, 5], None, [5]],
            }
        ],
        "refPy": "class Twitter:\n    def __init__(self):\n        self.t = 0\n        self.tweets = defaultdict(list)\n        self.follows = defaultdict(set)\n    def postTweet(self, userId: int, tweetId: int) -> None:\n        self.t -= 1\n        self.tweets[userId].append((self.t, tweetId))\n    def getNewsFeed(self, userId: int) -> List[int]:\n        h, res = [], []\n        for uid in self.follows[userId] | {userId}:\n            arr = self.tweets[uid]\n            if arr:\n                idx = len(arr) - 1\n                ts, tid = arr[idx]\n                heapq.heappush(h, (ts, tid, uid, idx - 1))\n        while h and len(res) < 10:\n            ts, tid, uid, nxt = heapq.heappop(h)\n            res.append(tid)\n            if nxt >= 0:\n                nts, ntid = self.tweets[uid][nxt]\n                heapq.heappush(h, (nts, ntid, uid, nxt - 1))\n        return res\n    def follow(self, followerId: int, followeeId: int) -> None:\n        if followerId != followeeId:\n            self.follows[followerId].add(followeeId)\n    def unfollow(self, followerId: int, followeeId: int) -> None:\n        self.follows[followerId].discard(followeeId)\n",
    },
    {
        "id": 66, "slug": "find-median-from-data-stream", "method": "findMedian", "execMode": "class_ops", "className": "MedianFinder", "compareMode": "float_1e5",
        "pySig": "class MedianFinder:\n    def __init__(self):\n        pass\n    def addNum(self, num: int) -> None:\n        pass\n    def findMedian(self) -> float:",
        "javaSig": "public double findMedian()", "javaRet": "return 0.0;",
        "time": "O(log N)", "space": "O(N)", "invariant": "Max-heap `small` (lower half) and min-heap `large` (upper half) balanced within 1 element",
        "prompt": "Design `MedianFinder` supporting `addNum(num)` in `O(log N)` and `findMedian()` in `O(1)`.",
        "firstLine": "Create two heaps in `__init__`: `self.small = []` (max-heap via negation) and `self.large = []` (min-heap).",
        "steps": [
            "Push `-num` to `small`, then move `-heappop(small)` to `large` so ordering `max(small) <= min(large)` holds",
            "If `len(large) > len(small)`, move `heappop(large)` back to `small` (`-val`)",
            "In `findMedian()`: if `len(small) > len(large)` return `-small[0]`, else `(-small[0] + large[0]) / 2.0`"
        ],
        "cases": [
            {
                "input": {"ops": ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"], "args": [[], [1], [2], [], [3], []]},
                "expected": [None, None, None, 1.5, None, 2.0],
            }
        ],
        "refPy": "class MedianFinder:\n    def __init__(self):\n        self.small = []\n        self.large = []\n    def addNum(self, num: int) -> None:\n        heapq.heappush(self.small, -num)\n        heapq.heappush(self.large, -heapq.heappop(self.small))\n        if len(self.large) > len(self.small):\n            heapq.heappush(self.small, -heapq.heappop(self.large))\n    def findMedian(self) -> float:\n        if len(self.small) > len(self.large):\n            return float(-self.small[0])\n        return (-self.small[0] + self.large[0]) / 2.0\n",
    },
]
