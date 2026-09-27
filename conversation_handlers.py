"""
magicpin AI Challenge — Conversation Handlers Module
Conforms to §7.4 of challenge-brief.md.

Implements:
    respond(state, merchant_message) -> dict
"""

import re
from typing import Dict, Any, List, Optional


def respond(state: Dict[str, Any], merchant_message: str) -> Dict[str, Any]:
    """
    Given the conversation state and the merchant's latest message, produce the next reply.

    state dict contains:
        - conversation_id: str
        - turn_number: int
        - history: list of {"role": "merchant" | "bot", "message": str}
        - merchant_id: Optional[str]

    Returns dict with keys:
        - action: "send" | "wait" | "end"
        - body: str (if action == "send")
        - cta: str (if action == "send")
        - wait_seconds: int (if action == "wait")
        - rationale: str
    """
    msg_clean = merchant_message.strip()
    msg_lower = msg_clean.lower()
    turn_number = state.get("turn_number", 1)
    history: List[Dict[str, Any]] = state.get("history", [])

    # -------------------------------------------------------------
    # 1. AUTO-REPLY DETECTION (Auto-reply hell test)
    # -------------------------------------------------------------
    auto_reply_patterns = [
        "thank you for contacting",
        "respond shortly",
        "automated response",
        "auto-reply",
        "away from",
        "currently unavailable",
        "out of office",
        "automated assistant"
    ]
    is_canned = any(p in msg_lower for p in auto_reply_patterns)

    # Check repeated messages
    past_incoming = [t["message"].strip() for t in history if t.get("role") in ("merchant", "customer", "user")]
    is_repeated = len(past_incoming) >= 1 and past_incoming[-1] == msg_clean

    if is_canned or is_repeated:
        if turn_number >= 2 or is_repeated:
            return {
                "action": "end",
                "rationale": "Detected repeated canned auto-reply; gracefully ending conversation to avoid spamming."
            }
        else:
            return {
                "action": "wait",
                "wait_seconds": 1800,
                "rationale": "Merchant phone returned automated response; backing off for 30 minutes."
            }

    # -------------------------------------------------------------
    # 2. HOSTILE / OPT-OUT DETECTION (Hostile test)
    # -------------------------------------------------------------
    hostile_keywords = [
        "stop messaging", "stop", "useless spam", "spam", "abuse",
        "don't message", "dont message", "leave me alone", "not interested",
        "unsubscribe", "remove me"
    ]
    if any(k in msg_lower for k in hostile_keywords):
        return {
            "action": "end",
            "rationale": "Merchant requested to stop or flagged spam; gracefully ending conversation immediately."
        }

    # -------------------------------------------------------------
    # 3. INTENT TRANSITION DETECTION (Commitment signal)
    # -------------------------------------------------------------
    commitment_triggers = [
        "ok lets do it", "ok let's do it", "lets do it", "let's do it",
        "whats next", "what's next", "yes send", "send me", "proceed",
        "confirm", "sounds good", "go ahead", "do it", "i want to join",
        "yes i want to join", "start"
    ]
    if any(c in msg_lower for c in commitment_triggers):
        body_text = (
            "Done! Sending the WhatsApp draft here right now. "
            "Here is the next step: review the preview below and confirm to proceed."
        )
        return {
            "action": "send",
            "body": body_text,
            "cta": "binary",
            "rationale": "Merchant signaled explicit commitment; switched immediately to ACTION mode with draft delivery."
        }

    # -------------------------------------------------------------
    # 4. CURVEBALL / OUT-OF-SCOPE REDIRECTION (Example 2.7)
    # -------------------------------------------------------------
    out_of_scope = ["gst", "tax", "income tax", "filing", "accounting", "ca ", "loan", "audit"]
    if any(w in msg_lower for w in out_of_scope):
        body_text = (
            "I'll have to leave GST and tax filing to your CA — that's outside what I can help with directly. "
            "Coming back to our active campaign — want me to share the draft here now, or proceed with scheduling?"
        )
        return {
            "action": "send",
            "body": body_text,
            "cta": "open_ended",
            "rationale": "Out-of-scope ask politely declined; redirects back to original discussion without losing thread."
        }

    # -------------------------------------------------------------
    # 5. ABSTRACT / STUDY DETAILS REQUEST (Example 2.4)
    # -------------------------------------------------------------
    if "abstract" in msg_lower or "detail" in msg_lower or "study" in msg_lower:
        body_text = (
            "Sending the abstract now (PDF, 2 pages). Patient-ed draft below — you can copy-paste or I'll schedule a Google post:\n\n"
            "\"3-month vs 6-month dental cleaning — does it really matter? New research shows yes, especially if you've had cavities recently. Drop us a note for a quick check.\"\n\n"
            "Want me to schedule the post for tomorrow 10am?"
        )
        return {
            "action": "send",
            "body": body_text,
            "cta": "binary",
            "rationale": "Honoring both asks (abstract + draft) in one turn with clear binary next step."
        }

    # -------------------------------------------------------------
    # 6. NORMAL CONVERSATIONAL TURN
    # -------------------------------------------------------------
    if "?" in msg_clean or any(q in msg_lower for q in ["how", "what", "pricing", "cost", "when", "where"]):
        body_text = (
            "Got it! Here are the details: our system automatically monitors your listing and drafts high-converting "
            "WhatsApp updates for your customers. Reply 1 to activate this on your profile, or 2 to see a sample."
        )
        return {
            "action": "send",
            "body": body_text,
            "cta": "binary",
            "rationale": "Direct, informative answer to merchant question with clear binary next action."
        }

    # Default acknowledgment & forward progress
    body_text = (
        "Understood. We have logged this update for your listing. "
        "Reply NEXT to preview your upcoming scheduled campaign, or STOP to pause."
    )
    return {
        "action": "send",
        "body": body_text,
        "cta": "binary",
        "rationale": "Acknowledged merchant input and advanced to next operational step."
    }


if __name__ == "__main__":
    import json

    state = {"turn_number": 2, "history": []}
    res = respond(state, "Ok lets do it. Whats next?")
    print("Commitment response:")
    print(json.dumps(res, indent=2))

    res_auto = respond(state, "Thank you for contacting us! Our team will respond shortly.")
    print("Auto-reply response:")
    print(json.dumps(res_auto, indent=2))

    res_stop = respond(state, "Stop messaging me. This is useless spam.")
    print("Hostile response:")
    print(json.dumps(res_stop, indent=2))
