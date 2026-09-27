import json
import re
import httpx
from typing import Dict, Any, Tuple, Optional
from app.config import settings
from app.templates import compose_grounded_message

class Composer:
    def __init__(self):
        pass

    async def compose(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Dict[str, Any],
        customer: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, str, str, list]:
        """
        Composes a proactive message.
        Attempts LLM generation with strict grounding guards.
        Falls back to high-precision deterministic templates if LLM is unavailable or times out.
        Returns: (body, cta, suppression_key, rationale, template_params)
        """
        # Default fallback computation
        fb_body, fb_cta, suppression_key, fb_rationale, fb_params = compose_grounded_message(
            category, merchant, trigger, customer
        )

        if not settings.llm_api_key or settings.llm_provider == "none":
            return fb_body, fb_cta, suppression_key, fb_rationale, fb_params

        try:
            llm_result = await self._call_llm(category, merchant, trigger, customer)
            if llm_result:
                body = llm_result.get("body", "")
                cta = llm_result.get("cta", "open_ended")
                rationale = llm_result.get("rationale", fb_rationale)
                params = llm_result.get("template_params", fb_params)

                # Validation guard: ensure no taboos
                taboos = category.get("voice", {}).get("vocab_taboo", [])
                if any(t.lower() in body.lower() for t in taboos):
                    return fb_body, fb_cta, suppression_key, fb_rationale, fb_params

                # Guard against URLs (Failure Mode F.4: Meta reject, -3 penalty)
                body = re.sub(r'https?://\S+|www\.\S+', '', body).strip()

                # Ensure non-empty
                if len(body.strip()) > 20:
                    return body, cta, suppression_key, rationale, params
        except Exception:
            pass

        return fb_body, fb_cta, suppression_key, fb_rationale, fb_params

    async def _call_llm(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Dict[str, Any],
        customer: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Calls external LLM with strict grounding constraints.
        """
        cat_slug = category.get("slug", "")
        tone = category.get("voice", {}).get("tone", "")
        taboos = category.get("voice", {}).get("vocab_taboo", [])

        prompt = f"""You are Vera, magicpin's proactive AI merchant growth assistant.
Compose an outreach message to this merchant based STRICTLY on the provided data.

RULES (from magicpin Judging Guidance):
1. DECISION QUALITY: Strong bots do NOT repeat every available fact. Choose the ONE key signal that drives the next message (trigger + merchant state).
2. SPECIFICITY & GROUNDING: Use real numbers, offers, dates, and local facts from the given input. Never invent or fabricate data (penalty -2). Generic messages lose.
3. CATEGORY FIT: Tone is '{tone}'. Respect business type (clinical, visual, timely, or utility-first). Taboos to strictly AVOID: {taboos}. If dentists, address as 'Dr. <Name>' in peer-clinical tone.
4. ENGAGEMENT COMPULSION: Bold does not mean hype — use a sharp hook from real context. Keep asks short and low-friction with one clear next step (e.g. 'Reply 1', 'Reply YES', or a low-effort choice).
5. CLEANLINESS: No internal jargon ('trigger', 'payload', 'system', etc.). NO URLs (Meta rejects messages with links; penalty -3). Max 3 sentences.

DATA:
Category: {cat_slug}
Merchant: {json.dumps(merchant.get('identity', {}))}
Performance: {json.dumps(merchant.get('performance', {}))}
Offers: {json.dumps([o.get('title') for o in merchant.get('offers', []) if o.get('status') == 'active'])}
Signals: {merchant.get('signals', [])}
Trigger: {json.dumps(trigger)}
Customer: {json.dumps(customer.get('identity', {})) if customer else 'None'}

Return ONLY valid JSON in this format:
{{
  "body": "<the message text, max 3 sentences>",
  "cta": "open_ended" or "binary",
  "rationale": "<why this message was composed>",
  "template_params": ["<param1>", "<param2>"]
}}"""

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            if settings.llm_provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model or 'gemini-1.5-flash'}:generateContent?key={settings.llm_api_key}"
                body = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600}
                }
                resp = await client.post(url, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    match = re.search(r'\{[\s\S]*\}', text)
                    if match:
                        return json.loads(match.group())

            elif settings.llm_provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
                body = {
                    "model": settings.llm_model or "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You compose grounded merchant messages. Return JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"}
                }
                resp = await client.post(url, json=body, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return json.loads(data["choices"][0]["message"]["content"])

        return None

composer = Composer()
