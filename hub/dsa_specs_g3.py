"""DSA Catalog Specs — Group 3: Problems #67 to #99 (Backtracking, Graphs, 1D Dynamic Programming)."""

SPECS_G3 = [
    {
        "id": 67, "slug": "subsets", "method": "subsets", "compareMode": "unordered",
        "pySig": "def subsets(self, nums: List[int]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> subsets(int[] nums)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * 2^N)", "space": "O(N)", "invariant": "At index i: branch 1 includes nums[i], branch 2 skips nums[i]",
        "prompt": "Given an integer array `nums` of unique elements, return all possible subsets (the power set).",
        "firstLine": "Create `res = []`, `path = []`, and write `dfs(i)` branching on include vs skip.",
        "steps": [
            "Initialize `res = []` and `path = []`",
            "In `dfs(i)`: if `i == len(nums)`, append `path[:]` to `res` and return",
            "Append `nums[i]`, call `dfs(i + 1)`, pop `path.pop()`, then call `dfs(i + 1)`"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 3]}, "expected": [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]},
            {"input": {"nums": [0]}, "expected": [[], [0]]},
        ],
        "refPy": "class Solution:\n    def subsets(self, nums: List[int]) -> List[List[int]]:\n        res, path = [], []\n        def dfs(i):\n            if i == len(nums):\n                res.append(path[:])\n                return\n            path.append(nums[i])\n            dfs(i + 1)\n            path.pop()\n            dfs(i + 1)\n        dfs(0)\n        return res\n",
    },
    {
        "id": 68, "slug": "combination-sum", "method": "combinationSum", "compareMode": "unordered",
        "pySig": "def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> combinationSum(int[] candidates, int target)", "javaRet": "return new ArrayList<>();",
        "time": "O(2^(T/M))", "space": "O(T/M)", "invariant": "Reuse allowed -> recurse at same index i; advance i + 1 to skip",
        "prompt": "Return all unique combinations of `candidates` where chosen numbers sum to `target` (unlimited reuse allowed).",
        "firstLine": "Create `res = []`, `path = []`, and write `dfs(i, rem)` starting at `(0, target)`.",
        "steps": [
            "If `rem == 0`, append `path[:]` to `res`; if `i == len(candidates) or rem < 0`, return",
            "Include `candidates[i]` and call `dfs(i, rem - candidates[i])` (same `i` allows reuse)",
            "Pop from `path` and call `dfs(i + 1, rem)` to move to the next candidate"
        ],
        "cases": [
            {"input": {"candidates": [2, 3, 6, 7], "target": 7}, "expected": [[2, 2, 3], [7]]},
            {"input": {"candidates": [2], "target": 1}, "expected": []},
        ],
        "refPy": "class Solution:\n    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:\n        res, path = [], []\n        def dfs(i, rem):\n            if rem == 0:\n                res.append(path[:])\n                return\n            if i == len(candidates) or rem < 0:\n                return\n            path.append(candidates[i])\n            dfs(i, rem - candidates[i])\n            path.pop()\n            dfs(i + 1, rem)\n        dfs(0, target)\n        return res\n",
    },
    {
        "id": 69, "slug": "permutations", "method": "permute", "compareMode": "unordered",
        "pySig": "def permute(self, nums: List[int]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> permute(int[] nums)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * N!)", "space": "O(N)", "invariant": "Track `used` set/boolean array; choose -> explore -> unchoose",
        "prompt": "Given an array `nums` of distinct integers, return all possible permutations.",
        "firstLine": "Create `res = []`, `path = []`, and `used = [False] * len(nums)`.",
        "steps": [
            "When `len(path) == len(nums)`, append `path[:]` to `res`",
            "Loop `i` over `range(len(nums))` skipping indices where `used[i]` is `True`",
            "Mark `used[i] = True`, append `nums[i]`, recurse, then undo both"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 3]}, "expected": [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]},
            {"input": {"nums": [1]}, "expected": [[1]]},
        ],
        "refPy": "class Solution:\n    def permute(self, nums: List[int]) -> List[List[int]]:\n        res, path, used = [], [], [False] * len(nums)\n        def dfs():\n            if len(path) == len(nums):\n                res.append(path[:])\n                return\n            for i, x in enumerate(nums):\n                if not used[i]:\n                    used[i] = True\n                    path.append(x)\n                    dfs()\n                    path.pop()\n                    used[i] = False\n        dfs()\n        return res\n",
    },
    {
        "id": 70, "slug": "subsets-ii", "method": "subsetsWithDup", "compareMode": "unordered",
        "pySig": "def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> subsetsWithDup(int[] nums)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * 2^N)", "space": "O(N)", "invariant": "Sort nums; on skip branch advance past all equal duplicates",
        "prompt": "Given integer array `nums` that may contain duplicates, return all unique subsets.",
        "firstLine": "Call `nums.sort()` first so identical numbers sit side-by-side.",
        "steps": [
            "Sort `nums` and initialize `res = []`, `path = []`",
            "Branch 1: append `nums[i]`, recurse `dfs(i + 1)`, and `path.pop()`",
            "Branch 2: advance `i` while `i + 1 < len(nums) and nums[i] == nums[i + 1]`, then recurse `dfs(i + 1)`"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 2]}, "expected": [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]},
            {"input": {"nums": [0]}, "expected": [[], [0]]},
        ],
        "refPy": "class Solution:\n    def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:\n        nums.sort()\n        res, path = [], []\n        def dfs(i):\n            if i == len(nums):\n                res.append(path[:])\n                return\n            path.append(nums[i])\n            dfs(i + 1)\n            path.pop()\n            while i + 1 < len(nums) and nums[i] == nums[i + 1]:\n                i += 1\n            dfs(i + 1)\n        dfs(0)\n        return res\n",
    },
    {
        "id": 71, "slug": "combination-sum-ii", "method": "combinationSum2", "compareMode": "unordered",
        "pySig": "def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> combinationSum2(int[] candidates, int target)", "javaRet": "return new ArrayList<>();",
        "time": "O(2^N)", "space": "O(N)", "invariant": "Sort candidates; skip j > start when candidates[j] == candidates[j - 1]",
        "prompt": "Return all unique combinations in `candidates` summing to `target` where each element may be used at most once.",
        "firstLine": "Sort `candidates` so duplicate branches at the same tree depth can be skipped.",
        "steps": [
            "Sort `candidates` ascending",
            "In `dfs(start, rem)`: if `rem == 0`, record `path[:]`; loop `j` from `start` to `len - 1`",
            "Skip if `j > start and candidates[j] == candidates[j - 1]`; break if `candidates[j] > rem`; else recurse `dfs(j + 1, rem - candidates[j])`"
        ],
        "cases": [
            {"input": {"candidates": [10, 1, 2, 7, 6, 1, 5], "target": 8}, "expected": [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]},
            {"input": {"candidates": [2, 5, 2, 1, 2], "target": 5}, "expected": [[1, 2, 2], [5]]},
        ],
        "refPy": "class Solution:\n    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:\n        candidates.sort()\n        res, path = [], []\n        def dfs(start, rem):\n            if rem == 0:\n                res.append(path[:])\n                return\n            for j in range(start, len(candidates)):\n                if j > start and candidates[j] == candidates[j - 1]:\n                    continue\n                if candidates[j] > rem:\n                    break\n                path.append(candidates[j])\n                dfs(j + 1, rem - candidates[j])\n                path.pop()\n        dfs(0, target)\n        return res\n",
    },
    {
        "id": 72, "slug": "word-search", "method": "exist",
        "pySig": "def exist(self, board: List[List[str]], word: str) -> bool:",
        "javaSig": "public boolean exist(char[][] board, String word)", "javaRet": "return false;",
        "time": "O(R * C * 4^L)", "space": "O(L)", "invariant": "Temporarily mark board[r][c] = '#' before 4-way DFS and restore on backtrack",
        "prompt": "Given an `m x n` character `board` and string `word`, return `True` if `word` exists along adjacent horizontal/vertical cells without reusing a cell.",
        "firstLine": "Store `rows, cols = len(board), len(board[0])` and write `dfs(r, c, idx)`.",
        "steps": [
            "In `dfs(r, c, i)`: return `True` if `i == len(word)`; return `False` if out-of-bounds or `board[r][c] != word[i]`",
            "Save `ch = board[r][c]`, mark `board[r][c] = '#'`, explore 4 neighbors for `i + 1`, then restore `board[r][c] = ch`",
            "Try starting `dfs(r, c, 0)` from every cell `(r, c)`"
        ],
        "cases": [
            {"input": {"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "word": "ABCCED"}, "expected": True},
            {"input": {"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "word": "ABCB"}, "expected": False},
        ],
        "refPy": "class Solution:\n    def exist(self, board: List[List[str]], word: str) -> bool:\n        R, C = len(board), len(board[0])\n        def dfs(r, c, i):\n            if i == len(word):\n                return True\n            if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != word[i]:\n                return False\n            tmp = board[r][c]\n            board[r][c] = '#'\n            found = dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or dfs(r, c+1, i+1) or dfs(r, c-1, i+1)\n            board[r][c] = tmp\n            return found\n        return any(dfs(r, c, 0) for r in range(R) for c in range(C))\n",
    },
    {
        "id": 73, "slug": "palindrome-partitioning", "method": "partition", "compareMode": "unordered",
        "pySig": "def partition(self, s: str) -> List[List[str]]:",
        "javaSig": "public List<List<String>> partition(String s)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * 2^N)", "space": "O(N)", "invariant": "Try every prefix s[i:j+1] that is a palindrome, then recurse from j + 1",
        "prompt": "Partition string `s` such that every substring in the partition is a palindrome; return all possible partitions.",
        "firstLine": "Create `res = []`, `path = []`, and backtrack `dfs(start)` checking `sub == sub[::-1]`.",
        "steps": [
            "When `start == len(s)`, append `path[:]` to `res`",
            "Loop `end` from `start` to `len(s) - 1` and slice `sub = s[start : end + 1]`",
            "If `sub == sub[::-1]`, push `sub`, call `dfs(end + 1)`, and `path.pop()`"
        ],
        "cases": [
            {"input": {"s": "aab"}, "expected": [["a", "a", "b"], ["aa", "b"]]},
            {"input": {"s": "a"}, "expected": [["a"]]},
        ],
        "refPy": "class Solution:\n    def partition(self, s: str) -> List[List[str]]:\n        res, path = [], []\n        def dfs(i):\n            if i == len(s):\n                res.append(path[:])\n                return\n            for j in range(i, len(s)):\n                sub = s[i:j+1]\n                if sub == sub[::-1]:\n                    path.append(sub)\n                    dfs(j + 1)\n                    path.pop()\n        dfs(0)\n        return res\n",
    },
    {
        "id": 74, "slug": "letter-combinations-of-a-phone-number", "method": "letterCombinations", "compareMode": "unordered",
        "pySig": "def letterCombinations(self, digits: str) -> List[str]:",
        "javaSig": "public List<String> letterCombinations(String digits)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * 4^N)", "space": "O(N)", "invariant": "Map digits '2'-'9' to keypad letters and backtrack character by character",
        "prompt": "Given string `digits` containing `'2'-'9'`, return all possible letter combinations on a phone keypad (`[]` if empty).",
        "firstLine": "Guard `if not digits: return []`, define `pad = {'2':'abc', ...}`, and backtrack `dfs(i)`.",
        "steps": [
            "Return `[]` immediately if `digits` is empty",
            "Define keypad dictionary `'2'..'9'` and `path = []`, `res = []`",
            "At `dfs(i)`: if `i == len(digits)` append `''.join(path)`; else loop over `pad[digits[i]]`"
        ],
        "cases": [
            {"input": {"digits": "23"}, "expected": ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]},
            {"input": {"digits": ""}, "expected": []},
        ],
        "refPy": "class Solution:\n    def letterCombinations(self, digits: str) -> List[str]:\n        if not digits:\n            return []\n        pad = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}\n        res, path = [], []\n        def dfs(i):\n            if i == len(digits):\n                res.append(''.join(path))\n                return\n            for ch in pad[digits[i]]:\n                path.append(ch)\n                dfs(i + 1)\n                path.pop()\n        dfs(0)\n        return res\n",
    },
    {
        "id": 75, "slug": "n-queens", "method": "solveNQueens", "compareMode": "unordered",
        "pySig": "def solveNQueens(self, n: int) -> List[List[str]]:",
        "javaSig": "public List<List<String>> solveNQueens(int n)", "javaRet": "return new ArrayList<>();",
        "time": "O(N!)", "space": "O(N^2)", "invariant": "Track occupied cols, (r - c) diagonals, and (r + c) anti-diagonals in sets",
        "prompt": "Place `n` non-attacking queens on an `n x n` chessboard and return all distinct board configurations.",
        "firstLine": "Create sets `cols = set()`, `pos_diag = set()` (`r + c`), `neg_diag = set()` (`r - c`), and `board`.",
        "steps": [
            "Track `cols`, `pos_diag` (`r + c`), and `neg_diag` (`r - c`)",
            "Place one queen per row `r`: skip column `c` if any of the 3 sets already contains it",
            "Add to all 3 sets, set `'Q'`, recurse `dfs(r + 1)`, then undo all 3 sets and restore `'.'`"
        ],
        "cases": [
            {"input": {"n": 4}, "expected": [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]},
            {"input": {"n": 1}, "expected": [["Q"]]},
        ],
        "refPy": "class Solution:\n    def solveNQueens(self, n: int) -> List[List[str]]:\n        cols, pos, neg = set(), set(), set()\n        board = [['.'] * n for _ in range(n)]\n        res = []\n        def dfs(r):\n            if r == n:\n                res.append([''.join(row) for row in board])\n                return\n            for c in range(n):\n                if c in cols or (r + c) in pos or (r - c) in neg:\n                    continue\n                cols.add(c); pos.add(r + c); neg.add(r - c)\n                board[r][c] = 'Q'\n                dfs(r + 1)\n                board[r][c] = '.'\n                cols.remove(c); pos.remove(r + c); neg.remove(r - c)\n        dfs(0)\n        return res\n",
    },
    {
        "id": 76, "slug": "number-of-islands", "method": "numIslands",
        "pySig": "def numIslands(self, grid: List[List[str]]) -> int:",
        "javaSig": "public int numIslands(char[][] grid)", "javaRet": "return 0;",
        "time": "O(R * C)", "space": "O(R * C)", "invariant": "Flood-fill sink connected '1' cells to '0' and increment island count",
        "prompt": "Given a 2D `grid` of `'1'`s (land) and `'0'`s (water), count the number of islands.",
        "firstLine": "Set `islands = 0` and write `sink(r, c)` that flips `'1'` to `'0'` across 4 neighbors.",
        "steps": [
            "Write `sink(r, c)`: return if out-of-bounds or `grid[r][c] != '1'`; set `grid[r][c] = '0'` and recurse 4 ways",
            "Loop over every `(r, c)` in `grid`: if `grid[r][c] == '1'`, increment `islands += 1` and call `sink(r, c)`",
            "Return `islands`"
        ],
        "cases": [
            {"input": {"grid": [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]]}, "expected": 3},
            {"input": {"grid": [["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def numIslands(self, grid: List[List[str]]) -> int:\n        R, C = len(grid), len(grid[0])\n        def sink(r, c):\n            if r < 0 or r >= R or c < 0 or c >= C or grid[r][c] != '1':\n                return\n            grid[r][c] = '0'\n            sink(r+1, c); sink(r-1, c); sink(r, c+1); sink(r, c-1)\n        ans = 0\n        for r in range(R):\n            for c in range(C):\n                if grid[r][c] == '1':\n                    ans += 1\n                    sink(r, c)\n        return ans\n",
    },
    {
        "id": 77, "slug": "clone-graph", "method": "cloneGraph",
        "argTypes": {"node": "GraphNode"}, "returnType": "GraphNode",
        "pySig": "def cloneGraph(self, node: Optional[GraphNode]) -> Optional[GraphNode]:",
        "javaSig": "public Object cloneGraph(Object node)", "javaRet": "return null;",
        "time": "O(V + E)", "space": "O(V)", "invariant": "old_to_new map breaks graph cycles during DFS/BFS cloning",
        "prompt": "Return a deep copy of a connected undirected graph starting from `node`.",
        "firstLine": "Guard `if not node: return None`, create `clones = {}`, and memoize `dfs(curr)` BEFORE recursing on neighbors.",
        "steps": [
            "Return `None` if `not node`; store `clones = {}`",
            "In `dfs(n)`: if `n in clones`, return `clones[n]`; create `copy = GraphNode(n.val)` and store `clones[n] = copy`",
            "Populate `copy.neighbors = [dfs(nb) for nb in n.neighbors]` and return `copy`"
        ],
        "cases": [
            {"input": {"node": [[2, 4], [1, 3], [2, 4], [1, 3]]}, "expected": [[2, 4], [1, 3], [2, 4], [1, 3]]},
            {"input": {"node": []}, "expected": []},
        ],
        "refPy": "class Solution:\n    def cloneGraph(self, node: Optional[GraphNode]) -> Optional[GraphNode]:\n        if not node:\n            return None\n        clones = {}\n        def dfs(n):\n            if n in clones:\n                return clones[n]\n            cp = GraphNode(n.val)\n            clones[n] = cp\n            for nb in n.neighbors:\n                cp.neighbors.append(dfs(nb))\n            return cp\n        return dfs(node)\n",
    },
    {
        "id": 78, "slug": "max-area-of-island", "method": "maxAreaOfIsland",
        "pySig": "def maxAreaOfIsland(self, grid: List[List[int]]) -> int:",
        "javaSig": "public int maxAreaOfIsland(int[][] grid)", "javaRet": "return 0;",
        "time": "O(R * C)", "space": "O(R * C)", "invariant": "area(r, c) = 1 + sum of 4 neighbors after marking grid[r][c] = 0",
        "prompt": "Given binary matrix `grid`, return the maximum area of an island (`0` if no land).",
        "firstLine": "Write `dfs(r, c)` returning `0` on water/bounds, else zeroing `grid[r][c]` and returning `1 + 4-way sum`.",
        "steps": [
            "Define `dfs(r, c)`: if out-of-bounds or `grid[r][c] == 0`, return `0`",
            "Mark `grid[r][c] = 0` and return `1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)`",
            "Return the maximum `dfs(r, c)` across all cells"
        ],
        "cases": [
            {"input": {"grid": [[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0], [1, 1, 0, 0, 0]]}, "expected": 4},
            {"input": {"grid": [[0, 0, 0]]}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:\n        R, C = len(grid), len(grid[0])\n        def dfs(r, c):\n            if r < 0 or r >= R or c < 0 or c >= C or grid[r][c] == 0:\n                return 0\n            grid[r][c] = 0\n            return 1 + dfs(r+1, c) + dfs(r-1, c) + dfs(r, c+1) + dfs(r, c-1)\n        return max((dfs(r, c) for r in range(R) for c in range(C)), default=0)\n",
    },
    {
        "id": 79, "slug": "pacific-atlantic-water-flow", "method": "pacificAtlantic", "compareMode": "unordered",
        "pySig": "def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> pacificAtlantic(int[][] heights)", "javaRet": "return new ArrayList<>();",
        "time": "O(R * C)", "space": "O(R * C)", "invariant": "Reverse uphill flood from Pacific borders & Atlantic borders -> set intersection",
        "prompt": "Return all `[r, c]` grid coordinates from which rain water can flow to BOTH the Pacific (top/left) and Atlantic (bottom/right) oceans.",
        "firstLine": "Create two visited sets `pac = set()` and `atl = set()`, flooding uphill (`heights[nr][nc] >= heights[r][c]`) from ocean borders.",
        "steps": [
            "Write `dfs(r, c, visit, prev_h)` moving to neighbors with `heights >= prev_h`",
            "Seed `pac` from top row & left col; seed `atl` from bottom row & right col",
            "Return `[[r, c] for (r, c) in (pac & atl)]`"
        ],
        "cases": [
            {"input": {"heights": [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]}, "expected": [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]},
            {"input": {"heights": [[1]]}, "expected": [[0, 0]]},
        ],
        "refPy": "class Solution:\n    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:\n        R, C = len(heights), len(heights[0])\n        pac, atl = set(), set()\n        def dfs(r, c, vis, prev):\n            if (r, c) in vis or r < 0 or r >= R or c < 0 or c >= C or heights[r][c] < prev:\n                return\n            vis.add((r, c))\n            h = heights[r][c]\n            dfs(r+1, c, vis, h); dfs(r-1, c, vis, h); dfs(r, c+1, vis, h); dfs(r, c-1, vis, h)\n        for c in range(C):\n            dfs(0, c, pac, heights[0][c])\n            dfs(R-1, c, atl, heights[R-1][c])\n        for r in range(R):\n            dfs(r, 0, pac, heights[r][0])\n            dfs(r, C-1, atl, heights[r][C-1])\n        return [[r, c] for r, c in (pac & atl)]\n",
    },
    {
        "id": 80, "slug": "surrounded-regions", "method": "solve", "returnType": "InPlaceArg0",
        "pySig": "def solve(self, board: List[List[str]]) -> None:",
        "javaSig": "public void solve(char[][] board)", "javaRet": "",
        "time": "O(R * C)", "space": "O(R * C)", "invariant": "Mark border-connected 'O's as 'T'; flip remaining 'O' -> 'X', then 'T' -> 'O'",
        "prompt": "Capture all `'O'` regions completely surrounded by `'X'` in-place by flipping surrounded `'O'`s to `'X'`.",
        "firstLine": "DFS from all border `'O'` cells marking them safe as `'T'`.",
        "steps": [
            "Run DFS from every border cell with `'O'`, temporarily marking safe regions as `'T'`",
            "Scan the board: flip remaining `'O'` cells (surrounded!) to `'X'`",
            "Restore `'T'` cells back to `'O'`"
        ],
        "cases": [
            {"input": {"board": [["X", "X", "X", "X"], ["X", "O", "O", "X"], ["X", "X", "O", "X"], ["X", "O", "X", "X"]]}, "expected": [["X", "X", "X", "X"], ["X", "X", "X", "X"], ["X", "X", "X", "X"], ["X", "O", "X", "X"]]},
        ],
        "refPy": "class Solution:\n    def solve(self, board: List[List[str]]) -> None:\n        R, C = len(board), len(board[0])\n        def dfs(r, c):\n            if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != 'O':\n                return\n            board[r][c] = 'T'\n            dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)\n        for r in range(R):\n            dfs(r, 0); dfs(r, C-1)\n        for c in range(C):\n            dfs(0, c); dfs(R-1, c)\n        for r in range(R):\n            for c in range(C):\n                if board[r][c] == 'O': board[r][c] = 'X'\n                elif board[r][c] == 'T': board[r][c] = 'O'\n",
    },
    {
        "id": 81, "slug": "rotting-oranges", "method": "orangesRotting",
        "pySig": "def orangesRotting(self, grid: List[List[int]]) -> int:",
        "javaSig": "public int orangesRotting(int[][] grid)", "javaRet": "return -1;",
        "time": "O(R * C)", "space": "O(R * C)", "invariant": "Multi-source BFS from all initial rotten (2) cells simultaneously",
        "prompt": "Given `grid` (`0`=empty, `1`=fresh, `2`=rotten), return minimum minutes until zero fresh oranges remain, or `-1` if impossible.",
        "firstLine": "Seed `q = deque()` with all rotten `(r, c)` cells and count initial `fresh` oranges.",
        "steps": [
            "Scan `grid`: count `fresh` (`1`s) and enqueue all rotten (`2`s) into `q`",
            "While `q and fresh > 0`: pop one full BFS wave, rotting adjacent `1`s (`grid[nr][nc] = 2`, `fresh -= 1`) and incrementing `minutes += 1`",
            "Return `minutes` if `fresh == 0` else `-1`"
        ],
        "cases": [
            {"input": {"grid": [[2, 1, 1], [1, 1, 0], [0, 1, 1]]}, "expected": 4},
            {"input": {"grid": [[2, 1, 1], [0, 1, 1], [1, 0, 1]]}, "expected": -1},
        ],
        "refPy": "class Solution:\n    def orangesRotting(self, grid: List[List[int]]) -> int:\n        R, C = len(grid), len(grid[0])\n        q = deque()\n        fresh = 0\n        for r in range(R):\n            for c in range(C):\n                if grid[r][c] == 2: q.append((r, c))\n                elif grid[r][c] == 1: fresh += 1\n        mins = 0\n        while q and fresh > 0:\n            for _ in range(len(q)):\n                r, c = q.popleft()\n                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n                    nr, nc = r + dr, c + dc\n                    if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:\n                        grid[nr][nc] = 2\n                        fresh -= 1\n                        q.append((nr, nc))\n            mins += 1\n        return mins if fresh == 0 else -1\n",
    },
    {
        "id": 82, "slug": "course-schedule", "method": "canFinish",
        "pySig": "def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:",
        "javaSig": "public boolean canFinish(int numCourses, int[][] prerequisites)", "javaRet": "return true;",
        "time": "O(V + E)", "space": "O(V + E)", "invariant": "Kahn's topological BFS: acyclic iff visited_count == numCourses",
        "prompt": "Given `numCourses` and `[course, prereq]` pairs, return `True` if you can finish all courses (no directed cycle).",
        "firstLine": "Build `adj = defaultdict(list)` and `indeg = [0] * numCourses`, then enqueue all zero-indegree courses.",
        "steps": [
            "Populate `adj[pre].append(crs)` and `indeg[crs] += 1`",
            "Push all `c` with `indeg[c] == 0` into `q = deque()`",
            "Pop from `q`, increment `done += 1`, decrement neighbor indegrees (enqueuing when `0`), and return `done == numCourses`"
        ],
        "cases": [
            {"input": {"numCourses": 2, "prerequisites": [[1, 0]]}, "expected": True},
            {"input": {"numCourses": 2, "prerequisites": [[1, 0], [0, 1]]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:\n        adj = defaultdict(list)\n        indeg = [0] * numCourses\n        for crs, pre in prerequisites:\n            adj[pre].append(crs)\n            indeg[crs] += 1\n        q = deque(i for i in range(numCourses) if indeg[i] == 0)\n        done = 0\n        while q:\n            u = q.popleft()\n            done += 1\n            for v in adj[u]:\n                indeg[v] -= 1\n                if indeg[v] == 0:\n                    q.append(v)\n        return done == numCourses\n",
    },
    {
        "id": 83, "slug": "course-schedule-ii", "method": "findOrder", "compareMode": "any_of",
        "pySig": "def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:",
        "javaSig": "public int[] findOrder(int numCourses, int[][] prerequisites)", "javaRet": "return new int[]{};",
        "time": "O(V + E)", "space": "O(V + E)", "invariant": "Kahn's BFS order list; return [] if cycle leaves len(order) < numCourses",
        "prompt": "Return a valid course ordering to finish all `numCourses`, or `[]` if a cycle makes it impossible.",
        "firstLine": "Build `adj` + `indeg`, seed `q` with `indeg == 0` courses, and record popped courses into `order = []`.",
        "steps": [
            "Build `adj[pre].append(crs)` and `indeg[crs] += 1`",
            "Pop zero-indegree nodes from `q`, append to `order`, and push neighbors whose `indeg` drops to `0`",
            "Return `order` if `len(order) == numCourses` else `[]`"
        ],
        "cases": [
            {"input": {"numCourses": 4, "prerequisites": [[1, 0], [2, 0], [3, 1], [3, 2]]}, "expected": [[0, 1, 2, 3], [0, 2, 1, 3]]},
            {"input": {"numCourses": 2, "prerequisites": [[1, 0], [0, 1]]}, "expected": [[]]},
        ],
        "refPy": "class Solution:\n    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:\n        adj = defaultdict(list)\n        indeg = [0] * numCourses\n        for crs, pre in prerequisites:\n            adj[pre].append(crs)\n            indeg[crs] += 1\n        q = deque(i for i in range(numCourses) if indeg[i] == 0)\n        order = []\n        while q:\n            u = q.popleft()\n            order.append(u)\n            for v in adj[u]:\n                indeg[v] -= 1\n                if indeg[v] == 0:\n                    q.append(v)\n        return order if len(order) == numCourses else []\n",
    },
    {
        "id": 84, "slug": "graph-valid-tree", "method": "validTree",
        "pySig": "def validTree(self, n: int, edges: List[List[int]]) -> bool:",
        "javaSig": "public boolean validTree(int n, int[][] edges)", "javaRet": "return false;",
        "time": "O(V + E)", "space": "O(V)", "invariant": "Tree iff len(edges) == n - 1 AND zero Union-Find cycles",
        "prompt": "Given `n` nodes (`0..n-1`) and undirected `edges`, return `True` if the edges form a valid tree.",
        "firstLine": "Check `if len(edges) != n - 1: return False`, then Union-Find `parent = list(range(n))`.",
        "steps": [
            "Immediately return `False` if `len(edges) != n - 1`",
            "Initialize `parent = list(range(n))` with path-compressed `find(x)`",
            "For `u, v` in `edges`: if `find(u) == find(v)` return `False`, else union them; return `True`"
        ],
        "cases": [
            {"input": {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [1, 4]]}, "expected": True},
            {"input": {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def validTree(self, n: int, edges: List[List[int]]) -> bool:\n        if len(edges) != n - 1:\n            return False\n        p = list(range(n))\n        def find(x):\n            while p[x] != x:\n                p[x] = p[p[x]]\n                x = p[x]\n            return x\n        for u, v in edges:\n            ru, rv = find(u), find(v)\n            if ru == rv:\n                return False\n            p[ru] = rv\n        return True\n",
    },
    {
        "id": 85, "slug": "number-of-connected-components-in-an-undirected-graph", "method": "countComponents",
        "pySig": "def countComponents(self, n: int, edges: List[List[int]]) -> int:",
        "javaSig": "public int countComponents(int n, int[][] edges)", "javaRet": "return n;",
        "time": "O(V + E)", "space": "O(V)", "invariant": "Start with n components; each successful Union-Find merge decrements count by 1",
        "prompt": "Given `n` nodes and undirected `edges`, return the number of connected components.",
        "firstLine": "Initialize `parent = list(range(n))` and `comps = n`.",
        "steps": [
            "Initialize `parent = list(range(n))` and `comps = n`",
            "Write `find(x)` with path compression",
            "For `u, v` in `edges`: if `find(u) != find(v)`, union them and decrement `comps -= 1`; return `comps`"
        ],
        "cases": [
            {"input": {"n": 5, "edges": [[0, 1], [1, 2], [3, 4]]}, "expected": 2},
            {"input": {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def countComponents(self, n: int, edges: List[List[int]]) -> int:\n        p = list(range(n))\n        comps = n\n        def find(x):\n            while p[x] != x:\n                p[x] = p[p[x]]\n                x = p[x]\n            return x\n        for u, v in edges:\n            ru, rv = find(u), find(v)\n            if ru != rv:\n                p[ru] = rv\n                comps -= 1\n        return comps\n",
    },
    {
        "id": 86, "slug": "redundant-connection", "method": "findRedundantConnection",
        "pySig": "def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:",
        "javaSig": "public int[] findRedundantConnection(int[][] edges)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "First edge [u, v] whose endpoints already share a Union-Find root closes the cycle",
        "prompt": "Given a tree of `1..n` plus one extra cycle-creating edge, return that redundant edge.",
        "firstLine": "Initialize `parent = list(range(len(edges) + 1))` and union edges one by one.",
        "steps": [
            "Create `parent = list(range(len(edges) + 1))`",
            "For `u, v` in `edges`: find roots `ru, rv`",
            "If `ru == rv`, return `[u, v]`; otherwise set `parent[ru] = rv`"
        ],
        "cases": [
            {"input": {"edges": [[1, 2], [1, 3], [2, 3]]}, "expected": [2, 3]},
            {"input": {"edges": [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]}, "expected": [1, 4]},
        ],
        "refPy": "class Solution:\n    def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:\n        p = list(range(len(edges) + 1))\n        def find(x):\n            while p[x] != x:\n                p[x] = p[p[x]]\n                x = p[x]\n            return x\n        for u, v in edges:\n            ru, rv = find(u), find(v)\n            if ru == rv:\n                return [u, v]\n            p[ru] = rv\n        return []\n",
    },
    {
        "id": 87, "slug": "word-ladder", "method": "ladderLength",
        "pySig": "def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:",
        "javaSig": "public int ladderLength(String beginWord, String endWord, List<String> wordList)", "javaRet": "return 0;",
        "time": "O(N * L^2)", "space": "O(N * L^2)", "invariant": "Wildcard pattern buckets (h*t -> hot, hit) + unweighted shortest-path BFS",
        "prompt": "Return the number of words in the shortest single-letter transformation sequence from `beginWord` to `endWord` (`0` if unreachable).",
        "firstLine": "Guard `if endWord not in wordList: return 0`, index wildcard patterns `w[:i] + '*' + w[i+1:]`, and run BFS.",
        "steps": [
            "Return `0` if `endWord` is absent; build `patterns[pat].append(word)` for `wordList + [beginWord]`",
            "Run level-order BFS starting from `q = deque([(beginWord, 1)])` and `visited = {beginWord}`",
            "Return `steps` as soon as `word == endWord`, or `0` if `q` empties"
        ],
        "cases": [
            {"input": {"beginWord": "hit", "endWord": "cog", "wordList": ["hot", "dot", "dog", "lot", "log", "cog"]}, "expected": 5},
            {"input": {"beginWord": "hit", "endWord": "cog", "wordList": ["hot", "dot", "dog", "lot", "log"]}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:\n        if endWord not in wordList:\n            return 0\n        pats = defaultdict(list)\n        for w in set(wordList) | {beginWord}:\n            for i in range(len(w)):\n                pats[w[:i] + '*' + w[i+1:]].append(w)\n        q = deque([(beginWord, 1)])\n        vis = {beginWord}\n        while q:\n            w, d = q.popleft()\n            if w == endWord:\n                return d\n            for i in range(len(w)):\n                for nw in pats[w[:i] + '*' + w[i+1:]]:\n                    if nw not in vis:\n                        vis.add(nw)\n                        q.append((nw, d + 1))\n        return 0\n",
    },
    {
        "id": 88, "slug": "climbing-stairs", "method": "climbStairs",
        "pySig": "def climbStairs(self, n: int) -> int:",
        "javaSig": "public int climbStairs(int n)", "javaRet": "return 1;",
        "time": "O(N)", "space": "O(1)", "invariant": "ways(i) = ways(i - 1) + ways(i - 2) rolling Fibonacci pair",
        "prompt": "You can climb `1` or `2` steps at a time; return how many distinct ways reach step `n`.",
        "firstLine": "Set `one, two = 1, 1` and roll forward `n - 1` times.",
        "steps": [
            "Initialize `a, b = 1, 1`",
            "Loop `n - 1` times updating `a, b = b, a + b`",
            "Return `b` (handling `n == 1` cleanly)"
        ],
        "cases": [
            {"input": {"n": 2}, "expected": 2},
            {"input": {"n": 3}, "expected": 3},
            {"input": {"n": 5}, "expected": 8},
        ],
        "refPy": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        a, b = 1, 1\n        for _ in range(n - 1):\n            a, b = b, a + b\n        return b\n",
    },
    {
        "id": 89, "slug": "min-cost-climbing-stairs", "method": "minCostClimbingStairs",
        "pySig": "def minCostClimbingStairs(self, cost: List[int]) -> int:",
        "javaSig": "public int minCostClimbingStairs(int[] cost)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "dp[i] = cost[i] + min(dp[i+1], dp[i+2])",
        "prompt": "Given step `cost`, you may start at index `0` or `1` and climb `1` or `2` steps; return minimum cost to reach past the top.",
        "firstLine": "Track two rolling variables `prev2, prev1 = cost[0], cost[1]`.",
        "steps": [
            "Initialize `a, b = cost[0], cost[1]`",
            "For `i` from `2` to `len(cost) - 1`, update `a, b = b, cost[i] + min(a, b)`",
            "Return `min(a, b)`"
        ],
        "cases": [
            {"input": {"cost": [10, 15, 20]}, "expected": 15},
            {"input": {"cost": [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]}, "expected": 6},
        ],
        "refPy": "class Solution:\n    def minCostClimbingStairs(self, cost: List[int]) -> int:\n        a, b = cost[0], cost[1]\n        for i in range(2, len(cost)):\n            a, b = b, cost[i] + min(a, b)\n        return min(a, b)\n",
    },
    {
        "id": 90, "slug": "house-robber", "method": "rob",
        "pySig": "def rob(self, nums: List[int]) -> int:",
        "javaSig": "public int rob(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "rob1, rob2 = rob2, max(rob1 + x, rob2)",
        "prompt": "Given non-negative `nums` representing cash in each house (cannot rob adjacent houses), return the max cash.",
        "firstLine": "Set `rob1, rob2 = 0, 0` and loop over `x` in `nums`.",
        "steps": [
            "Initialize `rob1 = 0`, `rob2 = 0`",
            "For each `x` in `nums`, compute `nxt = max(rob1 + x, rob2)` and shift `rob1, rob2 = rob2, nxt`",
            "Return `rob2`"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 3, 1]}, "expected": 4},
            {"input": {"nums": [2, 7, 9, 3, 1]}, "expected": 12},
        ],
        "refPy": "class Solution:\n    def rob(self, nums: List[int]) -> int:\n        r1 = r2 = 0\n        for x in nums:\n            r1, r2 = r2, max(r1 + x, r2)\n        return r2\n",
    },
    {
        "id": 91, "slug": "house-robber-ii", "method": "rob",
        "pySig": "def rob(self, nums: List[int]) -> int:",
        "javaSig": "public int rob(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "Circular ring -> max(nums[0], linear_rob(nums[:-1]), linear_rob(nums[1:]))",
        "prompt": "Houses are arranged in a circle (first & last are adjacent); return maximum non-adjacent cash.",
        "firstLine": "Handle single-house `nums[0]`, then run linear `rob_line` on `nums[:-1]` and `nums[1:]`.",
        "steps": [
            "If `len(nums) == 1`, return `nums[0]`",
            "Write `rob_line(arr)` using two rolling variables `r1, r2`",
            "Return `max(rob_line(nums[:-1]), rob_line(nums[1:]))`"
        ],
        "cases": [
            {"input": {"nums": [2, 3, 2]}, "expected": 3},
            {"input": {"nums": [1, 2, 3, 1]}, "expected": 4},
            {"input": {"nums": [5]}, "expected": 5},
        ],
        "refPy": "class Solution:\n    def rob(self, nums: List[int]) -> int:\n        if len(nums) == 1:\n            return nums[0]\n        def line(arr):\n            r1 = r2 = 0\n            for x in arr:\n                r1, r2 = r2, max(r1 + x, r2)\n            return r2\n        return max(line(nums[:-1]), line(nums[1:]))\n",
    },
    {
        "id": 92, "slug": "longest-palindromic-substring", "method": "longestPalindrome", "compareMode": "any_of",
        "pySig": "def longestPalindrome(self, s: str) -> str:",
        "javaSig": "public String longestPalindrome(String s)", "javaRet": "return \"\";",
        "time": "O(N^2)", "space": "O(1)", "invariant": "Expand around every odd center (i, i) and even center (i, i + 1)",
        "prompt": "Given string `s`, return the longest palindromic substring in `s`.",
        "firstLine": "Write helper `expand(l, r)` returning `(start, end)` and check both `(i, i)` and `(i, i + 1)` at each `i`.",
        "steps": [
            "Write `expand(l, r)` expanding outward while `l >= 0 and r < len(s) and s[l] == s[r]`",
            "For each `i` in `range(len(s))`, test odd center `(i, i)` and even center `(i, i + 1)`",
            "Track and return the longest slice `s[best_l : best_r]`"
        ],
        "cases": [
            {"input": {"s": "babad"}, "expected": ["bab", "aba"]},
            {"input": {"s": "cbbd"}, "expected": ["bb"]},
        ],
        "refPy": "class Solution:\n    def longestPalindrome(self, s: str) -> str:\n        best = ''\n        for i in range(len(s)):\n            for l, r in ((i, i), (i, i + 1)):\n                while l >= 0 and r < len(s) and s[l] == s[r]:\n                    if r - l + 1 > len(best):\n                        best = s[l:r+1]\n                    l -= 1; r += 1\n        return best\n",
    },
    {
        "id": 93, "slug": "palindromic-substrings", "method": "countSubstrings",
        "pySig": "def countSubstrings(self, s: str) -> int:",
        "javaSig": "public int countSubstrings(String s)", "javaRet": "return 0;",
        "time": "O(N^2)", "space": "O(1)", "invariant": "Count expansions from every odd (i, i) and even (i, i + 1) center",
        "prompt": "Given string `s`, return the number of palindromic substrings in it.",
        "firstLine": "Set `count = 0` and expand outward from `(i, i)` and `(i, i + 1)` for every `i`.",
        "steps": [
            "Initialize `count = 0`",
            "For every index `i`, expand `(l, r)` from `(i, i)` and `(i, i + 1)`",
            "Increment `count += 1` each step while `s[l] == s[r]`"
        ],
        "cases": [
            {"input": {"s": "abc"}, "expected": 3},
            {"input": {"s": "aaa"}, "expected": 6},
        ],
        "refPy": "class Solution:\n    def countSubstrings(self, s: str) -> int:\n        cnt = 0\n        for i in range(len(s)):\n            for l, r in ((i, i), (i, i + 1)):\n                while l >= 0 and r < len(s) and s[l] == s[r]:\n                    cnt += 1\n                    l -= 1; r += 1\n        return cnt\n",
    },
    {
        "id": 94, "slug": "decode-ways", "method": "numDecodings",
        "pySig": "def numDecodings(self, s: str) -> int:",
        "javaSig": "public int numDecodings(String s)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "dp[i] = (dp[i+1] if s[i]!='0') + (dp[i+2] if 10 <= int(s[i:i+2]) <= 26)",
        "prompt": "Given digit string `s` (`'1'->'A' .. '26'->'Z'`), return the number of ways to decode it.",
        "firstLine": "Scan right-to-left with `dp1, dp2 = 1, 0` (`dp[n] = 1`).",
        "steps": [
            "Initialize `dp1, dp2 = 1, 0`",
            "Loop `i` from `len(s) - 1` down to `0`: if `s[i] == '0'`, `cur = 0`; else `cur = dp1` (+ `dp2` if `10 <= int(s[i:i+2]) <= 26`)",
            "Shift `dp1, dp2 = cur, dp1` and return `dp1`"
        ],
        "cases": [
            {"input": {"s": "12"}, "expected": 2},
            {"input": {"s": "226"}, "expected": 3},
            {"input": {"s": "06"}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def numDecodings(self, s: str) -> int:\n        dp1, dp2 = 1, 0\n        for i in range(len(s) - 1, -1, -1):\n            if s[i] == '0':\n                cur = 0\n            else:\n                cur = dp1\n                if i + 1 < len(s) and 10 <= int(s[i:i+2]) <= 26:\n                    cur += dp2\n            dp1, dp2 = cur, dp1\n        return dp1\n",
    },
    {
        "id": 95, "slug": "coin-change", "method": "coinChange",
        "pySig": "def coinChange(self, coins: List[int], amount: int) -> int:",
        "javaSig": "public int coinChange(int[] coins, int amount)", "javaRet": "return -1;",
        "time": "O(amount * len(coins))", "space": "O(amount)", "invariant": "dp[a] = min(dp[a], 1 + dp[a - c]) with sentinel amount + 1",
        "prompt": "Given `coins` denominations and `amount`, return the fewest coins needed to make `amount` (`-1` if impossible).",
        "firstLine": "Create `dp = [amount + 1] * (amount + 1)` with base case `dp[0] = 0`.",
        "steps": [
            "Allocate `dp = [amount + 1] * (amount + 1)` and set `dp[0] = 0`",
            "For `a` from `1` to `amount` and each `c` in `coins`: if `a >= c`, set `dp[a] = min(dp[a], 1 + dp[a - c])`",
            "Return `dp[amount]` if `<= amount` else `-1`"
        ],
        "cases": [
            {"input": {"coins": [1, 2, 5], "amount": 11}, "expected": 3},
            {"input": {"coins": [2], "amount": 3}, "expected": -1},
            {"input": {"coins": [1], "amount": 0}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def coinChange(self, coins: List[int], amount: int) -> int:\n        dp = [amount + 1] * (amount + 1)\n        dp[0] = 0\n        for a in range(1, amount + 1):\n            for c in coins:\n                if a >= c and dp[a - c] + 1 < dp[a]:\n                    dp[a] = dp[a - c] + 1\n        return dp[amount] if dp[amount] <= amount else -1\n",
    },
    {
        "id": 96, "slug": "maximum-product-subarray", "method": "maxProduct",
        "pySig": "def maxProduct(self, nums: List[int]) -> int:",
        "javaSig": "public int maxProduct(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "Track BOTH cur_max and cur_min because a negative flips min into max",
        "prompt": "Given integer array `nums`, find a contiguous non-empty subarray with the largest product and return that product.",
        "firstLine": "Track `best = nums[0]` and `cur_min = cur_max = 1`.",
        "steps": [
            "Initialize `best = max(nums)` and `cur_min = cur_max = 1`",
            "For `x` in `nums`: compute candidates `(x, x * cur_max, x * cur_min)`",
            "Set `cur_max = max(cands)`, `cur_min = min(cands)`, and `best = max(best, cur_max)`"
        ],
        "cases": [
            {"input": {"nums": [2, 3, -2, 4]}, "expected": 6},
            {"input": {"nums": [-2, 0, -1]}, "expected": 0},
            {"input": {"nums": [-2, 3, -4]}, "expected": 24},
        ],
        "refPy": "class Solution:\n    def maxProduct(self, nums: List[int]) -> int:\n        best = max(nums)\n        cmin = cmax = 1\n        for x in nums:\n            cands = (x, x * cmax, x * cmin)\n            cmax, cmin = max(cands), min(cands)\n            best = max(best, cmax)\n        return best\n",
    },
    {
        "id": 97, "slug": "word-break", "method": "wordBreak",
        "pySig": "def wordBreak(self, s: str, wordDict: List[str]) -> bool:",
        "javaSig": "public boolean wordBreak(String s, List<String> wordDict)", "javaRet": "return false;",
        "time": "O(N * W * L)", "space": "O(N)", "invariant": "dp[i] is True iff some word w matches s[i:i+len(w)] and dp[i+len(w)] is True",
        "prompt": "Return `True` if string `s` can be segmented into a space-separated sequence of words from `wordDict`.",
        "firstLine": "Create `dp = [False] * (len(s) + 1)` with `dp[len(s)] = True`.",
        "steps": [
            "Allocate `dp = [False] * (len(s) + 1)` and set `dp[len(s)] = True`",
            "Loop `i` from `len(s) - 1` down to `0` and check each `w` in `wordDict`",
            "If `s.startswith(w, i)` and `dp[i + len(w)]`, set `dp[i] = True` and `break`; return `dp[0]`"
        ],
        "cases": [
            {"input": {"s": "leetcode", "wordDict": ["leet", "code"]}, "expected": True},
            {"input": {"s": "catsandog", "wordDict": ["cats", "dog", "sand", "and", "cat"]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def wordBreak(self, s: str, wordDict: List[str]) -> bool:\n        dp = [False] * (len(s) + 1)\n        dp[len(s)] = True\n        for i in range(len(s) - 1, -1, -1):\n            for w in wordDict:\n                if s.startswith(w, i) and dp[i + len(w)]:\n                    dp[i] = True\n                    break\n        return dp[0]\n",
    },
    {
        "id": 98, "slug": "longest-increasing-subsequence", "method": "lengthOfLIS",
        "pySig": "def lengthOfLIS(self, nums: List[int]) -> int:",
        "javaSig": "public int lengthOfLIS(int[] nums)", "javaRet": "return 0;",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Patience-sorting `tails` array maintained via bisect_left",
        "prompt": "Given integer array `nums`, return the length of the longest strictly increasing subsequence.",
        "firstLine": "Create `tails = []` and place each `x` at `idx = bisect_left(tails, x)`.",
        "steps": [
            "Initialize `tails = []`",
            "For `x` in `nums`: find `idx = bisect_left(tails, x)`",
            "If `idx == len(tails)`, append `x`; else overwrite `tails[idx] = x`; return `len(tails)`"
        ],
        "cases": [
            {"input": {"nums": [10, 9, 2, 5, 3, 7, 101, 18]}, "expected": 4},
            {"input": {"nums": [0, 1, 0, 3, 2, 3]}, "expected": 4},
            {"input": {"nums": [7, 7, 7, 7]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def lengthOfLIS(self, nums: List[int]) -> int:\n        tails = []\n        for x in nums:\n            i = bisect_left(tails, x)\n            if i == len(tails):\n                tails.append(x)\n            else:\n                tails[i] = x\n        return len(tails)\n",
    },
    {
        "id": 99, "slug": "partition-equal-subset-sum", "method": "canPartition",
        "pySig": "def canPartition(self, nums: List[int]) -> bool:",
        "javaSig": "public boolean canPartition(int[] nums)", "javaRet": "return false;",
        "time": "O(N * sum)", "space": "O(sum)", "invariant": "0/1 knapsack reachable sums set toward total // 2",
        "prompt": "Return `True` if `nums` can be partitioned into two subsets with equal sum.",
        "firstLine": "Guard `total = sum(nums); if total % 2: return False`, then track reachable sums `dp = {0}`.",
        "steps": [
            "Compute `total = sum(nums)`; return `False` if odd, else `target = total // 2`",
            "Maintain `dp = {0}`; for each `x` in `nums`, update `dp |= {s + x for s in dp if s + x <= target}`",
            "Return `target in dp`"
        ],
        "cases": [
            {"input": {"nums": [1, 5, 11, 5]}, "expected": True},
            {"input": {"nums": [1, 2, 3, 5]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def canPartition(self, nums: List[int]) -> bool:\n        tot = sum(nums)\n        if tot % 2:\n            return False\n        target = tot // 2\n        dp = {0}\n        for x in nums:\n            dp = dp | {s + x for s in dp if s + x <= target}\n            if target in dp:\n                return True\n        return target in dp\n",
    },
]
