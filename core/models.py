"""Data models shared by the analyzer, loader, and user interface."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Submission:
    """A successfully parsed Python submission."""

    path: Path
    source: str
    tree: object
    display_name: str


@dataclass
class PairResult:
    """Similarity measurements and explanation for a submission pair."""

    submission_a: Submission
    submission_b: Submission
    score: float
    sequence_score: float
    subtree_score: float
    control_score: float
    verdict: str
    reasons: List[str] = field(default_factory=list)
    matching_ranges: Tuple[List[Tuple[int, int]], List[Tuple[int, int]]] = field(
        default_factory=lambda: ([], [])
    )


@dataclass
class AnalysisReport:
    """Complete output of one folder analysis."""

    pairs: List[PairResult]
    skipped_files: Dict[Path, str]
    elapsed_seconds: float
    file_count: int
