# 🐧 Linux Systems & Networking: Exhaustive Interview Question Bank (Top 30 Questions)

> **Target Level**: Senior / Staff SRE & Platform Engineer (6.5+ YoE)  
> **Evaluation Focus**: Kernel subsystems, memory management, TCP/IP state machine, eBPF, and live system diagnostics.

---

### Q1: Explain what happens under the hood when a Linux process calls `malloc(100MB)` vs when it actually writes to that memory.
> **Deep Answer**:
> 1. When `malloc(100MB)` is called, the C standard library (`glibc`) uses either `brk()` (for small allocations) or `mmap(MAP_ANONYMOUS | MAP_PRIVATE)` (for allocations $\ge 128\text{KB}$) to request address space from the kernel.
> 2. The kernel updates the process's Virtual Memory Areas (VMA) and returns a virtual address pointer. **No physical RAM is allocated at this stage** (due to Linux optimistic memory overcommit, governed by `vm.overcommit_memory`). VSZ (Virtual Memory Size) increases by 100MB, but RSS (Resident Set Size) remains unchanged.
> 3. When the process performs its first write to a byte in that range:
>    - The CPU's Memory Management Unit (MMU) attempts to translate the virtual address to a physical address using the Page Table.
>    - Because no physical page frame is mapped, the MMU triggers a **Page Fault Exception (Major or Minor Page Fault)**.
>    - The CPU switches to kernel mode and enters the page fault handler (`do_page_fault`).
>    - The kernel allocates a physical $4\text{KB}$ page frame from the buddy allocator, zeros it out (to prevent data leaks from previous processes), updates the page table entry (PTE), and returns to user space.
>    - RSS now increments by $4\text{KB}$.

---

### Q2: What is the exact difference between a Major Page Fault and a Minor Page Fault, and what is the SRE impact?
> **Deep Answer**:
> - **Minor Page Fault**: Occurs when the page is already in physical memory (e.g. in the Page Cache, or a newly mapped anonymous page that just needs a page table mapping). No disk I/O is required. Resolution takes sub-microseconds ($< 1\mu\text{s}$).
> - **Major Page Fault**: Occurs when the requested page is NOT in physical memory and must be fetched synchronously from disk (e.g. cold binary read, mmap file read, or swapped-out anonymous memory). Disk I/O suspends the process thread. Resolution takes milliseconds ($2–15\text{ms}$).
> - **SRE Impact**: High rates of Major Page Faults (monitored via `sar -B` or `pgfault`/`pgmajfault` in `/proc/vmstat`) indicate active memory thrashing, severe disk I/O bottlenecks, or aggressive swapping, causing catastrophic P99 application latency spikes.

---

### Q3: How does the Linux Out-Of-Memory (OOM) Killer decide which process to kill? How can you protect critical daemons?
> **Deep Answer**:
> 1. When kernel page allocation fails and direct reclaim (`kswapd`) cannot free sufficient memory, `out_of_memory()` is invoked.
> 2. The kernel calculates an `oom_score` (ranging from 0 to 1000) for every candidate process:
>    $$\text{oom\_score} \approx \left(\frac{\text{Process RSS + Swap Pages}}{\text{Total Available RAM}}\right) \times 1000 + \text{oom\_score\_adj}$$
> 3. The process with the highest score receives `SIGKILL` (Exit code 137).
> 4. **Protection**:
>    - Set `/proc/<PID>/oom_score_adj` to `-1000` (e.g. `sshd`, `kubelet`, `containerd`, `systemd-journald`), making them completely immune to OOM kills.
>    - In Kubernetes, Pod QoS class dictates `oom_score_adj`:
>      - **Guaranteed Pods** (`requests == limits`): `oom_score_adj = -997`.
>      - **Burstable Pods** (`requests < limits`): `oom_score_adj = 1000 - (1000 * request_memory / node_capacity)`.
>      - **BestEffort Pods** (no requests/limits): `oom_score_adj = 1000` (killed first).

---

