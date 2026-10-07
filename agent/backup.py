"""Recoverable snapshots for project files before controlled edits."""
from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "memory" / "snapshots"

def snapshot(paths: list[str] | None = None):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    selected = [(ROOT / p).resolve() for p in paths] if paths else [ROOT / "agent", ROOT / "skills"]
    for source in selected:
        if source != ROOT and ROOT not in source.parents:
            raise ValueError(f"Snapshot path must stay inside project: {source}")
        if not source.exists():
            raise FileNotFoundError(source)
    target = SNAPSHOTS / stamp
    target.mkdir(parents=True, exist_ok=False)
    for source in selected:
        if source.is_file():
            destination = target / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        elif source.is_dir():
            shutil.copytree(source, target / source.relative_to(ROOT), ignore=shutil.ignore_patterns("venv", "__pycache__"))
    return str(target)
