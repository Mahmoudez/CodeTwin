"""Conservative AST normalization for comparing Python program structure."""

import ast
import builtins
from typing import Dict, Set

SMALL_INTEGERS = {0, 1, -1}
BUILTIN_NAMES: Set[str] = set(dir(builtins))


class AstNormalizer(ast.NodeTransformer):
    """Rename user identifiers and canonicalize safe equivalent syntax."""

    def __init__(self) -> None:
        """Create an isolated name map for one syntax tree."""
        self.names: Dict[str, str] = {}
        self.imported: Set[str] = set()

    def _canonical(self, name: str, kind: str = "VAR") -> str:
        """Return a stable placeholder for a user-defined identifier."""
        if name in BUILTIN_NAMES or name in self.imported:
            return name
        if name not in self.names:
            self.names[name] = f"{kind}_{len(self.names)}"
        return self.names[name]

    def visit_Import(self, node: ast.Import) -> ast.AST:
        """Preserve imported module names and bind aliases consistently."""
        for alias in node.names:
            bound = alias.asname or alias.name.split(".")[0]
            self.imported.add(bound)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        """Preserve imported symbols and module names."""
        if node.module:
            self.imported.add(node.module.split(".")[0])
        for alias in node.names:
            self.imported.add(alias.asname or alias.name)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Normalize function names and remove leading docstrings."""
        node.name = self._canonical(node.name, "FUNC")
        node.body = self._without_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        """Normalize async function names and remove leading docstrings."""
        node.name = self._canonical(node.name, "FUNC")
        node.body = self._without_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """Normalize class names and remove leading docstrings."""
        node.name = self._canonical(node.name, "CLASS")
        node.body = self._without_docstring(node.body)
        self.generic_visit(node)
        return node

    @staticmethod
    def _without_docstring(body: list) -> list:
        """Remove a module, class, or function's leading string expression."""
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            return body[1:]
        return body

    def visit_Name(self, node: ast.Name) -> ast.AST:
        """Canonicalize names that are not builtins or imported symbols."""
        node.id = self._canonical(node.id)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        """Canonicalize function argument names."""
        node.arg = self._canonical(node.arg, "ARG")
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        """Keep small integers and replace other literal values by type."""
        if isinstance(node.value, bool) or node.value is None:
            return node
        if isinstance(node.value, int) and node.value in SMALL_INTEGERS:
            return node
        node.value = "STRING" if isinstance(node.value, str) else "NUM" if isinstance(node.value, (int, float, complex)) else "BYTES" if isinstance(node.value, bytes) else "LITERAL"
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        """Rewrite simple ``x += y`` into the equivalent assignment form."""
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            replacement = ast.Assign(
                targets=[node.target],
                value=ast.BinOp(left=ast.copy_location(ast.Name(id=node.target.id, ctx=ast.Load()), node.target), op=node.op, right=node.value),
            )
            return ast.copy_location(replacement, node)
        return node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        """Represent ``x != y`` and ``not x == y`` with the same AST shape."""
        self.generic_visit(node)
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.NotEq):
            node.ops[0] = ast.Eq()
            return ast.copy_location(ast.UnaryOp(op=ast.Not(), operand=node), node)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        """Canonicalize ``not (x != y)`` to ``x == y`` where unambiguous."""
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and isinstance(node.operand, ast.Compare) and len(node.operand.ops) == 1:
            compare = node.operand
            if isinstance(compare.ops[0], ast.NotEq):
                compare.ops[0] = ast.Eq()
                return ast.copy_location(compare, node)
        return node


def normalize_ast(tree: ast.AST) -> ast.AST:
    """Return a normalized copy of a parsed Python AST."""
    normalized = AstNormalizer().visit(ast.fix_missing_locations(tree))
    return ast.fix_missing_locations(normalized)
