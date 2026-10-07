"""Run bounded project checks without passing a command through a shell."""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.resolve()
WORKSPACE = ROOT / "workspace"
ALLOWED = {"python", "python.exe", "py", "py.exe", "git", "git.exe"}
GIT_READ_ONLY = {"status", "diff", "show", "log", "rev-parse", "branch"}
_SECRET = re.compile(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|((?:password|passwd|api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"']?)[^\s,;\"']+|bearer\s+[A-Za-z0-9._~+/-]+=*)")


def _redact(value):
    return _SECRET.sub(lambda match: (match.group(1) or "") + "[REDACTED]", value)


def run(command: str):
    """Accept command text or JSON {argv:[...],cwd,timeout}; shell syntax is not supported."""
    try:
        raw = str(command or "").strip()
        request = json.loads(raw) if raw.startswith("{") else {"command": raw}
        if not isinstance(request, dict):
            return {"ok": False, "error": "input_must_be_command_or_json"}
        raw_argv = request.get("argv")
        if isinstance(raw_argv, list) and all(isinstance(part, str) for part in raw_argv):
            argv = raw_argv
            cmd = " ".join(argv)
        else:
            cmd = str(request.get("command", "")).strip()
            argv = shlex.split(cmd, posix=os.name != "nt")
        if not argv or Path(argv[0]).name.lower() not in ALLOWED:
            return {"ok": False, "error": "executable_not_allowed", "allowed": sorted(ALLOWED)}
        if len(argv) > 100 or any(len(part) > 4000 for part in argv):
            return {"ok": False, "error": "arguments_too_large"}
        executable = Path(argv[0]).name.lower()
        if executable.startswith("python") or executable.startswith("py"):
            argv[0] = sys.executable
        else:
            resolved_git = shutil.which(argv[0])
            if not resolved_git:
                return {"ok": False, "error": "git_not_found"}
            argv[0] = resolved_git
        if any(token in cmd for token in ("|", ";", "&&", "||", ">", "<", "`", "$(", "&")):
            return {"ok": False, "error": "shell_operators_not_allowed"}
        if executable.startswith("git") and (len(argv) < 2 or argv[1].lower() not in GIT_READ_ONLY):
            return {"ok": False, "error": "git_operation_not_read_only"}
        if executable.startswith("python") or executable.startswith("py"):
            if any(arg == "-c" or arg.startswith("-c") for arg in argv[1:]):
                return {"ok": False, "error": "inline_code_not_allowed"}
        cwd = (WORKSPACE / str(request.get("cwd", "."))).resolve()
        if cwd != WORKSPACE and WORKSPACE not in cwd.parents:
            return {"ok": False, "error": "working_directory_outside_workspace"}
        if not cwd.is_dir():
            return {"ok": False, "error": "working_directory_not_found", "cwd": str(cwd)}
        timeout = max(1, min(int(request.get("timeout", 60)), 180))
        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            result = subprocess.run(argv, cwd=str(cwd), stdout=stdout_file, stderr=stderr_file, timeout=timeout, shell=False)
            stdout_size, stderr_size = stdout_file.tell(), stderr_file.tell()
            stdout_file.seek(max(0, stdout_size - 12000))
            stderr_file.seek(max(0, stderr_size - 6000))
            stdout = stdout_file.read().decode("utf-8", errors="replace")
            stderr = stderr_file.read().decode("utf-8", errors="replace")
        return {"ok": result.returncode == 0, "return_code": result.returncode,
                "stdout": _redact(stdout), "stderr": _redact(stderr),
                "cwd": str(cwd.relative_to(ROOT)), "command": argv, "timeout_seconds": timeout,
                "isolated": False}
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "error": "timeout", "timeout_seconds": exc.timeout, "isolated": False}
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": type(exc).__name__, "isolated": False}
