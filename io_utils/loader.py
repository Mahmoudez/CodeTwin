"""Read Python submissions from a folder while collecting parse errors."""

import ast
from pathlib import Path
from typing import Dict, List, Tuple

from core.models import Submission


def load_submissions(folder: Path) -> Tuple[List[Submission], Dict[Path, str]]:
    """Read and parse direct-child ``.py`` files from ``folder``."""
    submissions: List[Submission] = []
    skipped: Dict[Path, str] = {}
    for path in sorted(Path(folder).glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            submissions.append(Submission(path, source, tree, path.stem))
        except (OSError, UnicodeError, SyntaxError) as error:
            if isinstance(error, SyntaxError):
                reason = f"Syntax error on line {error.lineno}: {error.msg}"
            else:
                reason = str(error)
            skipped[path] = reason
    return submissions, skipped
