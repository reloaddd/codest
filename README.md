# Codest

Codest is a competitive programming judge — the engine behind something like Codeforces or LeetCode, built from scratch to understand backend systems end to end rather than to clone a product.

The premise behind the project: most backend tutorials teach concepts in isolation — a CRUD app here, an auth example there, a Redis caching demo somewhere else — and you never feel what it's like to maintain one system as it grows in complexity. Codest is the opposite bet. It's one system, built in phases, where each phase forces a different hard problem that a toy CRUD app never would: running code you don't trust, handling a flood of submissions at the exact same second, keeping a leaderboard live without hammering the database, and proving who submitted first when timing actually matters.

## What it does

A user picks a problem, writes a solution in their browser, and submits it. Codest compiles/runs that code against a set of test cases inside an isolated sandbox, judges it correct or not, and reports back — live, over a WebSocket connection, not by the user refreshing a page. Across a contest, submissions feed a leaderboard ranked by correctness and speed, the same shape real competitive programming platforms use.

## Why this domain, specifically

A judge isn't just "another CRUD app with extra steps." Six pressures fall out of the domain naturally, and each one maps to a real backend discipline:

- **Untrusted code execution** — the system has to run arbitrary, potentially hostile user code without that code touching the host machine, the network, or other people's submissions. This is the centerpiece of the whole project: container isolation, resource limits, and security-first design, not just "call subprocess.run()."
- **A contended resource under load** — many users submitting in the same instant, especially near a contest deadline, surfaces real concurrency problems: race conditions, locking, and idempotency, not just "the database is slow."
- **Work that can't block the request** — running code takes real time; the API can't sit there waiting. This is what makes a job queue a structural requirement of the system, not an optimization bolted on later.
- **A frequently-read, infrequently-changed view** — the leaderboard and problem statements are read constantly and written rarely, the textbook case for caching done properly, including the cache-invalidation bugs that come with it.
- **A reason to search well** — filtering problems by tag, difficulty, and solved status is a genuine (if modest) search problem, not paperwork.
- **State someone is actively watching** — a submission's status changes over several seconds while a real person stares at the screen waiting for it. That's what makes WebSocket a real requirement here, not a tech-demo feature.

## Architecture

```
                        ┌─────────────────────┐
                        │   Client (browser)    │
                        └──────────┬───────────┘
                                   │ REST + WebSocket
                                   ▼
                        ┌─────────────────────┐
                        │     API layer        │
                        │  Auth · REST routes   │
                        │  WebSocket gateway     │
                        └──────────┬───────────┘
                   ┌───────────────┼───────────────┐
                   ▼               ▼               ▼
          ┌───────────────┐ ┌──────────────┐ ┌───────────────┐
          │   Data layer    │ │  Async layer  │ │ Integrations   │
          │ Postgres · Redis│ │ Job queue +    │ │ Container       │
          │ search index    │ │ background     │ │ runtime, email   │
          │                 │ │ workers         │ │ (where relevant) │
          └───────────────┘ └──────┬───────┘ └───────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │  Sandboxed execution  │
                        │  One throwaway,        │
                        │  resource-limited       │
                        │  container per           │
                        │  submission               │
                        └─────────────────────┘
```

A submission's actual journey through the system:

1. **Submit** — the client sends code to the API layer, which validates and writes a row to Postgres with status `pending` and a server-stamped timestamp (the database itself generates this timestamp at the instant the row commits — not the client, and not application code — so it can't be spoofed by a fast or slow network).
2. **Queue** — the API responds immediately and hands the job to a queue. The request never blocks waiting for code to run.
3. **Judge** — a worker pulls the job, spins up an isolated, resource-limited container with no network access, runs the submitted code against each test case, and tears the container down immediately after. Nothing about this step trusts the submitted code.
4. **Report live** — as each test case resolves, the worker pushes a status update over a pub/sub channel; any open WebSocket connection watching that submission receives it instantly, no polling involved.
5. **Rank** — on acceptance, the leaderboard updates via a Redis sorted set, ordered by correctness and submission time, kept in sync with the source of truth in Postgres rather than replacing it.

## Design principles behind the system

**Server-authoritative facts, not client-reported ones.** Submission timestamps, judging verdicts, and leaderboard positions are all things the system computes itself, never values a client hands it. This matters most in contest mode: a tiebreak by submission time only means something if a contestant has no way to influence what that time says.

**Postgres is the source of truth; everything else is a derived view.** Redis holds the leaderboard and cached reads, but if it vanished entirely, Codest could rebuild it from Postgres. Nothing important is allowed to live only in a cache.

**Isolation is layered, not assumed.** No internet access, hard memory/CPU/process limits, a non-root user, a read-only filesystem, and a forced timeout all apply to every execution — the system treats every submission as hostile by default rather than trusting it until proven otherwise.

**Decoupling over convenience.** The API that accepts a submission and the worker that judges it are different processes that never block on each other. This is what makes the live-status experience and the horizontal scaling story both possible later — a slow or stuck judge never takes the API down with it.

**Built to also run fully offline.** Beyond the cloud-hosted version, Codest's contest mode is designed to run on an isolated local network with no internet access at all — the same model real onsite competitive programming contests (ICPC-style) use. A venue's network simply has no route to the outside world; every device on it can still reach the judge server directly. Submission timestamps are still stamped by the judge server's own clock the instant a request lands, so the offline mode keeps the same tamper-proof guarantee as the hosted one — nothing about contest fairness depends on the internet being reachable at all.

## What this project is, and isn't

Codest isn't trying to be a production-ready competitor to existing judges — it's a deliberately full-scope build meant to exercise nearly every core discipline in backend engineering inside one coherent system: relational modeling, authentication, concurrency, queuing, caching, real-time communication, search, containerized security, observability, and deployment. The goal is a system whose every component has a real reason to exist, where "why did you build it this way" always has an actual answer.