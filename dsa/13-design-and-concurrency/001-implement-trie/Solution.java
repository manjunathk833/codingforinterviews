public class Solution {

    static class TrieNode {
        // TODO: Define node members if needed
    }

    public static class Trie {
        public Trie() {
            // TODO: Initialize your data structure here
        }

        public void insert(String word) {
            // TODO: Implement insert
        }

        public boolean search(String word) {
            // TODO: Implement search
            return false;
        }

        public boolean startsWith(String prefix) {
            // TODO: Implement startsWith
            return false;
        }
    }

    public static void main(String[] args) {
        Trie trie = new Trie();

        trie.insert("apple");
        assert trie.search("apple") : "Test 1 Failed: Expected true";
        assert !trie.search("app") : "Test 2 Failed: Expected false";
        assert trie.startsWith("app") : "Test 3 Failed: Expected true";

        trie.insert("app");
        assert trie.search("app") : "Test 4 Failed: Expected true";

        System.out.println("All 4 Java Trie test cases passed!");
    }
}
