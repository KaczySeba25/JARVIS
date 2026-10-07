"""Runs a compact integration diagnostic over the Jarvis runtime layers."""
import importlib.util
from pathlib import Path
def run(argument=None):
    root=Path(__file__).resolve().parent.parent; checks={"core":importlib.util.find_spec("jarvis_core") is not None,"state_dir":(root/"memory").is_dir(),"skills_dir":(root/"skills").is_dir(),"tests":(root/"tests"/"run_tests.py").exists()}
    return {"checks":checks,"passed":sum(checks.values()),"total":len(checks),"ready":all(checks.values())}
