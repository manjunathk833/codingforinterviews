"""Blank Workspace — Lab 09: Reverse-Dependency Test Impact Analysis (TIA) Graph."""
from collections import deque
from typing import Dict, List, Set


def select_impacted_tests(
    dep_graph: Dict[str, List[str]],
    changed_files: List[str],
    global_triggers: Set[str],
) -> List[str]:
    """Return sorted `test_*` targets transitively impacted by `changed_files`."""
    raise NotImplementedError("Implement select_impacted_tests()")
