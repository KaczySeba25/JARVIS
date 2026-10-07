"""Metadata registry for skills; implementation remains small and discoverable."""
from dataclasses import dataclass
from pathlib import Path
import ast
import json
from datetime import datetime, timezone

@dataclass(frozen=True)
class SkillMeta:
    name: str
    description: str
    risk: str
    needs_network: bool
    has_run: bool
    has_module_doc: bool
    last_verified: str | None = None
    source_count: int = 0

def discover(directory: Path) -> list[SkillMeta]:
    high_risk = {"system_cmd", "code_tester", "vault_manager", "universal_login", "skill_lifecycle", "skill_builder", "workspace_runner", "workspace_history"}
    medium_risk = {"code_writer", "self_improvement", "memory_save", "memory_forget", "memory_manage", "file_manager", "task_manager", "notification_router", "workflow_scheduler"}
    network = {"web_research", "deep_research", "market_data", "security_audit", "universal_login"}
    result = []
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("__"): continue
        has_run = False
        has_module_doc = False
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            doc = ast.get_docstring(tree) or "Brak opisu."
            has_module_doc = bool(ast.get_docstring(tree))
            has_run = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run" for node in tree.body)
            declared = next((node.value.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "RISK_LEVEL" for target in node.targets) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)), None)
        except SyntaxError:
            doc = "Błąd składni."
            declared = None
        risk = declared if declared in {"low", "medium", "high", "critical"} else "high" if path.stem in high_risk else "medium" if path.stem in medium_risk else "low"
        manifest = Path(directory).resolve().parent / "memory" / "skill_versions" / f"{path.stem}.json"
        last_verified, source_count = None, 0
        try:
            metadata = json.loads(manifest.read_text(encoding="utf-8")).get("metadata", {})
            verified = metadata.get("verified_at")
            last_verified = str(verified)[:32] if verified else None
            source_count = min(50, len(metadata.get("research_sources", [])))
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        result.append(SkillMeta(path.stem, doc.splitlines()[0][:160], risk, path.stem in network, has_run, has_module_doc, last_verified, source_count))
    return result
