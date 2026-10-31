"""Self-acquisition workflow: inspect and validate local skill candidates without executing foreign code."""
from __future__ import annotations
import ast
import json
from pathlib import Path

RISK_LEVEL = "medium"
ROOT = Path(__file__).resolve().parent.parent

def run(argument=None):
    data = argument if isinstance(argument, dict) else json.loads(str(argument or "{}"))
    path = Path(str(data.get("path", ""))).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return {"ok": False, "blocked": True, "reason": "path_outside_project"}
    if not path.is_file() or path.suffix != ".py":
        return {"ok": False, "error": "python_skill_file_required"}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        has_run = "run" in names
        imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import) and node.names]
        return {"ok": has_run, "path": str(path), "syntax_valid": True, "has_run": has_run, "imports": imports[:50], "activation": "review_required", "executed": False, "reason": "AST validation only; import and activation require an approved review."}
    except SyntaxError as exc:
        return {"ok": False, "path": str(path), "syntax_valid": False, "error": str(exc)}
