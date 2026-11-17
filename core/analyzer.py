"""Coordinate loading and pairwise similarity analysis."""

import time
from pathlib import Path
from typing import Callable, Optional

from core.fingerprint import build_fingerprint
from core.models import AnalysisReport
from core.normalizer import normalize_ast
from core.similarity import score_pair
from io_utils.loader import load_submissions


class Analyzer:
    """Analyze all Python submissions in a selected folder."""

    def run(self, folder: Path, progress_callback: Optional[Callable[[str], None]] = None) -> AnalysisReport:
        """Load, fingerprint, and rank every unique pair in ``folder``."""
        started = time.perf_counter()
        submissions, skipped = load_submissions(folder)
        total_pairs = len(submissions) * (len(submissions) - 1) // 2
        fingerprints = {}
        for index, submission in enumerate(submissions, start=1):
            fingerprints[submission.path] = build_fingerprint(normalize_ast(submission.tree))
            if progress_callback:
                progress_callback(f"Fingerprinting {index}/{len(submissions)} files")
        pairs = []
        completed = 0
        for index, first in enumerate(submissions):
            for second in submissions[index + 1:]:
                pairs.append(score_pair(first, second, fingerprints[first.path], fingerprints[second.path]))
                completed += 1
                if progress_callback:
                    progress_callback(f"Comparing {completed}/{total_pairs} pairs")
        pairs.sort(key=lambda item: item.score, reverse=True)
        return AnalysisReport(pairs, skipped, time.perf_counter() - started, len(submissions))
