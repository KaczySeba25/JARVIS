# ADR-001: Local-first core and supervised execution

**Status:** Accepted
**Date:** 2026-09-28

## Context

Jarvis ma działać bez kosztów, wykonywać zadania przez skille i zachować kontrolę użytkownika nad czynnościami ryzykownymi.

## Decision

Rdzeń pozostaje local-first: pamięć jest przechowywana lokalnie, a dostawca modelu jest wymienny. Jarvis nie zakłada z góry domeny przyszłych zadań; najpierw bada wymagania i źródła.

## Consequences

- Możemy rozwijać i testować bez płatnych usług.
- Ryzykowne działania są izolowane i wymagają jawnych bramek.
- Domenowe decyzje są wynikiem researchu Jarvisa, nie wiedzy zaszytej w rdzeniu.
