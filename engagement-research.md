# Vera Engagement Framework — Research: Current Merchant Data Access

**Status**: Research notes on production Vera data access paths.
**Last updated**: 2026-04-26

---

## Existing vs New Components

1. **CategoryContext**: Net new knowledge pack containing voice profile, taboos, peer stats, and digest.
2. **MerchantContext**: Aggregates merchant snapshot, identity, performance snapshots, offers, and customer aggregates.
3. **TriggerContext**: Normalized event primitive across internal and external signals.
4. **CustomerContext**: Rich CRM relationship, visit dates, past services, preferred slots, and consent scope.
5. **EngagementComposer**: Grounded LLM composer with deterministic fallback ensuring 0% hallucination and 100% SLA compliance.