### Q4: Explain the TCP 3-Way Handshake and the role of the SYN Queue vs Accept Queue. What happens when either queue overflows?
> **Deep Answer**:
> - **Step 1**: Client sends `SYN (Seq=x)`.
> - **Step 2**: Server kernel receives SYN, creates an embryonic socket in the **SYN Queue (SYN Backlog)**, and replies with `SYN-ACK (Seq=y, Ack=x+1)`.
> - **Step 3**: Client replies with `ACK (Ack=y+1)`.
> - **Step 4**: Server kernel receives ACK, transitions connection to `ESTABLISHED`, removes it from the SYN Queue, and moves it to the **Accept Queue (Listen Backlog)**. The application process (e.g. NGINX, Go HTTP server) is notified via `epoll` / `kqueue` to call `accept()`.
> - **Queue Overflow Behaviors**:
>   1. **SYN Queue Overflow** (`net.ipv4.tcp_max_syn_backlog`): Incoming SYNs are dropped. If `net.ipv4.tcp_syncookies = 1`, the kernel bypasses the SYN queue by encoding state into the initial sequence number.
>   2. **Accept Queue Overflow** (`net.core.somaxconn` & `listen(backlog)`):
>      - If `net.ipv4.tcp_abort_on_overflow = 0` (default): The server silently drops the client's final ACK packet. The client thinks the connection is established, but the server does not, forcing the client to retransmit or time out.
>      - If `tcp_abort_on_overflow = 1`: The server immediately resets the connection with a `RST` packet.

---

### Q5: What causes sockets to get stuck in `TIME_WAIT` vs `CLOSE_WAIT`? How do you remediate both?
> **Deep Answer**:
> - **`TIME_WAIT`**:
>   - **Who**: Entered by the side that initiates the **active close** (sends the first `FIN`).
>   - **Why**: Stays in `TIME_WAIT` for `2 * MSL` (Maximum Segment Lifetime, 60s in Linux) to ensure:
>     1. Any delayed/duplicate packets in flight from the old connection die before a new connection reuses the same 4-tuple `(SrcIP, SrcPort, DstIP, DstPort)`.
>     2. The final ACK reaches the peer (retransmitting ACK if peer re-sends FIN).
>   - **Remediation**: Not a bug, but can exhaust ephemeral ports under high connection churn. Enable HTTP Keep-Alive connection pooling, enable `net.ipv4.tcp_tw_reuse = 1`, and expand `net.ipv4.ip_local_port_range`.
> - **`CLOSE_WAIT`**:
>   - **Who**: Entered by the **passive closer** upon receiving a `FIN`.
>   - **Why**: The local kernel acknowledged the remote FIN, but the **local application has NOT called `close(fd)`**.
>   - **Remediation**: This is **100% an application bug** (unclosed HTTP response body, leaking connection pool, or deadlocked worker thread). `tcp_tw_reuse` has zero effect on `CLOSE_WAIT`. Profilers and thread dumps must be taken to fix the unclosed file descriptors.

---

### Q6: What is the difference between `epoll` level-triggered (LT) and edge-triggered (ET) modes?
> **Deep Answer**:
> - **Level-Triggered (LT - Default)**: `epoll_wait()` will repeatedly notify the application as long as data remains in the socket read buffer. If the app reads 100 bytes of a 500-byte message, `epoll_wait()` will immediately return again on the next loop.
> - **Edge-Triggered (ET)**: `epoll_wait()` delivers a notification **only when the socket state changes** (e.g. from no data to new data arriving). The application **MUST** read in a non-blocking loop until `read()` returns `EAGAIN` or `EWOULDBLOCK`. If not drained completely, the remaining data will sit unread indefinitely.
> - **Performance**: Edge-triggered reduces spurious wakeups in ultra-high concurrency servers (e.g. NGINX, Envoy), but requires strict non-blocking socket handling.

---

### Q7: Explain CFS CPU Bandwidth Throttling in Kubernetes. Why can an application experience latency spikes even when CPU utilization is 25%?
> **Deep Answer**:
> - Kubernetes CPU limits use Linux CFS (Completely Fair Scheduler) quotas:
>   - Period: `cpu.cfs_period_us` (default $100,000\mu\text{s} = 100\text{ms}$).
>   - Quota: `cpu.cfs_quota_us` (e.g. 2 cores = $200,000\mu\text{s}$ per period).
> - In a multi-threaded application (e.g. Java JVM, Node.js with worker threads, Go with `GOMAXPROCS=8`), if 8 threads consume the 200ms quota within the first 25ms of the 100ms window, the Linux kernel **deschedules and suspends all threads for the remaining 75ms**.
> - Even though Prometheus scrapes average CPU over 1 minute ($25\%$), within individual 100ms periods the app is repeatedly frozen, causing massive P99 and P99.9 latency degradation.
> - **Verification**: `cat /sys/fs/cgroup/cpu/cpu.stat` -> inspect `nr_throttled` and `throttled_time`.
> - **Fix**: Increase CPU quota, set `GOMAXPROCS` to match CPU limit, or remove CPU limits while retaining strict CPU requests.

