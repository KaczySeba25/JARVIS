# Security status

Jarvis has no embedded domain-specific execution client. Future risky integrations must be researched, sandboxed and gated by Jarvis.

The local `agent/.env` file contains provider credentials and must never be shared or committed. The readiness audit checks that local configuration exists but never prints its values. Rotate credentials whenever they are exposed.

Use `agent/.env.example` as the configuration template.
