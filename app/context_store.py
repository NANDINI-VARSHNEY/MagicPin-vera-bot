import threading
from typing import Dict, Tuple, Optional, Any
from app.models import ContextCounts

class ContextStore:
    def __init__(self):
        self._lock = threading.RLock()
        # Key: (scope, context_id) -> {"version": int, "payload": dict, "delivered_at": str}
        self._store: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Tracking sent suppressions: key -> sent_at
        self._sent_suppressions: Dict[str, float] = {}

    def push(self, scope: str, context_id: str, version: int, payload: Dict[str, Any], delivered_at: str) -> Tuple[bool, Optional[int]]:
        """
        Store context idempotently.
        Returns: (success, current_version_if_conflict)
        """
        key = (scope, context_id)
        with self._lock:
            current = self._store.get(key)
            if current:
                cur_ver = current["version"]
                if cur_ver >= version:
                    return False, cur_ver
            self._store[key] = {
                "version": version,
                "payload": payload,
                "delivered_at": delivered_at
            }
            return True, None

    def get(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            data = self._store.get((scope, context_id))
            return data["payload"] if data else None

    def get_category(self, slug: str) -> Optional[Dict[str, Any]]:
        return self.get("category", slug)

    def get_merchant(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        return self.get("merchant", merchant_id)

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self.get("customer", customer_id)

    def get_trigger(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        return self.get("trigger", trigger_id)

    def get_counts(self) -> ContextCounts:
        counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
        with self._lock:
            for (scope, _), _ in self._store.items():
                if scope in counts:
                    counts[scope] += 1
        return ContextCounts(**counts)

    def is_suppressed(self, suppression_key: str, cooldown_seconds: float = 3600) -> bool:
        if not suppression_key:
            return False
        with self._lock:
            import time
            last_sent = self._sent_suppressions.get(suppression_key)
            if last_sent and (time.time() - last_sent) < cooldown_seconds:
                return True
            return False

    def mark_suppressed(self, suppression_key: str):
        if suppression_key:
            import time
            with self._lock:
                self._sent_suppressions[suppression_key] = time.time()

# Global singleton
context_store = ContextStore()
