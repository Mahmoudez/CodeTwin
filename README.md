# Code Twin

Code Twin is a desktop tool for comparing Python programming submissions by their abstract syntax trees (ASTs). Select a folder containing one `.py` file per student, run an analysis, and inspect the highest scoring pairs.

## Run

Requires Python 3.10 or newer. Tkinter must be included with the Python installation. No pip packages are needed.

```bash
python main.py
```

Choose a folder, select **Analyze**, adjust the minimum score slider, and double-click a row to inspect code. The `samples/` folder is ready for a demo. CSV and JSON export the current full report.

## Architecture

```text
Tk UI ──worker thread──> Analyzer
                           ├── Loader (source + parse errors)
                           ├── Normalizer (canonical AST)
                           ├── Fingerprinter (tokens, subtree hashes, flow)
                           └── Similarity scorer ──> ranked report
                                                   ├── CSV / JSON
                                                   └── table / heatmap / diff UI
```

`core.models` holds the shared report objects. The UI polls a thread-safe queue with Tk's `after()` method, so the analysis work does not block the event loop. The loader currently analyzes direct child `.py` files in the selected folder and skips unreadable or invalid files with an explanation.

## How comparison works

Comments and formatting do not appear in an AST. Code is normalized to canonical user names and literal placeholders, then represented by a preorder node-type sequence, a multiset of hashes for deeper subtrees and function bodies, and an ordered control-flow skeleton. The default score weights sequence similarity at 40%, subtree overlap at 40%, and control-flow similarity at 20%. Names, docstrings, formatting, and many harmless edits can change text while leaving these structural features similar, which makes AST comparison more useful than a raw text diff for finding likely copied work. The result is a review aid, not a finding of misconduct.

Safe normalizations include variable/function/argument/class renaming, literal abstraction, `+=` expansion, and canonical handling of `!=` versus `not ==`. The tool deliberately does not rewrite arbitrary `for` loops into `while` loops: proving those transformations equivalent requires data-flow and side-effect analysis, and unsafe rewrites could create misleading matches. For simple counter loops the control-flow and subtree features can still surface overlap, but no special loop canonicalizer is currently applied.

## Verdicts and interface

Scores of at least 85% are labeled **Highly suspicious**; scores from 65% to below 85% are **Suspicious**; lower scores are **Likely different**. The ranked table supports header sorting and live threshold filtering. The heatmap provides a matrix overview. Pair details show source side by side, score components, reasons, and line highlights for matching hashed subtrees. Use Ctrl+O to choose a folder, Ctrl+R to analyze, and Ctrl+E to export CSV.

## Limitations and future work

- Similarity is evidence for human review, not proof of copying; common assignment patterns can score highly.
- The canonical renaming is traversal-based rather than scope-aware, so shadowing and unusual binding patterns can reduce accuracy.
- Hash matching identifies structurally identical subtrees; semantically equivalent but differently structured code can be missed.
- Loops, comprehensions, recursion, and algorithmic equivalence are not proven equivalent by this tool.
- Large folders require every unique pair to be compared, so runtime grows quadratically with the number of submissions.
- Source is decoded as UTF-8 and only direct `.py` children are loaded.

Future improvements could add scope-aware symbol normalization, careful loop-pattern rewrites, configurable weights, recursive folder selection, and an optional baseline comparison against common solutions.
