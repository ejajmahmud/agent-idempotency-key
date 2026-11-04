"""Tests for agent-idempotency-key."""
import unittest
from agent_idempotency_key.guard import IdempotencyGuard


class TestIdempotencyGuard(unittest.TestCase):
    def setUp(self):
        self.guard = IdempotencyGuard(default_ttl=10.0)

    def test_idempotent_execution(self):
        call_count = 0

        def tool():
            nonlocal call_count
            call_count += 1
            return {"order_id": 42}

        res1, is_cached1 = self.guard.execute("txn_01", "create_order", {}, tool)
        self.assertFalse(is_cached1)
        self.assertEqual(call_count, 1)

        res2, is_cached2 = self.guard.execute("txn_01", "create_order", {}, tool)
        self.assertTrue(is_cached2)
        self.assertEqual(call_count, 1)
        self.assertEqual(res1, res2)


if __name__ == "__main__":
    unittest.main()
