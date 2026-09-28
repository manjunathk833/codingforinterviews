class TrieNode:
    def __init__(self):
        # TODO: Define node members if needed
        pass


class Solution:
    class Trie:
        def __init__(self):
            # TODO: Initialize your data structure here
            pass

        def insert(self, word: str) -> None:
            # TODO: Implement insert
            pass

        def search(self, word: str) -> bool:
            # TODO: Implement search
            return False

        def startsWith(self, prefix: str) -> bool:
            # TODO: Implement startsWith
            return False


if __name__ == "__main__":
    trie = Solution.Trie()

    trie.insert("apple")
    assert trie.search("apple") is True, "Test 1 Failed"
    assert trie.search("app") is False, "Test 2 Failed"
    assert trie.startsWith("app") is True, "Test 3 Failed"

    trie.insert("app")
    assert trie.search("app") is True, "Test 4 Failed"

    print("All 4 Python Trie test cases passed!")
