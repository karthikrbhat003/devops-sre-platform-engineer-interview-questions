# ☁️ Multi-Cloud Architecture & Disaster Recovery (AWS + GCP)

> **Senior/Staff Interview Scope**: Designing cross-cloud resilience between AWS and GCP (excluding Azure), dedicated interconnects (AWS Direct Connect + GCP Cloud Interconnect via Equinix/Megaport), zero-trust cross-cloud identity federation, and hybrid data synchronization.

---

## 1. AWS + GCP Hybrid Architecture & Interconnect Backbone

```mermaid
flowchart TD
    subgraph AWS_Cloud["Primary Cloud: AWS Enterprise"]
        AWS_VPC["AWS VPC (10.100.0.0/16)"]
        EKS["Amazon EKS Production"]
        Aurora["Amazon Aurora PostgreSQL"]
        S3["Amazon S3 Data Lake"]
        TGW["AWS Transit Gateway"]
        
        AWS_VPC --> EKS
        AWS_VPC --> Aurora
        TGW --> AWS_VPC
    end

    subgraph Equinix_Fabric["Equinix Fabric / Megaport (Private Layer 2/3 Backbone)"]
        DX["AWS Direct Connect (10 Gbps)"]
        IC["GCP Dedicated Interconnect (10 Gbps)"]
        BGP["BGP Peering & IPSec Failover Tunnel"]
        
        DX <--> BGP <--> IC
    end

    subgraph GCP_Cloud["Secondary Cloud / AI Engine: Google Cloud (GCP)"]
        GCP_VPC["GCP Shared VPC (10.200.0.0/16)"]
        GKE["Google Kubernetes Engine (GKE)"]
        CloudSQL["Google Cloud SQL (Replica)"]
        GCS["Google Cloud Storage Bucket"]
        CloudRouter["GCP Cloud Router"]
        
        GCP_VPC --> GKE
        GCP_VPC --> CloudSQL
        CloudRouter --> GCP_VPC
    end

    TGW <--> DX
    IC <--> CloudRouter

    subgraph Data_Sync_Engine["Cross-Cloud Continuous Data Sync"]
        Aurora -. CDC / Debezium Kafka Streaming .-> CloudSQL
        S3 -. Storage Transfer Service (STS) .-> GCS
    end
```

---

## 2. Multi-Cloud DR Tiers & Tradeoffs

| DR Pattern | RPO (Data Loss) | RTO (Downtime) | Cost Multiplier | Operational Complexity |
|---|---|---|---|---|
| **Backup & Restore (Cold DR)** | Hours (Snapshot interval) | 4–12 Hours | $1.05\times$ | Low |
| **Pilot Light (Warm Standby)** | Minutes (Continuous DB replication) | 15–30 Minutes | $1.3\times$ | Moderate |
| **Warm Standby (Active-Passive)** | Sub-second | 2–5 Minutes | $1.6\times$ | High |
| **Multi-Cloud Active-Active** | Zero (Synchronous) to ms | **Zero (Instant failover)** | $2.2\times$ | Very High |

---

## 3. Cross-Cloud Identity & Secrets Management

Avoid static AWS access keys stored in GCP or vice versa:
1. **GCP Workload Identity Federation**:
   - GKE pods authenticate to AWS STS using OIDC JSON Web Tokens (JWT) to assume an IAM Role in AWS without any stored credentials.
2. **HashiCorp Vault Multi-Cloud Secrets**:
   - Vault deployed across AWS and GCP cluster nodes with Raft storage replication.
   - Microservices in either cloud authenticate to Vault via native AWS IAM or GCP IAM auth methods.

---

## 4. Cross-Cloud Storage Replication

- **AWS S3 to GCP Cloud Storage**:
  - Use **GCP Storage Transfer Service (STS)** for continuous asynchronous synchronization.
  - Generates HMAC keys in AWS S3 and runs scheduled micro-batch delta replication every 5 minutes.
  - Ensures disaster recovery datasets remain hot in GCP with near-zero RPO.
