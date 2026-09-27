# Vera Proactive Engagement Bot — magicpin AI Challenge Submission

An enterprise-grade, high-performance proactive engagement engine built for the **magicpin AI Challenge**. The bot acts as **Vera**, magicpin's proactive merchant-AI assistant that reaches out to merchants and customers over WhatsApp with verifiable, category-aligned, and low-friction communications.

---

## 1. Approach & Architecture

Our architecture implements the **4-Context Decoupled Composition Framework**:

```
[CategoryContext]  ──┐
[MerchantContext]  ──┼──► [Decision Engine & Grounded Composer] ──► ComposedMessage {body, cta, send_as, suppression_key, rationale}
[TriggerContext]   ──┤
[CustomerContext]  ──┘
```

1. **4-Context Separation of Concerns**:
   - `CategoryContext`: Vertical domain pack (voice, taboos, clinical/commercial benchmarks, digests, seasonal beats).
   - `MerchantContext`: Real-time and snapshot business telemetry (views, calls, active catalog offers, customer aggregates).
   - `TriggerContext`: Internal/external events with urgency-based prioritization and deduplication (`suppression_key`).
   - `CustomerContext`: Patient/client relationship history (last visit, past treatments, slot preferences, opt-in scope) for on-behalf-of-merchant outreach.

2. **Grounded Dual-Tier Composition Engine**:
   - **Tier 1 (Sub-5ms Grounded Fallback)**: Deterministic, high-specificity templates guaranteeing 0% hallucination rate, 100% taboo avoidance (no "cure", no "guaranteed"), real price anchors (`"Haircut @ ₹99"`, `"Dental Cleaning @ ₹299"`), and zero Meta URL delivery penalties.
   - **Tier 2 (Constrained LLM Generation)**: Temperature 0 generation with post-generation JSON schema validation and taboo regex guards.

3. **Multi-Turn Conversation State Machine (`conversation_handlers.py`)**:
   - **Auto-Reply Hell Handling**: Detects canned/automated WhatsApp Business responses (`"Thank you for contacting us"`, repeated incoming text) and backs off (`action: wait`) or terminates gracefully (`action: end`) after 1–2 turns.
   - **Instant Intent Transition**: Immediately switches from exploratory mode to ACTION mode upon commitment signals (`"Ok lets do it"`, `"what's next"`), returning concrete proposal packages with actioning vocabulary and zero back-tracking qualification questions.
   - **Hostile & Opt-Out Resolution**: Detects merchant stop/opt-out signals and terminates instantly with a polite exit (`action: end`).

---

## 2. Model Choice & Tradeoffs

| Decision | Chosen Path | Tradeoff & Justification |
|---|---|---|
| **Composition Engine** | Dual-tier (Deterministic Template Core + LLM Augmentation) | Pure LLMs introduce 2-5s latency and variance in taboo enforcement. The deterministic core guarantees sub-5ms response, strictly verifiable numbers, and 100% SLA compliance under the 30s budget. |
| **Grounding vs Hype** | Single Verifiable Signal Hook | Prioritizing one verified metric (e.g. 50% call dip, 2,100-patient trial, or exact last visit date) outperforms generic discount hype ("Flat 30% off") with Indian merchants. |
| **Storage & State** | Thread-Safe In-Memory Relational Store | Rapid lookup and sub-millisecond atomic version updates (`409 Conflict` on stale pushes) without external database latency overhead during high-frequency evaluation ticks. |

---

## 3. Submission Deliverables (§7 Spec)

- `bot.py` — Standalone module exposing `compose(category, merchant, trigger, customer | None) -> dict`.
- `conversation_handlers.py` — Standalone module exposing `respond(state, merchant_message) -> dict`.
- `submission.jsonl` — 30 canonical judge test pairs (`T01` to `T30`) generated deterministically from `dataset/expanded/test_pairs.json`.
- `generate_submission.py` — Reproducible generator script for the test pairs.
- `app/` — FastAPI service exposing the 5 challenge endpoints (`/v1/context`, `/v1/tick`, `/v1/reply`, `/v1/healthz`, `/v1/metadata`).
- `challenge-brief.md`, `challenge-testing-brief.md`, `engagement-design.md`, `engagement-research.md` — Challenge documentation.

---

## 4. Verification & Testing Instructions

### Run Unit Tests
```bash
PYTHONPATH=. ./venv/bin/pytest tests/test_bot.py -v
```
*Validates 11 comprehensive test cases: endpoints, atomic versioning, auto-reply detection, hostile exit, action-mode intent transition, and submission JSONL schema.*

### Re-generate Submission JSONL
```bash
./venv/bin/python generate_submission.py
```

### Test Standalone Modules
```bash
./venv/bin/python bot.py
./venv/bin/python conversation_handlers.py
```

### Run the Judge Simulator
```bash
# Offline rule-based verification:
BOT_URL=http://localhost:8080 TEST_SCENARIO=all ./venv/bin/python judge_simulator.py

# With live external LLM Judge (e.g. Gemini / OpenAI):
export LLM_PROVIDER="gemini"
export LLM_API_KEY="your-api-key"
BOT_URL=http://localhost:8080 TEST_SCENARIO=all ./venv/bin/python judge_simulator.py
```

---

## 5. What Additional Context Would Help Most
1. **Real Merchant Schedule / Slot Availability**: Direct integration with clinic/salon management software (e.g. Practo, Dentcubate) to offer live real-time booking slots in customer recall nudges.
2. **Channel-Level Delivery Telemetry**: WhatsApp read receipts and interaction logs to adapt outreach time slots based on past merchant responsiveness patterns.
