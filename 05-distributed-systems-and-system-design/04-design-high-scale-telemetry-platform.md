# 🏗️ System Design: High-Scale Telemetry Platform (10M Metrics/Sec)

> **Interview Prompt**:  
> *"Design a centralized observability and telemetry ingestion platform capable of handling 10 Million metric samples per second, 1 Million log events per second, and distributed tracing across 10,000 microservices with sub-second query latency for SRE dashboards."*

---

## 1. Scale & Back-of-the-Envelope Estimation

- **Ingestion Scale**:
  - $10,000,000\text{ metric samples/sec}$.
  - Each sample $\approx 16\text{ bytes}$ (Timestamp 8B + Float64 Value 8B + Metric ID hash).
  - Network Ingress: $10\text{M} \times 16\text{B} = 160\text{ MB/sec} = 1.28\text{ Gbps}$.
  - Uncompressed Daily Volume: $160\text{ MB/s} \times 86400\text{ s} \approx 13.8\text{ TB/day}$.
  - After TSDB Gorilla / Snappy compression ($\approx 2\text{ bytes/sample}$): $\approx 1.7\text{ TB/day}$.
- **SLA / SLO**:
  - Ingestion Availability: $99.99\%$ (Data loss $< 0.001\%$).
  - P99 Dashboard Query Latency: $< 500\text{ms}$ for 1-hour ranges, $< 2\text{s}$ for 30-day ranges.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Data_Sources["1. Telemetry Sources (10,000 Microservices)"]
        Workloads["Application Pods & Nodes"]
        LocalCollector["OTel Collector DaemonSets (Host Metrics & Spans)"]
        Workloads --> LocalCollector
    end

    subgraph Ingestion_Edge["2. Ingestion Gateway Layer"]
        LB["NLB / Anycast Load Balancer"]
        EdgeGateways["Stateless OTel Gateways / Ingestion Proxies"]
        LocalCollector -->|gRPC OTLP / Push| LB --> EdgeGateways
    end

    subgraph Message_Buffer["3. Distributed Buffer (Decouples Spikes)"]
        Kafka["Apache Kafka / Redpanda Cluster<br/>(Partitioned by Metric Name Hash & Tenant ID)"]
        EdgeGateways --> Kafka
    end

    subgraph Processing_Engine["4. Stream Processing & Compaction Layer"]
        Flink["Apache Flink / Vector Stream Processors<br/>- Deduplication & Out-of-order alignment<br/>- Dynamic High-Cardinality Scrubbing<br/>- Pre-aggregating 1m / 5m rollups"]
        Kafka --> Flink
    end

    subgraph Storage_Tiering["5. Storage Layer (Hot / Warm / Cold Tiering)"]
        HotTier["Hot Tier (0-24h): Mimir / ClickHouse SSD Nodes"]
        ColdTier["Cold Tier (1d-3yr): Object Storage (S3 / GCS Parquet Blocks)"]
        Flink --> HotTier
        HotTier -->|Flush TSDB Blocks| ColdTier
    end

    subgraph Query_Federation["6. Query & Visualization Engine"]
        QueryFrontend["Thanos Query / Mimir Query-Frontend (Cache + Split)"]
        Grafana["Grafana Dashboards & Prometheus Alerts"]
        Grafana --> QueryFrontend
        QueryFrontend --> HotTier
        QueryFrontend --> ColdTier
    end
```

---

## 3. Deep-Dive Design Decisions

### 1. Partitioning & Sharding Strategy in Kafka
- **Partition Key**: `hash(tenant_id + metric_name)`.
- **Rationale**: Guarantees that all time-series samples for a given metric land in the same Kafka partition, ensuring strict temporal order for Flink stream processing without cross-partition shuffles.

### 2. Stream Processing with Apache Flink
- Computes **sliding-window rollups** (1-minute and 5-minute averages, P50, P95, P99 quantiles) directly in-stream before writing to storage.
- When dashboards query a 30-day view, they query pre-aggregated rollups instead of scanning 25 billion raw data points.

### 3. Query Splitting & Caching (Mimir Query Frontend)
- A PromQL query for `[30d]` is split into 30 parallel 1-day sub-queries.
- Sub-query results are cached in **Redis / Memcached**. Subsequent dashboard reloads return instant cache hits.
