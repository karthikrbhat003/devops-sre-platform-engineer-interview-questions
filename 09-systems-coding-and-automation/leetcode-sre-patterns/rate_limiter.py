#!/usr/bin/env python3
"""
Thread-Safe Rate Limiter Algorithms for SRE Interviews
1. Token Bucket Algorithm (Allows burst capacity up to capacity)
2. Sliding Window Log Algorithm (Accurate rate limiting over time window)
"""

import time
import threading
from collections import deque
from typing import Dict

class TokenBucketRateLimiter:
    """
    Token Bucket Rate Limiter:
    - capacity: maximum burst tokens allowed
    - refill_rate: tokens added per second
    """
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def allow_request(self, tokens_needed: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill_time
            # Refill tokens based on elapsed time
            self.tokens = min(float(self.capacity), self.tokens + elapsed * self.refill_rate)
            self.last_refill_time = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

class SlidingWindowLogRateLimiter:
    """
    Sliding Window Log Rate Limiter per Client ID:
    - limit: max requests allowed
    - window_seconds: sliding time window in seconds
    """
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window_seconds = window_seconds
        self.client_logs: Dict[str, deque] = {}
        self.lock = threading.Lock()

    def allow_request(self, client_id: str) -> bool:
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            if client_id not in self.client_logs:
                self.client_logs[client_id] = deque()

            log = self.client_logs[client_id]
            # Evict timestamps older than the sliding window
            while log and log[0] <= window_start:
                log.popleft()

            if len(log) < self.limit:
                log.append(now)
                return True
            return False

if __name__ == "__main__":
    print("Testing Token Bucket Rate Limiter (Capacity: 3, Refill: 1 token/sec)...")
    tb = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
    for i in range(5):
        allowed = tb.allow_request()
        print(f"  Req {i+1}: {'ALLOWED ✅' if allowed else 'THROTTLED ❌'}")
        time.sleep(0.2)

    time.sleep(1.5)
    print("After 1.5s refill:")
    print(f"  Req 6: {'ALLOWED ✅' if tb.allow_request() else 'THROTTLED ❌'}")

    print("\nTesting Sliding Window Rate Limiter (Limit: 2 req / 1 sec)...")
    sw = SlidingWindowLogRateLimiter(limit=2, window_seconds=1.0)
    print(f"  Client A Req 1: {'ALLOWED ✅' if sw.allow_request('client-A') else 'THROTTLED ❌'}")
    print(f"  Client A Req 2: {'ALLOWED ✅' if sw.allow_request('client-A') else 'THROTTLED ❌'}")
    print(f"  Client A Req 3: {'ALLOWED ✅' if sw.allow_request('client-A') else 'THROTTLED ❌'}")
    print(f"  Client B Req 1: {'ALLOWED ✅' if sw.allow_request('client-B') else 'THROTTLED ❌'}")
