# Jarvis project review — 2026-10-02

## Direction

Jarvis is a general assistant for work on Sebastian's computer and online. It has no fixed business domain and does not control the smart home. Earlier projects are examples of work Jarvis should eventually be capable of handling, not hard-coded goals. See [JARVIS_VISION.md](JARVIS_VISION.md) and [USER_PROJECT_CONTEXT.md](USER_PROJECT_CONTEXT.md).

## Foundations added

- Persistent task records, progress events and approval plans in the local SQLite database.
- Explicit plan approval/resume, rejection, expiry, a post-login handoff and a visible task timeline.
- Local memory review/edit/delete actions and expanded credential redaction.
- Skill version metadata with research links, check date and known limitations.
- Project-file creation and recovery confined to `workspace/`.
- Bounded Python/Git commands with no shell, plus a visible-process runner for approved demos.
- Password-free manual sign-in handoff; old bulk placeholder skill generation disabled.

## Current limits

- Many existing skills remain helpers or stubs; their names do not mean expert-level behavior.
- Plan approval scopes list permitted skills and readable boundaries, but do not yet enforce recipient-level, amount-level or field-level restrictions.
- Generated Python is not isolated in a Windows OS sandbox. User approval gates its execution; it is not a security sandbox.
- No general service connection, outbound email, online publishing, or external-action connector is configured. A browser sign-in alone does not connect a service.
- Task evidence records tool output, but external publication still needs service receipts or independent browser verification.
- Memory search is local lexical matching, not robust semantic understanding.

## Verification

Python syntax compilation succeeded for the changed files. The automated test suite was not run after these changes. No live accounts, email services, stores, or trading endpoints were connected.
