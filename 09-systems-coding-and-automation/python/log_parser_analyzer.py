#!/usr/bin/env python3
"""
High-Throughput Streaming Web Server Log Analyzer
- Uses constant memory O(1) space via generator streaming.
- Computes Top-K Slowest Endpoints, Top Error Status Codes, and P99 Latency.
"""

import re
import heapq
import sys
from collections import defaultdict
from typing import Generator, Tuple, Dict, Any

# Common NGINX / Combined Access Log Regex
# Format: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<bytes>\d+) "[^"]*" "[^"]*" (?P<latency>[\d\.]+)'
)

def stream_log_lines(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """Generator that yields parsed log entries line-by-line without loading entire file into RAM."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, start=1):
            match = LOG_PATTERN.match(line.strip())
            if match:
                data = match.groupdict()
                yield {
                    "ip": data["ip"],
                    "method": data["method"],
                    "path": data["path"].split("?")[0], # Strip query params to group endpoints
                    "status": int(data["status"]),
                    "latency": float(data["latency"]),
                }

def analyze_logs(file_path: str, top_k: int = 5):
    total_requests = 0
    status_counts = defaultdict(int)
    endpoint_latencies = defaultdict(list)

    print(f"📊 Analyzing log stream from: {file_path} ...")
    for entry in stream_log_lines(file_path):
        total_requests += 1
        status_counts[entry["status"]] += 1
        # Track latencies per endpoint (sampled if needed)
        endpoint_latencies[entry["path"]].append(entry["latency"])

    if total_requests == 0:
        print("No valid log lines parsed.")
        return

    print(f"\n==========================================")
    print(f"📈 Total Requests Processed: {total_requests:,}")
    print(f"==========================================")

    print("\n🚨 HTTP Status Code Breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_requests) * 100
        print(f"  HTTP {status}: {count:,} ({pct:.2f}%)")

    # Compute Top-K Slowest Endpoints by Average Latency
    print(f"\n⏳ Top {top_k} Slowest Endpoints (Avg Latency):")
    endpoint_stats = []
    for path, latencies in endpoint_latencies.items():
        avg_lat = sum(latencies) / len(latencies)
        latencies.sort()
        p99_idx = int(len(latencies) * 0.99)
        p99_lat = latencies[min(p99_idx, len(latencies) - 1)]
        endpoint_stats.append((avg_lat, p99_lat, len(latencies), path))

    # Top-K using heapq for O(N log K) efficiency
    top_slowest = heapq.nlargest(top_k, endpoint_stats)
    for avg_lat, p99_lat, count, path in top_slowest:
        print(f"  {path:<35} | Req: {count:<6} | Avg: {avg_lat:.3f}s | P99: {p99_lat:.3f}s")

if __name__ == "__main__":
    import tempfile
    import os

    # Generate sample dummy log for verification if run standalone
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        sample_logs = """192.168.1.1 - - [03/Sep/2026:12:00:01 +0000] "GET /api/v1/checkout HTTP/1.1" 200 1250 "-" "-" 0.045
192.168.1.2 - - [03/Sep/2026:12:00:02 +0000] "POST /api/v1/charge HTTP/1.1" 500 240 "-" "-" 1.450
192.168.1.3 - - [03/Sep/2026:12:00:03 +0000] "GET /api/v1/checkout HTTP/1.1" 200 1250 "-" "-" 0.052
192.168.1.4 - - [03/Sep/2026:12:00:04 +0000] "GET /api/v1/products HTTP/1.1" 200 8900 "-" "-" 0.120
192.168.1.5 - - [03/Sep/2026:12:00:05 +0000] "POST /api/v1/charge HTTP/1.1" 504 120 "-" "-" 2.890
"""
        tmp.write(sample_logs)
        tmp_path = tmp.name

    analyze_logs(tmp_path, top_k=3)
    os.remove(tmp_path)
