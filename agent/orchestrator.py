"""State machine preventing loops, silent failure and uncontrolled autonomy."""
from dataclasses import dataclass, field
from enum import Enum
import time

class State(str, Enum):
    IDLE="idle"; PLANNING="planning"; RESEARCHING="researching"; WAITING_APPROVAL="waiting_approval"; WAITING_USER="waiting_user"; EXECUTING="executing"; VERIFYING="verifying"; NEEDS_REVIEW="needs_review"; BLOCKED="blocked"; DONE="done"

@dataclass
class Orchestration:
    goal: str
    state: State = State.IDLE
    steps: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 3
    started: float = field(default_factory=time.time)

    def transition(self, state: State):
        if self.state == State.DONE and state != State.IDLE: raise RuntimeError("Zadanie już zakończone.")
        self.state = state

    def retry_allowed(self):
        self.attempts += 1
        if self.attempts > self.max_attempts:
            self.state = State.BLOCKED
            return False
        return True

    def finish(self, step: str):
        if step not in self.completed: self.completed.append(step)
        if self.steps and set(self.steps) <= set(self.completed): self.state = State.DONE
