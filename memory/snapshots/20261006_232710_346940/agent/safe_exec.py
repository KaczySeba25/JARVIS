"""Bounded execution helpers for skills and external processes."""
import subprocess
import sys

def python_file(path: str, timeout=10):
    return subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout)
