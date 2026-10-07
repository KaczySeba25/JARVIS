"""Draft -> validate -> review lifecycle for Jarvis-created skills."""
from __future__ import annotations
import json
import ast
import os
import keyword
import py_compile
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "memory" / "skill_drafts"
ACTIVE = ROOT / "skills"
VERSIONS = ROOT / "memory" / "skill_versions"

_DANGEROUS_IMPORTS = {"subprocess", "ctypes", "multiprocessing", "winreg", "pty", "os", "sys", "builtins", "importlib", "socket"}
_DANGEROUS_CALLS = {"eval", "exec", "compile", "__import__", "system", "popen", "globals", "locals", "open", "getattr", "setattr", "delattr", "vars"}

def _safe_name(name: str) -> bool:
    return bool(name and name.isidentifier() and not keyword.iskeyword(name) and not name.startswith("_"))

def _static_review(path: Path) -> list[str]:
    """Reject import-time actions and common escape hatches in generated skills."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    issues = []
    declared_risk = None
    for node in tree.body:
        allowed = isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef, ast.AsyncFunctionDef))
        allowed = allowed or isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        if not allowed:
            issues.append("Niedozwolona konstrukcja poza funkcją run().")
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "RISK_LEVEL" for target in node.targets) and isinstance(node.value, ast.Constant):
            declared_risk = node.value.value
        if isinstance(node, ast.Expr) and not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            issues.append("Kod wykonywalny poza funkcją run() zostaje odrzucony.")
        if isinstance(node, ast.Assign) and not isinstance(node.value, ast.Constant):
            issues.append("Inicjalizacja wykonywalna poza run() zostaje odrzucona.")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = [*node.args.defaults, *(value for value in node.args.kw_defaults if value is not None)]
            annotations = [node.returns, *[arg.annotation for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs) if arg.annotation]]
            if node.decorator_list or any(isinstance(child, ast.Call) for expr in [*defaults, *annotations] for child in ast.walk(expr)):
                issues.append("Dekorator lub wywołanie domyślne poza run() zostaje odrzucone.")
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] in _DANGEROUS_IMPORTS for alias in node.names):
                issues.append("Niedozwolony import w skillu tworzonym automatycznie.")
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in _DANGEROUS_IMPORTS:
            issues.append("Niedozwolony import w skillu tworzonym automatycznie.")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _DANGEROUS_CALLS:
                issues.append(f"Niedozwolona funkcja: {node.func.id}.")
    if declared_risk not in {"high", "critical"}:
        issues.append("Nowy skill musi pozostać oznaczony jako wysokiego ryzyka.")
    return sorted(set(issues))

def create_draft(name: str, code: str) -> Path:
    if not _safe_name(name) or not code.strip():
        raise ValueError("Nieprawidłowa nazwa albo pusty kod.")
    DRAFTS.mkdir(parents=True, exist_ok=True)
    path = DRAFTS / f"{name}.py"
    try:
        tree = ast.parse(code)
        has_risk = any(isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "RISK_LEVEL" for target in node.targets) for node in tree.body)
        if not has_risk:
            insertion_line = 0
            for index, node in enumerate(tree.body):
                is_doc = index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
                is_future = isinstance(node, ast.ImportFrom) and node.module == "__future__"
                if is_doc or is_future:
                    insertion_line = node.end_lineno
                else:
                    break
            lines = code.splitlines(keepends=True)
            lines.insert(insertion_line, 'RISK_LEVEL = "high"\n')
            code = "".join(lines)
    except SyntaxError:
        pass
    path.write_text(code, encoding="utf-8")
    return path

def validate(name: str) -> dict:
    if not _safe_name(name):
        return {"name": str(name), "syntax": False, "execution": False, "promoted": False, "errors": ["Nieprawidłowa nazwa draftu."]}
    path = (DRAFTS / f"{name}.py").resolve()
    if path.parent != DRAFTS.resolve():
        return {"name": name, "syntax": False, "execution": False, "promoted": False, "errors": ["Draft poza dozwolonym folderem."]}
    report = {"name": name, "path": str(path), "syntax": False, "execution": False, "promoted": False, "errors": []}
    if not path.exists():
        report["errors"].append("Brak draftu.")
        return report
    try:
        py_compile.compile(str(path), doraise=True)
        report["syntax"] = True
    except Exception as exc:
        report["errors"].append(f"Składnia: {exc}")
        return report
    issues = _static_review(path)
    if issues:
        report["errors"].extend(issues)
        return report
    probe = "import importlib.util,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location('draft',p); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); print('RUN_OK' if callable(getattr(m,'run',None)) else 'NO_RUN')"
    try:
        result = subprocess.run([sys.executable, "-c", probe, str(path)], capture_output=True, text=True, timeout=10, cwd=str(ROOT))
        if result.returncode == 0 and "RUN_OK" in result.stdout:
            report["execution"] = True
        else:
            report["errors"].append((result.stderr or result.stdout).strip()[:1000])
    except subprocess.TimeoutExpired:
        report["errors"].append("Przekroczony limit 10 sekund.")
    (path.with_suffix(".report.json")).write_text(json.dumps({**report, "checked_at": time.time()}, indent=2, ensure_ascii=False), encoding="utf-8")
    return report

def promote(name: str, confirm=False, metadata: dict | None = None) -> str:
    if not _safe_name(name):
        return "Odrzucono: nieprawidłowa nazwa skilla."
    report = validate(name)
    if not (report["syntax"] and report["execution"]): return "Odrzucono: " + json.dumps(report, ensure_ascii=False)
    if not confirm: return "Zweryfikowano. Promocja wymaga osobnego potwierdzenia użytkownika."
    source, target = (DRAFTS / f"{name}.py").resolve(), (ACTIVE / f"{name}.py").resolve()
    if source.parent != DRAFTS.resolve() or target.parent != ACTIVE.resolve():
        return "Odrzucono: ścieżka poza dozwolonym folderem."
    ACTIVE.mkdir(parents=True, exist_ok=True)
    if target.exists():
        VERSIONS.mkdir(parents=True, exist_ok=True)
        backup = VERSIONS / f"{name}_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 1000000:06d}.py"
        shutil.copy2(target, backup)
    else:
        backup = None
    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    os.replace(temporary, target)
    VERSIONS.mkdir(parents=True, exist_ok=True)
    manifest = {"backup": backup.name if backup else None, "promoted_at": time.time(), "metadata": metadata or {}}
    (VERSIONS / f"{name}.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    version_id = time.strftime('%Y%m%d_%H%M%S')
    history = VERSIONS / f"{name}.history.jsonl"
    with history.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"version": version_id, **manifest}, ensure_ascii=False, default=str) + "\n")
    return f"Skill {name} aktywowany po walidacji."

def rollback(name: str) -> dict:
    """Restore the previous skill revision, or remove a newly added broken skill."""
    if not _safe_name(name):
        return {"rolled_back": False, "reason": "invalid_name"}
    manifest = VERSIONS / f"{name}.json"
    target = (ACTIVE / f"{name}.py").resolve()
    if not manifest.exists() or target.parent != ACTIVE.resolve():
        return {"rolled_back": False, "reason": "no_managed_revision"}
    info = json.loads(manifest.read_text(encoding="utf-8"))
    backup_name = info.get("backup")
    if backup_name:
        backup = (VERSIONS / backup_name).resolve()
        if backup.parent != VERSIONS.resolve() or not backup.is_file():
            return {"rolled_back": False, "reason": "backup_missing"}
        temporary = target.with_suffix(".py.rollback")
        shutil.copy2(backup, temporary)
        os.replace(temporary, target)
    else:
        target.unlink(missing_ok=True)
    manifest.unlink(missing_ok=True)
    return {"rolled_back": True, "skill": name, "restored": backup_name}
