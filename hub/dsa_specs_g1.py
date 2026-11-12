"""DSA Catalog Specs — Group 1: Problems #1 to #34 (Arrays, Two Pointers, Sliding Window, Stack, Binary Search)."""

SPECS_G1 = [
    {
        "id": 1, "slug": "two-sum", "method": "twoSum",
        "pySig": "def twoSum(self, nums: List[int], target: int) -> List[int]:",
        "javaSig": "public int[] twoSum(int[] nums, int target)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "need = target - x in seen_index_map",
        "prompt": "Given an integer array `nums` and an integer `target`, return indices `[i, j]` of the two numbers that add up to `target`.",
        "firstLine": "Create an empty dictionary `seen = {}` mapping each number you've visited to its array index.",
        "steps": [
            "Create `seen = {}` to store `value -> index` as you scan",
            "Loop `for i, num in enumerate(nums):` and compute `need = target - num`",
            "If `need in seen`, return `[seen[need], i]`; otherwise store `seen[num] = i`"
        ],
        "cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            {"input": {"nums": [-3, 4, 3, 90], "target": 0}, "expected": [0, 2]},
        ],
        "refPy": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        seen = {}\n        for i, x in enumerate(nums):\n            need = target - x\n            if need in seen:\n                return [seen[need], i]\n            seen[x] = i\n        return []\n",
    },
    {
        "id": 2, "slug": "contains-duplicate", "method": "containsDuplicate",
        "pySig": "def containsDuplicate(self, nums: List[int]) -> bool:",
        "javaSig": "public boolean containsDuplicate(int[] nums)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(N)", "invariant": "x in seen_set -> duplicate found in O(1)",
        "prompt": "Given an integer array `nums`, return `True` if any value appears at least twice, and `False` if every element is distinct.",
        "firstLine": "Create an empty set `seen = set()` to remember every number you have seen so far.",
        "steps": [
            "Initialize `seen = set()` for O(1) membership checks",
            "Loop over each `x` in `nums`; if `x in seen`, immediately return `True`",
            "Add `x` to `seen`; return `False` after the loop finishes"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 3, 1]}, "expected": True},
            {"input": {"nums": [1, 2, 3, 4]}, "expected": False},
            {"input": {"nums": []}, "expected": False},
        ],
        "refPy": "class Solution:\n    def containsDuplicate(self, nums: List[int]) -> bool:\n        seen = set()\n        for x in nums:\n            if x in seen:\n                return True\n            seen.add(x)\n        return False\n",
    },
    {
        "id": 3, "slug": "valid-anagram", "method": "isAnagram",
        "pySig": "def isAnagram(self, s: str, t: str) -> bool:",
        "javaSig": "public boolean isAnagram(String s, String t)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(1)", "invariant": "len(s) == len(t) and count[26] == all zeros",
        "prompt": "Given two lowercase strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise.",
        "firstLine": "Guard first: `if len(s) != len(t): return False`, then create `counts = [0] * 26`.",
        "steps": [
            "If `len(s) != len(t)`, return `False` immediately",
            "Create `counts = [0] * 26`; increment for chars in `s` and decrement for chars in `t`",
            "Return `True` only if all 26 entries in `counts` equal `0`"
        ],
        "cases": [
            {"input": {"s": "anagram", "t": "nagaram"}, "expected": True},
            {"input": {"s": "rat", "t": "car"}, "expected": False},
            {"input": {"s": "ab", "t": "a"}, "expected": False},
            {"input": {"s": "listen", "t": "silent"}, "expected": True},
        ],
        "refPy": "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        if len(s) != len(t):\n            return False\n        counts = [0] * 26\n        for a, b in zip(s, t):\n            counts[ord(a) - 97] += 1\n            counts[ord(b) - 97] -= 1\n        return all(c == 0 for c in counts)\n",
    },
    {
        "id": 4, "slug": "group-anagrams", "method": "groupAnagrams", "compareMode": "anagram_groups",
        "pySig": "def groupAnagrams(self, strs: List[str]) -> List[List[str]]:",
        "javaSig": "public List<List<String>> groupAnagrams(String[] strs)", "javaRet": "return new ArrayList<>();",
        "time": "O(N * K)", "space": "O(N * K)", "invariant": "key = tuple(count[26]) -> buckets[key].append(word)",
        "prompt": "Given an array of lowercase strings `strs`, group the anagrams together in any order.",
        "firstLine": "Create `buckets = defaultdict(list)` so words with the same 26-letter count share one list.",
        "steps": [
            "Create `buckets = defaultdict(list)`",
            "For each `word` in `strs`, build `count = [0] * 26` from its characters",
            "Append `word` to `buckets[tuple(count)]` and return `list(buckets.values())`"
        ],
        "cases": [
            {"input": {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]}, "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
            {"input": {"strs": [""]}, "expected": [[""]]},
            {"input": {"strs": ["a"]}, "expected": [["a"]]},
        ],
        "refPy": "class Solution:\n    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:\n        buckets = defaultdict(list)\n        for w in strs:\n            cnt = [0] * 26\n            for ch in w:\n                cnt[ord(ch) - 97] += 1\n            buckets[tuple(cnt)].append(w)\n        return list(buckets.values())\n",
    },
    {
        "id": 5, "slug": "top-k-frequent-elements", "method": "topKFrequent", "compareMode": "unordered",
        "pySig": "def topKFrequent(self, nums: List[int], k: int) -> List[int]:",
        "javaSig": "public int[] topKFrequent(int[] nums, int k)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "freq_buckets[count].append(num) -> scan from N down to 1",
        "prompt": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements in any order.",
        "firstLine": "Count frequencies with `freq = Counter(nums)` and create `buckets = [[] for _ in range(len(nums) + 1)]`.",
        "steps": [
            "Count each number's frequency in `freq = {}`",
            "Place each `num` into `buckets[count]` where index = frequency (`0..len(nums)`)",
            "Walk `buckets` backward from highest frequency and collect until `len(res) == k`"
        ],
        "cases": [
            {"input": {"nums": [1, 1, 1, 2, 2, 3], "k": 2}, "expected": [1, 2]},
            {"input": {"nums": [1], "k": 1}, "expected": [1]},
            {"input": {"nums": [4, 4, 1, 2, 2, 2, 3], "k": 2}, "expected": [2, 4]},
        ],
        "refPy": "class Solution:\n    def topKFrequent(self, nums: List[int], k: int) -> List[int]:\n        freq = Counter(nums)\n        buckets = [[] for _ in range(len(nums) + 1)]\n        for num, c in freq.items():\n            buckets[c].append(num)\n        res = []\n        for c in range(len(nums), 0, -1):\n            for num in buckets[c]:\n                res.append(num)\n                if len(res) == k:\n                    return res\n        return res\n",
    },
    {
        "id": 6, "slug": "product-of-array-except-self", "method": "productExceptSelf",
        "pySig": "def productExceptSelf(self, nums: List[int]) -> List[int]:",
        "javaSig": "public int[] productExceptSelf(int[] nums)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(1)", "invariant": "res[i] = prefix_prod_left[i] * suffix_prod_right[i]",
        "prompt": "Given `nums`, return an array `res` where `res[i]` equals the product of all elements of `nums` except `nums[i]`, without using division.",
        "firstLine": "Allocate `res = [1] * len(nums)` and `prefix = 1`.",
        "steps": [
            "Create `res = [1] * len(nums)` and pass left-to-right storing running `prefix` product",
            "Initialize `suffix = 1` and pass right-to-left multiplying `res[i] *= suffix`",
            "Update `suffix *= nums[i]` each step and return `res`"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 3, 4]}, "expected": [24, 12, 8, 6]},
            {"input": {"nums": [-1, 1, 0, -3, 3]}, "expected": [0, 0, 9, 0, 0]},
        ],
        "refPy": "class Solution:\n    def productExceptSelf(self, nums: List[int]) -> List[int]:\n        n = len(nums)\n        res = [1] * n\n        prefix = 1\n        for i in range(n):\n            res[i] = prefix\n            prefix *= nums[i]\n        suffix = 1\n        for i in range(n - 1, -1, -1):\n            res[i] *= suffix\n            suffix *= nums[i]\n        return res\n",
    },
    {
        "id": 7, "slug": "encode-and-decode-strings", "method": "encode", "execMode": "codec_strings", "className": "Codec",
        "pySig": "class Codec:\n    def encode(self, strs: List[str]) -> str:",
        "javaSig": "public String encode(List<String> strs)", "javaRet": "return \"\";",
        "time": "O(N)", "space": "O(N)", "invariant": "frame = f'{len(s)}#{s}' prevents delimiter collisions",
        "prompt": "Design `Codec` with `encode(strs)` and `decode(s)` to serialize and deserialize any list of strings (even strings containing `#` or digits).",
        "firstLine": "In `encode`, join each string `w` as `f\"{len(w)}#{w}\"`; in `decode`, read digits up to `'#'` to get the exact slice length.",
        "steps": [
            "In `encode(strs)`: format every string as `f'{len(w)}#{w}'` and join them",
            "In `decode(s)`: keep pointer `i = 0`; find `'#'` at index `j` to parse `length = int(s[i:j])`",
            "Slice `s[j + 1 : j + 1 + length]`, append to result, and set `i = j + 1 + length`"
        ],
        "cases": [
            {"input": {"strs": ["lint", "code", "love", "you"]}, "expected": ["lint", "code", "love", "you"]},
            {"input": {"strs": ["we", "say", ":", "yes", "10#tricky"]}, "expected": ["we", "say", ":", "yes", "10#tricky"]},
            {"input": {"strs": [""]}, "expected": [""]},
        ],
        "refPy": "class Codec:\n    def encode(self, strs: List[str]) -> str:\n        return ''.join(f'{len(w)}#{w}' for w in strs)\n\n    def decode(self, s: str) -> List[str]:\n        res, i = [], 0\n        while i < len(s):\n            j = s.index('#', i)\n            ln = int(s[i:j])\n            res.append(s[j + 1: j + 1 + ln])\n            i = j + 1 + ln\n        return res\n",
    },
    {
        "id": 8, "slug": "longest-consecutive-sequence", "method": "longestConsecutive",
        "pySig": "def longestConsecutive(self, nums: List[int]) -> int:",
        "javaSig": "public int longestConsecutive(int[] nums)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(N)", "invariant": "Only start counting at x when (x - 1) not in num_set",
        "prompt": "Given an unsorted integer array `nums`, return the length of the longest consecutive elements sequence in `O(N)` time.",
        "firstLine": "Put all numbers into `num_set = set(nums)` and set `best = 0`.",
        "steps": [
            "Convert `nums` to `num_set = set(nums)` for O(1) lookup",
            "Loop `for x in num_set:` and check `if x - 1 not in num_set:` (start of streak!)",
            "Advance `y = x` while `y in num_set` and update `best = max(best, y - x)`"
        ],
        "cases": [
            {"input": {"nums": [100, 4, 200, 1, 3, 2]}, "expected": 4},
            {"input": {"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, "expected": 9},
            {"input": {"nums": []}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def longestConsecutive(self, nums: List[int]) -> int:\n        num_set = set(nums)\n        best = 0\n        for x in num_set:\n            if x - 1 not in num_set:\n                y = x\n                while y in num_set:\n                    y += 1\n                best = max(best, y - x)\n        return best\n",
    },
    {
        "id": 9, "slug": "subarray-sum-equals-k", "method": "subarraySum",
        "pySig": "def subarraySum(self, nums: List[int], k: int) -> int:",
        "javaSig": "public int subarraySum(int[] nums, int k)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(N)", "invariant": "ans += prefix_counts[curr_sum - k]",
        "prompt": "Given an integer array `nums` and an integer `k`, return the total number of contiguous subarrays whose sum equals `k`.",
        "firstLine": "Seed `prefix_counts = {0: 1}`, `curr = 0`, and `ans = 0`.",
        "steps": [
            "Initialize `prefix_counts = {0: 1}`, `curr = 0`, `ans = 0`",
            "For each `x` in `nums`, add `x` to `curr` and add `prefix_counts.get(curr - k, 0)` to `ans`",
            "Record `prefix_counts[curr] = prefix_counts.get(curr, 0) + 1` and return `ans`"
        ],
        "cases": [
            {"input": {"nums": [1, 1, 1], "k": 2}, "expected": 2},
            {"input": {"nums": [1, 2, 3], "k": 3}, "expected": 2},
            {"input": {"nums": [1, -1, 0], "k": 0}, "expected": 3},
        ],
        "refPy": "class Solution:\n    def subarraySum(self, nums: List[int], k: int) -> int:\n        counts = {0: 1}\n        curr = ans = 0\n        for x in nums:\n            curr += x\n            ans += counts.get(curr - k, 0)\n            counts[curr] = counts.get(curr, 0) + 1\n        return ans\n",
    },
    {
        "id": 10, "slug": "first-missing-positive", "method": "firstMissingPositive",
        "pySig": "def firstMissingPositive(self, nums: List[int]) -> int:",
        "javaSig": "public int firstMissingPositive(int[] nums)", "javaRet": "return 1;",
        "time": "O(N)", "space": "O(1)", "invariant": "Place each x in [1..N] at index x - 1 via cyclic swap",
        "prompt": "Given an unsorted integer array `nums`, return the smallest missing positive integer in `O(N)` time and `O(1)` auxiliary space.",
        "firstLine": "Store `n = len(nums)` and loop `i` from `0` to `n - 1`, swapping `nums[i]` into slot `nums[i] - 1` while valid.",
        "steps": [
            "For each index `i`, while `1 <= nums[i] <= n` and `nums[nums[i] - 1] != nums[i]`, swap them",
            "Scan `i` from `0` to `n - 1`: if `nums[i] != i + 1`, return `i + 1`",
            "If all `1..n` are in place, return `n + 1`"
        ],
        "cases": [
            {"input": {"nums": [1, 2, 0]}, "expected": 3},
            {"input": {"nums": [3, 4, -1, 1]}, "expected": 2},
            {"input": {"nums": [7, 8, 9, 11, 12]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def firstMissingPositive(self, nums: List[int]) -> int:\n        n = len(nums)\n        for i in range(n):\n            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:\n                target_idx = nums[i] - 1\n                nums[i], nums[target_idx] = nums[target_idx], nums[i]\n        for i in range(n):\n            if nums[i] != i + 1:\n                return i + 1\n        return n + 1\n",
    },
    {
        "id": 11, "slug": "valid-palindrome", "method": "isPalindrome",
        "pySig": "def isPalindrome(self, s: str) -> bool:",
        "javaSig": "public boolean isPalindrome(String s)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(1)", "invariant": "left < right skipping non-alnum; s[left].lower() == s[right].lower()",
        "prompt": "Given a string `s`, return `True` if it reads the same forward and backward after converting to lowercase and ignoring non-alphanumeric characters.",
        "firstLine": "Set `left, right = 0, len(s) - 1` and loop `while left < right:`.",
        "steps": [
            "Initialize `left = 0` and `right = len(s) - 1`",
            "Skip non-alphanumeric chars using `.isalnum()` on both sides while `left < right`",
            "Compare `s[left].lower() == s[right].lower()`; return `False` on mismatch, else move inward"
        ],
        "cases": [
            {"input": {"s": "A man, a plan, a canal: Panama"}, "expected": True},
            {"input": {"s": "race a car"}, "expected": False},
            {"input": {"s": " "}, "expected": True},
        ],
        "refPy": "class Solution:\n    def isPalindrome(self, s: str) -> bool:\n        l, r = 0, len(s) - 1\n        while l < r:\n            while l < r and not s[l].isalnum():\n                l += 1\n            while l < r and not s[r].isalnum():\n                r -= 1\n            if s[l].lower() != s[r].lower():\n                return False\n            l += 1\n            r -= 1\n        return True\n",
    },
    {
        "id": 12, "slug": "two-sum-ii-input-array-is-sorted", "method": "twoSum",
        "pySig": "def twoSum(self, numbers: List[int], target: int) -> List[int]:",
        "javaSig": "public int[] twoSum(int[] numbers, int target)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(1)", "invariant": "sum < target -> l += 1; sum > target -> r -= 1",
        "prompt": "Given a 1-indexed sorted integer array `numbers`, return `[index1, index2]` (1-indexed) of the two numbers summing to `target` using `O(1)` extra space.",
        "firstLine": "Set `l, r = 0, len(numbers) - 1` and compare `numbers[l] + numbers[r]` against `target`.",
        "steps": [
            "Initialize `l = 0` and `r = len(numbers) - 1`",
            "Compute `cur = numbers[l] + numbers[r]`; if `cur == target`, return `[l + 1, r + 1]`",
            "If `cur < target`, increment `l`; otherwise decrement `r`"
        ],
        "cases": [
            {"input": {"numbers": [2, 7, 11, 15], "target": 9}, "expected": [1, 2]},
            {"input": {"numbers": [2, 3, 4], "target": 6}, "expected": [1, 3]},
            {"input": {"numbers": [-1, 0], "target": -1}, "expected": [1, 2]},
        ],
        "refPy": "class Solution:\n    def twoSum(self, numbers: List[int], target: int) -> List[int]:\n        l, r = 0, len(numbers) - 1\n        while l < r:\n            s = numbers[l] + numbers[r]\n            if s == target:\n                return [l + 1, r + 1]\n            if s < target:\n                l += 1\n            else:\n                r -= 1\n        return []\n",
    },
    {
        "id": 13, "slug": "3sum", "method": "threeSum", "compareMode": "unordered",
        "pySig": "def threeSum(self, nums: List[int]) -> List[List[int]]:",
        "javaSig": "public List<List<Integer>> threeSum(int[] nums)", "javaRet": "return new ArrayList<>();",
        "time": "O(N^2)", "space": "O(1)", "invariant": "Sort nums; fix nums[i] (skipping dups) + two-pointer l, r",
        "prompt": "Given an integer array `nums`, return all unique triplets `[nums[i], nums[j], nums[k]]` whose sum is `0`.",
        "firstLine": "Call `nums.sort()`, create `res = []`, and loop `i` over `range(len(nums))` skipping duplicate anchors.",
        "steps": [
            "Sort `nums` ascending and initialize `res = []`",
            "Loop `i`: skip if `i > 0 and nums[i] == nums[i - 1]`, then set `l, r = i + 1, len(nums) - 1`",
            "Converge `l` and `r` toward `-nums[i]`, recording triplets and skipping duplicate `nums[l]`"
        ],
        "cases": [
            {"input": {"nums": [-1, 0, 1, 2, -1, -4]}, "expected": [[-1, -1, 2], [-1, 0, 1]]},
            {"input": {"nums": [0, 1, 1]}, "expected": []},
            {"input": {"nums": [0, 0, 0]}, "expected": [[0, 0, 0]]},
        ],
        "refPy": "class Solution:\n    def threeSum(self, nums: List[int]) -> List[List[int]]:\n        nums.sort()\n        res = []\n        for i, a in enumerate(nums):\n            if a > 0:\n                break\n            if i > 0 and a == nums[i - 1]:\n                continue\n            l, r = i + 1, len(nums) - 1\n            while l < r:\n                s = a + nums[l] + nums[r]\n                if s < 0:\n                    l += 1\n                elif s > 0:\n                    r -= 1\n                else:\n                    res.append([a, nums[l], nums[r]])\n                    l += 1\n                    while l < r and nums[l] == nums[l - 1]:\n                        l += 1\n        return res\n",
    },
    {
        "id": 14, "slug": "container-with-most-water", "method": "maxArea",
        "pySig": "def maxArea(self, height: List[int]) -> int:",
        "javaSig": "public int maxArea(int[] height)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "area = (r - l) * min(h[l], h[r]); always move the shorter wall",
        "prompt": "Given `height` of vertical lines, find two lines that form a container holding the maximum amount of water.",
        "firstLine": "Set `l, r = 0, len(height) - 1` and `best = 0`.",
        "steps": [
            "Initialize `l = 0`, `r = len(height) - 1`, and `best = 0`",
            "While `l < r`, update `best = max(best, (r - l) * min(height[l], height[r]))`",
            "Move the pointer with the smaller height inward (`l += 1` if `height[l] < height[r]` else `r -= 1`)"
        ],
        "cases": [
            {"input": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, "expected": 49},
            {"input": {"height": [1, 1]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        l, r = 0, len(height) - 1\n        best = 0\n        while l < r:\n            best = max(best, (r - l) * min(height[l], height[r]))\n            if height[l] < height[r]:\n                l += 1\n            else:\n                r -= 1\n        return best\n",
    },
    {
        "id": 15, "slug": "trapping-rain-water", "method": "trap",
        "pySig": "def trap(self, height: List[int]) -> int:",
        "javaSig": "public int trap(int[] height)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "water[i] bounded by min(left_max, right_max) - height[i]",
        "prompt": "Given non-negative elevation map `height` where each bar has width `1`, compute how much water is trapped after raining.",
        "firstLine": "Guard `if not height: return 0`, then set `l, r = 0, len(height) - 1` and `left_max, right_max = height[l], height[r]`.",
        "steps": [
            "Initialize `l, r = 0, len(height) - 1`, `left_max, right_max = height[l], height[r]`, `water = 0`",
            "While `l < r`, advance whichever side has the smaller max (`left_max < right_max`)",
            "Update that side's max and add `side_max - height[idx]` to `water`"
        ],
        "cases": [
            {"input": {"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}, "expected": 6},
            {"input": {"height": [4, 2, 0, 3, 2, 5]}, "expected": 9},
        ],
        "refPy": "class Solution:\n    def trap(self, height: List[int]) -> int:\n        if not height:\n            return 0\n        l, r = 0, len(height) - 1\n        lmax, rmax = height[l], height[r]\n        water = 0\n        while l < r:\n            if lmax < rmax:\n                l += 1\n                lmax = max(lmax, height[l])\n                water += lmax - height[l]\n            else:\n                r -= 1\n                rmax = max(rmax, height[r])\n                water += rmax - height[r]\n        return water\n",
    },
    {
        "id": 16, "slug": "best-time-to-buy-and-sell-stock", "method": "maxProfit",
        "pySig": "def maxProfit(self, prices: List[int]) -> int:",
        "javaSig": "public int maxProfit(int[] prices)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "min_price = min(min_price, p); best = max(best, p - min_price)",
        "prompt": "Given `prices[i]` of a stock on day `i`, return the maximum profit from buying on one day and selling on a later day (`0` if none).",
        "firstLine": "Set `min_price = float('inf')` and `best = 0`.",
        "steps": [
            "Track `min_price = float('inf')` and `best = 0`",
            "Loop over `p` in `prices`: update `min_price = min(min_price, p)`",
            "Update `best = max(best, p - min_price)` and return `best`"
        ],
        "cases": [
            {"input": {"prices": [7, 1, 5, 3, 6, 4]}, "expected": 5},
            {"input": {"prices": [7, 6, 4, 3, 1]}, "expected": 0},
        ],
        "refPy": "class Solution:\n    def maxProfit(self, prices: List[int]) -> int:\n        min_p = float('inf')\n        best = 0\n        for p in prices:\n            if p < min_p:\n                min_p = p\n            elif p - min_p > best:\n                best = p - min_p\n        return best\n",
    },
    {
        "id": 17, "slug": "longest-substring-without-repeating-characters", "method": "lengthOfLongestSubstring",
        "pySig": "def lengthOfLongestSubstring(self, s: str) -> int:",
        "javaSig": "public int lengthOfLongestSubstring(String s)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(min(N, M))", "invariant": "Window [left..right] contains zero duplicate characters",
        "prompt": "Given a string `s`, find the length of the longest substring without repeating characters.",
        "firstLine": "Create `seen = set()`, `left = 0`, and `best = 0`.",
        "steps": [
            "Initialize `seen = set()`, `left = 0`, `best = 0`",
            "For `right, ch in enumerate(s)`: while `ch in seen`, remove `s[left]` and increment `left`",
            "Add `ch` to `seen` and update `best = max(best, right - left + 1)`"
        ],
        "cases": [
            {"input": {"s": "abcabcbb"}, "expected": 3},
            {"input": {"s": "bbbbb"}, "expected": 1},
            {"input": {"s": "pwwkew"}, "expected": 3},
        ],
        "refPy": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        seen = set()\n        left = best = 0\n        for right, ch in enumerate(s):\n            while ch in seen:\n                seen.remove(s[left])\n                left += 1\n            seen.add(ch)\n            best = max(best, right - left + 1)\n        return best\n",
    },
    {
        "id": 18, "slug": "longest-repeating-character-replacement", "method": "characterReplacement",
        "pySig": "def characterReplacement(self, s: str, k: int) -> int:",
        "javaSig": "public int characterReplacement(String s, int k)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(1)", "invariant": "(right - left + 1) - max_freq <= k",
        "prompt": "Given uppercase string `s` and integer `k`, return the length of the longest single-letter substring achievable after at most `k` replacements.",
        "firstLine": "Create `counts = {}`, `left = 0`, `max_freq = 0`, and `best = 0`.",
        "steps": [
            "Maintain character `counts` in window `[left..right]` and running `max_freq`",
            "If `(right - left + 1) - max_freq > k`, decrement `counts[s[left]]` and advance `left += 1`",
            "Update `best = max(best, right - left + 1)` each step"
        ],
        "cases": [
            {"input": {"s": "ABAB", "k": 2}, "expected": 4},
            {"input": {"s": "AABABBA", "k": 1}, "expected": 4},
        ],
        "refPy": "class Solution:\n    def characterReplacement(self, s: str, k: int) -> int:\n        counts = {}\n        left = max_f = best = 0\n        for right, ch in enumerate(s):\n            counts[ch] = counts.get(ch, 0) + 1\n            max_f = max(max_f, counts[ch])\n            if (right - left + 1) - max_f > k:\n                counts[s[left]] -= 1\n                left += 1\n            best = max(best, right - left + 1)\n        return best\n",
    },
    {
        "id": 19, "slug": "permutation-in-string", "method": "checkInclusion",
        "pySig": "def checkInclusion(self, s1: str, s2: str) -> bool:",
        "javaSig": "public boolean checkInclusion(String s1, String s2)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(1)", "invariant": "Fixed-width window of len(s1) matching 26-char frequency array",
        "prompt": "Given lowercase strings `s1` and `s2`, return `True` if `s2` contains any permutation of `s1` as a substring.",
        "firstLine": "Guard `if len(s1) > len(s2): return False`, then build `need = [0]*26` and `win = [0]*26` for the first `len(s1)` chars.",
        "steps": [
            "If `len(s1) > len(s2)`, return `False`; populate 26-count arrays `need` and `win` for `[0..len(s1))`",
            "If `need == win`, return `True`; slide `i` from `len(s1)` to `len(s2) - 1`",
            "Add `s2[i]` and remove `s2[i - len(s1)]` in `win`, returning `True` whenever `win == need`"
        ],
        "cases": [
            {"input": {"s1": "ab", "s2": "eidbaooo"}, "expected": True},
            {"input": {"s1": "ab", "s2": "eidboaoo"}, "expected": False},
        ],
        "refPy": "class Solution:\n    def checkInclusion(self, s1: str, s2: str) -> bool:\n        if len(s1) > len(s2):\n            return False\n        need, win = [0] * 26, [0] * 26\n        m = len(s1)\n        for i in range(m):\n            need[ord(s1[i]) - 97] += 1\n            win[ord(s2[i]) - 97] += 1\n        if need == win:\n            return True\n        for i in range(m, len(s2)):\n            win[ord(s2[i]) - 97] += 1\n            win[ord(s2[i - m]) - 97] -= 1\n            if need == win:\n                return True\n        return False\n",
    },
    {
        "id": 20, "slug": "minimum-window-substring", "method": "minWindow",
        "pySig": "def minWindow(self, s: str, t: str) -> str:",
        "javaSig": "public String minWindow(String s, String t)", "javaRet": "return \"\";",
        "time": "O(N + M)", "space": "O(1)", "invariant": "have == need_unique -> record min span and shrink left",
        "prompt": "Given strings `s` and `t`, return the shortest substring of `s` that contains every character of `t` (including duplicates), or `\"\"` if none exists.",
        "firstLine": "Count `need = Counter(t)`, track `win = {}`, `have = 0`, `left = 0`, and `best = (-1, -1, float('inf'))`.",
        "steps": [
            "Build `need = Counter(t)` and `required = len(need)`",
            "Expand `right`: increment `win[ch]` and increment `have` when `win[ch] == need[ch]`",
            "While `have == required`, update best window, shrink `left`, and decrement `have` if `win[s[left]] < need[s[left]]`"
        ],
        "cases": [
            {"input": {"s": "ADOBECODEBANC", "t": "ABC"}, "expected": "BANC"},
            {"input": {"s": "a", "t": "a"}, "expected": "a"},
            {"input": {"s": "a", "t": "aa"}, "expected": ""},
        ],
        "refPy": "class Solution:\n    def minWindow(self, s: str, t: str) -> str:\n        if not t or not s:\n            return ''\n        need = Counter(t)\n        win = {}\n        have, req = 0, len(need)\n        best_len, best_span = float('inf'), (0, 0)\n        l = 0\n        for r, ch in enumerate(s):\n            win[ch] = win.get(ch, 0) + 1\n            if ch in need and win[ch] == need[ch]:\n                have += 1\n            while have == req:\n                if (r - l + 1) < best_len:\n                    best_len = r - l + 1\n                    best_span = (l, r + 1)\n                left_ch = s[l]\n                win[left_ch] -= 1\n                if left_ch in need and win[left_ch] < need[left_ch]:\n                    have -= 1\n                l += 1\n        return '' if best_len == float('inf') else s[best_span[0]:best_span[1]]\n",
    },
    {
        "id": 21, "slug": "sliding-window-maximum", "method": "maxSlidingWindow",
        "pySig": "def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:",
        "javaSig": "public int[] maxSlidingWindow(int[] nums, int k)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(K)", "invariant": "Monotonic decreasing deque of indices -> dq[0] is window max",
        "prompt": "Given integer array `nums` and window size `k`, return the maximum value in each sliding window as it moves left to right.",
        "firstLine": "Create `dq = deque()` (storing indices in decreasing value order) and `res = []`.",
        "steps": [
            "Maintain `dq = deque()` of indices; pop front if `dq[0] <= i - k`",
            "Pop back while `dq` is non-empty and `nums[dq[-1]] <= nums[i]`, then append `i`",
            "Whenever `i >= k - 1`, append `nums[dq[0]]` to `res`"
        ],
        "cases": [
            {"input": {"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3}, "expected": [3, 3, 5, 5, 6, 7]},
            {"input": {"nums": [1], "k": 1}, "expected": [1]},
        ],
        "refPy": "class Solution:\n    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:\n        dq = deque()\n        res = []\n        for i, x in enumerate(nums):\n            while dq and dq[0] <= i - k:\n                dq.popleft()\n            while dq and nums[dq[-1]] <= x:\n                dq.pop()\n            dq.append(i)\n            if i >= k - 1:\n                res.append(nums[dq[0]])\n        return res\n",
    },
    {
        "id": 22, "slug": "valid-parentheses", "method": "isValid",
        "pySig": "def isValid(self, s: str) -> bool:",
        "javaSig": "public boolean isValid(String s)", "javaRet": "return false;",
        "time": "O(N)", "space": "O(N)", "invariant": "Every closing bracket matches stack.pop(); stack empty at end",
        "prompt": "Given a string `s` containing `'()[]{}'`, return `True` if every bracket is closed in the right order.",
        "firstLine": "Create `stack = []` and `pairs = {')': '(', ']': '[', '}': '{'}`.",
        "steps": [
            "Define `pairs = {')': '(', ']': '[', '}': '{'}` and `stack = []`",
            "For `ch` in `s`: if `ch in pairs`, verify `stack` is non-empty and `stack.pop() == pairs[ch]`",
            "Otherwise push `ch` onto `stack`; return `len(stack) == 0` at the end"
        ],
        "cases": [
            {"input": {"s": "()[]{}"}, "expected": True},
            {"input": {"s": "(]"}, "expected": False},
            {"input": {"s": "([{}])"}, "expected": True},
        ],
        "refPy": "class Solution:\n    def isValid(self, s: str) -> bool:\n        pairs = {')': '(', ']': '[', '}': '{'}\n        stack = []\n        for ch in s:\n            if ch in pairs:\n                if not stack or stack.pop() != pairs[ch]:\n                    return False\n            else:\n                stack.append(ch)\n        return not stack\n",
    },
    {
        "id": 23, "slug": "min-stack", "method": "getMin", "execMode": "class_ops", "className": "MinStack",
        "pySig": "class MinStack:\n    def __init__(self):\n        pass\n    def push(self, val: int) -> None:\n        pass\n    def pop(self) -> None:\n        pass\n    def top(self) -> int:\n        return 0\n    def getMin(self) -> int:",
        "javaSig": "public int getMin()", "javaRet": "return 0;",
        "time": "O(1)", "space": "O(N)", "invariant": "stack stores (val, current_min_so_far) pairs",
        "prompt": "Design a `MinStack` supporting `push`, `pop`, `top`, and retrieving `getMin` in constant `O(1)` time.",
        "firstLine": "In `__init__`, set `self.stack = []`, and on `push(val)` push `(val, min(val, self.stack[-1][1]))`.",
        "steps": [
            "Store `self.stack = []` of `(val, min_so_far)` tuples",
            "On `push(val)`, compute `cur_min = val if not self.stack else min(val, self.stack[-1][1])`",
            "Return `self.stack[-1][0]` for `top()` and `self.stack[-1][1]` for `getMin()`"
        ],
        "cases": [
            {
                "input": {"ops": ["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"], "args": [[], [-2], [0], [-3], [], [], [], []]},
                "expected": [None, None, None, None, -3, None, 0, -2],
            }
        ],
        "refPy": "class MinStack:\n    def __init__(self):\n        self.stack = []\n    def push(self, val: int) -> None:\n        m = val if not self.stack else min(val, self.stack[-1][1])\n        self.stack.append((val, m))\n    def pop(self) -> None:\n        self.stack.pop()\n    def top(self) -> int:\n        return self.stack[-1][0]\n    def getMin(self) -> int:\n        return self.stack[-1][1]\n",
    },
    {
        "id": 24, "slug": "evaluate-reverse-polish-notation", "method": "evalRPN",
        "pySig": "def evalRPN(self, tokens: List[str]) -> int:",
        "javaSig": "public int evalRPN(String[] tokens)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(N)", "invariant": "Operand -> push; Operator -> pop b, pop a, push(a op b) truncating toward 0",
        "prompt": "Evaluate an arithmetic expression in Reverse Polish Notation (`+`, `-`, `*`, `/` truncating toward zero).",
        "firstLine": "Create `stack = []` and loop over `tok` in `tokens`.",
        "steps": [
            "Create `stack = []`",
            "When `tok` is in `{'+', '-', '*', '/'}`, pop `b = stack.pop()`, then `a = stack.pop()`",
            "Push `int(a / b)` for division (truncates toward zero in Python!) or `int(tok)` for numbers; return `stack[0]`"
        ],
        "cases": [
            {"input": {"tokens": ["2", "1", "+", "3", "*"]}, "expected": 9},
            {"input": {"tokens": ["4", "13", "5", "/", "+"]}, "expected": 6},
            {"input": {"tokens": ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]}, "expected": 22},
        ],
        "refPy": "class Solution:\n    def evalRPN(self, tokens: List[str]) -> int:\n        stack = []\n        for t in tokens:\n            if t in {'+', '-', '*', '/'}:\n                b, a = stack.pop(), stack.pop()\n                if t == '+': stack.append(a + b)\n                elif t == '-': stack.append(a - b)\n                elif t == '*': stack.append(a * b)\n                else: stack.append(int(a / b))\n            else:\n                stack.append(int(t))\n        return stack[0]\n",
    },
    {
        "id": 25, "slug": "daily-temperatures", "method": "dailyTemperatures",
        "pySig": "def dailyTemperatures(self, temperatures: List[int]) -> List[int]:",
        "javaSig": "public int[] dailyTemperatures(int[] temperatures)", "javaRet": "return new int[]{};",
        "time": "O(N)", "space": "O(N)", "invariant": "Monotonic decreasing stack of unresolved day indices",
        "prompt": "Given `temperatures`, return an array `ans` where `ans[i]` is the number of days until a warmer temperature (`0` if none).",
        "firstLine": "Create `ans = [0] * len(temperatures)` and `stack = []` (indices waiting for a warmer day).",
        "steps": [
            "Allocate `ans = [0] * len(temperatures)` and `stack = []`",
            "For `i, temp in enumerate(temperatures)`: while `stack` and `temperatures[stack[-1]] < temp`, pop `prev` and set `ans[prev] = i - prev`",
            "Append `i` to `stack` and return `ans`"
        ],
        "cases": [
            {"input": {"temperatures": [73, 74, 75, 71, 69, 72, 76, 73]}, "expected": [1, 1, 4, 2, 1, 1, 0, 0]},
            {"input": {"temperatures": [30, 40, 50, 60]}, "expected": [1, 1, 1, 0]},
        ],
        "refPy": "class Solution:\n    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:\n        ans = [0] * len(temperatures)\n        stack = []\n        for i, t in enumerate(temperatures):\n            while stack and temperatures[stack[-1]] < t:\n                prev = stack.pop()\n                ans[prev] = i - prev\n            stack.append(i)\n        return ans\n",
    },
    {
        "id": 26, "slug": "car-fleet", "method": "carFleet",
        "pySig": "def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:",
        "javaSig": "public int carFleet(int target, int[] position, int[] speed)", "javaRet": "return 0;",
        "time": "O(N log N)", "space": "O(N)", "invariant": "Sort by position desc; car merges if arrival_time <= fleet_ahead_time",
        "prompt": "Given `target` mile and cars at `position[i]` moving at `speed[i]` (cars cannot pass), return how many car fleets arrive at `target`.",
        "firstLine": "Sort `cars = sorted(zip(position, speed), reverse=True)` and track `fleets = 0`, `cur_slowest = 0.0`.",
        "steps": [
            "Pair and sort `(pos, spd)` from closest to `target` down to farthest",
            "Compute `eta = (target - pos) / spd` for each car",
            "If `eta > cur_slowest`, it forms a new fleet (`fleets += 1`, `cur_slowest = eta`); return `fleets`"
        ],
        "cases": [
            {"input": {"target": 12, "position": [10, 8, 0, 5, 3], "speed": [2, 4, 1, 1, 3]}, "expected": 3},
            {"input": {"target": 100, "position": [0, 2, 4], "speed": [4, 2, 1]}, "expected": 1},
        ],
        "refPy": "class Solution:\n    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:\n        fleets = 0\n        slowest = 0.0\n        for pos, spd in sorted(zip(position, speed), reverse=True):\n            eta = (target - pos) / spd\n            if eta > slowest:\n                fleets += 1\n                slowest = eta\n        return fleets\n",
    },
    {
        "id": 27, "slug": "largest-rectangle-in-histogram", "method": "largestRectangleArea",
        "pySig": "def largestRectangleArea(self, heights: List[int]) -> int:",
        "javaSig": "public int largestRectangleArea(int[] heights)", "javaRet": "return 0;",
        "time": "O(N)", "space": "O(N)", "invariant": "Monotonic increasing stack of (start_idx, height) pairs",
        "prompt": "Given bar `heights` of width `1` in a histogram, return the area of the largest rectangle inside the histogram.",
        "firstLine": "Create `stack = []` of `(start_idx, height)` pairs and `best = 0`.",
        "steps": [
            "Initialize `stack = []` and `best = 0`",
            "For `i, h in enumerate(heights)`: while `stack` and `stack[-1][1] > h`, pop `(idx, height)`, update `best = max(best, height * (i - idx))`, and move `start = idx`",
            "Push `(start, h)`; after loop, flush remaining `(idx, height)` using `len(heights) - idx`"
        ],
        "cases": [
            {"input": {"heights": [2, 1, 5, 6, 2, 3]}, "expected": 10},
            {"input": {"heights": [2, 4]}, "expected": 4},
        ],
        "refPy": "class Solution:\n    def largestRectangleArea(self, heights: List[int]) -> int:\n        stack = []\n        best = 0\n        for i, h in enumerate(heights):\n            start = i\n            while stack and stack[-1][1] > h:\n                idx, ph = stack.pop()\n                best = max(best, ph * (i - idx))\n                start = idx\n            stack.append((start, h))\n        n = len(heights)\n        for idx, ph in stack:\n            best = max(best, ph * (n - idx))\n        return best\n",
    },
    {
        "id": 28, "slug": "binary-search", "method": "search",
        "pySig": "def search(self, nums: List[int], target: int) -> int:",
        "javaSig": "public int search(int[] nums, int target)", "javaRet": "return -1;",
        "time": "O(log N)", "space": "O(1)", "invariant": "Target (if present) stays inside closed interval [l, r]",
        "prompt": "Given sorted array `nums` and `target`, return its index in `O(log N)` time, or `-1` if absent.",
        "firstLine": "Set `l, r = 0, len(nums) - 1` and loop `while l <= r:`.",
        "steps": [
            "Initialize `l = 0`, `r = len(nums) - 1`",
            "Compute `mid = (l + r) // 2`; if `nums[mid] == target`, return `mid`",
            "If `nums[mid] < target`, set `l = mid + 1`; else `r = mid - 1`; return `-1` if not found"
        ],
        "cases": [
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected": 4},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected": -1},
        ],
        "refPy": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        l, r = 0, len(nums) - 1\n        while l <= r:\n            mid = (l + r) // 2\n            if nums[mid] == target:\n                return mid\n            if nums[mid] < target:\n                l = mid + 1\n            else:\n                r = mid - 1\n        return -1\n",
    },
    {
        "id": 29, "slug": "search-a-2d-matrix", "method": "searchMatrix",
        "pySig": "def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:",
        "javaSig": "public boolean searchMatrix(int[][] matrix, int target)", "javaRet": "return false;",
        "time": "O(log(M * N))", "space": "O(1)", "invariant": "1D index mid maps to (mid // cols, mid % cols)",
        "prompt": "Given a row-and-column sorted `m x n` `matrix` where each row starts greater than the previous row's end, return `True` if `target` exists.",
        "firstLine": "Set `rows, cols = len(matrix), len(matrix[0])` and binary search `l, r = 0, rows * cols - 1`.",
        "steps": [
            "Treat the matrix as a virtual sorted array of length `rows * cols`",
            "For `mid = (l + r) // 2`, look up `val = matrix[mid // cols][mid % cols]`",
            "Adjust `l` or `r` just like standard binary search"
        ],
        "cases": [
            {"input": {"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 3}, "expected": True},
            {"input": {"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 13}, "expected": False},
        ],
        "refPy": "class Solution:\n    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:\n        rows, cols = len(matrix), len(matrix[0])\n        l, r = 0, rows * cols - 1\n        while l <= r:\n            mid = (l + r) // 2\n            val = matrix[mid // cols][mid % cols]\n            if val == target:\n                return True\n            if val < target:\n                l = mid + 1\n            else:\n                r = mid - 1\n        return False\n",
    },
    {
        "id": 30, "slug": "koko-eating-bananas", "method": "minEatingSpeed",
        "pySig": "def minEatingSpeed(self, piles: List[int], h: int) -> int:",
        "javaSig": "public int minEatingSpeed(int[] piles, int h)", "javaRet": "return 1;",
        "time": "O(N log M)", "space": "O(1)", "invariant": "Binary search answer space k in [1..max(piles)] using sum(ceil(p/k)) <= h",
        "prompt": "Given banana `piles` and `h` hours, return the minimum integer eating speed `k` so Koko finishes all bananas within `h` hours.",
        "firstLine": "Set speed range `l, r = 1, max(piles)` and binary search the smallest valid `k`.",
        "steps": [
            "Initialize `l, r = 1, max(piles)` and `ans = r`",
            "Test `mid = (l + r) // 2`: compute `hours = sum((p + mid - 1) // mid for p in piles)`",
            "If `hours <= h`, record `ans = mid` and try slower (`r = mid - 1`); else `l = mid + 1`"
        ],
        "cases": [
            {"input": {"piles": [3, 6, 7, 11], "h": 8}, "expected": 4},
            {"input": {"piles": [30, 11, 23, 4, 20], "h": 5}, "expected": 30},
        ],
        "refPy": "class Solution:\n    def minEatingSpeed(self, piles: List[int], h: int) -> int:\n        l, r = 1, max(piles)\n        ans = r\n        while l <= r:\n            mid = (l + r) // 2\n            hrs = sum((p + mid - 1) // mid for p in piles)\n            if hrs <= h:\n                ans = mid\n                r = mid - 1\n            else:\n                l = mid + 1\n        return ans\n",
    },
    {
        "id": 31, "slug": "find-minimum-in-rotated-sorted-array", "method": "findMin",
        "pySig": "def findMin(self, nums: List[int]) -> int:",
        "javaSig": "public int findMin(int[] nums)", "javaRet": "return 0;",
        "time": "O(log N)", "space": "O(1)", "invariant": "nums[mid] > nums[r] -> pivot minimum lies strictly right of mid",
        "prompt": "Given a rotated sorted array `nums` of unique elements, return the minimum element in `O(log N)` time.",
        "firstLine": "Set `l, r = 0, len(nums) - 1` and loop `while l < r:` comparing `nums[mid]` with `nums[r]`.",
        "steps": [
            "Initialize `l = 0`, `r = len(nums) - 1`",
            "While `l < r`, compute `mid = (l + r) // 2`",
            "If `nums[mid] > nums[r]`, set `l = mid + 1`; otherwise set `r = mid`; return `nums[l]`"
        ],
        "cases": [
            {"input": {"nums": [3, 4, 5, 1, 2]}, "expected": 1},
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2]}, "expected": 0},
            {"input": {"nums": [11, 13, 15, 17]}, "expected": 11},
        ],
        "refPy": "class Solution:\n    def findMin(self, nums: List[int]) -> int:\n        l, r = 0, len(nums) - 1\n        while l < r:\n            mid = (l + r) // 2\n            if nums[mid] > nums[r]:\n                l = mid + 1\n            else:\n                r = mid\n        return nums[l]\n",
    },
    {
        "id": 32, "slug": "search-in-rotated-sorted-array", "method": "search",
        "pySig": "def search(self, nums: List[int], target: int) -> int:",
        "javaSig": "public int search(int[] nums, int target)", "javaRet": "return -1;",
        "time": "O(log N)", "space": "O(1)", "invariant": "At least one half [l..mid] or [mid..r] is strictly sorted",
        "prompt": "Given rotated sorted array `nums` of unique integers and `target`, return the index of `target` in `O(log N)` time or `-1`.",
        "firstLine": "Set `l, r = 0, len(nums) - 1` and check whether `[l..mid]` is the sorted half (`nums[l] <= nums[mid]`).",
        "steps": [
            "Loop `while l <= r:` with `mid = (l + r) // 2`; return `mid` if `nums[mid] == target`",
            "If `nums[l] <= nums[mid]` (left half sorted): check `nums[l] <= target < nums[mid]` to pick left vs right",
            "Else (right half sorted): check `nums[mid] < target <= nums[r]` to pick right vs left"
        ],
        "cases": [
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}, "expected": 4},
            {"input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, "expected": -1},
        ],
        "refPy": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        l, r = 0, len(nums) - 1\n        while l <= r:\n            mid = (l + r) // 2\n            if nums[mid] == target:\n                return mid\n            if nums[l] <= nums[mid]:\n                if nums[l] <= target < nums[mid]:\n                    r = mid - 1\n                else:\n                    l = mid + 1\n            else:\n                if nums[mid] < target <= nums[r]:\n                    l = mid + 1\n                else:\n                    r = mid - 1\n        return -1\n",
    },
    {
        "id": 33, "slug": "time-based-key-value-store", "method": "get", "execMode": "class_ops", "className": "TimeMap",
        "pySig": "class TimeMap:\n    def __init__(self):\n        pass\n    def set(self, key: str, value: str, timestamp: int) -> None:\n        pass\n    def get(self, key: str, timestamp: int) -> str:",
        "javaSig": "public String get(String key, int timestamp)", "javaRet": "return \"\";",
        "time": "O(log N)", "space": "O(N)", "invariant": "Timestamps per key are strictly increasing -> rightmost ts <= timestamp",
        "prompt": "Design `TimeMap` supporting `set(key, value, timestamp)` and `get(key, timestamp)` returning the latest value with `ts <= timestamp` (or `\"\"`).",
        "firstLine": "In `__init__`, store `self.store = defaultdict(list)` of `(timestamp, value)` pairs.",
        "steps": [
            "Append `(timestamp, value)` to `self.store[key]` on `set`",
            "On `get(key, timestamp)`, binary search `arr = self.store.get(key, [])`",
            "Track the rightmost `val` where `arr[mid][0] <= timestamp`, returning `\"\"` if none"
        ],
        "cases": [
            {
                "input": {"ops": ["TimeMap", "set", "get", "get", "set", "get", "get"], "args": [[], ["foo", "bar", 1], ["foo", 1], ["foo", 3], ["foo", "bar2", 4], ["foo", 4], ["foo", 5]]},
                "expected": [None, None, "bar", "bar", None, "bar2", "bar2"],
            }
        ],
        "refPy": "class TimeMap:\n    def __init__(self):\n        self.store = defaultdict(list)\n    def set(self, key: str, value: str, timestamp: int) -> None:\n        self.store[key].append((timestamp, value))\n    def get(self, key: str, timestamp: int) -> str:\n        arr = self.store.get(key, [])\n        l, r, res = 0, len(arr) - 1, ''\n        while l <= r:\n            mid = (l + r) // 2\n            if arr[mid][0] <= timestamp:\n                res = arr[mid][1]\n                l = mid + 1\n            else:\n                r = mid - 1\n        return res\n",
    },
    {
        "id": 34, "slug": "median-of-two-sorted-arrays", "method": "findMedianSortedArrays", "compareMode": "float_1e5",
        "pySig": "def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:",
        "javaSig": "public double findMedianSortedArrays(int[] nums1, int[] nums2)", "javaRet": "return 0.0;",
        "time": "O(log(min(M, N)))", "space": "O(1)", "invariant": "Binary search partition i on shorter array so Aleft <= Bright and Bleft <= Aright",
        "prompt": "Given two sorted arrays `nums1` and `nums2`, return their median in `O(log(min(m, n)))` time.",
        "firstLine": "Ensure `A` is the shorter array (`if len(B) < len(A): A, B = B, A`) and set `half = (len(A) + len(B)) // 2`.",
        "steps": [
            "Ensure `A` is shorter than `B`, set `total = len(A) + len(B)` and `half = total // 2`",
            "Binary search `i` on `A` and set `j = half - i - 2`, checking `Aleft <= Bright` and `Bleft <= Aright`",
            "Return `min(Aright, Bright)` if `total` is odd, else `(max(Aleft, Bleft) + min(Aright, Bright)) / 2`"
        ],
        "cases": [
            {"input": {"nums1": [1, 3], "nums2": [2]}, "expected": 2.0},
            {"input": {"nums1": [1, 2], "nums2": [3, 4]}, "expected": 2.5},
        ],
        "refPy": "class Solution:\n    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:\n        A, B = nums1, nums2\n        if len(B) < len(A):\n            A, B = B, A\n        total = len(A) + len(B)\n        half = total // 2\n        l, r = 0, len(A) - 1\n        while True:\n            i = (l + r) // 2\n            j = half - i - 2\n            Al = A[i] if i >= 0 else float('-inf')\n            Ar = A[i + 1] if (i + 1) < len(A) else float('inf')\n            Bl = B[j] if j >= 0 else float('-inf')\n            Br = B[j + 1] if (j + 1) < len(B) else float('inf')\n            if Al <= Br and Bl <= Ar:\n                if total % 2:\n                    return float(min(Ar, Br))\n                return (max(Al, Bl) + min(Ar, Br)) / 2.0\n            elif Al > Br:\n                r = i - 1\n            else:\n                l = i + 1\n",
    },
]
