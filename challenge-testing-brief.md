# magicpin AI Challenge — Testing & Evaluation Brief

**Status**: Companion to `challenge-brief.md`. Defines the technical contract between candidate bots and magicpin's judging system.
**Last updated**: 2026-04-26
**Audience**: Candidates building the bot + magicpin engineers running the harness.

---

## 1. Endpoints

1. `POST /v1/context` — Ingest 4 contexts (`category`, `merchant`, `customer`, `trigger`). Idempotent by `(context_id, version)`. Returns 200 on success, 409 on stale version conflict.
2. `POST /v1/tick` — Periodic wake-up with `available_triggers`. Bot inspects context state and returns proactive `actions[]`.
3. `POST /v1/reply` — Handles merchant or customer reply. Returns `action`: `"send"`, `"wait"`, or `"end"`.
4. `GET /v1/healthz` — Liveness probe with uptime and `contexts_loaded` counts.
5. `GET /v1/metadata` — Team and architecture metadata.
6. `POST /v1/teardown` — Optional teardown to wipe state.

---

## 2. Replay Tests (Top 10 Scenarios)

1. **Auto-reply hell**: Detects canned / repeated merchant greetings and backs off (`action: wait`) or terminates (`action: end`).
2. **Intent transition**: Detects explicit commitment ("Ok lets do it", "proceed") and switches immediately to ACTION mode. Must NOT ask further qualifying questions.
3. **Hostile / opt-out**: Detects opt-out or hostility ("Stop messaging me") and gracefully exits immediately.
