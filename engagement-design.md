# Vera Engagement Framework — Design

**Status**: Architectural design for Vera's proactive engagement framework.
**Last updated**: 2026-04-26

---

## 4-Context Framework

Every message Vera sends is composed from 4 context layers:
- `CategoryContext` (slow-changing vertical knowledge)
- `MerchantContext` (fast-changing merchant state and performance)
- `TriggerContext` (event prompting this outreach)
- `CustomerContext` (optional customer/patient state for on-behalf-of-merchant outreach)

### Loops enabled by this architecture:
- Research digest release (`research_digest_release`)
- Performance monitor (`perf_spike`, `perf_dip`, `milestone_reached`)
- Review-pattern detector (`review_theme_emerged`)
- Recall scheduler (`recall_due`)
- Lapse detector (`customer_lapsed_soft`, `customer_lapsed_hard`)
- Appointment reminder (`appointment_tomorrow`)
