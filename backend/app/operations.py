"""Process-local request measurements; no credentials, bodies or raw URLs are retained."""
from collections import Counter, deque
from datetime import datetime, timezone
import math
import threading


class Operations:
    def __init__(self):
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.lock = threading.Lock()
        self.counts = Counter()
        self.latencies = deque(maxlen=200)

    def record(self, status, latency_ms):
        with self.lock:
            self.counts[str(status)] += 1
            self.latencies.append(latency_ms)

    def snapshot(self):
        with self.lock:
            latencies = sorted(self.latencies)
            return {"started_at": self.started_at, "scope": "Current backend process; resets on restart",
                    "requests": sum(self.counts.values()), "status_counts": dict(self.counts),
                    "sample_size": len(latencies), "sample_limit": 200,
                    "p95_request_ms": round(latencies[max(0, math.ceil(len(latencies) * .95) - 1)], 2) if latencies else None}
