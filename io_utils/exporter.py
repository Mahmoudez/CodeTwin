"""Export an analysis report to portable CSV and JSON files.

Two public functions (same names and arguments the UI already calls):
    export_csv(report, destination)   -> opens nicely in Excel
    export_json(report, destination)  -> easy for other programs to read

IMPORTANT: the only place that knows the field names of a pair is
`pair_to_row()`. If a field name is wrong, fix it there and nothing else
in this file needs to change.
"""

import csv
import json
from pathlib import Path

from core.models import AnalysisReport

CSV_HEADERS = ["Student A", "Student B", "Score", "Verdict", "Reasons"]


def pair_to_row(pair) -> dict:
    """Turn one PairResult into a plain dictionary.

    Adjust the attribute names here to match core/models.py.
    """
    return {
        "Student A": pair.submission_a.display_name,
        "Student B": pair.submission_b.display_name,
        "Score": round(pair.score * 100, 1),
        "Verdict": pair.verdict,
        "Reasons": " | ".join(pair.reasons),
    }


def export_csv(report: AnalysisReport, destination: Path) -> None:
    """Save the ranked pairs as a CSV file."""
    # utf-8-sig so Excel shows non-English text correctly
    with Path(destination).open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for pair in report.pairs:
            writer.writerow(pair_to_row(pair))


def export_json(report: AnalysisReport, destination: Path) -> None:
    """Save ranked pairs, skipped files, and timing data as JSON."""
    payload = {
        "file_count": report.file_count,
        "elapsed_seconds": report.elapsed_seconds,
        "skipped_files": {str(path): reason for path, reason in report.skipped_files.items()},
        "pairs": [pair_to_row(pair) for pair in report.pairs],
    }
    Path(destination).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )