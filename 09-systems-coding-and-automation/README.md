# 💻 Systems Coding & Automation (Go, Python & SRE Patterns)

> **Senior/Staff Interview Scope**: Production-grade systems programming, concurrency (Go channels/goroutines, Python asyncio), API client SDKs (`client-go`, `boto3`), and top SRE algorithm patterns (Token Bucket Rate Limiters, LRU Caches, Log Stream Parsers, Dependency Graph Resolvers).

---

## 📖 Question Bank

- 🎯 [**Exhaustive Systems Coding Interview Question Bank (Top 20 Questions)**](./interview-questions-exhaustive.md)

---

## 📂 Code Practice Modules (Clickable Files)

### 1. Go Systems Engineering
- [**`go/worker_pool.go`**](./go/worker_pool.go) — *Concurrent worker pool with error group, cancellation context, and bounded queue.*
- [**`go/k8s_pod_watcher.go`**](./go/k8s_pod_watcher.go) — *Kubernetes `client-go` Informer watcher for monitoring CrashLooping and OOMKilled pods.*

### 2. Python Automation & Async
- [**`python/log_parser_analyzer.py`**](./python/log_parser_analyzer.py) — *High-throughput streaming log parser extracting Top-K slow endpoints and status codes using minimal memory ($O(1)$ space).*
- [**`python/aws_cost_anomaly_detector.py`**](./python/aws_cost_anomaly_detector.py) — *CloudWatch / Cost Explorer anomaly detection script using `boto3`.*

### 3. Core SRE Algorithm Patterns
- [**`leetcode-sre-patterns/rate_limiter.py`**](./leetcode-sre-patterns/rate_limiter.py) — *Thread-safe Token Bucket & Sliding Window Log Rate Limiter implementations.*
- [**`leetcode-sre-patterns/lru_cache.py`**](./leetcode-sre-patterns/lru_cache.py) — *Thread-safe $O(1)$ Least Recently Used (LRU) Cache using Doubly Linked List and Hash Map.*
