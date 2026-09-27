"""
magicpin AI Challenge — Vera Bot Submission Module
Conforms to §7.1 of challenge-brief.md.

Implements:
    compose(category, merchant, trigger, customer) -> dict
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to sys.path so app modules are importable
sys.path.insert(0, str(Path(__file__).parent))

from app.templates import compose_grounded_message


def compose(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Composes a grounded outbound WhatsApp message.

    Inputs are the dicts loaded from the dataset JSON:
        - category: CategoryContext dict
        - merchant: MerchantContext dict
        - trigger: TriggerContext dict
        - customer: Optional CustomerContext dict

    Returns a dict with keys:
        - body: the WhatsApp message text
        - cta: call-to-action type ("binary", "open_ended", "multi_choice_slot", "none")
        - send_as: "vera" (merchant-facing) or "merchant_on_behalf" (customer-facing)
        - suppression_key: deduplication key
        - rationale: brief explanation of why this message was composed
    """
    body, cta, suppression_key, rationale, _ = compose_grounded_message(
        category=category,
        merchant=merchant,
        trigger=trigger,
        customer=customer
    )

    send_as = "merchant_on_behalf" if customer is not None else "vera"

    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": suppression_key,
        "rationale": rationale
    }


if __name__ == "__main__":
    import json

    print("Vera Bot compose() module loaded successfully.")
    sample_cat = {"slug": "dentists", "voice": {"tone": "peer_clinical", "vocab_taboo": ["cure"]}}
    sample_mx = {"identity": {"name": "Dr. Meera", "locality": "Lajpat Nagar"}}
    sample_trg = {"id": "trg_sample", "kind": "cde_opportunity", "payload": {"credits": 2}}

    msg = compose(sample_cat, sample_mx, sample_trg, None)
    print(json.dumps(msg, indent=2))
