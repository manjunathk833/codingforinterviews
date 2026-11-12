"""DSA Catalog Specs — Group 4: Problems #100 to #128 (2D DP, Greedy & Intervals, Design & Concurrency, Bit Manipulation) + 12 Warmup Drills."""

SPECS_G4 = [
    {
        "id": 100, "slug": "unique-paths", "method": "uniquePaths",
        "pySig": "def uniquePaths(self, m: int, n: int) -> int:",
        "javaSig": "public int uniquePaths(int m, int n)", "javaRet": "return 1;",
        "time": "O(M * N)", "space": "O(N)", "invariant": "row[c] = row[c] (from above) + row[c + 1] (from right)",
        "prompt": "A robot starts at top-left of an `m x n` grid and can only move right or down. Return how many unique paths reach bottom-right.",
        "firstLine": "Create a 1D DP row `row = [1] * n` representing paths from the bottom row.",
        "steps": [
            "Initialize `row = [1] * n` (bottom edge has 1 path everywhere)",
            "Repeat `m - 1` times updating right-to-left: `for c in range(n - 2, -1, -1): row[c] += row[c + 1]`",
            "Return `row[0]`"
        ],
        "cases": [
            {"input": {"m": 3, "n": 7}, "expected": 28},
            {"input": {"m": 3, "n": 2}, "expected": 3},
            {"input": {"m": 1, "n": 1}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def uniquePaths(self, m: int, n: int) -> int:\n        row = [1] * n\n        for _ in range(m - 1):\n            for c in range(n - 2, -1, -1):\n                row[c] += row[c + 1]\n        return row[0]\n",
    },
    {
        "id": 101, "slug": "longest-common-subsequence", "method": "longestCommonSubsequence",
        "pySig": "def longestCommonSubsequence(self, text1: str, text2: str) -> int:",
        "javaSig": "public int longestCommonSubsequence(String text1, String text2)", "javaRet": "return 0;",
        "time": "O(M * N)", "space": "O(M * N)", "invariant": "match -> 1 + dp[i+1][j+1]; mismatch -> max(dp[i+1][j], dp[i][j+1])",
        "prompt": "Given two strings `text1` and `text2`, return the length of their longest common subsequence.",
        "firstLine": "Create a zero-padded `(m + 1) x (n + 1)` 2D table `dp` and fill bottom-up.",
        "steps": [
            "Allocate `dp = [[0] * (len(text2) + 1) for _ in range(len(text1) + 1)]`",
            "Loop `i` backward from `len(text1)-1` and `j` backward from `len(text2)-1`",
            "If `text1[i] == text2[j]`, set `dp[i][j] = 1 + dp[i+1][j+1]`; else `max(dp[i+1][j], dp[i][j+1])`; return `dp[0][0]`"
        ],
        "cases": [
            {"input": {"text1": "abcde", "text2": "ace"}, "expected": 3},
            {"input": {"text1": "abc", "text2": "def"}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def longestCommonSubsequence(self, text1: str, text2: str) -> int:\n        m, n = len(text1), len(text2)\n        dp = [[0] * (n + 1) for _ in range(m + 1)]\n        for i in range(m - 1, -1, -1):\n            for j in range(n - 1, -1, -1):\n                if text1[i] == text2[j]:\n                    dp[i][j] = 1 + dp[i + 1][j + 1]\n                else:\n                    dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])\n        return dp[0][0]\n",
    },
    {
        "id": 102, "slug": "best-time-to-buy-and-sell-stock-with-cooldown", "method": "maxProfit",
        "pySig": "def maxProfit(self, prices: List[int]) -> int:",
        "javaSig": "public int maxProfit(int[] prices)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "3 states per day: hold, sold (cooldown next day), rest",
        "prompt": "Find maximum profit from unlimited stock trades with a mandatory 1-day cooldown after selling.",
        "firstLine": "Track 3 state machines initialized at day 0: `hold = -prices[0]`, `sold = 0`, `rest = 0`.",
        "steps": [
            "Guard empty `prices`; initialize `hold = -prices[0]`, `sold = 0`, `rest = 0`",
            "Each day compute `new_hold = max(hold, rest - p)`, `new_sold = hold + p`, `new_rest = max(rest, sold)`",
            "Return `max(sold, rest)` after the last day"
        ],
        "cases": [
            {"input": {"prices": [1, 2, 3, 0, 2]}, "expected": 3},
            {"input": {"prices": [1]}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def maxProfit(self, prices: List[int]) -> int:\n        if not prices:\n            return 0\n        hold, sold, rest = -prices[0], 0, 0\n        for p in prices[1:]:\n            hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)\n        return max(sold, rest)\n",
    },
    {
        "id": 103, "slug": "coin-change-ii", "method": "change",
        "pySig": "def change(self, amount: int, coins: List[int]) -> int:",
        "javaSig": "public int change(int amount, int[] coins)", "javaRet": "return 0;",
        "time": "O(amount * len(coins))", "space": "O(amount)", "invariant": "Outer loop over coins (NOT amount) avoids counting duplicate permutations",
        "prompt": "Given integer `amount` and `coins`, return the number of combinations that sum to `amount`.",
        "firstLine": "Create `dp = [0] * (amount + 1)` with `dp[0] = 1`, iterating outer loop over `coins`.",
        "steps": [
            "Allocate `dp = [0] * (amount + 1)` and set `dp[0] = 1`",
            "Outer loop `for c in coins:` and inner loop `for a in range(c, amount + 1):`",
            "Add `dp[a] += dp[a - c]` and return `dp[amount]`"
        ],
        "cases": [
            {"input": {"amount": 5, "coins": [1, 2, 5]}, "expected": 4},
            {"input": {"amount": 3, "coins": [2]}, "expected": 0},
            {"input": {"amount": 10, "coins": [10]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def change(self, amount: int, coins: List[int]) -> int:\n        dp = [0] * (amount + 1)\n        dp[0] = 1\n        for c in coins:\n            for a in range(c, amount + 1):\n                dp[a] += dp[a - c]\n        return dp[amount]\n",
    },
    {
        "id": 104, "slug": "target-sum", "method": "findTargetSumWays",
        "pySig": "def findTargetSumWays(self, nums: List[int], target: int) -> int:",
        "javaSig": "public int findTargetSumWays(int[] nums, int target)", "javaRet": "return 0;",
        "time": "O(N * S)", "space": "O(S)", "invariant": "Map running sums -> ways count at each index step",
        "prompt": "Assign `+` or `-` before every integer in `nums` and return how many expressions evaluate to `target`.",
        "firstLine": "Initialize `dp = {0: 1}` mapping current sum -> way count.",
        "steps": [
            "Start with `dp = defaultdict(int); dp[0] = 1`",
            "For each `x` in `nums`, build `nxt = defaultdict(int)` adding `cnt` to both `s + x` and `s - x`",
            "Set `dp = nxt` each step and return `dp.get(target, 0)`"
        ],
        "cases": [
            {"input": {"nums": [1, 1, 1, 1, 1], "target": 3}, "expected": 5},
            {"input": {"nums": [1], "target": 1}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def findTargetSumWays(self, nums: List[int], target: int) -> int:\n        dp = {0: 1}\n        for x in nums:\n            nxt = defaultdict(int)\n            for s, cnt in dp.items():\n                nxt[s + x] += cnt\n                nxt[s - x] += cnt\n            dp = nxt\n        return dp.get(target, 0)\n",
    },
    {
        "id": 105, "slug": "interleaving-string", "method": "isInterleave",
        "pySig": "def isInterleave(self, s1: str, s2: str, s3: str) -> bool:",
        "javaSig": "public boolean isInterleave(String s1, String s2, String s3)", "javaRet": "return false;",
        "time": "O(M * N)", "space": "O(M * N)", "invariant": "dp[i][j] holds if s1[i:] and s2[j:] interleave to s3[i + j:]",
        "prompt": "Return `True` if `s3` is formed by an interleaving of `s1` and `s2` preserving relative order.",
        "firstLine": "Guard `if len(s1) + len(s2) != len(s3): return False`, then fill `(m+1) x (n+1)` table bottom-up.",
        "steps": [
            "Check `len(s1) + len(s2) == len(s3)` first",
            "Allocate `dp` of booleans with `dp[m][n] = True`",
            "Fill `i` from `m` down to `0`, `j` from `n` down to `0`: advance `(i+1, j)` if `s1[i]==s3[i+j]` or `(i, j+1)` if `s2[j]==s3[i+j]`"
        ],
        "cases": [
            {"input": {"s1": "aabcc", "s2": "dbbca", "s3": "aadbbcbcac"}, "expected": True},
            {"input": {"s1": "aabcc", "s2": "dbbca", "s3": "aadbbbaccc"}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:\n        m, n = len(s1), len(s2)\n        if m + n != len(s3):\n            return False\n        dp = [[False] * (n + 1) for _ in range(m + 1)]\n        dp[m][n] = True\n        for i in range(m, -1, -1):\n            for j in range(n, -1, -1):\n                if i < m and s1[i] == s3[i + j] and dp[i + 1][j]:\n                    dp[i][j] = True\n                if j < n and s2[j] == s3[i + j] and dp[i][j + 1]:\n                    dp[i][j] = True\n        return dp[0][0]\n",
    },
    {
        "id": 106, "slug": "edit-distance", "method": "minDistance",
        "pySig": "def minDistance(self, word1: str, word2: str) -> int:",
        "javaSig": "public int minDistance(String word1, String word2)", "javaRet": "return 0;",
        "time": "O(M * N)", "space": "O(M * N)", "invariant": "Match -> dp[i+1][j+1]; mismatch -> 1 + min(insert, delete, replace)",
        "prompt": "Given `word1` and `word2`, return the minimum insert/delete/replace operations to convert `word1` into `word2`.",
        "firstLine": "Build `(m+1) x (n+1)` table with base edges `dp[i][n] = m - i` and `dp[m][j] = n - j`.",
        "steps": [
            "Allocate `(m+1) x (n+1)` `dp` table and fill bottom row / right column base lengths",
            "Loop `i` backward and `j` backward",
            "If `word1[i] == word2[j]`, take `dp[i+1][j+1]`; else `1 + min(dp[i+1][j], dp[i][j+1], dp[i+1][j+1])`"
        ],
        "cases": [
            {"input": {"word1": "horse", "word2": "ros"}, "expected": 3},
            {"input": {"word1": "intention", "word2": "execution"}, "expected": 5},
        ],
        "refPy": "class Solution:\n    def minDistance(self, word1: str, word2: str) -> int:\n        m, n = len(word1), len(word2)\n        dp = [[0] * (n + 1) for _ in range(m + 1)]\n        for i in range(m + 1): dp[i][n] = m - i\n        for j in range(n + 1): dp[m][j] = n - j\n        for i in range(m - 1, -1, -1):\n            for j in range(n - 1, -1, -1):\n                if word1[i] == word2[j]:\n                    dp[i][j] = dp[i + 1][j + 1]\n                else:\n                    dp[i][j] = 1 + min(dp[i + 1][j], dp[i][j + 1], dp[i + 1][j + 1])\n        return dp[0][0]\n",
    },
    {
        "id": 107, "slug": "burst-balloons", "method": "maxCoins",
        "pySig": "def maxCoins(self, nums: List[int]) -> int:",
        "javaSig": "public int maxCoins(int[] nums)", "javaRet": "return 0;",
        "time": "O(N^3)", "space": "O(N^2)", "invariant": "Pad [1] + nums + [1]; pick `k` as the LAST balloon burst in interval (l, r)",
        "prompt": "Burst balloons in any order earning `nums[i-1]*nums[i]*nums[i+1]` coins per burst; return the maximum total coins.",
        "firstLine": "Pad `vals = [1] + nums + [1]` and use interval DP `dp[l][r]` choosing which balloon bursts LAST.",
        "steps": [
            "Pad `vals = [1] + nums + [1]` and allocate `dp` of size `n x n`",
            "Iterate interval width from `2` up to `len(vals) - 1`, then left `l` (`r = l + width`)",
            "Loop `k` in `(l + 1 .. r - 1)` choosing `k` last: `vals[l]*vals[k]*vals[r] + dp[l][k] + dp[k][r]`"
        ],
        "cases": [
            {"input": {"nums": [3, 1, 5, 8]}, "expected": 167},
            {"input": {"nums": [1, 5]}, "expected": 10},
        ],
        "refPy": "class Solution:\n    def maxCoins(self, nums: List[int]) -> int:\n        v = [1] + nums + [1]\n        n = len(v)\n        dp = [[0] * n for _ in range(n)]\n        for length in range(2, n):\n            for l in range(0, n - length):\n                r = l + length\n                best = 0\n                for k in range(l + 1, r):\n                    c = v[l] * v[k] * v[r] + dp[l][k] + dp[k][r]\n                    if c > best:\n                        best = c\n                dp[l][r] = best\n        return dp[0][n - 1]\n",
    },
    {
        "id": 108, "slug": "maximum-subarray", "method": "maxSubArray",
        "pySig": "def maxSubArray(self, nums: List[int]) -> int:",
        "javaSig": "public int maxSubArray(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "Kadane: cur = max(x, cur + x); best = max(best, cur)",
        "prompt": "Given integer array `nums`, find the contiguous subarray with the largest sum and return its sum.",
        "firstLine": "Initialize `cur = best = nums[0]` and loop over `nums[1:]`.",
        "steps": [
            "Set `cur = best = nums[0]`",
            "For `x` in `nums[1:]`: drop negative prefix via `cur = max(x, cur + x)`",
            "Update `best = max(best, cur)` and return `best`"
        ],
        "cases": [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23},
            {"input": {"nums": [-3, -1]}, "expected": -1},
        ],
        "refPy": "class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:\n        cur = best = nums[0]\n        for x in nums[1:]:\n            cur = max(x, cur + x)\n            if cur > best:\n                best = cur\n        return best\n",
    },
    {
        "id": 109, "slug": "jump-game", "method": "canJump",
        "pySig": "def canJump(self, nums: List[int]) -> bool:",
        "javaSig": "public boolean canJump(int[] nums)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(1)", "invariant": "Shift `goal` left whenever `i + nums[i] >= goal`",
        "prompt": "At index `i`, max jump length is `nums[i]`. Return `True` if you can reach the last index from index `0`.",
        "firstLine": "Set `goal = len(nums) - 1` and walk backward from `goal - 1` down to `0`.",
        "steps": [
            "Initialize `goal = len(nums) - 1`",
            "For `i` from `len(nums) - 2` down to `0`: if `i + nums[i] >= goal`, set `goal = i`",
            "Return `goal == 0`"
        ],
        "cases": [
            {"input": {"nums": [2, 3, 1, 1, 4]}, "expected": True},
            {"input": {"nums": [3, 2, 1, 0, 4]}, "expected": False},
        ],
        "refPy": "class Solution:\n    def canJump(self, nums: List[int]) -> bool:\n        goal = len(nums) - 1\n        for i in range(len(nums) - 2, -1, -1):\n            if i + nums[i] >= goal:\n                goal = i\n        return goal == 0\n",
    },
    {
        "id": 110, "slug": "jump-game-ii", "method": "jump",
        "pySig": "def jump(self, nums: List[int]) -> int:",
        "javaSig": "public int jump(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "BFS window [l..r] per jump -> next r is max(i + nums[i])",
        "prompt": "Return the minimum number of jumps to reach `len(nums) - 1` from index `0` (guaranteed reachable).",
        "firstLine": "Track current BFS reach range `l = r = 0` and `jumps = 0` while `r < len(nums) - 1`.",
        "steps": [
            "Initialize `l = r = jumps = 0`",
            "While `r < len(nums) - 1`: compute `farthest = max(i + nums[i] for i in range(l, r + 1))`",
            "Shift `l, r = r + 1, farthest` and increment `jumps += 1`; return `jumps`"
        ],
        "cases": [
            {"input": {"nums": [2, 3, 1, 1, 4]}, "expected": 2},
            {"input": {"nums": [2, 3, 0, 1, 4]}, "expected": 2},
        ],
        "refPy": "class Solution:\n    def jump(self, nums: List[int]) -> int:\n        l = r = jumps = 0\n        while r < len(nums) - 1:\n            far = max(i + nums[i] for i in range(l, r + 1))\n            l, r = r + 1, far\n            jumps += 1\n        return jumps\n",
    },
    {
        "id": 111, "slug": "gas-station", "method": "canCompleteCircuit",
        "pySig": "def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:",
        "javaSig": "public int canCompleteCircuit(int[] gas, int[] cost)", "javaRet": "return -1;",
        "time": "O(N)", "space": "O(1)", "invariant": "If sum(gas) >= sum(cost), reset start = i + 1 whenever tank drops < 0",
        "prompt": "Find the starting gas station index to complete a circular route once (`-1` if impossible).",
        "firstLine": "Guard `if sum(gas) < sum(cost): return -1`, then set `tank = 0` and `start = 0`.",
        "steps": [
            "If `sum(gas) < sum(cost)`, return `-1` immediately",
            "Loop `i` over stations accumulating `tank += gas[i] - cost[i]`",
            "Whenever `tank < 0`, reset `tank = 0` and `start = i + 1`; return `start`"
        ],
        "cases": [
            {"input": {"gas": [1, 2, 3, 4, 5], "cost": [3, 4, 5, 1, 2]}, "expected": 3},
            {"input": {"gas": [2, 3, 4], "cost": [3, 4, 3]}, "expected": -1},
        ],
        "refPy": "class Solution:\n    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:\n        if sum(gas) < sum(cost):\n            return -1\n        tank = start = 0\n        for i in range(len(gas)):\n            tank += gas[i] - cost[i]\n            if tank < 0:\n                tank = 0\n                start = i + 1\n        return start\n",
    },
    {
        "id": 112, "slug": "hand-of-straights", "method": "isNStraightHand",
        "pySig": "def isNStraightHand(self, hand: List[int], groupSize: int) -> bool:",
        "javaSig": "public boolean isNStraightHand(int[] hand, int groupSize)", "javaRet": "return false;",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Always start the next straight at the smallest remaining card value",
        "prompt": "Return `True` if `hand` cards can be rearranged into groups of `groupSize` consecutive integers.",
        "firstLine": "Check `if len(hand) % groupSize: return False`, then build `counts = Counter(hand)` and min-heap of unique keys.",
        "steps": [
            "Return `False` if `len(hand) % groupSize != 0`",
            "Count `counts = Counter(hand)` and sort unique keys `for x in sorted(counts)`",
            "While `counts[x] > 0`, verify `[x, x + 1, ..., x + groupSize - 1]` all have count > 0 and decrement each"
        ],
        "cases": [
            {"input": {"hand": [1, 2, 3, 6, 2, 3, 4, 7, 8], "groupSize": 3}, "expected": True},
            {"input": {"hand": [1, 2, 3, 4, 5], "groupSize": 4}, "expected": False},
        ],
        "refPy": "class Solution:\n    def isNStraightHand(self, hand: List[int], groupSize: int) -> bool:\n        if len(hand) % groupSize != 0:\n            return False\n        cnt = Counter(hand)\n        for start in sorted(cnt):\n            need = cnt[start]\n            if need > 0:\n                for val in range(start, start + groupSize):\n                    if cnt[val] < need:\n                        return False\n                    cnt[val] -= need\n        return True\n",
    },
    {
        "id": 113, "slug": "merge-intervals", "method": "merge",
        "pySig": "def merge(self, intervals: List[List[int]]) -> List[List[int]]:",
        "javaSig": "public int[][] merge(int[][] intervals)", "javaRet": "return new int[][]{};",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Sort by start; overlap iff cur[0] <= merged[-1][1]",
        "prompt": "Given an array of `intervals`, merge all overlapping intervals and return the disjoint result.",
        "firstLine": "Sort `intervals.sort(key=lambda x: x[0])` and seed `merged = [intervals[0][:]]`.",
        "steps": [
            "Sort `intervals` by start time and put the first interval into `merged`",
            "For `s, e` in `intervals[1:]`: if `s <= merged[-1][1]`, extend `merged[-1][1] = max(merged[-1][1], e)`",
            "Otherwise append `[s, e]` to `merged`"
        ],
        "cases": [
            {"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}, "expected": [[1, 6], [8, 10], [15, 18]]},
            {"input": {"intervals": [[1, 4], [4, 5]]}, "expected": [[1, 5]]},
        ],
        "refPy": "class Solution:\n    def merge(self, intervals: List[List[int]]) -> List[List[int]]:\n        intervals.sort(key=lambda x: x[0])\n        res = [list(intervals[0])]\n        for s, e in intervals[1:]:\n            if s <= res[-1][1]:\n                res[-1][1] = max(res[-1][1], e)\n            else:\n                res.append([s, e])\n        return res\n",
    },
    {
        "id": 114, "slug": "insert-interval", "method": "insert",
        "pySig": "def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:",
        "javaSig": "public int[][] insert(int[][] intervals, int[] newInterval)", "javaRet": "return new int[][]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "3 regions: strictly before -> expand overlapping union -> strictly after",
        "prompt": "Insert `newInterval` into sorted non-overlapping `intervals` and merge any overlaps in `O(N)` time.",
        "firstLine": "Initialize `res = []` and compare each `iv` (`[s, e]`) against `newInterval`.",
        "steps": [
            "If `newInterval[1] < s`, append `newInterval` + remaining slice and return immediately",
            "Elif `newInterval[0] > e`, append `iv` to `res`",
            "Else merge `newInterval = [min(newInterval[0], s), max(newInterval[1], e)]`; append `newInterval` after loop"
        ],
        "cases": [
            {"input": {"intervals": [[1, 3], [6, 9]], "newInterval": [2, 5]}, "expected": [[1, 5], [6, 9]]},
            {"input": {"intervals": [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], "newInterval": [4, 8]}, "expected": [[1, 2], [3, 10], [12, 16]]},
        ],
        "refPy": "class Solution:\n    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:\n        res = []\n        cur = list(newInterval)\n        for i, (s, e) in enumerate(intervals):\n            if cur[1] < s:\n                res.append(cur)\n                return res + intervals[i:]\n            elif cur[0] > e:\n                res.append([s, e])\n            else:\n                cur = [min(cur[0], s), max(cur[1], e)]\n        res.append(cur)\n        return res\n",
    },
    {
        "id": 115, "slug": "non-overlapping-intervals", "method": "eraseOverlapIntervals",
        "pySig": "def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:",
        "javaSig": "public int eraseOverlapIntervals(int[][] intervals)", "javaRet": "return 0;",
        "time": "O(N log N)", "space": "O(1)", "invariant": "On overlap, always keep the interval with the SMALLER end time",
        "prompt": "Return the minimum number of intervals to remove so the rest are non-overlapping.",
        "firstLine": "Sort `intervals.sort()`, track `prev_end = intervals[0][1]`, and `removed = 0`.",
        "steps": [
            "Sort `intervals` by start time; set `prev_end = intervals[0][1]` and `removed = 0`",
            "For `s, e` in `intervals[1:]`: if `s >= prev_end`, update `prev_end = e`",
            "Else increment `removed += 1` and greedily keep `prev_end = min(prev_end, e)`"
        ],
        "cases": [
            {"input": {"intervals": [[1, 2], [2, 3], [3, 4], [1, 3]]}, "expected": 1},
            {"input": {"intervals": [[1, 2], [1, 2], [1, 2]]}, "expected": 2},
        ],
        "refPy": "class Solution:\n    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:\n        intervals.sort()\n        prev_end = intervals[0][1]\n        removed = 0\n        for s, e in intervals[1:]:\n            if s >= prev_end:\n                prev_end = e\n            else:\n                removed += 1\n                prev_end = min(prev_end, e)\n        return removed\n",
    },
    {
        "id": 116, "slug": "meeting-rooms", "method": "canAttendMeetings",
        "pySig": "def canAttendMeetings(self, intervals: List[List[int]]) -> bool:",
        "javaSig": "public boolean canAttendMeetings(int[][] intervals)", "javaRet": "return true;",
        "time": "O(N log N)", "space": "O(1)", "invariant": "Sort by start; conflict iff intervals[i][0] < intervals[i - 1][1]",
        "prompt": "Given meeting time `intervals`, return `True` if a person could attend all meetings without overlap.",
        "firstLine": "Sort `intervals.sort(key=lambda x: x[0])` and check consecutive pairs.",
        "steps": [
            "Sort `intervals` ascending by start time",
            "Loop `i` from `1` to `len(intervals) - 1`",
            "If `intervals[i][0] < intervals[i - 1][1]`, return `False`; else return `True`"
        ],
        "cases": [
            {"input": {"intervals": [[0, 30], [5, 10], [15, 20]]}, "expected": False},
            {"input": {"intervals": [[7, 10], [2, 4]]}, "expected": True},
        ],
        "refPy": "class Solution:\n    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:\n        intervals.sort(key=lambda x: x[0])\n        for i in range(1, len(intervals)):\n            if intervals[i][0] < intervals[i - 1][1]:\n                return False\n        return True\n",
    },
    {
        "id": 117, "slug": "meeting-rooms-ii", "method": "minMeetingRooms",
        "pySig": "def minMeetingRooms(self, intervals: List[List[int]]) -> int:",
        "javaSig": "public int minMeetingRooms(int[][] intervals)", "javaRet": "return 0;",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Sweep sorted start and end times with two pointers to count max concurrent rooms",
        "prompt": "Given meeting `intervals`, return the minimum number of conference rooms required.",
        "firstLine": "Extract `starts = sorted(i[0] for i in intervals)` and `ends = sorted(i[1] for i in intervals)`.",
        "steps": [
            "Sort `starts` and `ends` independently; set `s = e = count = best = 0`",
            "While `s < len(intervals)`: if `starts[s] < ends[e]`, increment `s += 1` and `count += 1`",
            "Else increment `e += 1` and `count -= 1`; track `best = max(best, count)`"
        ],
        "cases": [
            {"input": {"intervals": [[0, 30], [5, 10], [15, 20]]}, "expected": 2},
            {"input": {"intervals": [[7, 10], [2, 4]]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def minMeetingRooms(self, intervals: List[List[int]]) -> int:\n        starts = sorted(iv[0] for iv in intervals)\n        ends = sorted(iv[1] for iv in intervals)\n        s = e = cnt = best = 0\n        while s < len(intervals):\n            if starts[s] < ends[e]:\n                s += 1\n                cnt += 1\n                best = max(best, cnt)\n            else:\n                e += 1\n                cnt -= 1\n        return best\n",
    },
    {
        "id": 118, "slug": "minimum-interval-to-include-each-query", "method": "minInterval",
        "pySig": "def minInterval(self, intervals: List[List[int]], queries: List[int]) -> List[int]:",
        "javaSig": "public int[] minInterval(int[][] intervals, int[] queries)", "javaRet": "return new int[]{};",
        "time": "O(N log N + Q log Q)", "space": "O(N + Q)", "invariant": "Sort both intervals & queries; min-heap of (length, right_end) stores active intervals",
        "prompt": "For each `q` in `queries`, find the smallest interval `[l, r]` covering `l <= q <= r` (`-1` if none).",
        "firstLine": "Sort `intervals` by left bound, keep min-heap `heap = []` of `(end - start + 1, end)`, and answer `sorted(queries)`.",
        "steps": [
            "Sort `intervals`; maintain pointer `i = 0`, min-heap `heap = []`, and map `ans_map = {}`",
            "For each sorted query `q`: push all intervals with `l <= q`, then pop expired intervals with `heap[0][1] < q`",
            "Record `ans_map[q] = heap[0][0] if heap else -1`, then map back to original `queries` order"
        ],
        "cases": [
            {"input": {"intervals": [[1, 4], [2, 4], [3, 6], [4, 4]], "queries": [2, 3, 4, 5]}, "expected": [3, 3, 1, 4]},
            {"input": {"intervals": [[2, 3], [2, 5], [1, 8], [20, 25]], "queries": [2, 19, 5, 22]}, "expected": [2, -1, 4, 6]},
        ],
        "refPy": "class Solution:\n    def minInterval(self, intervals: List[List[int]], queries: List[int]) -> List[int]:\n        intervals.sort()\n        heap, res, i = [], {}, 0\n        for q in sorted(set(queries)):\n            while i < len(intervals) and intervals[i][0] <= q:\n                l, r = intervals[i]\n                heapq.heappush(heap, (r - l + 1, r))\n                i += 1\n            while heap and heap[0][1] < q:\n                heapq.heappop(heap)\n            res[q] = heap[0][0] if heap else -1\n        return [res[q] for q in queries]\n",
    },
    {
        "id": 119, "slug": "implement-trie-prefix-tree", "method": "search", "execMode": "class_ops", "className": "Trie",
        "pySig": "class Trie:\n    def __init__(self):\n        pass\n    def insert(self, word: str) -> None:\n        pass\n    def search(self, word: str) -> bool:\n        return False\n    def startsWith(self, prefix: str) -> bool:",
        "javaSig": "public boolean search(String word)", "javaRet": "return false;",
        "time": "O(L)", "space": "O(Total Chars)", "invariant": "Nested dict/node trie with explicit end-of-word marker '#'",
        "prompt": "Implement a `Trie` supporting `insert(word)`, `search(word)`, and `startsWith(prefix)`.",
        "firstLine": "Initialize `self.root = {}` and mark completed words with key `'#'`.",
        "steps": [
            "Set `self.root = {}` in `__init__`",
            "In `insert(word)`: walk character by character with `cur = cur.setdefault(ch, {})`, then set `cur['#'] = True`",
            "In `search`/`startsWith`: walk `word`/`prefix`; check `'#' in cur` for exact match"
        ],
        "cases": [
            {
                "input": {"ops": ["Trie", "insert", "search", "search", "startsWith", "insert", "search"], "args": [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]},
                "expected": [None, None, True, False, True, None, True],
            }
        ],
        "refPy": "class Trie:\n    def __init__(self):\n        self.root = {}\n    def insert(self, word: str) -> None:\n        cur = self.root\n        for ch in word:\n            cur = cur.setdefault(ch, {})\n        cur['#'] = True\n    def search(self, word: str) -> bool:\n        cur = self.root\n        for ch in word:\n            if ch not in cur: return False\n            cur = cur[ch]\n        return '#' in cur\n    def startsWith(self, prefix: str) -> bool:\n        cur = self.root\n        for ch in prefix:\n            if ch not in cur: return False\n            cur = cur[ch]\n        return True\n",
    },
    {
        "id": 120, "slug": "design-add-and-search-words-data-structure", "method": "search", "execMode": "class_ops", "className": "WordDictionary",
        "pySig": "class WordDictionary:\n    def __init__(self):\n        pass\n    def addWord(self, word: str) -> None:\n        pass\n    def search(self, word: str) -> bool:",
        "javaSig": "public boolean search(String word)", "javaRet": "return false;",
        "time": "O(L) / O(26^dots)", "space": "O(Total Chars)", "invariant": "Trie + DFS branching on '.' wildcard across all child keys",
        "prompt": "Design `WordDictionary` supporting `addWord(word)` and `search(word)` where `'.'` matches any single letter.",
        "firstLine": "Store `self.root = {}` like a Trie and add recursive helper `dfs(idx, node)` for wildcards.",
        "steps": [
            "Insert words into nested dicts with `node['#'] = True`",
            "In `dfs(i, node)`: if `i == len(word)`, return `'#' in node`",
            "If `word[i] == '.'`, return `any(dfs(i+1, child) for k, child in node.items() if k != '#')`; else step down `word[i]`"
        ],
        "cases": [
            {
                "input": {"ops": ["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"], "args": [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]]},
                "expected": [None, None, None, None, False, True, True, True],
            }
        ],
        "refPy": "class WordDictionary:\n    def __init__(self):\n        self.root = {}\n    def addWord(self, word: str) -> None:\n        cur = self.root\n        for ch in word:\n            cur = cur.setdefault(ch, {})\n        cur['#'] = True\n    def search(self, word: str) -> bool:\n        def dfs(i, node):\n            if i == len(word):\n                return '#' in node\n            ch = word[i]\n            if ch == '.':\n                return any(dfs(i + 1, nxt) for k, nxt in node.items() if k != '#')\n            if ch not in node:\n                return False\n            return dfs(i + 1, node[ch])\n        return dfs(0, self.root)\n",
    },
    {
        "id": 121, "slug": "word-search-ii", "method": "findWords", "compareMode": "unordered",
        "pySig": "def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:",
        "javaSig": "public List<String> findWords(char[][] board, String[] words)", "javaRet": "return new ArrayList<>();",
        "time": "O(R * C * 4^L)", "space": "O(Total Word Chars)", "invariant": "Build Trie from all words once -> single backtracking DFS across the board",
        "prompt": "Given character `board` and word list `words`, return all words present on the board using adjacent non-repeating cells.",
        "firstLine": "Build a `trie = {}` storing the full word string at `node['$'] = word`, then run 4-way DFS.",
        "steps": [
            "Insert every word from `words` into `trie` marking leaves `cur['$'] = w`",
            "Run `dfs(r, c, node)` pruning immediately when `board[r][c] not in node`",
            "If `'$' in nxt`, record `found.append(nxt.pop('$'))` to deduplicate without re-scanning, and backtrack `board[r][c]`"
        ],
        "cases": [
            {"input": {"board": [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]], "words": ["oath", "pea", "eat", "rain"]}, "expected": ["eat", "oath"]},
            {"input": {"board": [["a", "b"], ["c", "d"]], "words": ["abcb"]}, "expected": []},
        ],
        "refPy": "class Solution:\n    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:\n        trie = {}\n        for w in words:\n            cur = trie\n            for ch in w:\n                cur = cur.setdefault(ch, {})\n            cur['$'] = w\n        R, C = len(board), len(board[0])\n        res = []\n        def dfs(r, c, node):\n            ch = board[r][c]\n            if ch not in node:\n                return\n            nxt = node[ch]\n            if '$' in nxt:\n                res.append(nxt.pop('$'))\n            board[r][c] = '#'\n            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n                nr, nc = r + dr, c + dc\n                if 0 <= nr < R and 0 <= nc < C and board[nr][nc] != '#':\n                    dfs(nr, nc, nxt)\n            board[r][c] = ch\n            if not nxt:\n                node.pop(ch)\n        for r in range(R):\n            for c in range(C):\n                dfs(r, c, trie)\n        return res\n",
    },
    {
        "id": 122, "slug": "lfu-cache", "method": "get", "execMode": "class_ops", "className": "LFUCache",
        "pySig": "class LFUCache:\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        return -1\n    def put(self, key: int, value: int) -> None:",
        "javaSig": "public int get(int key)", "javaRet": "return -1;",
        "time": "O(1)", "space": "O(capacity)", "invariant": "key -> (val, freq) map + freq -> OrderedDict of keys + min_freq tracker",
        "prompt": "Design an `LFUCache(capacity)` supporting `O(1)` `get(key)` and `put(key, value)` (evict least-frequent, tie-break by LRU).",
        "firstLine": "Maintain `self.kv = {}`, `self.freqs = defaultdict(OrderedDict)`, and `self.min_f = 0`.",
        "steps": [
            "Write `_touch(key, new_val=None)` updating frequency from `f` to `f + 1` and bumping `self.min_f` when `freqs[min_f]` empties",
            "On `get(key)`: return `-1` if absent, else `_touch(key)` and return value",
            "On `put(key, val)`: handle `cap == 0`; update if present, else evict `freqs[min_f].popitem(last=False)` when full and insert at `freq = 1`"
        ],
        "cases": [
            {
                "input": {"ops": ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"], "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]},
                "expected": [None, None, None, 1, None, -1, 3, None, -1, 3, 4],
            }
        ],
        "refPy": "class LFUCache:\n    def __init__(self, capacity: int):\n        self.cap = capacity\n        self.kv = {}\n        self.freqs = defaultdict(OrderedDict)\n        self.min_f = 0\n    def _touch(self, key, new_val=None):\n        v, f = self.kv[key]\n        if new_val is not None:\n            v = new_val\n        del self.freqs[f][key]\n        if not self.freqs[f] and f == self.min_f:\n            self.min_f += 1\n        self.freqs[f + 1][key] = None\n        self.kv[key] = (v, f + 1)\n        return v\n    def get(self, key: int) -> int:\n        return self._touch(key) if key in self.kv else -1\n    def put(self, key: int, value: int) -> None:\n        if self.cap <= 0:\n            return\n        if key in self.kv:\n            self._touch(key, value)\n            return\n        if len(self.kv) == self.cap:\n            evict_k, _ = self.freqs[self.min_f].popitem(last=False)\n            del self.kv[evict_k]\n        self.kv[key] = (value, 1)\n        self.freqs[1][key] = None\n        self.min_f = 1\n",
    },
    {
        "id": 123, "slug": "design-bounded-blocking-queue", "method": "size", "execMode": "class_ops", "className": "BoundedBlockingQueue",
        "pySig": "class BoundedBlockingQueue:\n    def __init__(self, capacity: int):\n        pass\n    def enqueue(self, element: int) -> None:\n        pass\n    def dequeue(self) -> int:\n        return 0\n    def size(self) -> int:",
        "javaSig": "public int size()", "javaRet": "return 0;",
        "time": "O(1)", "space": "O(capacity)", "invariant": "threading.Condition() with not_full and not_empty condition waits around deque",
        "prompt": "Design a thread-safe `BoundedBlockingQueue(capacity)` with blocking `enqueue(element)`, blocking `dequeue()`, and `size()`.",
        "firstLine": "Store `self.cap = capacity`, `self.q = deque()`, and `self.cond = threading.Condition()`.",
        "steps": [
            "Initialize `self.q = deque()`, `self.cap = capacity`, `self.cond = threading.Condition()`",
            "In `enqueue(x)`: `with self.cond: while len(self.q) == self.cap: self.cond.wait(); self.q.append(x); self.cond.notify_all()`",
            "In `dequeue()`: wait `while not self.q`, pop left, `notify_all()`, return value; `size()` returns `len(self.q)` under lock"
        ],
        "cases": [
            {
                "input": {"ops": ["BoundedBlockingQueue", "enqueue", "enqueue", "size", "dequeue", "enqueue", "dequeue", "dequeue", "size"], "args": [[2], [1], [2], [], [], [3], [], [], []]},
                "expected": [None, None, None, 2, 1, None, 2, 3, 0],
            }
        ],
        "refPy": "class BoundedBlockingQueue:\n    def __init__(self, capacity: int):\n        self.cap = capacity\n        self.q = deque()\n        self.cond = threading.Condition()\n    def enqueue(self, element: int) -> None:\n        with self.cond:\n            while len(self.q) >= self.cap:\n                self.cond.wait()\n            self.q.append(element)\n            self.cond.notify_all()\n    def dequeue(self) -> int:\n        with self.cond:\n            while not self.q:\n                self.cond.wait()\n            val = self.q.popleft()\n            self.cond.notify_all()\n            return val\n    def size(self) -> int:\n        with self.cond:\n            return len(self.q)\n",
    },
    {
        "id": 124, "slug": "single-number", "method": "singleNumber",
        "pySig": "def singleNumber(self, nums: List[int]) -> int:",
        "javaSig": "public int singleNumber(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "a ^ a = 0 and a ^ 0 = a -> XOR cancels every pair",
        "prompt": "Every element in `nums` appears twice except one; find that single unique element in `O(N)` time and `O(1)` space.",
        "firstLine": "Start `ans = 0` and XOR every number into it (`ans ^= x`).",
        "steps": [
            "Initialize `ans = 0`",
            "Loop `for x in nums: ans ^= x`",
            "Return `ans`"
        ],
        "cases": [
            {"input": {"nums": [2, 2, 1]}, "expected": 1},
            {"input": {"nums": [4, 1, 2, 1, 2]}, "expected": 4},
        ],
        "refPy": "class Solution:\n    def singleNumber(self, nums: List[int]) -> int:\n        ans = 0\n        for x in nums:\n            ans ^= x\n        return ans\n",
    },
    {
        "id": 125, "slug": "number-of-1-bits", "method": "hammingWeight",
        "pySig": "def hammingWeight(self, n: int) -> int:",
        "javaSig": "public int hammingWeight(int n)", "javaRet": "return 0;",
        "time": "O(popcount)", "space": "O(1)", "invariant": "Brian Kernighan: n &= (n - 1) clears lowest set 1-bit per iteration",
        "prompt": "Return the number of set (`1`) bits (Hamming weight) of an unsigned integer `n`.",
        "firstLine": "Loop `while n:` clearing the lowest 1-bit with `n &= (n - 1)` and incrementing `cnt += 1`.",
        "steps": [
            "Initialize `cnt = 0`",
            "While `n`: execute `n &= (n - 1)` and `cnt += 1`",
            "Return `cnt`"
        ],
        "cases": [
            {"input": {"n": 11}, "expected": 3},
            {"input": {"n": 128}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def hammingWeight(self, n: int) -> int:\n        cnt = 0\n        while n:\n            n &= (n - 1)\n            cnt += 1\n        return cnt\n",
    },
    {
        "id": 126, "slug": "counting-bits", "method": "countBits",
        "pySig": "def countBits(self, n: int) -> List[int]:",
        "javaSig": "public int[] countBits(int n)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "dp[i] = dp[i >> 1] + (i & 1) in one linear pass",
        "prompt": "For `0 <= i <= n`, return an array `ans` of length `n + 1` where `ans[i]` is the count of `1` bits in `i`.",
        "firstLine": "Allocate `dp = [0] * (n + 1)` and compute `dp[i] = dp[i >> 1] + (i & 1)`.",
        "steps": [
            "Allocate `dp = [0] * (n + 1)`",
            "Loop `i` from `1` to `n`",
            "Set `dp[i] = dp[i >> 1] + (i & 1)` and return `dp`"
        ],
        "cases": [
            {"input": {"n": 2}, "expected": [0, 1, 1]},
            {"input": {"n": 5}, "expected": [0, 1, 1, 2, 1, 2]},
        ],
        "refPy": "class Solution:\n    def countBits(self, n: int) -> List[int]:\n        dp = [0] * (n + 1)\n        for i in range(1, n + 1):\n            dp[i] = dp[i >> 1] + (i & 1)\n        return dp\n",
    },
    {
        "id": 127, "slug": "reverse-bits", "method": "reverseBits",
        "pySig": "def reverseBits(self, n: int) -> int:",
        "javaSig": "public int reverseBits(int n)", "javaRet": "return 0;",
        "time": "O(1)", "space": "O(1)", "invariant": "For 32 bits: res = (res << 1) | (n & 1); n >>= 1",
        "prompt": "Reverse the bits of a given 32-bit unsigned integer `n`.",
        "firstLine": "Set `res = 0` and loop 32 times shifting `res` left while pulling `n & 1`.",
        "steps": [
            "Initialize `res = 0`",
            "Loop 32 times: `res = (res << 1) | (n & 1)`, then `n >>= 1`",
            "Return `res`"
        ],
        "cases": [
            {"input": {"n": 43261596}, "expected": 964176192},
            {"input": {"n": 4294967293}, "expected": 3221225471},
        ],
        "refPy": "class Solution:\n    def reverseBits(self, n: int) -> int:\n        res = 0\n        for _ in range(32):\n            res = (res << 1) | (n & 1)\n            n >>= 1\n        return res\n",
    },
    {
        "id": 128, "slug": "missing-number", "method": "missingNumber",
        "pySig": "def missingNumber(self, nums: List[int]) -> int:",
        "javaSig": "public int missingNumber(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "expected_sum(0..n) - sum(nums) OR XOR indices 0..n with values",
        "prompt": "Given `nums` containing `n` distinct numbers from `[0..n]`, return the single missing number in `O(N)` time and `O(1)` space.",
        "firstLine": "Compute `n = len(nums)` and XOR or subtract `n * (n + 1) // 2 - sum(nums)`.",
        "steps": [
            "Store `n = len(nums)`",
            "Start with `res = n` and XOR `res ^= i ^ nums[i]` for `i` in `range(n)`",
            "Return `res`"
        ],
        "cases": [
            {"input": {"nums": [3, 0, 1]}, "expected": 2},
            {"input": {"nums": [0, 1]}, "expected": 2},
            {"input": {"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}, "expected": 8},
        ],
        "refPy": "class Solution:\n    def missingNumber(self, nums: List[int]) -> int:\n        res = len(nums)\n        for i, x in enumerate(nums):\n            res ^= i ^ x\n        return res\n",
    },
]

WARMUP_DRILLS = [
    {
        "id": "drill-hashmap-freq",
        "title": "1. Hash Map Frequency Counter",
        "minutes": 3,
        "goal": "Count frequencies in one pass without importing Counter(). Used in ~35% of coding interviews.",
        "firstLine": "Create `counts = {}` and update `counts[x] = counts.get(x, 0) + 1` inside a loop.",
        "starterPy": "def count_frequencies(items: list[str]) -> dict[str, int]:\n    # Step 1: Create empty dict counts = {}\n    # Step 2: Loop through items and increment counts[x]\n    # Step 3: Return counts\n    pass\n",
        "cases": [
            {"input": {"items": ["a", "b", "a", "c", "b", "a"]}, "expected": {"a": 3, "b": 2, "c": 1}},
            {"input": {"items": []}, "expected": {}},
        ],
        "refPy": "def count_frequencies(items: list[str]) -> dict[str, int]:\n    counts = {}\n    for x in items:\n        counts[x] = counts.get(x, 0) + 1\n    return counts\n",
        "fnName": "count_frequencies",
    },
    {
        "id": "drill-two-pointers",
        "title": "2. Two-Pointer Left/Right Converge",
        "minutes": 3,
        "goal": "Find if any pair in a sorted list sums to `target` in O(1) extra space.",
        "firstLine": "Set `l, r = 0, len(nums) - 1` and loop `while l < r:`.",
        "starterPy": "def sorted_pair_exists(nums: list[int], target: int) -> bool:\n    # Step 1: Initialize l = 0, r = len(nums) - 1\n    # Step 2: Check nums[l] + nums[r] == target\n    # Step 3: Move l += 1 if too small, r -= 1 if too large\n    pass\n",
        "cases": [
            {"input": {"nums": [1, 3, 4, 8, 12], "target": 11}, "expected": True},
            {"input": {"nums": [1, 2, 3, 9], "target": 8}, "expected": False},
        ],
        "refPy": "def sorted_pair_exists(nums: list[int], target: int) -> bool:\n    l, r = 0, len(nums) - 1\n    while l < r:\n        s = nums[l] + nums[r]\n        if s == target:\n            return True\n        if s < target:\n            l += 1\n        else:\n            r -= 1\n    return False\n",
        "fnName": "sorted_pair_exists",
    },
    {
        "id": "drill-sliding-window",
        "title": "3. Sliding Window Expand & Shrink",
        "minutes": 4,
        "goal": "Longest subarray of positive integers with sum <= `k`.",
        "firstLine": "Track `left = 0`, `win_sum = 0`, `best = 0` and shrink `while win_sum > k:`.",
        "starterPy": "def longest_subarray_at_most_k(nums: list[int], k: int) -> int:\n    # Step 1: left = 0, win_sum = 0, best = 0\n    # Step 2: Expand right: win_sum += val; shrink left while win_sum > k\n    # Step 3: best = max(best, right - left + 1); return best\n    pass\n",
        "cases": [
            {"input": {"nums": [2, 1, 5, 1, 3, 2], "k": 7}, "expected": 3},
            {"input": {"nums": [1, 1, 1, 1], "k": 2}, "expected": 2},
        ],
        "refPy": "def longest_subarray_at_most_k(nums: list[int], k: int) -> int:\n    left = win_sum = best = 0\n    for right, x in enumerate(nums):\n        win_sum += x\n        while win_sum > k and left <= right:\n            win_sum -= nums[left]\n            left += 1\n        best = max(best, right - left + 1)\n    return best\n",
        "fnName": "longest_subarray_at_most_k",
    },
    {
        "id": "drill-binary-search",
        "title": "4. Binary Search (Zero Infinite-Loop Bugs)",
        "minutes": 3,
        "goal": "Type standard closed-interval binary search `l <= r` cleanly from memory.",
        "firstLine": "Use `l, r = 0, len(nums) - 1` and `while l <= r:` returning `mid` on hit.",
        "starterPy": "def binary_search_index(nums: list[int], target: int) -> int:\n    # Step 1: l, r = 0, len(nums) - 1\n    # Step 2: mid = (l + r) // 2; return mid if nums[mid] == target\n    # Step 3: Narrow to l = mid + 1 or r = mid - 1; return -1 if absent\n    pass\n",
        "cases": [
            {"input": {"nums": [1, 4, 7, 10, 15], "target": 10}, "expected": 3},
            {"input": {"nums": [1, 4, 7, 10, 15], "target": 6}, "expected": -1},
        ],
        "refPy": "def binary_search_index(nums: list[int], target: int) -> int:\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        mid = (l + r) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[mid] < target:\n            l = mid + 1\n        else:\n            r = mid - 1\n    return -1\n",
        "fnName": "binary_search_index",
    },
    {
        "id": "drill-monotonic-stack",
        "title": "5. Monotonic Stack Next-Greater Element",
        "minutes": 5,
        "goal": "For each `nums[i]`, find distance to next strictly greater element (`0` if none).",
        "firstLine": "Create `ans = [0] * len(nums)` and `stack = []` storing waiting indices.",
        "starterPy": "def days_until_higher(nums: list[int]) -> list[int]:\n    # Step 1: ans = [0] * len(nums), stack = []\n    # Step 2: While stack and nums[stack[-1]] < x: pop idx, set ans[idx] = i - idx\n    # Step 3: Append i to stack and return ans\n    pass\n",
        "cases": [
            {"input": {"nums": [73, 74, 75, 71, 69, 72, 76, 73]}, "expected": [1, 1, 4, 2, 1, 1, 0, 0]},
            {"input": {"nums": [5, 4, 3]}, "expected": [0, 0, 0]},
        ],
        "refPy": "def days_until_higher(nums: list[int]) -> list[int]:\n    ans = [0] * len(nums)\n    stack = []\n    for i, x in enumerate(nums):\n        while stack and nums[stack[-1]] < x:\n            prev = stack.pop()\n            ans[prev] = i - prev\n        stack.append(i)\n    return ans\n",
        "fnName": "days_until_higher",
    },
    {
        "id": "drill-linked-list-rev",
        "title": "6. Linked List Pointer Reversal",
        "minutes": 4,
        "goal": "Reverse a Python list simulated or linked chain via `prev, curr` invariant (in-place array/node drill).",
        "firstLine": "Track `prev, curr = None, head` and save `nxt = curr.next` before rewiring.",
        "starterPy": "from typing import Optional\nfrom utils.dsa_helpers import ListNode\n\ndef reverse_chain(head: Optional[ListNode]) -> Optional[ListNode]:\n    # Step 1: prev, curr = None, head\n    # Step 2: While curr: save nxt = curr.next, flip curr.next = prev\n    # Step 3: Shift prev, curr = curr, nxt; return prev\n    pass\n",
        "argTypes": {"head": "ListNode"}, "returnType": "ListNode",
        "cases": [
            {"input": {"head": [1, 2, 3, 4]}, "expected": [4, 3, 2, 1]},
            {"input": {"head": []}, "expected": []},
        ],
        "refPy": "from typing import Optional\nfrom utils.dsa_helpers import ListNode\n\ndef reverse_chain(head: Optional[ListNode]) -> Optional[ListNode]:\n    prev, curr = None, head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev, curr = curr, nxt\n    return prev\n",
        "fnName": "reverse_chain",
    },
    {
        "id": "drill-tree-dfs",
        "title": "7. Binary Tree DFS Height / Sum",
        "minutes": 3,
        "goal": "Type classic `if not root: return 0` bottom-up tree recursion cleanly.",
        "firstLine": "Handle `if not root: return 0`, then combine left & right subtree sums.",
        "starterPy": "from typing import Optional\nfrom utils.dsa_helpers import TreeNode\n\ndef sum_tree_nodes(root: Optional[TreeNode]) -> int:\n    # Step 1: if not root: return 0\n    # Step 2: return root.val + sum_tree_nodes(root.left) + sum_tree_nodes(root.right)\n    pass\n",
        "argTypes": {"root": "TreeNode"},
        "cases": [
            {"input": {"root": [1, 2, 3, 4]}, "expected": 10},
            {"input": {"root": []}, "expected": 0},
        ],
        "refPy": "from typing import Optional\nfrom utils.dsa_helpers import TreeNode\n\ndef sum_tree_nodes(root: Optional[TreeNode]) -> int:\n    if not root:\n        return 0\n    return root.val + sum_tree_nodes(root.left) + sum_tree_nodes(root.right)\n",
        "fnName": "sum_tree_nodes",
    },
    {
        "id": "drill-bfs-queue",
        "title": "8. Queue BFS Traversal Order",
        "minutes": 4,
        "goal": "Shortest-path graph BFS using `deque` and `visited` set (guard visited BEFORE pushing!).",
        "firstLine": "Create `q = deque([start])`, `visited = {start}`, and `order = []`.",
        "starterPy": "from collections import deque\n\ndef bfs_order(graph: dict[int, list[int]], start: int) -> list[int]:\n    # Step 1: q = deque([start]), visited = {start}, order = []\n    # Step 2: Popleft u, append u to order\n    # Step 3: Push unvisited neighbors to visited + q; return order\n    pass\n",
        "cases": [
            {"input": {"graph": {0: [1, 2], 1: [2], 2: [3], 3: []}, "start": 0}, "expected": [0, 1, 2, 3]},
        ],
        "refPy": "from collections import deque\n\ndef bfs_order(graph: dict[int, list[int]], start: int) -> list[int]:\n    q = deque([start])\n    visited = {start}\n    order = []\n    while q:\n        u = q.popleft()\n        order.append(u)\n        for v in graph.get(u, []):\n            if v not in visited:\n                visited.add(v)\n                q.append(v)\n    return order\n",
        "fnName": "bfs_order",
    },
    {
        "id": "drill-heap-topk",
        "title": "9. Heap Top-K (`heapq` Bounded Min-Heap)",
        "minutes": 4,
        "goal": "Keep the K largest numbers from a stream in `O(N log K)` time.",
        "firstLine": "Create `heap = []` and pop whenever `len(heap) > k`.",
        "starterPy": "import heapq\n\ndef top_k_sorted_desc(nums: list[int], k: int) -> list[int]:\n    # Step 1: heap = []\n    # Step 2: Push each x via heapq.heappush; heappop when len(heap) > k\n    # Step 3: Return sorted(heap, reverse=True)\n    pass\n",
        "cases": [
            {"input": {"nums": [5, 1, 9, 3, 7, 2], "k": 3}, "expected": [9, 7, 5]},
            {"input": {"nums": [4], "k": 1}, "expected": [4]},
        ],
        "refPy": "import heapq\n\ndef top_k_sorted_desc(nums: list[int], k: int) -> list[int]:\n    h = []\n    for x in nums:\n        heapq.heappush(h, x)\n        if len(h) > k:\n            heapq.heappop(h)\n    return sorted(h, reverse=True)\n",
        "fnName": "top_k_sorted_desc",
    },
    {
        "id": "drill-backtracking",
        "title": "10. Backtracking (Choose -> Explore -> Unchoose)",
        "minutes": 5,
        "goal": "Generate all `k`-sized subsets (combinations) of `nums`.",
        "firstLine": "Write `dfs(start, path)` recording `path[:]` whenever `len(path) == k`.",
        "starterPy": "def combine_k(nums: list[int], k: int) -> list[list[int]]:\n    # Step 1: res, path = [], []\n    # Step 2: Base case len(path) == k -> res.append(path[:])\n    # Step 3: Loop i from start: append, dfs(i+1), path.pop()\n    pass\n",
        "compareMode": "unordered",
        "cases": [
            {"input": {"nums": [1, 2, 3], "k": 2}, "expected": [[1, 2], [1, 3], [2, 3]]},
        ],
        "refPy": "def combine_k(nums: list[int], k: int) -> list[list[int]]:\n    res, path = [], []\n    def dfs(start):\n        if len(path) == k:\n            res.append(path[:])\n            return\n        for i in range(start, len(nums)):\n            path.append(nums[i])\n            dfs(i + 1)\n            path.pop()\n    dfs(0)\n    return res\n",
        "fnName": "combine_k",
    },
    {
        "id": "drill-grid-flood",
        "title": "11. Grid 4-Neighbor Flood Fill",
        "minutes": 4,
        "goal": "Count connected cells of value `1` starting at `(sr, sc)` using DFS/BFS.",
        "firstLine": "Bounds-check `0 <= r < R and 0 <= c < C`, mark visited, and explore `(1,0), (-1,0), (0,1), (0,-1)`.",
        "starterPy": "def region_area(grid: list[list[int]], sr: int, sc: int) -> int:\n    # Step 1: Return 0 if out of bounds or grid[r][c] != 1\n    # Step 2: Mark grid[r][c] = 0 so it isn't revisited\n    # Step 3: Return 1 + sum of 4 neighbor recursive calls\n    pass\n",
        "cases": [
            {"input": {"grid": [[1, 1, 0], [0, 1, 1], [0, 0, 0]], "sr": 0, "sc": 0}, "expected": 4},
        ],
        "refPy": "def region_area(grid: list[list[int]], sr: int, sc: int) -> int:\n    R, C = len(grid), len(grid[0])\n    def dfs(r, c):\n        if r < 0 or r >= R or c < 0 or c >= C or grid[r][c] != 1:\n            return 0\n        grid[r][c] = 0\n        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)\n    return dfs(sr, sc)\n",
        "fnName": "region_area",
    },
    {
        "id": "drill-dp-rolling",
        "title": "12. 1D Rolling Dynamic Programming Loop",
        "minutes": 3,
        "goal": "House-robber style max non-adjacent sum in `O(1)` memory.",
        "firstLine": "Initialize `prev2 = prev1 = 0` and update `prev2, prev1 = prev1, max(prev2 + x, prev1)`.",
        "starterPy": "def max_non_adjacent_sum(nums: list[int]) -> int:\n    # Step 1: prev2, prev1 = 0, 0\n    # Step 2: Loop x in nums updating rolling transition\n    # Step 3: Return prev1\n    pass\n",
        "cases": [
            {"input": {"nums": [2, 7, 9, 3, 1]}, "expected": 12},
            {"input": {"nums": [5]}, "expected": 5},
        ],
        "refPy": "def max_non_adjacent_sum(nums: list[int]) -> int:\n    p2 = p1 = 0\n    for x in nums:\n        p2, p1 = p1, max(p2 + x, p1)\n    return p1\n",
        "fnName": "max_non_adjacent_sum",
    },
]
