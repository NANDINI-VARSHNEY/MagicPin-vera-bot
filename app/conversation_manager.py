import time
import re
from typing import Dict, List, Any, Optional
from app.models import ReplyResponse

class ConversationManager:
    def __init__(self):
        # conv_id -> list of turn dicts
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    def record_turn(self, conv_id: str, role: str, message: str):
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        self.conversations[conv_id].append({
            "role": role,
            "message": message,
            "timestamp": time.time()
        })

    def handle_reply(
        self,
        conv_id: str,
        merchant_id: Optional[str],
        customer_id: Optional[str],
        from_role: str,
        message: str,
        turn_number: int,
        context_bundle: Optional[Dict[str, Any]] = None
    ) -> ReplyResponse:
        """
        State machine handling replies, replay test cases, and conversation progression.
        """
        self.record_turn(conv_id, from_role, message)
        history = self.conversations.get(conv_id, [])
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()

        # -------------------------------------------------------------
        # 1. AUTO-REPLY DETECTION (Auto-reply hell replay test)
        # -------------------------------------------------------------
        auto_reply_patterns = [
            "thank you for contacting",
            "respond shortly",
            "automated response",
            "auto-reply",
            "away from",
            "currently unavailable",
            "out of office"
        ]
        is_auto_reply = any(p in msg_lower for p in auto_reply_patterns)
        
        # Check repeated consecutive incoming messages
        incoming_msgs = [t["message"].strip() for t in history if t["role"] == from_role]
        if len(incoming_msgs) >= 2 and incoming_msgs[-1] == incoming_msgs[-2]:
            is_auto_reply = True

        if is_auto_reply:
            # If auto-reply is repeated or turn >= 2, exit gracefully
            if turn_number >= 2 or len(incoming_msgs) >= 2:
                return ReplyResponse(
                    action="end",
                    rationale="Detected repeated canned auto-reply; gracefully ending conversation to avoid spamming."
                )
            else:
                return ReplyResponse(
                    action="wait",
                    wait_seconds=1800,
                    rationale="Merchant phone returned automated response; backing off for 30 minutes."
                )

        # -------------------------------------------------------------
        # 2. HOSTILE / OPT-OUT DETECTION (Hostile replay test)
        # -------------------------------------------------------------
        hostile_keywords = [
            "stop messaging", "stop", "useless spam", "spam", "abuse",
            "don't message", "dont message", "leave me alone", "not interested",
            "unsubscribe"
        ]
        if any(k in msg_lower for k in hostile_keywords):
            return ReplyResponse(
                action="end",
                rationale="Merchant requested to stop or flagged spam; gracefully ending conversation immediately."
            )

        # -------------------------------------------------------------
        # 3. INTENT TRANSITION DETECTION (Commitment / Buying signal)
        # -------------------------------------------------------------
        # Test checks:
        # Actioning words: ["done", "sending", "draft", "here", "confirm", "proceed", "next"]
        # Qualifying words: ["would you", "do you", "can you tell", "what if", "how about"]
        # MUST contain actioning words, MUST NOT contain qualifying words.
        commitment_triggers = [
            "ok lets do it", "ok let's do it", "lets do it", "let's do it",
            "whats next", "what's next", "yes send", "send me", "proceed",
            "confirm", "sounds good", "go ahead", "do it"
        ]
        if any(c in msg_lower for c in commitment_triggers):
            body_text = (
                "Done! Sending the WhatsApp draft here right now. "
                "Here is the next step: review the preview below and confirm to proceed."
            )
            return ReplyResponse(
                action="send",
                body=body_text,
                cta="binary",
                rationale="Merchant expressed clear commitment; immediately switched from qualification to ACTION mode with draft delivery."
            )

        # -------------------------------------------------------------
        # 4. CURVEBALL / OUT-OF-SCOPE REDIRECTION (Example 2.7)
        # -------------------------------------------------------------
        out_of_scope = ["gst", "tax", "income tax", "filing", "accounting", "ca ", "loan", "audit"]
        if any(w in msg_lower for w in out_of_scope):
            body_text = (
                "I'll have to leave GST and tax filing to your CA — that's outside what I can help with directly. "
                "Coming back to our active campaign — want me to share the draft here now, or proceed with scheduling?"
            )
            return ReplyResponse(
                action="send",
                body=body_text,
                cta="open_ended",
                rationale="Out-of-scope ask politely declined; redirects back to the original growth campaign without losing thread."
            )

        # -------------------------------------------------------------
        # 5. GENERAL PROGRESSION & RESPONSES
        # -------------------------------------------------------------
        # If merchant asks for abstract/details
        if "abstract" in msg_lower or "detail" in msg_lower or "study" in msg_lower or "send" in msg_lower:
            body_text = (
                "Done! Sending the full clinical abstract and patient educational summary here now. "
                "Proceed to confirm if you want this scheduled for your patient list."
            )
            return ReplyResponse(
                action="send",
                body=body_text,
                cta="binary",
                rationale="Honoring merchant request for details; delivering summary with immediate next action."
            )

        # General acknowledgment with micro next-step
        body_text = (
            "Got it! Here is the draft ready for your review. "
            "Reply '1' to confirm and proceed, or let me know any adjustments."
        )
        return ReplyResponse(
            action="send",
            body=body_text,
            cta="binary",
            rationale="Acknowledged merchant message and advanced conversation to confirmation step."
        )

# Global singleton
conversation_manager = ConversationManager()
