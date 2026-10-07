"""Read-only project inventory and code health summary."""
from pathlib import Path
import ast

def run(root: str | None = None):
    root = root or str(Path(__file__).resolve().parent.parent)
    base = Path(root)
    if not base.exists(): return "Folder projektu nie istnieje."
    files = [p for p in base.rglob("*") if p.is_file() and "venv" not in p.parts and "__pycache__" not in p.parts]
    py = [p for p in files if p.suffix == ".py"]
    errors = []
    for path in py:
        try: ast.parse(path.read_text(encoding="utf-8-sig"))
        except Exception as exc: errors.append(f"{path}: {exc}")
    return f"Projekt: {len(files)} plików, {len(py)} Python, błędy składni: {len(errors)}\n" + "\n".join(errors[:20])
