# 🚀 Senior DevOps / SRE / Platform Engineer Master Interview Preparation

> **Target Profile**: 6.5+ Years Experience | Senior / Lead / Staff DevOps, SRE & Platform Engineer  
> **Target Tier**: MAANG (Meta, Apple, Amazon, Google), Tier-1 Tech (Uber, Stripe, Datadog, Netflix, Coinbase), and Multi-Region / Multi-Cloud Enterprises (AWS + GCP focus).  
> **Repository Rules & Standards**: Read [AGENTS.md](./AGENTS.md) for engineering standards and evaluation criteria.

---

## 📅 Study Roadmaps & Timelines

- ⚡ [**3-Month Fast-Track Schedule (12 Weeks / 20 hrs/week)**](./roadmap/3-month-fast-track.md)
- 🎯 [**6-Month Mastery Track Schedule (24 Weeks / 10-15 hrs/week)**](./roadmap/6-month-mastery-track.md)

---

## 🎯 Master Question Banks (400 Exhaustive Senior/Staff Questions)

| # | Pillar | Question Count | Exhaustive Question Bank (Deep Answers & Follow-ups) |
|---|---|:---:|---|
| **01** | Linux Systems & Low-Level Networking | **40** | 📖 [**Top 40 Linux & Networking Questions Bank**](./01-linux-systems-networking/interview-questions-exhaustive.md) |
| **02** | Enterprise CI/CD & DevSecOps | **40** | 📖 [**Top 40 CI/CD & DevSecOps Questions Bank**](./02-enterprise-cicd-release-engineering/interview-questions-exhaustive.md) |
| **03** | Observability & Telemetry at Scale | **40** | 📖 [**Top 40 Observability & Telemetry Questions Bank**](./03-observability-telemetry-at-scale/interview-questions-exhaustive.md) |
| **04** | AI for SRE & AI Platform (LLMOps) | **40** | 📖 [**Top 40 AI for SRE & GPU Infra Questions Bank**](./04-ai-for-sre-and-ai-platform-engineering/interview-questions-exhaustive.md) |
| **05** | Distributed Systems & System Design | **40** | 📖 [**Top 40 System Design & Multi-Region Questions Bank**](./05-distributed-systems-and-system-design/interview-questions-exhaustive.md) |
| **06** | Kubernetes Platform Engineering | **40** | 📖 [**Top 40 Kubernetes Internals Questions Bank**](./06-kubernetes-platform-engineering/interview-questions-exhaustive.md) |
| **07** | Cloud Architecture (AWS + GCP) | **40** | 📖 [**Top 40 AWS & GCP Enterprise Questions Bank**](./07-cloud-architecture-aws-gcp/interview-questions-exhaustive.md) |
| **08** | IaC & Infrastructure Automation | **40** | 📖 [**Top 40 IaC, Terragrunt & Policy Questions Bank**](./08-iac-and-infrastructure-automation/interview-questions-exhaustive.md) |
| **09** | Systems Coding & Automation | **40** | 📖 [**Top 40 Systems Coding (Go/Python) Questions Bank**](./09-systems-coding-and-automation/interview-questions-exhaustive.md) |
| **10** | Behavioral Leadership & Incidents | **40** | 📖 [**Top 40 Behavioral & War Room Questions Bank**](./10-behavioral-leadership-and-incident-management/interview-questions-exhaustive.md) |
| **Total** | | **400** | **Complete One-Stop Interview Preparation Suite** |

---

## 🧭 Master Syllabus & Interactive Tracker

### [01. Linux Systems & Low-Level Networking](./01-linux-systems-networking/01-linux-kernel-memory-cpu-io.md)
- [ ] 🎯 **[Exhaustive Linux Interview Question Bank (40 Questions)](./01-linux-systems-networking/interview-questions-exhaustive.md)**
- [ ] [01. Linux Kernel, Memory, CPU & I/O Deep Dive](./01-linux-systems-networking/01-linux-kernel-memory-cpu-io.md) — *cgroups v2, page cache dirty ratio, OOM score calculation, CFS bandwidth throttling*
- [ ] [02. Linux Networking: TCP/IP Stack, Sockets & DNS](./01-linux-systems-networking/02-networking-tcp-udp-dns-bgp.md) — *TCP 3-way handshake, socket queues, conntrack limits, MTU/MSS, CoreDNS ndots:5*
- [ ] [03. Live Systems Troubleshooting Playbook](./01-linux-systems-networking/03-live-troubleshooting-playbook.md) — *The USE Method, perf, strace, sysdig, ss, tcpdump, bpftrace*
- [ ] [Drill 1: High Load Average with Low CPU Utilization](./01-linux-systems-networking/scenarios/scenario-01-high-load-low-cpu.md)
- [ ] [Drill 2: Mysterious 502 Bad Gateway & Port Exhaustion](./01-linux-systems-networking/scenarios/scenario-02-mysterious-502-and-port-exhaustion.md)

