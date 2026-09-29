class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Solution:
    class Trie:
        def __init__(self):
            self.root = TrieNode()

        def insert(self, word: str) -> None:
            curr = self.root
            for c in word:
                if c not in curr.children:
                    curr.children[c] = TrieNode()
                curr = curr.children[c]
            curr.is_end_of_word = True

        def search(self, word: str) -> bool:
            node = self._find_node(word)
            return node is not None and node.is_end_of_word

        def startsWith(self, prefix: str) -> bool:
            return self._find_node(prefix) is not None

        def _find_node(self, prefix: str):
            curr = self.root
            for c in prefix:
                if c not in curr.children:
                    return None
                curr = curr.children[c]
            return curr


if __name__ == "__main__":
    trie = Solution.Trie()

    trie.insert("apple")
    assert trie.search("apple") is True, "Test 1 Failed"
    assert trie.search("app") is False, "Test 2 Failed"
    assert trie.startsWith("app") is True, "Test 3 Failed"

    trie.insert("app")
    assert trie.search("app") is True, "Test 4 Failed"

    print("All 4 Python Trie test cases passed!")
