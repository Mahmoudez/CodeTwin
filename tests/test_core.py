"""Focused regression tests for AST similarity and input error handling."""

import tempfile
import unittest
from pathlib import Path

from core.analyzer import Analyzer
from core.fingerprint import build_fingerprint
from core.normalizer import normalize_ast
from core.similarity import score_pair
from io_utils.loader import load_submissions


class CoreTests(unittest.TestCase):
    """Verify key similarity and syntax-error behavior."""

    def _pair_score(self, left: str, right: str) -> float:
        """Score two in-memory snippets through the production pipeline."""
        import ast
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "first.py"
            second_path = Path(directory) / "second.py"
            first_path.write_text(left, encoding="utf-8")
            second_path.write_text(right, encoding="utf-8")
            submissions, _ = load_submissions(Path(directory))
            fingerprints = [build_fingerprint(normalize_ast(item.tree)) for item in submissions]
            return score_pair(submissions[0], submissions[1], *fingerprints).score

    def test_renamed_copy_scores_high(self) -> None:
        """Variable and function renaming should preserve high similarity."""
        first = "def total(x, values):\n    for value in values:\n        if value > 0:\n            x += value\n    return x\n"
        second = "def amount(start, entries):\n    for entry in entries:\n        if entry > 0:\n            start = start + entry\n    return start\n"
        self.assertGreaterEqual(self._pair_score(first, second), 0.85)

    def test_different_solution_scores_low(self) -> None:
        """A structurally different algorithm should remain below threshold."""
        first = "def total(x, values):\n    for value in values:\n        if value > 0:\n            x += value\n    return x\n"
        second = "def search(items, target):\n    left = 0\n    right = len(items)\n    while left < right:\n        middle = (left + right) // 2\n        if items[middle] == target:\n            return middle\n        right = middle\n    return -1\n"
        self.assertLess(self._pair_score(first, second), 0.6)

    def test_syntax_error_is_reported_as_skipped(self) -> None:
        """Malformed student code is reported without aborting folder load."""
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "good.py").write_text("print('ok')\n", encoding="utf-8")
            (folder / "broken.py").write_text("def broken(:\n", encoding="utf-8")
            report = Analyzer().run(folder)
            self.assertEqual(report.file_count, 1)
            self.assertIn(folder / "broken.py", report.skipped_files)


if __name__ == "__main__":
    unittest.main()