---

### [02. Enterprise CI/CD & Release Engineering](./02-enterprise-cicd-release-engineering/01-pipeline-architecture-at-scale.md)
- [ ] 🎯 **[Exhaustive CI/CD & DevSecOps Interview Question Bank (40 Questions)](./02-enterprise-cicd-release-engineering/interview-questions-exhaustive.md)**
- [ ] [01. Pipeline Architecture at Scale](./02-enterprise-cicd-release-engineering/01-pipeline-architecture-at-scale.md) — *Monorepo vs multi-repo, BuildKit remote caching, K8s ARC runner pools*
- [ ] [02. Progressive Delivery: Canary, Blue-Green & Rollbacks](./02-enterprise-cicd-release-engineering/02-progressive-delivery-canary-bluegreen.md) — *Argo Rollouts, Flagger, AnalysisTemplates, automated rollback*
- [ ] [03. Software Supply Chain Security (DevSecOps)](./02-enterprise-cicd-release-engineering/03-supply-chain-security-devsecops.md) — *SLSA 3, Sigstore/Cosign keyless signing, Syft SBOMs, OIDC IAM federation*
- [ ] [04. Ephemeral Environments & PR Preview Platforms](./02-enterprise-cicd-release-engineering/04-ephemeral-environments-preview-apps.md) — *vCluster, dynamic PR environments, TTL Janitor garbage collection*
- [ ] [Drill 1: Flaky CI Pipelines & A Broken Canary Rollout](./02-enterprise-cicd-release-engineering/scenarios/scenario-01-flaky-builds-and-broken-rollout.md)

---

### [03. Observability & Telemetry at Scale](./03-observability-telemetry-at-scale/01-opentelemetry-architecture-pipelines.md)
- [ ] 🎯 **[Exhaustive Observability Interview Question Bank (40 Questions)](./03-observability-telemetry-at-scale/interview-questions-exhaustive.md)**
- [ ] [01. OpenTelemetry Architecture & High-Throughput Pipelines](./03-observability-telemetry-at-scale/01-opentelemetry-architecture-pipelines.md) — *OTel Collector topologies, tail-based sampling, batching*
- [ ] [02. Metrics at Scale: Prometheus, Thanos, Mimir & VictoriaMetrics](./03-observability-telemetry-at-scale/02-metrics-at-scale-thanos-mimir.md) — *TSDB mechanics, Thanos (Sidecar/Store/Compact), Mimir*
- [ ] [03. Distributed Tracing & Centralized Logging](./03-observability-telemetry-at-scale/03-distributed-tracing-and-logging.md) — *W3C Trace Context, Tempo, Grafana Loki, Vector log pipelines*
- [ ] [04. eBPF-Based Zero-Code Observability](./03-observability-telemetry-at-scale/04-ebpf-zero-code-observability.md) — *Grafana Beyla, Pixie, Cilium Hubble, continuous profiling*
- [ ] [05. SLI, SLO & Error Budget Engineering](./03-observability-telemetry-at-scale/05-slo-sli-error-budget-alerting.md) — *Multi-window multi-burn-rate alerting PromQL formulas*
- [ ] [Drill 1: High-Cardinality Metric Explosion & Prometheus OOM Crash](./03-observability-telemetry-at-scale/scenarios/scenario-01-high-cardinality-prometheus-crash.md)

---

