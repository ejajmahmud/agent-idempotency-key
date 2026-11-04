"""Idempotency guard preventing duplicate tool side-effects."""
import time
import hashlib
import json
from typing import Dict, Any, Optional, Callable, Tuple


class IdempotencyGuard:
    def __init__(self, default_ttl: float = 300.0):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl = default_ttl

    def _hash_payload(self, tool_name: str, params: Dict[str, Any]) -> str:
        raw = f"{tool_name}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def execute(
        self,
        idempotency_key: str,
        tool_name: str,
        params: Dict[str, Any],
        handler: Callable[[], Any]
    ) -> Tuple[Any, bool]:
        """Returns (result, is_cached_replay)."""
        now = time.time()
        self._cleanup(now)

        if idempotency_key in self._store:
            entry = self._store[idempotency_key]
            if entry["status"] == "COMPLETED":
                return entry["result"], True
            elif entry["status"] == "PENDING":
                raise RuntimeError(f"Concurrent request in-flight for key: {idempotency_key}")

        # Acquire lock
        payload_hash = self._hash_payload(tool_name, params)
        self._store[idempotency_key] = {
            "status": "PENDING",
            "hash": payload_hash,
            "created_at": now,
            "result": None
        }

        try:
            result = handler()
            self._store[idempotency_key]["status"] = "COMPLETED"
            self._store[idempotency_key]["result"] = result
            return result, False
        except Exception:
            del self._store[idempotency_key]
            raise

    def _cleanup(self, now: float):
        expired = [k for k, v in self._store.items() if now - v["created_at"] > self._ttl]
        for k in expired:
            del self._store[k]
