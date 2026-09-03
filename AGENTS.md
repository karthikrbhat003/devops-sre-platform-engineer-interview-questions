# 🤖 Agent Rules & Repository Instructions

This document governs the engineering standards, technical depth, and architectural rules for maintaining and expanding the `devops-sre-platform-engineer-interview-prep` repository.

---

## 🎯 Target Persona & Evaluation Standard

- **Target Candidate**: 6.5+ Years Experience (Senior SRE / Senior Platform Engineer / Lead DevOps / Staff Track).
- **Target Tier**: MAANG (Meta, Apple, Amazon, Google), Tier-1 Tech (Uber, Stripe, Datadog, Netflix, Coinbase), and Multi-Region / Multi-Cloud Enterprise Tech.
- **Evaluation Bar**: L5 (Senior) / L6 (Staff) level:
  - **No surface-level summaries**: Always explain the **underlying mechanism** (e.g. not just "increase memory", but explain `cgroups v2 memory.max`, page cache direct reclaim, `oom_score_adj`, and kernel page tables).
  - **Always include failure modes & tradeoffs**: Every architectural choice must detail what happens during partial network partitions, disk stalls, or regional outages.
  - **Production-grade configurations**: YAML manifests, PromQL alerts, Go code, and Python scripts must be fully functional and syntactically valid.

---

## 📚 Repository Structure & Pillar Rules

1. **Pillar 01: Linux Systems & Networking**:
   - Kernel virtual memory, page cache dirty ratios, cgroups v2, CFS quota throttling.
   - TCP state machines, socket queue depths (`somaxconn`, `syn_backlog`), conntrack limits, MTU/MSS, CoreDNS `ndots:5`.
   - Methodical troubleshooting using the USE method, `perf`, `strace`, `sysdig`, `ss`, `tcpdump`, `bpftrace`.
2. **Pillar 02: Enterprise CI/CD & Release Engineering**:
   - Monorepo vs polyrepo build caching (Dagger, Bazel, BuildKit).
   - Progressive delivery with Argo Rollouts and Flagger (canary analysis, automated rollback).
   - Supply chain security (SLSA 3, Cosign keyless signing, Syft SBOMs, OIDC without keys).
   - Ephemeral preview environments with vCluster and automated TTL garbage collection.
3. **Pillar 03: Observability & Telemetry at Scale**:
   - OpenTelemetry Collector pipeline topology, processors, tail-based vs head-based sampling.
   - High-scale metrics engines (Prometheus TSDB internals, Thanos Sidecar/Store/Compact, Grafana Mimir).
   - Distributed tracing (W3C context, Tempo, Jaeger) and logging (Loki, Vector).
   - eBPF zero-code telemetry (Grafana Beyla, Pixie, Cilium Hubble) and continuous profiling.
   - Mathematical SLI/SLO formulation and Google SRE multi-window multi-burn-rate PromQL alerting.
4. **Pillar 04: AI for SRE & AI Platform Engineering (LLMOps)**:
   - AIOps: LLM agentic incident triage, automated RCA workflows, RAG on post-mortems.
   - GPU orchestration on Kubernetes: NVIDIA GPU Operator, MIG partitioning, GPU time-slicing.
   - LLM serving infra: vLLM PagedAttention, Triton dynamic batching, KEDA queue autoscaling.
   - AI FinOps: Spot GPU fleet orchestration with Karpenter, JuiceFS model streaming.
5. **Pillar 05: Distributed Systems & System Design**:
   - 45-minute 5-phase interview framework with back-of-the-envelope scale math.
   - Multi-Region Active-Active architectures, DynamoDB Global Tables, Aurora Multi-Region, Anycast BGP.
   - Multi-cloud disaster recovery (AWS + GCP Direct Connect / Interconnect, STS data sync).
   - High-scale telemetry (10M metrics/sec) and Internal Developer Platform (IDP) designs.
6. **Pillar 06: Kubernetes Platform Engineering**:
   - Control plane internals (etcd Raft consensus, API server OCC `resourceVersion`, Kubelet PLEG).
   - Networking (Cilium eBPF host routing, Gateway API, Istio Ambient Mesh).
   - Autoscaling (Karpenter NodePools vs CAS, PDBs, Topology Spread Constraints).
   - Operator development in Go (`controller-runtime`, Informer cache, status subresources).
   - Policy-as-code (Kyverno ClusterPolicies, OPA Gatekeeper).
7. **Pillar 07: Cloud Architecture (AWS + GCP)**:
   - AWS Organizations, Transit Gateway route tables, PrivateLink, IAM ABAC.
   - GCP Shared VPC, VPC Service Controls, GKE vs EKS architectural deep dive.
   - Multi-cloud interconnect (Equinix Fabric BGP, Workload Identity OIDC STS).
   - FinOps: Cross-AZ data egress reduction, Savings Plans, unit cost metrics.
8. **Pillar 08: IaC & Infrastructure Automation**:
   - Terragrunt DRY multi-account architecture, remote state locking, `moved` blocks.
   - Drift detection automation with Atlantis and scheduled cron pipelines.
   - Policy-as-code in IaC (OPA Conftest Rego rules, Checkov gates).
9. **Pillar 09: Systems Coding & Automation**:
   - Go concurrency: Goroutines, channels, worker pools, `client-go` Informers.
   - Python automation: Asyncio, streaming log parsers ($O(1)$ memory), `boto3` scripts.
   - SRE algorithms: Token Bucket, Sliding Window Rate Limiters, $O(1)$ LRU Cache.
10. **Pillar 10: Behavioral Leadership & Incident Management**:
    - 15 STAR stories covering P0 Outages, Technical Disagreements, Ambiguity, and Mentorship.
    - Incident Commander War Room operations, communication cadence, blameless post-mortems.
    - Senior (L5) vs Staff (L6) hiring rubric and impact signals.

---

## 📝 Linking & Formatting Standards

1. **Relative Markdown Links**: Always use relative links (e.g. `[Topic](./01-linux-kernel-memory-cpu-io.md)` or `[Parent](../01-linux-systems-networking/...)`) so links work seamlessly across all local IDEs, VS Code, Cursor, and GitHub/GitLab.
2. **Mermaid Diagrams**: Include clear visual flowcharts, sequence diagrams, and architecture diagrams in all major topic guides.
3. **Exhaustive Question Banks**: Every module must include an `interview-questions-exhaustive.md` containing 20–25+ deep, senior-level interview questions with comprehensive model answers, edge cases, and follow-ups.
