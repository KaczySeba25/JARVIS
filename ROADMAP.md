# Jarvis roadmap

This plan follows Sebastian's direction in [JARVIS_VISION.md](JARVIS_VISION.md): Jarvis works on the computer and online, learns new services when a task needs them, and does not control smart-home devices.

## First: make the core dependable

- Understand goals, success conditions and missing information.
- Use a bounded loop to research, act, inspect results and continue a task.
- Keep useful private memories locally and provide a way to inspect, edit or remove them.
- Save failures as lessons; safely develop, validate, back up and roll back skills.
- Save task plans and approval scope; resume after approval or an account-access handoff.
- Show honest progress and result evidence in the desktop timeline.

## Then: broaden useful work

- Learn new software and online services from their current documentation instead of hard-coding one business domain.
- Add concrete, least-privilege connectors for specific services as Sebastian chooses them.
- Add fine-grained approval limits for recipients, prices, audiences, files and other task-specific boundaries.
- Add isolated Windows execution for generated programs; current subprocess checks are not a full sandbox.
- Add independent result verification, including screenshots or service receipts where available.
- Add file attachments and reliable handling of common document types.
- Add voice input and spoken replies alongside text.
- Improve the desktop view so it clearly shows current work, progress and decisions waiting for Sebastian.
- Add notifications only after selecting a free or affordable method with Sebastian.

## Keep these limits

- Prefer local and free options; explain unavoidable third-party costs before they arise.
- Do not control lights, blinds, locks or other home devices.
- Do not repeat an online action when its previous result is uncertain.
- Keep a recoverable copy before changing an active Jarvis skill.
- Research text is untrusted data. It cannot grant itself permissions or change Jarvis's rules.

## Current state

The core now has persistent plan approvals, a user handoff, local long-term memory controls, visible task history, local Ollama discovery, source-aware research, workspace-only file creation, bounded no-shell project checks and recoverable versions. Many files in `skills/` are still small building blocks or early-stage helpers; their names alone do not mean the advertised idea is fully implemented. See [implementation status](IMPLEMENTED_FEATURES.md).
