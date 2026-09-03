# 🏛️ 45-Minute Infrastructure System Design Framework

> **Senior/Staff Interview Scope**: How to lead, structure, and ace a 45-minute Infrastructure & Distributed Systems Design interview at MAANG / Tier-1 tech companies.

---

## 1. The 5-Phase 45-Minute Time Allocation

```mermaid
gantt
    title 45-Minute System Design Interview Pacing
    dateFormat  m
    axisFormat %M min
    section Structure
    Phase 1: Clarify Scope, Scale & SLOs   :p1, 0, 5m
    Phase 2: High-Level Architecture      :p2, after p1, 10m
    Phase 3: Component Deep-Dive & Flows  :p3, after p2, 15m
    Phase 4: Failure Scenarios & Edge Cases:p4, after p3, 10m
    Phase 5: Operational Wrap-Up & Tradeoffs:p5, after p4, 5m
```

---

## 2. The Step-by-Step Execution Playbook

### Phase 1: Clarify Requirements, Scope & Scale (Minutes 0–5)
- **Functional Requirements**:
  - What are the core user/platform use cases? (e.g. "Ingest 10M metrics/sec with sub-second dashboard query responses").
- **Non-Functional Requirements**:
  - **Availability**: 99.99% (52 minutes downtime/year).
  - **Latency**: P99 read latency < 200ms, write latency < 50ms.
  - **Consistency Model**: Eventual consistency vs Strong consistency (Linearizable).
  - **RPO / RTO**: Recovery Point Objective (data loss) vs Recovery Time Objective (downtime).
- **Scale Calculations (Back-of-the-Envelope)**:
  - Throughput: $10,000,000\text{ samples/sec} \times 16\text{ bytes/sample} = 160\text{ MB/sec} = 1.28\text{ Gbps}$.
  - Storage: $160\text{ MB/sec} \times 86400\text{ sec/day} \approx 13.8\text{ TB/day}$ (Raw) $\rightarrow \approx 2\text{ TB/day}$ after $7\times$ compression.

### Phase 2: High-Level Architecture Diagram (Minutes 5–15)
- Lay out the end-to-end flow:
  1. Edge Ingress / Anycast DNS / Global Load Balancing.
  2. Compute & Ingestion Layer (Stateless microservices, buffer queues like Kafka).
  3. Processing Engine (Flink / Workers).
  4. Storage Layer (Hot/Warm/Cold tiering).
  5. Egress / Query Gateway.

### Phase 3: Component Deep Dive (Minutes 15–30)
- Pick the 2-3 most challenging technical bottlenecks:
  - Partitioning and Sharding strategy (Consistent Hashing vs Range-based).
  - State replication & consensus (Raft, Paxos, Multi-Leader).
  - Cache invalidation and write-through vs write-back policies.

### Phase 4: Resilience, Failure Scenarios & Bottlenecks (Minutes 30–40)
- Proactively address catastrophic failures before the interviewer asks:
  - *"What happens if an entire AWS Region (us-east-1) goes completely dark?"*
  - *"How do we prevent a cascading thundering herd if the primary cache crashes?"*
  - *"How do we handle split-brain in network partitions (CAP theorem)?"*

### Phase 5: Wrap-Up, FinOps & Tradeoffs (Minutes 40–45)
- Summarize key design tradeoffs:
  - Consistency vs Availability (AP vs CP).
  - Cost vs Latency (Local NVMe SSD vs S3 Object storage).
  - Future roadmap improvements.
