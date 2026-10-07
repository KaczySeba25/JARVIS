"""Detect repeated actions and stop runaway agent loops."""
from collections import deque
import hashlib

class LoopGuard:
    def __init__(self, window=8): self.events = deque(maxlen=window)
    def allow(self, action: str) -> bool:
        key = hashlib.sha256(action.encode()).hexdigest()
        if self.events.count(key) >= 3: return False
        self.events.append(key)
        return True
