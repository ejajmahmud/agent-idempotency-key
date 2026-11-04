"""CLI for agent-idempotency-key."""
import sys
import argparse
from .guard import IdempotencyGuard


def main():
    parser = argparse.ArgumentParser(description="Agent Idempotency Key")
    parser.add_argument("--key", default="demo_key_1", help="Idempotency key")
    args = parser.parse_args()

    guard = IdempotencyGuard()
    res1, cached1 = guard.execute(args.key, "send_msg", {"to": "alice"}, lambda: "msg_sent_100")
    res2, cached2 = guard.execute(args.key, "send_msg", {"to": "alice"}, lambda: "msg_sent_100")
    print(f"Call 1 cached: {cached1}, Call 2 cached: {cached2}. Result: {res2}")
    sys.exit(0)


if __name__ == "__main__":
    main()
