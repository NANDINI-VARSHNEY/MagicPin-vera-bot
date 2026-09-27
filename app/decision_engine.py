import time
from typing import List
from app.models import TickRequest, TickAction
from app.context_store import context_store
from app.composer import composer
from app.config import settings

class DecisionEngine:
    async def evaluate_tick(self, req: TickRequest) -> List[TickAction]:
        actions: List[TickAction] = []
        sent_in_this_tick = set()

        for trg_id in req.available_triggers:
            if len(actions) >= settings.max_actions_per_tick:
                break

            trg = context_store.get_trigger(trg_id)
            if not trg:
                continue

            # Identify target merchant
            merchant_id = trg.get("merchant_id") or trg.get("payload", {}).get("merchant_id")
            if not merchant_id:
                # If trigger is category wide, check if there's an eligible merchant
                cat_slug = trg.get("payload", {}).get("category")
                if cat_slug:
                    # Look up first matching merchant
                    with context_store._lock:
                        for (scope, cid), val in context_store._store.items():
                            if scope == "merchant" and val["payload"].get("category_slug") == cat_slug:
                                merchant_id = cid
                                break

            if not merchant_id:
                continue

            # Don't send multiple messages to the same merchant in the same tick
            if merchant_id in sent_in_this_tick:
                continue

            # Check suppression
            suppression_key = trg.get("suppression_key", "")
            if suppression_key and context_store.is_suppressed(suppression_key, settings.cooldown_seconds_per_merchant):
                continue

            merchant = context_store.get_merchant(merchant_id)
            if not merchant:
                continue

            cat_slug = merchant.get("category_slug")
            category = context_store.get_category(cat_slug) if cat_slug else None
            if not category:
                continue

            customer_id = trg.get("customer_id")
            customer = context_store.get_customer(customer_id) if customer_id else None

            # Compose message
            body, cta, supp_key, rationale, params = await composer.compose(
                category=category,
                merchant=merchant,
                trigger=trg,
                customer=customer
            )

            conv_id = f"conv_{merchant_id}_{trg_id}"
            
            send_as = "merchant_on_behalf" if customer_id else "vera"
            template_name = "merchant_recall_reminder_v1" if customer_id else f"vera_{cat_slug}_v1"

            action = TickAction(
                conversation_id=conv_id,
                merchant_id=merchant_id,
                customer_id=customer_id,
                send_as=send_as,
                trigger_id=trg_id,
                template_name=template_name,
                template_params=params,
                body=body,
                cta=cta,
                suppression_key=supp_key,
                rationale=rationale
            )

            actions.append(action)
            sent_in_this_tick.add(merchant_id)
            if supp_key:
                context_store.mark_suppressed(supp_key)

        return actions

decision_engine = DecisionEngine()
