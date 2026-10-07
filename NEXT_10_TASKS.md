# Next 10 Jarvis improvement tasks

1. **Structured model output**: replace regex ACTION parsing with validated JSON plans and tool schemas.
2. **Evidence reconciliation**: compare multiple sources, detect conflicts and expire stale knowledge.
3. **Regression benchmark**: maintain a fixed suite of Polish tasks with quality scores and failure history.
4. **Skill contracts**: require metadata, input validation, risk declaration, timeout and deterministic smoke tests for every skill.
5. **Learning curriculum**: turn previous failures into repeatable exercises before promoting a new skill.
6. **Model routing**: route simple tasks to a local/smaller model and complex planning to the configured provider.
7. **Context management**: summarize old conversations and retrieve only relevant memories instead of using a fixed tail.
8. **Observability**: add latency, token, retry, tool success and confidence metrics with periodic reports.
9. **Recovery drills**: test provider outage, malformed data, corrupted state, interrupted tasks and rollback.
10. **Specialized-agent evaluation**: validate any newly built specialist against realistic data, failure cases and measurable success criteria before presenting it as ready.
