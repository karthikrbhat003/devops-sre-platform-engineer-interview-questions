# 🔌 Kubernetes CNI Networking, Ingress & Service Mesh

> **Senior/Staff Interview Scope**: CNI plugin mechanics (AWS VPC CNI vs Calico vs Cilium eBPF), kube-proxy iptables vs IPVS vs eBPF, Ingress Controllers vs Gateway API, and Service Mesh architectures (Sidecar Istio vs Ambient Mesh).

---

## 1. CNI Comparison Matrix

| Feature | AWS VPC CNI | Calico | Cilium (eBPF-Powered) |
|---|---|---|---|
| **IP Allocation** | Assigns real AWS VPC secondary ENI IPs directly to Pods | Uses private overlay CIDR (VXLAN / IP-in-IP) or BGP | BGP or Overlay (Geneve / VXLAN) or direct routing |
| **Throughput & Latency** | High (native AWS VPC routing, no encapsulation) | Good (slight encapsulation overhead in overlay mode) | **Highest** (eBPF kernel bypass; direct socket-level routing) |
| **Scale Bottleneck** | Limited by EC2 ENI & IP limits per instance type | High iptables rule count at 5,000+ services ($O(N)$ lookup) | **$O(1)$ BPF hash map lookup**; handles 50,000+ services with zero latency degradation |
| **Network Security** | AWS Security Groups for Pods | Calico NetworkPolicies (iptables) | Cilium L3-L7 NetworkPolicies + Hubble flow visibility |

---

## 2. Kube-Proxy: iptables vs Cilium eBPF Host-Routing

```mermaid
flowchart LR
    subgraph Traditional_Kube_Proxy["Traditional kube-proxy (iptables mode)"]
        Packet1["Packet from Pod"] --> IPtables["Traverse 10,000+ iptables rules sequentially (O(N) CPU overhead)"]
        IPtables --> Conntrack["Pass through Linux conntrack"]
        Conntrack --> Dest1["Destination Pod"]
    end

    subgraph Cilium_eBPF["Cilium eBPF Host Routing (Kube-Proxy Replacement)"]
        Packet2["Packet from Pod"] --> BPF_Sock["eBPF Socket Hook (sock_ops)"]
        BPF_Sock -->|Direct O(1) BPF Map Lookup| BPF_Redirect["BPF Redirect directly to Destination Socket"]
        BPF_Redirect --> Dest2["Destination Pod (Bypasses TCP/IP stack & iptables)"]
    end
```

---

## 3. Kubernetes Gateway API vs Traditional Ingress

- **Limitations of Ingress (`Ingress` resource)**:
  - Single monolithic resource combining routing, TLS, and load balancing.
  - Lacks role-oriented separation (Infrastructure team vs Application developer).
  - Relies heavily on messy vendor-specific annotations (`nginx.ingress.kubernetes.io/*`).
- **Gateway API (The Modern Standard)**:
  - **`GatewayClass`**: Defined by infrastructure/cloud platform team.
  - **`Gateway`**: Deployed by cluster operators (defines listening ports, IPs, certificates).
  - **`HTTPRoute` / `GRPCRoute`**: Owned and managed independently by application developers.

---

## 4. Service Mesh Evolution: Sidecar vs Ambient Mesh

- **Traditional Sidecar Mesh (Istio Envoy Sidecar)**:
  - Injects an Envoy proxy container into every application pod.
  - **Drawbacks**: High memory footprint (50MB–100MB RAM overhead per pod), slower pod startup, complex upgrades.
- **Istio Ambient Mesh (Sidecarless)**:
  - Splits L4 and L7 processing into two separate layers:
    1. **ztunnel (Zero-Trust Tunnel)**: Lightweight node-level DaemonSet handling mutual TLS (mTLS) and L4 routing.
    2. **Waypoint Proxy**: Dedicated L7 Envoy proxy deployed per namespace only when advanced Layer 7 policies (traffic splitting, fault injection) are required.
  - **Benefit**: Reduces service mesh infrastructure cost by **up to 70%** and eliminates pod restarts during mesh upgrades.
