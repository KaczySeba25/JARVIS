"""Static quality audit for Jarvis capabilities and dynamically loaded skills."""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CapabilityFinding:
    name: str
    status: str
    score: int
    checks: dict[str, bool]
    warnings: list[str]


def _audit_file(path: Path) -> CapabilityFinding:
    checks = {
        "parseable": False,
        "documented": False,
        "run_entrypoint": False,
        "error_boundary": False,
        "no_secret_literals": True,
    }
    warnings: list[str] = []
    try:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        checks["parseable"] = True
        checks["documented"] = bool(ast.get_docstring(tree))
        checks["run_entrypoint"] = any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run"
            for node in tree.body
        ) or any(
            isinstance(node, ast.ImportFrom) and any(alias.name == "run" for alias in node.names)
            for node in ast.walk(tree)
        )
        checks["error_boundary"] = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        checks["no_secret_literals"] = not any(
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and not any(ch in node.value for ch in "[]()?*+")
            and any(token in node.value.lower() for token in ("gsk_", "sk-", "api_key="))
            for node in ast.walk(tree)
        )
    except (OSError, SyntaxError) as exc:
        warnings.append(f"Nie można przeanalizować pliku: {type(exc).__name__}")
    if not checks["documented"]:
        warnings.append("Brak docstringa modułu.")
    if not checks["run_entrypoint"]:
        warnings.append("Brak kontraktu run(argument=None).")
    if not checks["error_boundary"]:
        warnings.append("Brak lokalnej granicy obsługi wyjątków.")
    if not checks["no_secret_literals"]:
        warnings.append("Wykryto wzorzec sekretu w kodzie.")
    # The runtime wrapper in JarvisCore is the common exception boundary. Local
    # try/except is a strengthening signal, not a reason to reject a skill.
    essential = ("parseable", "run_entrypoint", "no_secret_literals")
    score = round(100 * sum(checks[key] for key in essential) / len(essential))
    status = "pass" if all(checks[key] for key in essential) else "review"
    return CapabilityFinding(path.stem, status, score, checks, warnings)


def audit_skills(directory: Path) -> list[CapabilityFinding]:
    """Audit every skill without importing or executing it."""
    return [_audit_file(path) for path in sorted(directory.glob("*.py")) if not path.name.startswith("__")]


def report(directory: Path) -> dict:
    findings = audit_skills(directory)
    return {
        "directory": str(directory),
        "total": len(findings),
        "passed": sum(item.status == "pass" for item in findings),
        "review": sum(item.status == "review" for item in findings),
        "findings": [asdict(item) for item in findings],
    }


def main() -> int:
    root = Path(__file__).resolve().parent.parent / "skills"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report(root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