### [04. AI for SRE & AI Platform Engineering (LLMOps)](./04-ai-for-sre-and-ai-platform-engineering/01-aiops-llm-incident-triage-rca.md)
- [ ] 🎯 **[Exhaustive AI & GPU Infra Interview Question Bank (40 Questions)](./04-ai-for-sre-and-ai-platform-engineering/interview-questions-exhaustive.md)**
- [ ] [01. AIOps & LLM-Driven Incident Triage & Automated RCA](./04-ai-for-sre-and-ai-platform-engineering/01-aiops-llm-incident-triage-rca.md) — *LLM agentic triage, RAG on post-mortems, function calling*
- [ ] [02. GPU Orchestration on Kubernetes](./04-ai-for-sre-and-ai-platform-engineering/02-gpu-orchestration-kubernetes.md) — *NVIDIA GPU Operator, MIG partitioning, GPU time-slicing*
- [ ] [03. LLM Serving Infrastructure: vLLM, Triton & Ray](./04-ai-for-sre-and-ai-platform-engineering/03-llm-serving-infra-vllm-triton-ray.md) — *vLLM PagedAttention, Triton batching, KEDA scaling*
- [ ] [04. AI Infrastructure Cost Optimization & FinOps](./04-ai-for-sre-and-ai-platform-engineering/04-ai-infrastructure-cost-optimization.md) — *Spot GPU orchestration, model weight caching with JuiceFS*
- [ ] [Drill 1: CUDA Out-Of-Memory & Spot GPU Eviction Storm](./04-ai-for-sre-and-ai-platform-engineering/scenarios/scenario-01-gpu-oom-and-spot-eviction.md)

---

### [05. Distributed Systems & System Design](./05-distributed-systems-and-system-design/01-system-design-interview-framework.md)
- [ ] 🎯 **[Exhaustive System Design Interview Question Bank (40 Questions)](./05-distributed-systems-and-system-design/interview-questions-exhaustive.md)**
- [ ] [01. 45-Minute Infrastructure System Design Framework](./05-distributed-systems-and-system-design/01-system-design-interview-framework.md) — *5-phase interview execution formula, back-of-the-envelope scale*
- [ ] [02. Multi-Region Active-Active Distributed Architecture](./05-distributed-systems-and-system-design/02-multi-region-active-active.md) — *DynamoDB Global Tables, Aurora Multi-Region, Anycast BGP*
- [ ] [03. Multi-Cloud Architecture & Disaster Recovery (AWS + GCP)](./05-distributed-systems-and-system-design/03-multi-cloud-disaster-recovery.md) — *Equinix Direct Connect + Interconnect, STS data sync*
- [ ] [04. System Design: High-Scale Telemetry Platform (10M Metrics/Sec)](./05-distributed-systems-and-system-design/04-design-high-scale-telemetry-platform.md) — *Kafka + Flink + Thanos/ClickHouse*
- [ ] [05. System Design: Internal Developer Platform (IDP)](./05-distributed-systems-and-system-design/05-design-multi-tenant-developer-platform.md) — *Backstage + ArgoCD + Crossplane*

---

### [06. Kubernetes Platform Engineering](./06-kubernetes-platform-engineering/01-k8s-internals-and-control-plane.md)
- [ ] 🎯 **[Exhaustive Kubernetes Interview Question Bank (40 Questions)](./06-kubernetes-platform-engineering/interview-questions-exhaustive.md)**
- [ ] [01. Kubernetes Deep Internals & Control Plane Mechanics](./06-kubernetes-platform-engineering/01-k8s-internals-and-control-plane.md) — *etcd Raft consensus, API server OCC, Kubelet PLEG*
- [ ] [02. CNI Networking, Ingress & Service Mesh](./06-kubernetes-platform-engineering/02-cni-networking-and-service-mesh.md) — *Cilium eBPF host routing, Gateway API, Istio Ambient Mesh*
- [ ] [03. Karpenter vs Cluster Autoscaler & Cost-Effective Scheduling](./06-kubernetes-platform-engineering/03-karpenter-and-cluster-autoscaling.md) — *Karpenter NodePools, Spot orchestration, PDBs, Topology Spread*
- [ ] [04. Kubernetes Operator Development: CRDs & Controllers in Go](./06-kubernetes-platform-engineering/04-operator-development-crds-in-go.md) — *Kubebuilder, Informer caching, status subresources*
- [ ] [05. Kubernetes Policy-as-Code & Multi-Tenant Governance](./06-kubernetes-platform-engineering/05-policy-as-code-governance.md) — *Kyverno ClusterPolicies, non-root enforcement*

---