---

### Q8: What is eBPF and how does it differ from traditional Linux kernel modules (LKMs)?
> **Deep Answer**:
> - **eBPF (Extended Berkeley Packet Filter)**: Allows developers to run sandboxed bytecode inside the Linux kernel at runtime without modifying kernel source code or loading unverified binary modules.
> - **Safety & Verification**:
>   - LKMs run as unrestricted kernel code. A null pointer dereference or infinite loop in an LKM causes a kernel panic (`Kernel Oops`) and crashes the host machine.
>   - eBPF programs pass through an in-kernel **Verifier** that statically analyzes the bytecode to prove it cannot crash the kernel, contains no infinite loops, cannot access unauthorized memory, and always terminates.
>   - eBPF programs run via Just-In-Time (JIT) compilation at native machine speed.
> - **Use Cases in SRE**: High-performance networking (Cilium XDP/socket bypass), zero-code observability (Grafana Beyla, Pixie), and real-time security runtime enforcement (Tetragon, Falco).

---

### Q9: Walk me through what happens when a Linux server executes `strace -p <PID>`. What is the performance penalty?
> **Deep Answer**:
> - `strace` relies on the `ptrace()` system call (`PTRACE_ATTACH` and `PTRACE_SYSCALL`).
> - Every time the traced process executes any system call (e.g. `read`, `write`, `epoll_wait`):
>   1. The kernel pauses the target process before executing the syscall (`sys_enter`).
>   2. The kernel context-switches to `strace` to inspect arguments and registers.
>   3. The kernel executes the syscall.
>   4. The kernel pauses the target process again after execution (`sys_exit`).
>   5. The kernel context-switches back to `strace` to report return value and timing.
> - **Overhead**: System calls incur **$4\times$ to $10\times$ context-switch overhead**. In high-throughput production workloads, running `strace` can degrade application throughput by 50–90%.
> - **Modern Alternative**: Use **`bpftrace` / eBPF tracepoints** (e.g. `tracepoint:raw_syscalls:sys_enter`), which execute in-kernel with $< 1\%$ overhead without stopping the target process.

---

### Q10: What is the Linux Page Cache "Dirty Ratio" and how can it cause sudden 5-second application freezes on database servers?
> **Deep Answer**:
> - When an application writes to a file, Linux writes data to the Page Cache in RAM and marks the pages as "dirty" before asynchronously flushing them to disk via `kswapd` / flush threads.
> - Two critical sysctl knobs govern this:
>   1. `vm.dirty_background_ratio` (default ~10%): Background kernel threads begin flushing dirty pages to disk asynchronously without blocking the application.
>   2. `vm.dirty_ratio` (default ~20%): **Hard synchronous threshold**. If dirty pages reach this percentage of RAM, **all application threads calling `write()` are forced into synchronous disk flush mode**.
> - On servers with 256GB RAM, 20% is 51GB of dirty memory. If a heavy database write surge occurs, once 51GB is hit, the kernel freezes application write threads until tens of gigabytes are flushed to disk, causing multi-second I/O stalls.
> - **Fix**: Lower parameters to absolute byte values on large RAM servers:
>   ```bash
>   sysctl -w vm.dirty_background_bytes=268435456  # 256MB
>   sysctl -w vm.dirty_bytes=1073741824            # 1GB
>   ```

---

### Q11: Explain Linux `nf_conntrack` table mechanics. What happens when it fills up and how do you size it?
> **Deep Answer**:
> - **Mechanism**: `nf_conntrack` stores state for all active Layer 3/4 network flows (NAT, stateful iptables firewalls, kube-proxy). Every connection consumes a 64-bit kernel slab allocation.
> - **The Outage**: When `nf_conntrack_count >= nf_conntrack_max`, the kernel cannot allocate a new tracking record. It silently drops all incoming packets for new connections, printing `nf_conntrack: table full, dropping packet` in `dmesg`.
> - **Sizing Formula**:
>   $$\text{CONNTRACK\_MAX} = \text{RAM (Bytes)} / 16384 / (\text{ARCH} / 32)$$
>   For a 64GB RAM node: set `net.netfilter.nf_conntrack_max = 1048576` and `hashsize = nf_conntrack_max / 8 = 131072`.

