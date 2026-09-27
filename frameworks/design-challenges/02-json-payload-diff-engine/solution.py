"""SDET Challenge: Deep JSON Payload Diff Engine"""
from typing import Any, List, Set


class Solution:
    def compare(
        self,
        expected: Any,
        actual: Any,
        ignore_paths: Set[str] = None,
    ) -> List[str]:
        """Deeply compares two JSON structures and returns list of difference strings."""
        if ignore_paths is None:
            ignore_paths = set()

        differences = []

        def _compare(current_path: str, exp: Any, act: Any):
            if current_path in ignore_paths:
                return

            if exp is None and act is None:
                return

            if exp is None or act is None:
                differences.append(f"Path '{current_path}': expected [{exp}], but got [{act}]")
                return

            if isinstance(exp, dict) and isinstance(act, dict):
                all_keys = set(exp.keys()).union(set(act.keys()))
                for k in all_keys:
                    sub_path = f"{current_path}.{k}" if current_path else k
                    if k not in exp:
                        differences.append(f"Path '{sub_path}': expected [<ABSENT>], but got [{act[k]}]")
                    elif k not in act:
                        differences.append(f"Path '{sub_path}': expected [{exp[k]}], but got [<ABSENT>]")
                    else:
                        _compare(sub_path, exp[k], act[k])
            elif isinstance(exp, list) and isinstance(act, list):
                if len(exp) != len(act):
                    differences.append(f"Path '{current_path}.length': expected [{len(exp)}], but got [{len(act)}]")
                else:
                    for i, (item_exp, item_act) in enumerate(zip(exp, act)):
                        _compare(f"{current_path}[{i}]", item_exp, item_act)
            else:
                if exp != act:
                    differences.append(f"Path '{current_path}': expected [{exp}], but got [{act}]")

        _compare("", expected, actual)
        return differences


if __name__ == "__main__":
    engine = Solution()

    expected = {
        "status": "ACTIVE",
        "timestamp": 1600000000,
        "user": {"name": "Alice", "role": "ADMIN"},
    }

    actual = {
        "status": "ACTIVE",
        "timestamp": 1750000000,  # Dynamic
        "user": {"name": "Alice", "role": "USER"},  # Mismatch
    }

    # Test 1
    diffs = engine.compare(expected, actual, ignore_paths={"timestamp"})
    assert len(diffs) == 1, f"Test 1 Failed: expected 1 diff, got {diffs}"
    assert "user.role" in diffs[0], f"Test 1 Failed: expected diff on user.role, got {diffs[0]}"

    # Test 2: Identical
    diffs_identical = engine.compare(expected, expected)
    assert len(diffs_identical) == 0, "Test 2 Failed: Identical dicts reported diffs"

    print("All 2 Python JSON Diff Engine test cases passed!")