### [07. Cloud Architecture (AWS + GCP)](./07-cloud-architecture-aws-gcp/01-aws-enterprise-architecture.md)
- [ ] 🎯 **[Exhaustive AWS & GCP Interview Question Bank (40 Questions)](./07-cloud-architecture-aws-gcp/interview-questions-exhaustive.md)**
- [ ] [01. AWS Enterprise Deep Dive: Landing Zones, TGW & IAM ABAC](./07-cloud-architecture-aws-gcp/01-aws-enterprise-architecture.md) — *AWS Control Tower, Transit Gateway routing, PrivateLink*
- [ ] [02. Google Cloud (GCP) Essentials for AWS Architects](./07-cloud-architecture-aws-gcp/02-gcp-for-aws-architects.md) — *GCP Shared VPC, VPC-SC, GKE vs EKS deep comparison*
- [ ] [03. Multi-Cloud Interconnect, Security & Zero-Trust IAM](./07-cloud-architecture-aws-gcp/03-multi-cloud-interconnect-security.md) — *BGP dynamic routing, OIDC STS federation*
- [ ] [04. FinOps & Cloud Cost Optimization at Scale](./07-cloud-architecture-aws-gcp/04-finops-cloud-cost-engineering.md) — *Cross-AZ data egress elimination, Savings Plans*

---

### [08. IaC & Infrastructure Automation](./08-iac-and-infrastructure-automation/01-terragrunt-and-terraform-at-scale.md)
- [ ] 🎯 **[Exhaustive IaC & Automation Interview Question Bank (40 Questions)](./08-iac-and-infrastructure-automation/interview-questions-exhaustive.md)**
- [ ] [01. Production IaC: Terragrunt & Terraform at Scale](./08-iac-and-infrastructure-automation/01-terragrunt-and-terraform-at-scale.md) — *Terragrunt DRY patterns, state locking, `moved` blocks*
- [ ] [02. IaC Drift Detection & Atlantis GitOps Automation](./08-iac-and-infrastructure-automation/02-iac-drift-detection-and-atlantis.md) — *Atlantis PR workflows, drift detection cron*
- [ ] [03. Policy-as-Code in IaC: OPA Conftest, Checkov & Trivy](./08-iac-and-infrastructure-automation/03-policy-as-code-in-iac.md) — *OPA / Conftest Rego policies, Checkov security gates*

---

### [09. Systems Coding & Automation (Go & Python)](./09-systems-coding-and-automation/README.md)
- [ ] 🎯 **[Exhaustive Systems Coding Interview Question Bank (40 Questions)](./09-systems-coding-and-automation/interview-questions-exhaustive.md)**
- [ ] [Overview & Clickable Practice Guide](./09-systems-coding-and-automation/README.md)
- [ ] [Go: Concurrent Worker Pool with Context (`worker_pool.go`)](./09-systems-coding-and-automation/go/worker_pool.go)
- [ ] [Go: Kubernetes Informer Pod Watcher (`k8s_pod_watcher.go`)](./09-systems-coding-and-automation/go/k8s_pod_watcher.go)
- [ ] [Python: O(1) Streaming Access Log Analyzer (`log_parser_analyzer.py`)](./09-systems-coding-and-automation/python/log_parser_analyzer.py)
- [ ] [Python: AWS Cost Explorer Anomaly Detector (`aws_cost_anomaly_detector.py`)](./09-systems-coding-and-automation/python/aws_cost_anomaly_detector.py)
- [ ] [Algorithm: Token Bucket & Sliding Window Rate Limiter (`rate_limiter.py`)](./09-systems-coding-and-automation/leetcode-sre-patterns/rate_limiter.py)
- [ ] [Algorithm: Thread-Safe O(1) LRU Cache (`lru_cache.py`)](./09-systems-coding-and-automation/leetcode-sre-patterns/lru_cache.py)

---

### [10. Behavioral Leadership & Incident Management](./10-behavioral-leadership-and-incident-management/01-star-incident-story-matrix.md)
- [ ] 🎯 **[Exhaustive Behavioral & Leadership Interview Question Bank (40 Questions)](./10-behavioral-leadership-and-incident-management/interview-questions-exhaustive.md)**
- [ ] [01. 15 STAR Incident & Leadership Story Matrix](./10-behavioral-leadership-and-incident-management/01-star-incident-story-matrix.md) — *Structured answers for Outages, Disagreements, Ambiguity*
- [ ] [02. Incident Commander & War Room Operations Playbook](./10-behavioral-leadership-and-incident-management/02-incident-commander-war-room-playbook.md) — *ICS roles, communication cadences, post-mortems*
- [ ] [03. Senior vs Staff Engineer Evaluation Rubric](./10-behavioral-leadership-and-incident-management/03-senior-staff-interview-rubric.md) — *L5 vs L6 competency bar, impact metrics*
