# magicpin AI Challenge — Build a Merchant AI Assistant ("Vera")

**Status**: Brief — designed to be loaded as standalone context in a fresh AI session.
**Last updated**: 2026-04-26
**Audience**: Challenge participants + the AI judge that will evaluate submissions.

---

## 1. The challenge in one sentence

> Build an AI chatbot that engages and assists merchants on WhatsApp the way **Vera** (magicpin's merchant-AI assistant) does — but better. Same base dataset for every participant. AI judges the outcome.

---

## 2. About magicpin

magicpin is one of India's largest local-commerce platforms — a network of ~100,000 merchant partners across 50+ Indian cities. Customers discover merchants, transact, and earn cashback. Merchants benefit from visibility, walk-ins, and online orders.

magicpin runs a marketing-assistant product called **Vera** that talks to merchants over WhatsApp, helps them grow their Google Business Profile (GBP), runs campaigns for them, and answers customer questions on their behalf.

---

## 3. The 4-context framework

Every message Vera sends is composed from **four context layers**:

```
your_bot.compose(category, merchant, trigger, customer?) -> message
```

1. **CategoryContext**: Slow-changing vertical knowledge (slug, offer_catalog, voice, peer_stats, digest, seasonal_beats).
2. **MerchantContext**: Specific business's current state (identity, performance, offers, conversation_history, customer_aggregate, signals).
3. **TriggerContext**: The event prompting the outreach (id, scope, kind, source, payload, urgency, suppression_key).
4. **CustomerContext** (optional): Populated when sending on-behalf-of merchant to their patient/customer (identity, relationship, state, preferences, consent).

---

## 4. Submission Deliverables (§7)

1. `bot.py` (`compose(category, merchant, trigger, customer | None) -> dict`)
2. `submission.jsonl` (30 lines, one per canonical test pair)
3. `README.md` (1 page max explaining approach, model choice, tradeoffs)
4. Optional: `conversation_handlers.py` (`respond(state, merchant_message)`)
5. Public bot URL responding to `/v1/*`
