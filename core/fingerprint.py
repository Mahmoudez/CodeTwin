"""Extract comparable structural features from normalized Python ASTs."""

import ast
import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import Counter as CounterType, List, Tuple


@dataclass
class Fingerprint:
    """Structural features used by the similarity scorer."""

    tokens: List[str]
    subtree_hashes: CounterType[str]
    control_flow: List[Tuple[str, int]]
    hash_lines: dict


def build_fingerprint(tree: ast.AST) -> Fingerprint:
    """Build preorder tokens, subtree hashes, and a control-flow skeleton."""
    tokens: List[str] = []
    hashes: CounterType[str] = Counter()
    control: List[Tuple[str, int]] = []
    hash_lines = {}

    def walk(node: ast.AST, depth: int) -> None:
        tokens.append(type(node).__name__)
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            control.append(("loop", depth))
        elif isinstance(node, ast.If):
            control.append(("conditional", depth))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            control.append(("function", depth))
        elif isinstance(node, ast.Return):
            control.append(("return", depth))
        children = list(ast.iter_child_nodes(node))
        for child in children:
            walk(child, depth + 1)
        if depth >= 3 or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            digest = hashlib.sha256(ast.dump(node, include_attributes=False).encode("utf-8")).hexdigest()
            hashes[digest] += 1
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", start)
            if start is not None:
                hash_lines.setdefault(digest, []).append((start, end or start))

    walk(tree, 0)
    return Fingerprint(tokens, hashes, control, hash_lines)
