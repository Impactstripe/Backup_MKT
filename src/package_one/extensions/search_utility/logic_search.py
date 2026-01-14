import os
import re
from typing import List, Tuple


def search_in_files(query: str, root: str) -> List[Tuple[str, int, str]]:
    """Search for query (regex or plain text) in files under root.
    Returns list of tuples (filepath, line_number, line_text).
    """
    results = []
    pattern = re.compile(query, re.IGNORECASE)
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            # skip binary files by simple heuristic
            if fn.endswith(('.pyc', '.pyo', '.exe', '.dll')):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, start=1):
                        if pattern.search(line):
                            results.append((path, i, line.rstrip('\n')))
            except Exception:
                # ignore unreadable files
                continue
    return results


if __name__ == '__main__':
    # quick manual test
    for p, ln, txt in search_in_files('TODO', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))):
        print(f"{p}:{ln}: {txt}")
