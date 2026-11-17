"""Pairwise AST similarity scoring and matching source ranges."""

import ast
from difflib import SequenceMatcher
from typing import List, Tuple

from core.fingerprint import Fingerprint
from core.models import PairResult, Submission

SEQUENCE_WEIGHT = 0.40
SUBTREE_WEIGHT = 0.40
CONTROL_WEIGHT = 0.20


def _multiset_jaccard(first, second) -> float:
    """Compute multiset Jaccard similarity for hash counters."""
    keys = set(first) | set(second)
    union = sum(max(first[key], second[key]) for key in keys)
    if not union:
        return 1.0
    intersection = sum(min(first[key], second[key]) for key in keys)
    return intersection / union


def _control_similarity(first: List[Tuple[str, int]], second: List[Tuple[str, int]]) -> float:
    """Compare ordered control-flow labels and nesting depths."""
    if not first and not second:
        return 1.0
    return SequenceMatcher(None, first, second, autojunk=False).ratio()


def score_pair(first: Submission, second: Submission, fp_first: Fingerprint, fp_second: Fingerprint) -> PairResult:
    """Score a pair and explain its most useful structural similarities."""
    sequence = SequenceMatcher(None, fp_first.tokens, fp_second.tokens, autojunk=False).ratio()
    subtree = _multiset_jaccard(fp_first.subtree_hashes, fp_second.subtree_hashes)
    control = _control_similarity(fp_first.control_flow, fp_second.control_flow)
    score = SEQUENCE_WEIGHT * sequence + SUBTREE_WEIGHT * subtree + CONTROL_WEIGHT * control
    reasons = []
    if control >= 0.95:
        reasons.append("Identical control-flow skeleton")
    if subtree >= 0.65:
        reasons.append(f"{subtree:.0%} of structural subtrees match")
    if sequence >= 0.85:
        reasons.append(f"AST node sequence is {sequence:.0%} similar")
    if not reasons:
        reasons.append("Limited structural overlap")
    verdict = "Highly suspicious" if score >= 0.85 else "Suspicious" if score >= 0.65 else "Likely different"
    ranges = matching_line_ranges(fp_first, fp_second)
    return PairResult(first, second, score, sequence, subtree, control, verdict, reasons, ranges)


def matching_line_ranges(first: Fingerprint, second: Fingerprint) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return source line spans for structurally identical hashed subtrees."""
    common = first.subtree_hashes & second.subtree_hashes
    left: List[Tuple[int, int]] = []
    right: List[Tuple[int, int]] = []
    for digest, count in common.items():
        left.extend(first.hash_lines.get(digest, [])[:count])
        right.extend(second.hash_lines.get(digest, [])[:count])
    return _merge_ranges(left), _merge_ranges(right)


def _merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Sort and coalesce overlapping source ranges."""
    merged: List[Tuple[int, int]] = []
    for start, end in sorted(set(ranges)):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