---

### Q12: How does the Linux network stack handle hardware interrupts vs SoftIRQs (bottom halves) during a packet flood?
> **Deep Answer**:
> 1. Packet arrives at NIC $\rightarrow$ DMA writes packet to RX ring buffer $\rightarrow$ NIC raises a Hardware Interrupt (IRQ) on a CPU core.
> 2. The CPU hard interrupt handler quickly disables NIC interrupts and schedules a **Software Interrupt (`NET_RX_SOFTIRQ`)** via the NAPI (New API) poll subsystem.
> 3. NAPI polling loop runs in softirq context (`ksoftirqd/X`), pulling batches of packets (up to `net.core.netdev_max_backlog` and `net.core.netdev_budget`) and passing them up the TCP/IP stack.
> 4. **Bottleneck**: If `mpstat -P ALL 1` shows `%soft` pinned at 100% on a single CPU core (e.g. CPU 0), that core is overwhelmed by SoftIRQs.
> 5. **Fix**: Enable **RPS (Receive Packet Steering)** and **RSS (Receive Side Scaling)** to hash flows across all CPU cores (`/sys/class/net/eth0/queues/rx-*/rps_cpus`).

---

### Q13: What is the exact difference between `SIGTERM`, `SIGINT`, `SIGKILL`, and `SIGQUIT` at the kernel and process level?
> **Deep Answer**:
> - `SIGINT` (Signal 2): Generated by terminal (`Ctrl+C`). Can be caught, blocked, or ignored.
> - `SIGTERM` (Signal 15): Polite termination request. Sent by Kubernetes during pod termination (`preStop` / pod drain). The application can catch it, close DB pools, flush logs, and exit cleanly.
> - `SIGKILL` (Signal 9): **Kernel uncatchable override**. The kernel immediately halts the process and reclaims memory/descriptors. The application process code never executes a single instruction after SIGKILL.
> - `SIGQUIT` (Signal 3): Similar to `SIGINT` (`Ctrl+\`), but triggers the kernel to dump a core file (`core.<pid>`) for post-mortem debugging.

---

### Q14: Explain the Linux VFS (Virtual File System) and how Inodes, Dentries, and File Descriptors relate.
> **Deep Answer**:
> - **File Descriptor (FD)**: An integer index in a process's per-process file table pointing to an open file description.
> - **Dentry (Directory Entry)**: In-memory cache linking file path strings (e.g. `/var/log/app.log`) to an Inode number. Speeds up pathname lookups.
> - **Inode (Index Node)**: Filesystem metadata structure containing file size, permissions, owner, timestamps, and block pointers on disk. **Does NOT contain the filename**.
> - **Hard Link vs Symlink**:
>   - Hard link: Multiple dentries pointing to the exact same Inode number (reference count `i_nlink > 1`).
>   - Symlink: A separate Inode whose content is the text path string of another file.

---

### Q15: Why can a disk report "No space left on device" (`ENOSPC`) when `df -h` shows 50% free space?
> **Deep Answer**:
> - Two distinct resources limit Linux filesystems: **Data Blocks** and **Inodes**.
> - If an application generates millions of tiny 0-byte or 100-byte files (e.g. uncleaned PHP session files, unbatched cache tokens), it exhausts the pre-allocated Inode table long before filling disk storage capacity.
> - `df -h` reports data block capacity (e.g. 50% free).
> - `df -i` reports Inode capacity. When `IUse%` reaches 100%, any `creat()`, `open(O_CREAT)`, or `mkdir()` syscall immediately fails with `ENOSPC`.
> - **Remediation**: Find directory with highest inode count: `find / -xdev -printf '%h\n' | sort | uniq -c | sort -k 1 -n` and delete unneeded small files.

---

### Q16: How does Linux handle Swappiness (`vm.swappiness`), and should you disable Swap in Kubernetes?
> **Deep Answer**:
> - **`vm.swappiness` (0 to 100)**: Defines the kernel's relative preference for reclaiming Anonymous memory (via Swap) vs File-backed memory (via Page Cache eviction):
>   $$\text{Ratio} \approx \frac{\text{Reclaim Anonymous}}{\text{Reclaim Page Cache}}$$
> - Setting `vm.swappiness=0` instructs the kernel to avoid swapping anonymous pages unless the system is on the absolute verge of an OOM.
> - **Kubernetes Swap Tradeoff**:
>   - Historically, K8s required `swapoff -a` because the Kubelet couldn't accurately predict or enforce container memory limits if anonymous pages were secretly swapped to disk.
>   - In Kubernetes 1.28+ with cgroups v2, NodeSwap allows `LimitedSwap` where cgroup memory QoS is respected.

---

### Q17: What is Path MTU Discovery (PMTUD), and how do "PMTU Black Holes" cause hanging TCP connections?
> **Deep Answer**:
> - **PMTUD Mechanics**: Sender sets the **DF (Don't Fragment)** bit in the IP header of outbound packets. If a router along the internet path has an MTU smaller than the packet size (e.g. 1420 bytes on a VPN tunnel vs 1500 bytes on Ethernet), it drops the packet and sends back an **ICMP Type 3, Code 4 ("Fragmentation Needed and DF set")** packet containing its MTU.
> - **The Black Hole**:
>   - If an intermediate firewall or security group misconfigures ICMP filtering and drops all incoming ICMP packets, the sender **never receives the fragmentation notification**.
>   - **Symptoms**: Small packets (TCP SYN, ACK, HTTP headers) pass through fine because they are under 1420 bytes. When the server attempts to send the large HTTP response body (1500-byte packets), packets are silently dropped forever. The browser/client hangs indefinitely until timeout.
> - **Remediation**: Enable TCP MSS Clamping on the router/firewall: `iptables -t mangle -A POSTROUTING -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu`.

---

### Q18: What is the difference between Voluntary and Involuntary Context Switches (`pidstat -w`)?
> **Deep Answer**:
> - **Voluntary Context Switches (`cswch/s`)**:
>   - Occurs when a thread **willingly yields the CPU** because it is waiting for an unavailable resource (e.g. blocking on I/O read, mutex lock, sleep, or waiting for network socket).
>   - High voluntary switches = High I/O waiting or lock contention.
> - **Involuntary Context Switches (`nvcswch/s`)**:
>   - Occurs when the Linux CFS scheduler **preempts a running thread** because its allotted CPU time quantum expired or a higher-priority task became runnable.
>   - High involuntary switches = Severe CPU oversubscription (too many active threads fighting for too few physical CPU cores).

---

### Q19: Explain the DNS resolution sequence on Linux. How do `/etc/nsswitch.conf`, `/etc/hosts`, and `systemd-resolved` interact?
> **Deep Answer**:
> 1. When an application calls `getaddrinfo("api.internal")`, the C standard library reads `/etc/nsswitch.conf`.
> 2. The `hosts: files dns` directive instructs glibc to evaluate sources in order:
>    - **`files`**: Inspects `/etc/hosts` for static IP mappings.
>    - **`dns`**: Reads `/etc/resolv.conf` to query upstream recursive nameservers (`nameserver 10.0.0.2` or local `systemd-resolved` stub resolver `127.0.0.53:53`).
> 3. **`systemd-resolved`**: Manages split-DNS across multiple network interfaces, caching TTL responses locally and forwarding queries via DNS-over-TLS if configured.

---

### Q20: What is the difference between Unix Domain Sockets (UDS) and TCP Loopback (`127.0.0.1`) sockets?
> **Deep Answer**:
> - **TCP Loopback (`127.0.0.1:8080`)**:
>   - Traverses the full TCP/IP networking stack (packet encapsulation, checksums, TCP state machine, ACK validation, flow control, and iptables filtering).
> - **Unix Domain Sockets (`/var/run/app.sock`)**:
>   - Bypasses the entire TCP/IP networking stack.
>   - Data is transferred directly between user-space memory buffers in kernel space using memory copies without checksums, sequence numbers, or TCP headers.
>   - Supports passing OS File Descriptors and credentials (`SCM_RIGHTS`) between processes.
>   - **Performance**: UDS achieves **$2\times$ higher throughput and $> 50\%$ lower latency** than TCP loopback.

---

### Q21: What is the Linux "O_DIRECT" flag and why do high-performance databases (Postgres, Cassandra) use it?
> **Deep Answer**:
> - By default, Linux I/O is buffered: `read()` and `write()` copy data through the kernel Page Cache.
> - **Double Buffering Waste**: A database like Postgres maintains its own sophisticated in-memory buffer pool (shared buffers). Using standard OS buffered I/O means pages are stored **twice in RAM** (once in Postgres shared buffers and once in the Linux Page Cache).
> - **`O_DIRECT`**: Instructs the kernel to bypass the Page Cache entirely. I/O transfers data directly between user-space memory buffers and the block storage device via DMA.
> - Prevents Page Cache churn from evicting hot application cache pages.

---

### Q22: How do you trace dropped network packets on a live Linux server without running high-overhead packet captures?
> **Deep Answer**:
> 1. **`dropwatch`**:
>    ```bash
>    dropwatch -l kas
>    ```
>    Monitors the kernel `kfree_skb` tracepoint and outputs the exact kernel function address where packets are being dropped (e.g. `tcp_v4_rcv`, `ip_error_handler`, `nf_hook_slow`).
> 2. **`perf` Kernel Tracepoint**:
>    ```bash
>    perf record -g -a -e skb:kfree_skb sleep 5
>    perf script
>    ```
>    Prints the exact stack trace leading up to every dropped packet.
> 3. **`nstat` / `netstat -s`**:
>    ```bash
>    nstat -z | grep -iE 'drop|overflow|listen'
>    ```
>    Displays real-time hardware and protocol drop counters.

---

### Q23: Compare TCP Congestion Control algorithms: CUBIC vs Google BBR (Bottleneck Bandwidth and RTT).
> **Deep Answer**:
> - **Loss-Based (CUBIC - Traditional Linux Default)**:
>   - Assumes **Packet Loss = Congestion**.
>   - Aggressively grows congestion window ($cwnd$) until a packet is dropped, then slashes $cwnd$ by 30–50%.
>   - **The Bufferbloat Problem**: Fills up intermediate router buffers, inflating RTT latency across high-bandwidth long-distance fiber routes before dropping packets.
> - **Model-Based (Google BBR)**:
>   - Measures **max bandwidth** and **minimum RTT** continuously without relying on packet loss.
>   - Keeps the in-flight data volume matched to the physical **Bandwidth-Delay Product (BDP)**:
>     $$\text{BDP} = \text{Bottleneck Bandwidth} \times \text{Min RTT}$$
>   - **Performance**: Provides **$2\times$ to $10\times$ higher throughput** on lossy networks (e.g. cross-region cloud interconnections with 1% packet loss) and prevents bufferbloat.
>   - **Enable in Linux**: `sysctl -w net.ipv4.tcp_congestion_control=bbr`.

---

### Q24: How do the 7 Linux Namespaces isolate processes in container runtimes (`runc` / `containerd`)?
> **Deep Answer**:
> 1. **`pid`**: Isolates process IDs (container process sees itself as PID 1).
> 2. **`net`**: Isolates network devices, routing tables, IP addresses, and firewall iptables.
> 3. **`mnt`**: Isolates filesystem mount points (provides rootfs overlay).
> 4. **`ipc`**: Isolates System V IPC and POSIX message queues.
> 5. **`uts`**: Isolates hostname and NIS domain name.
> 6. **`user`**: Maps container UID 0 (root) to an unprivileged high UID (e.g. UID 100001) on the host for rootless containers.
> 7. **`cgroup`**: Isolates visibility of the cgroup root hierarchy.
> - **System Call**: Created via `clone(flags)` or `unshare(CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS)`.

---

### Q25: What are Transparent HugePages (THP) and why do in-memory databases (Redis, MongoDB) mandate disabling THP?
> **Deep Answer**:
> - Standard Linux page size is $4\text{KB}$. **HugePages** allocates $2\text{MB}$ or $1\text{GB}$ pages to reduce CPU Translation Lookaside Buffer (TLB) cache misses.
> - **THP (Transparent HugePages)** attempts to merge 4KB pages into 2MB huge pages automatically in the background.
> - **Why Redis / MongoDB Stalls with THP**:
>   - During background snapshotting (`BGSAVE` in Redis), the process forks using Copy-On-Write (COW).
>   - When a single 10-byte key is written, instead of duplicating a tiny 4KB page, the Linux kernel is forced to **allocate and copy an entire 2MB HugePage**, dramatically inflating memory usage and causing multi-millisecond write stalls.
> - **Remediation**: `echo never > /sys/kernel/mm/transparent_hugepage/enabled`.

---

### Q26: How do you interpret Linux Block Layer I/O statistics (`iostat -xz 1`)? Explain `await`, `r_await`, `w_await`, and `%util`.
> **Deep Answer**:
> - **`r/s` and `w/s`**: Read and Write IOPS (I/O requests per second).
> - **`rKB/s` and `wKB/s`**: Read/Write Throughput in KB/s.
> - **`aqu-sz` (Average Queue Size)**: Number of I/O requests queued waiting for the storage controller. An `aqu-sz > 1.0` indicates queuing.
> - **`await` (Total Latency)**: Average time (in milliseconds) for I/O requests to complete (includes time spent waiting in queue + physical disk service time).
> - **`r_await` vs `w_await`**: Isolates whether storage latency is driven by slow read operations or slow disk write flush operations.
> - **`%util` (Device Saturation)**: Percentage of time the block device was actively processing work. If `%util` reaches 100% and `await` climbs, the storage device is completely saturated.

---

### Q27: How does Linux TCP Window Auto-Tuning work? How do you calculate optimal `tcp_rmem` and `tcp_wmem`?
> **Deep Answer**:
> - **Bandwidth-Delay Product (BDP)**: The maximum amount of unacknowledged data in-flight required to saturate a network link:
>   $$\text{BDP (Bytes)} = \frac{\text{Bandwidth (bps)} \times \text{Round-Trip Time (s)}}{8}$$
> - **Example**: 10 Gbps Direct Connect link between US and Europe ($\text{RTT} = 80\text{ms}$):
>   $$\text{BDP} = \frac{10 \times 10^9 \times 0.080}{8} = 100,000,000\text{ Bytes} \approx 100\text{ MB}$$
> - If `net.ipv4.tcp_rmem` max window is capped at the default 4MB, maximum throughput across that 10G link will be artificially choked to only $400\text{ Mbps}$!
> - **Tuning**:
>   ```bash
>   sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728" # Max 128MB
>   sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"
>   ```

---

### Q28: What is NUMA (Non-Uniform Memory Access) and how does NUMA node pinning prevent latency degradation in multi-socket servers?
> **Deep Answer**:
> - In multi-socket enterprise servers (e.g. dual Intel Xeon / AMD EPYC), each CPU socket is directly connected to its own local bank of physical RAM (a **NUMA Node**).
> - **Remote Memory Access Penalty**:
>   - If CPU Core on Socket 0 accesses RAM attached to Socket 1, the memory request must traverse the inter-socket interconnect (Intel UPI / AMD Infinity Fabric), adding **$30–50\%$ memory latency**.
> - **SRE Mitigation**:
>   - In Kubernetes, configure the **Kubelet Topology Manager** with `single-numa-node` policy: pins high-performance workloads (e.g. database pods, vLLM inference) so that all container CPU threads and RAM pages are allocated strictly from the **same local NUMA node**.

---

### Q29: What is the difference between a Zombie Process (`Z` state) and an Orphan Process? How does PID 1 reap them?
> **Deep Answer**:
> - **Zombie Process (`Z` state in `ps`)**:
>   - A process that has terminated (`exit()`), freed its memory and descriptors, but **remains in the process table** because its parent process has not yet called `wait()` or `waitpid()` to read its exit status.
>   - **Impact**: Consumes zero RAM/CPU, but leaks a Process ID (PID). A flood of un-reaped zombies exhausts the kernel PID table (`/proc/sys/kernel/pid_max`), preventing any new processes from spawning.
> - **Orphan Process**:
>   - A running process whose parent process terminates before the child.
>   - The Linux kernel automatically re-parents orphan processes to **PID 1 (`systemd` / init container)**. PID 1 registers a `SIGCHLD` handler to continuously call `waitpid()` to reap child zombies immediately.

---

### Q30: How do you detect and fix UDP packet drops on high-throughput streaming and DNS servers?
> **Deep Answer**:
> 1. **Detection**:
>    ```bash
>    netstat -su | grep -iE 'receive errors|buffer errors|packet receive errors'
>    # Or:
>    nstat -z | grep -i 'UdpRcvbufErrors'
>    ```
> 2. **Root Cause**: Unlike TCP (which has flow control and ACK retries), UDP packets are dropped instantly if the socket receive buffer (`SO_RCVBUF`) is full when a new packet arrives.
> 3. **Remediation**:
>    - Increase default and maximum OS socket receive buffers:
>      ```bash
>      sysctl -w net.core.rmem_max=268435456 # 256MB
>      sysctl -w net.core.rmem_default=33554432 # 32MB
>      ```
>    - Configure multi-threaded packet polling using `SO_REUSEPORT` on the DNS/UDP listener application so multiple worker threads drain the socket queue in parallel.
