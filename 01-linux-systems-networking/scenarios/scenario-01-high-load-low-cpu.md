# 💥 Scenario 1: High Load Average with Low CPU Utilization

> **Interview Prompt**:  
> *"You receive an alert that a production payment processing server running on AWS EC2 has a 1-minute Load Average of 48.0 on an 8-core instance. However, Prometheus metrics show total CPU utilization is only 12%. The application is experiencing severe latency spikes. Walk me through how you isolate and fix this issue."*

---

## 1. Initial Assessment & Mental Model

- **Load Average Definition in Linux**: In Linux, load average counts both:
  1. **Runnable tasks (R state)**: Waiting for CPU or running on CPU.
  2. **Uninterruptible sleep tasks (D state)**: Waiting for hardware/kernel events, predominantly disk I/O, network file systems (NFS/EFS), or kernel mutex locks.
- **Hypothesis**: Since CPU is only 12%, the load is almost certainly driven by **tasks trapped in uninterruptible sleep (`D` state)** due to I/O bottlenecks or storage lock contention.

---

## 2. Step-by-Step Diagnostic Walkthrough

### Step 1: Confirm Task States
```bash
# Check running vs blocked processes
vmstat 1 5
```
- Look at the `r` (runnable) vs `b` (blocked / uninterruptible sleep) columns:
  - If `b` = 45 and `r` = 2, it confirms 45 processes are waiting on I/O or kernel locks.

### Step 2: Identify the Processes in `D` State
```bash
ps -eo state,pid,user,cmd | grep "^D"
```
- Outputs the exact PIDs and binary names stuck waiting for I/O.

### Step 3: Check Disk I/O & Storage Saturation
```bash
iostat -xz 1 5
```
- Key metrics to inspect:
  - `%util`: If close to 100%, the disk queue is completely saturated.
  - `await` / `r_await` / `w_await`: If average I/O latency is > 50–100ms, the storage subsystem is throttling.
  - Check AWS EBS volume status for **EBS Volume IOPS Burst Balance / Throughput exhaustion**.

### Step 4: Trace What System Call is Blocking
```bash
# Trace system call execution times of one of the blocked processes
strace -p <PID> -T -e trace=file,desc
```
- Common findings:
  - `write()` / `fsync()` blocking for hundreds of milliseconds.
  - Read/write calls to an NFS/EFS mount that has disconnected or reached metadata IOP limits.

### Step 5: Check Kernel Page Cache Dirty Pages
```bash
cat /proc/meminfo | grep -iE 'Dirty|Writeback'
```
- If `Dirty` memory is high and equals `vm.dirty_ratio`, all application writes are forced into **synchronous writeback mode**, stalling every write call.

---

## 3. Remediation & Long-Term Fixes

1. **Immediate Mitigation**:
   - If EBS throughput is throttled: Upgrade EBS volume type from `gp2` to `gp3` (provision higher IOPS and Throughput dynamically via AWS CLI without downtime).
   - If stuck on stale NFS mount: Force unmount (`umount -l /mnt/nfs`) or restart the storage broker.
2. **Kernel Parameter Tuning**:
   ```bash
   # Lower dirty ratio to trigger background flushing earlier before blocking app threads
   sysctl -w vm.dirty_background_ratio=5
   sysctl -w vm.dirty_ratio=10
   ```
3. **Application & Architectural Fix**:
   - Convert synchronous disk logging to asynchronous buffered ring-buffer logging.
   - Offload heavy disk operations to dedicated worker queues backed by local NVMe instance store or S3.
