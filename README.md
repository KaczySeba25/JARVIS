# Jarvis

Jarvis is a local-first personal assistant for work on your computer and with online services. It is not a smart-home controller and is not tied to a particular shop or business.

## Start

1. Run `Start_Jarvis.bat` to open the desktop window.
2. For a hosted model, add a provider key to `agent/.env`. For local use, start Ollama and install a model yourself; Jarvis will use an already-installed model and will not download one or create a paid account.
3. To use the text interface, run `agent/venv/Scripts/python.exe agent/agent.py` from this folder.

Copy `agent/.env.example` to `agent/.env` for the optional settings. Keep real keys only in the local `.env` or the protected vault.

## Current foundations

- Bounded multi-step tool use with explicit results returned to the model.
- Local conversation history and searchable long-term memory.
- Web research that saves source links and refuses to claim success when it cannot fetch sources.
- Draft, check, backup and rollback flow for Jarvis-created skills.
- Emergency stop and persistent error records.
- Persistent plans that wait for approval before their listed side-effecting tools run.
- Local memory controls, task history and a visible progress/evidence panel.
- A workspace-only project writer, bounded no-shell project checks, and a visible demo runner.
- A manual sign-in handoff that never asks for the user's password in chat.

The skill list includes both working tools and early-stage helpers. A skill's presence in the folder does not by itself mean the whole capability is finished. Start new work with [the current project status](PROJECT_STATUS_CURRENT.md), then see [the agreed Jarvis vision](JARVIS_VISION.md) and [the roadmap](ROADMAP.md). Historical source documents are kept in `reference/historical_user_documents/` and are not standing instructions.

See [implementation status and current limits](IMPLEMENTED_FEATURES.md) before treating any workflow as production-ready.

## Boundaries

- No smart-home, lighting, blind, lock or other home-device control.
- No external financial actions are enabled by default.
- Web pages and downloaded files are untrusted input, not instructions.
- Jarvis should report the work it actually completed and identify unverified results.
