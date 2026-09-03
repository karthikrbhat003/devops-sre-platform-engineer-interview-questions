# 💻 Systems Coding & Automation: Exhaustive Interview Question Bank (Top 30 Questions)

> **Target Level**: Senior / Staff SRE & Platform Engineer (6.5+ YoE)  
> **Evaluation Focus**: Go concurrency primitives (Goroutines, Channels, Select, Mutexes, Context), Python memory optimization, thread-safe data structures, and SRE algorithm design.

---

### Q1: Explain how Go channels work under the hood. What causes a goroutine to block, deadlock, or leak on channel operations?
> **Deep Answer**:
> - **Internal `hchan` Struct**:
>   - In the Go runtime, a channel is represented by the `hchan` struct in heap memory, containing:
>     1. `qcount`: Number of items currently in the circular buffer.
>     2. `dataqsiz`: Buffer capacity (0 for unbuffered).
>     3. `buf`: Pointer to the circular ring buffer array.
>     4. `recvq` & `sendq`: Linked lists of waiting goroutines (`sudog` structs).
>     5. `lock`: Internal `mutex` protecting all channel operations.
> - **Blocking & Scheduling (`gopark`)**:
>   - When a goroutine sends on a full channel or reads from an empty channel:
>     - The Go runtime creates a `sudog` representing the current goroutine and enqueues it into `sendq` or `recvq`.
>     - It calls `gopark()`, which changes the goroutine state from `_Grunning` to `_Gwaiting` and context-switches the OS thread (M) to execute other runnable goroutines without blocking the OS thread.
> - **Deadlocks & Leaks**:
>   - **Deadlock**: Occurs when all active goroutines in the program enter `_Gwaiting` on channels or mutexes, leaving no goroutine to send/receive. The runtime panics with `fatal error: all goroutines are asleep - deadlock!`.
>   - **Goroutine Leak**: Occurs when a goroutine sends to an unbuffered channel that has no receiver, or waits on a channel that is never closed/cancelled. Leaked goroutines remain in memory forever, causing gradual RAM exhaustion.
>   - **Prevention**: Always bind goroutine lifecycles to a `context.Context` and handle `<-ctx.Done()`.

---

### Q2: What is the difference between `sync.Mutex` and `sync.RWMutex` in Go, and when should you avoid `RWMutex`?
> **Deep Answer**:
> - **`sync.Mutex`**:
>   - Exclusive lock. Only one goroutine can hold the lock at any time (for both read and write operations).
> - **`sync.RWMutex`**:
>   - Readers-Writer lock. Multiple reader goroutines can hold `RLock()` simultaneously. Only a writer requiring `Lock()` acquires exclusive access.
> - **When to Avoid `RWMutex`**:
>   - `RWMutex` has higher internal CPU overhead (atomic operations on reader counts).
>   - If the workload has a high write ratio ($> 10–20\%$ writes) or critical sections are extremely short ($< 100\text{ns}$), a standard `sync.Mutex` is significantly faster.
>   - High reader contention on `RWMutex` can cause cache-line bouncing on multi-core CPUs. For ultra-high read throughput with rare writes, use **`atomic.Pointer` / Copy-On-Write (COW)** patterns.

---

### Q3: How do you parse and aggregate multi-gigabyte log files in Python without causing Out-Of-Memory (OOM) crashes?
> **Deep Answer**:
> 1. **Generator Streaming ($O(1)$ RAM)**:
>    - Never use `file.read()` or `file.readlines()`, which load the entire file into RAM.
>    - Use Python generator expressions to stream line by line:
>      ```python
>      def stream_lines(filename):
>          with open(filename, "r", encoding="utf-8") as f:
>              for line in f:
>                  yield line
>      ```
> 2. **Heap-Based Top-K Aggregation ($O(K)$ Memory)**:
>    - Use `heapq.nlargest()` or a min-heap of size $K$ to maintain the top $K$ slowest endpoints or largest consumers, avoiding the need to sort billions of records in memory.
> 3. **Avoid Object Overhead with Slots**:
>    - If parsing millions of structured records, use `__slots__` on data classes or named tuples to eliminate the default `__dict__` memory overhead (~$150\text{ bytes} \rightarrow 40\text{ bytes}$ per record).

---

### Q4: Implement a thread-safe Token Bucket Rate Limiter algorithm. Explain the refill formula.
> **Deep Answer**:
> - **Core Formula**:
>   $$\text{Current Tokens} = \min(\text{Capacity}, \text{Previous Tokens} + (\text{Current Time} - \text{Last Refill Time}) \times \text{Refill Rate})$$
> - **Thread-Safe Implementation**:
>   ```python
>   import time
>   import threading
>   
>   class TokenBucket:
>       def __init__(self, capacity: int, refill_rate: float):
>           self.capacity = float(capacity)
>           self.refill_rate = refill_rate
>           self.tokens = float(capacity)
>           self.last_refill = time.time()
>           self.lock = threading.Lock()
>   
>       def allow_request(self, tokens: int = 1) -> bool:
>           with self.lock:
>               now = time.time()
>               elapsed = now - self.last_refill
>               self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
>               self.last_refill = now
>               
>               if self.tokens >= tokens:
>                   self.tokens -= tokens
>                   return True
>               return False
>   ```

---

### Q5: How do you design an $O(1)$ Least Recently Used (LRU) Cache? Explain why a Doubly Linked List + Hash Map is required.
> **Deep Answer**:
> - **Data Structure Requirements**:
>   1. `get(key)` in $O(1)$ time.
>   2. `put(key, value)` in $O(1)$ time.
>   3. Eviction of least recently used item in $O(1)$ time.
> - **Why Hash Map Alone Fails**: A Hash Map provides $O(1)$ lookup, but cannot maintain chronological usage order in $O(1)$.
> - **Why Array / Singly Linked List Alone Fails**: Finding or moving an item in an array takes $O(N)$ time due to element shifting. In a singly linked list, deleting a node requires finding its predecessor ($O(N)$).
> - **The Combined Solution**:
>   - **Hash Map**: Maps `key -> DoublyLinkedListNode` for $O(1)$ direct access.
>   - **Doubly Linked List**: Has `prev` and `next` pointers. Removing any node is strictly $O(1)$:
>     ```python
>     node.prev.next = node.next
>     node.next.prev = node.prev
>     ```
>   - Adding the node to the front (Most Recently Used) is $O(1)$.
>   - Evicting the tail node (Least Recently Used) is $O(1)$.

---

### Q6: Explain the Go Memory Model and Escape Analysis. What causes a variable to escape from the stack to the heap?
> **Deep Answer**:
> - **Stack vs Heap**:
>   - Stack allocations are ultra-fast ($< 1\text{ns}$, pointer bump) and automatically reclaimed when the function returns.
>   - Heap allocations require global allocator lock/mcache, pointer tracking, and trigger Garbage Collector (GC) pauses.
> - **Escape Triggers**:
>   1. **Returning Pointers**: Returning a reference to a local struct from a function:
>      ```go
>      func createServer() *Server { return &Server{} } // Escapes to heap!
>      ```
>   2. **Passing to `interface{}`**: Calling `fmt.Println(x)` or converting concrete types to interfaces forces heap allocation.
>   3. **Dynamic Slices**: Slices whose size is not known at compile time or slice appends that exceed stack frame limits ($> 64\text{KB}$).
> - **Inspection**: Run `go build -gcflags="-m -m"` to view compiler escape analysis decisions.

---

### Q7: How does Go Garbage Collection work (Tricolor Mark-and-Sweep)? How do you tune GC overhead?
> **Deep Answer**:
> - **Concurrent Tricolor Mark-and-Sweep**:
>   - **White**: Unvisited objects (candidate garbage).
>   - **Grey**: Visited objects whose child pointers haven't been scanned.
>   - **Black**: Visited objects and all child references verified alive.
>   - Runs concurrently alongside application goroutines with sub-millisecond Stop-The-World (STW) pauses using a **Write Barrier**.
> - **Tuning with `GOGC` and `GOMEMLIMIT` (Go 1.19+)**:
>   - `GOGC=100` (default): Triggers GC when heap size doubles (100% growth).
>   - `GOMEMLIMIT=4GiB`: Sets a soft memory cap. The GC runs more frequently as memory approaches 4GB, preventing container OOM kills while minimizing GC CPU overhead under normal memory conditions.

---

### Q8: How do you implement a Graceful Cancellation Pipeline in Go using `context.WithCancel` and `sync.WaitGroup`?
> **Deep Answer**:
> ```go
> func ProcessPipeline(ctx context.Context, jobs <-chan Job) error {
>     g, ctx := errgroup.WithContext(ctx)
>     for i := 0; i < 5; i++ {
>         g.Go(func() error {
>             for {
>                 select {
>                 case <-ctx.Done():
>                     return ctx.Err()
>                 case job, ok := <-jobs:
>                     if !ok { return nil }
>                     if err := executeJob(ctx, job); err != nil {
>                         return err // Cancels context for all other sibling goroutines!
>                     }
>                 }
>             }
>         })
>     }
>     return g.Wait()
> }
> ```

---

### Q9: What is the Python GIL (Global Interpreter Lock), and how do you achieve true multi-core concurrency in Python?
> **Deep Answer**:
> - **The GIL**: A mutex in CPython that prevents multiple native OS threads from executing Python bytecodes simultaneously (protects CPython memory management and reference counting).
> - **Multi-Threading Limitation**: Python `threading` is effective ONLY for I/O-bound tasks (network calls, disk reads where threads release the GIL). For CPU-bound tasks (compression, hashing), Python multi-threading is slower than single-threading due to lock contention!
> - **True Multi-Core Concurrency**:
>   1. **`multiprocessing` / ProcessPoolExecutor**: Spawns separate OS processes with isolated memory spaces and separate GILs.
>   2. **C/Rust Extensions (PyO3 / Cython)**: Offloads heavy computation to native C/Rust functions that explicitly release the GIL (`Py_BEGIN_ALLOW_THREADS`).

---

### Q10: How does Python `asyncio` Event Loop work compared to Go Goroutines?
> **Deep Answer**:
> - **Python `asyncio` (Cooperative Multitasking - Single-Threaded)**:
>   - Single OS thread runs an event loop.
>   - Coroutines must explicitly yield control using `await`. If a blocking sync function (`time.sleep()` or heavy loop) runs without `await`, **the entire event loop freezes**, stalling all other concurrent tasks.
> - **Go Goroutines (Preemptive Multitasking - M:N Scheduler)**:
>   - $M$ user-space goroutines multiplexed across $N$ OS kernel threads.
>   - The Go runtime scheduler automatically preempts tight loops and non-cooperative goroutines at function prologue / safe points (preemptive scheduling).

---

### Q11: How do you solve the "Dependency Graph Resolution" problem (Topological Sort) for a microservice build system?
> **Deep Answer**:
> - **Kahn's Algorithm ($O(V + E)$)**:
>   1. Compute in-degree (number of incoming dependencies) for every service node.
>   2. Enqueue all nodes with in-degree `0` (services with zero dependencies) into a queue.
>   3. While queue is not empty:
>      - Pop service $U$, append to build sequence.
>      - For every service $V$ depending on $U$: decrement in-degree of $V$. If in-degree becomes `0`, enqueue $V$.
>   4. If visited count $\ne$ total services: **Cyclic Dependency Detected!**

---

### Q12: How do you design a sliding window counter algorithm for DDoS rate limiting in Redis?
> **Deep Answer**:
> - **Redis Sorted Set (ZSET) Sliding Window**:
>   - Key: `rate:<ip>`
>   - Member: Unique UUID / Timestamp
>   - Score: Current Unix Timestamp in milliseconds
> - **Multi-Command Transaction (Lua Script / Pipeline)**:
>   ```lua
>   local key = KEYS[1]
>   local now = tonumber(ARGV[1])
>   local window = tonumber(ARGV[2])
>   local limit = tonumber(ARGV[3])
>   
>   -- 1. Remove old timestamps outside current sliding window
>   redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
>   
>   -- 2. Count requests in window
>   local current_requests = redis.call('ZCARD', key)
>   
>   if current_requests < limit then
>       redis.call('ZADD', key, now, now .. '-' .. math.random())
>       redis.call('EXPIRE', key, math.ceil(window / 1000))
>       return 1 -- Allowed
>   else
>       return 0 -- Throttled
>   end
>   ```

---

### Q13: What is the difference between Shallow Copy vs Deep Copy in Python, and how does it cause memory corruption bugs?
> **Deep Answer**:
> - **Shallow Copy (`copy.copy()`)**:
>   - Creates a new outer collection object, but inserts references to the *same child objects* found in the original.
>   - Mutating a nested list or dict in the copy **silently mutates the original object**, causing dangerous race conditions and data corruption across concurrent requests.
> - **Deep Copy (`copy.deepcopy()`)**:
>   - Recursively copies all parent and nested objects into completely independent memory allocations.

---

### Q14: How do you write a thread-safe Singleton in Go using `sync.Once`?
> **Deep Answer**:
> ```go
> type DatabasePool struct {
>     conn *sql.DB
> }
> 
> var (
>     instance *DatabasePool
>     once     sync.Once
> )
> 
> func GetDatabasePool() *DatabasePool {
>     once.Do(func() {
>         // Thread-safe: Guaranteed to execute exactly once across all goroutines
>         instance = &DatabasePool{conn: initDB()}
>     })
>     return instance
> }
> ```

---

### Q15: How do you implement an Exponential Backoff and Jitter algorithm in Go?
> **Deep Answer**:
> ```go
> func RetryWithBackoff(ctx context.Context, fn func() error) error {
>     base := 100 * time.Millisecond
>     max := 5 * time.Second
>     for attempt := 0; attempt < 5; attempt++ {
>         err := fn()
>         if err == nil { return nil }
>         
>         // Full Jitter Formula: sleep = random(0, min(max, base * 2^attempt))
>         backoff := time.Duration(float64(base) * math.Pow(2, float64(attempt)))
>         if backoff > max { backoff = max }
>         jitter := time.Duration(rand.Int63n(int64(backoff)))
>         
>         select {
>         case <-time.After(jitter):
>         case <-ctx.Done():
>             return ctx.Err()
>         }
>     }
>     return errors.New("max retries exceeded")
> }
> ```

---

### Q16: Explain Python Context Managers (`__enter__` and `__exit__`) and how to build one with `@contextlib.contextmanager`.
> **Deep Answer**:
> ```python
> from contextlib import contextmanager
> import time
> 
> @contextmanager
> def measure_latency(operation_name: str):
>     start = time.perf_counter()
>     try:
>         yield # Code inside 'with' block executes here
>     finally:
>         duration = time.perf_counter() - start
>         print(f"[{operation_name}] Duration: {duration:.4f}s")
> 
> # Usage:
> with measure_latency("DatabaseQuery"):
>     execute_heavy_sql()
> ```

---

### Q17: How do you implement a Bounded Priority Queue in Python using `heapq`?
> **Deep Answer**:
> ```python
> import heapq
> from typing import Any
> 
> class BoundedPriorityQueue:
>     def __init__(self, max_size: int):
>         self.max_size = max_size
>         self.heap = [] # Min-heap stores (-priority, item)
> 
>     def push(self, priority: int, item: Any):
>         if len(self.heap) < self.max_size:
>             heapq.heappush(self.heap, (priority, item))
>         else:
>             # If incoming priority is higher than lowest priority in heap
>             heapq.heappushpop(self.heap, (priority, item))
> 
>     def pop(self):
>         return heapq.heappop(self.heap)[1]
> ```

---

### Q18: What is Go `select` statement mechanics? What happens when multiple channel cases are ready simultaneously?
> **Deep Answer**:
> - **`select` Mechanics**:
>   - Evaluates all channel send and receive expressions.
>   - If one case is ready, it executes that case.
>   - If none are ready and a `default` case exists, it executes `default` (non-blocking channel poll).
>   - If none are ready and no `default` exists, the goroutine enters `_Gwaiting` on all channels.
> - **Uniform Pseudo-Random Selection**:
>   - If **multiple cases are ready simultaneously**, Go **does NOT evaluate top-to-bottom**. It picks a case using a **uniform pseudo-random number generator** to prevent channel starvation.

---

### Q19: How do you safely serialize and deserialize JSON without reflection overhead in Go (EasyJSON / Sonic)?
> **Deep Answer**:
> - Standard `encoding/json` uses runtime reflection (`reflect.TypeOf`), which incurs high CPU overhead and memory allocations in high-throughput microservices.
> - **High-Performance Alternatives**:
>   - **`mailru/easyjson`**: Pre-generates type-specific serialization code ahead of time (zero reflection).
>   - **`bytedance/sonic`**: Uses JIT assembly generation at runtime using AVX/SIMD CPU instructions.
>   - **Performance**: Sonic/EasyJSON parses JSON **$3\times$ to $5\times$ faster** with 80% fewer heap allocations.

---

### Q20: How do you build a CLI tool in Go with Cobra/Viper supporting subcommands, environment variable overrides, and auto-completion?
> **Deep Answer**:
> 1. **Cobra**: Structure root command and subcommands (`deploy`, `rollback`, `status`).
> 2. **Viper**: Binds CLI flags (`--region`), configuration files (`config.yaml`), and environment variables (`APP_REGION` via `viper.AutomaticEnv()`).
> 3. **Flag Priority Precedence (Strict Standard)**:
>    $$\text{CLI Flag} > \text{Environment Variable} > \text{Config File} > \text{Default Value}$$
> 4. **Shell Completion**: Implement `rootCmd.GenBashCompletion(os.Stdout)` for instant tab auto-completion in bash/zsh.

---

### Q21: How does the Go Race Detector (`go test -race`) work under the hood? What is the performance overhead?
> **Deep Answer**:
> - **ThreadSanitizer (TSan) Engine**:
>   - Instruments every memory read and write instruction at compile time.
>   - Allocates **Shadow Memory**: Maps every 8-byte application memory chunk to several shadow memory words storing `(ThreadID, Epoch, Write/Read flag)`.
> - **Detection Rule**:
>   - If two goroutines access the same memory location concurrently without a synchronized happens-before relationship, and at least one is a write $\rightarrow$ **DATA RACE DETECTED**.
> - **Overhead**: Incurs **$2\times$ to $10\times$ CPU slowdown and $5\times$ to $20\times$ memory increase**. Never run with `-race` in production.

---

### Q22: Explain Python's Garbage Collection: Reference Counting vs Generational Cycle Detector.
> **Deep Answer**:
> 1. **Reference Counting (Immediate)**:
>    - Every Python object has an `ob_refcnt` header. Incremented on assignment; decremented on `del` or scope exit. When `ob_refcnt == 0`, memory is instantly reclaimed.
> 2. **The Cyclic Reference Problem**:
>    - If Object A references Object B, and Object B references Object A, their reference counts never drop to 0, creating a permanent memory leak.
> 3. **Generational Garbage Collector (`gc`)**:
>    - Inspects objects in 3 generations (Gen 0, Gen 1, Gen 2).
>    - Runs cyclic graph traversal to detect unreachable isolated reference loops and free them.
>    - **Optimization**: For latency-critical Python workers, tune thresholds with `gc.set_threshold(700, 10, 10)` or run `gc.disable()` during active request handling.

---

### Q23: Implement a Thread-Safe In-Memory Key-Value Store with TTL expiration in Go.
> **Deep Answer**:
> ```go
> type Item struct {
>     value     interface{}
>     expiresAt time.Time
> }
> 
> type MemoryCache struct {
>     sync.RWMutex
>     items map[string]Item
> }
> 
> func NewMemoryCache(cleanupInterval time.Duration) *MemoryCache {
>     c := &MemoryCache{items: make(map[string]Item)}
>     go func() {
>         for range time.Tick(cleanupInterval) {
>             c.Lock()
>             now := time.Now()
>             for k, v := range c.items {
>                 if now.After(v.expiresAt) { delete(c.items, k) }
>             }
>             c.Unlock()
>         }
>     }()
>     return c
> }
> 
> func (c *MemoryCache) Set(key string, val interface{}, ttl time.Duration) {
>     c.Lock()
>     defer c.Unlock()
>     c.items[key] = Item{value: val, expiresAt: time.Now().Add(ttl)}
> }
> ```

---

### Q24: Explain the Go Interface Trap: Why does `var err *MyError = nil; err != nil` evaluate to `true`?
> **Deep Answer**:
> - **Internal `iface` Representation**:
>   - In Go runtime, an interface value is a pair of pointers: `(type, data)`.
>   - An interface is strictly `nil` **ONLY if BOTH `type == nil` AND `data == nil`**.
> - **The Trap**:
>   - When assigning a typed `nil` pointer (`var customErr *CustomError = nil`) to an `error` interface:
>   - The interface `type` is set to `*CustomError`, while `data` is `nil`.
>   - Checking `if err != nil` evaluates to **`true`** because the type pointer is non-nil!
> - **Fix**: Always return the explicit untyped `nil` from functions: `return nil`.

---

### Q25: How do Python processes communicate via `multiprocessing.shared_memory` with zero serialization overhead?
> **Deep Answer**:
> - Traditional `multiprocessing.Queue` pickles and unpickles data over POSIX pipes, adding massive CPU and serialization latency for multi-megabyte NumPy arrays.
> - **`multiprocessing.shared_memory` (Python 3.8+)**:
>   - Allocates a POSIX shared memory block (`/dev/shm`).
>   - Both worker processes map the shared memory buffer directly into their virtual address spaces.
>   - Reads and writes occur at native RAM speed with **zero copies and zero pickling overhead**.

---

### Q26: How do you build a custom Prometheus Exporter in Go using `client_golang`?
> **Deep Answer**:
> ```go
> var (
>     httpDuration = prometheus.NewHistogramVec(
>         prometheus.HistogramOpts{
>             Name:    "app_http_request_duration_seconds",
>             Help:    "HTTP request latency distribution",
>             Buckets: prometheus.DefBuckets,
>         },
>         []string{"path", "method", "status"},
>     )
> )
> 
> func init() {
>     prometheus.MustRegister(httpDuration)
> }
> 
> func InstrumentMiddleware(next http.Handler) http.Handler {
>     return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
>         start := time.Now()
>         next.ServeHTTP(w, r)
>         httpDuration.WithLabelValues(r.URL.Path, r.Method, "200").Observe(time.Since(start).Seconds())
>     })
> }
> ```

---

### Q27: How do you build a high-concurrency TCP Reverse Proxy with connection pooling in Go?
> **Deep Answer**:
> - Use `net.Dialer` with `KeepAlive: 30s` and `sync.Pool` for byte copying:
>   ```go
>   func handleConnection(clientConn net.Conn, targetAddr string) {
>       defer clientConn.Close()
>       backendConn, err := net.DialTimeout("tcp", targetAddr, 2*time.Second)
>       if err != nil { return }
>       defer backendConn.Close()
>       
>       // Bidirectional Zero-Copy Splice
>       go io.Copy(backendConn, clientConn)
>       io.Copy(clientConn, backendConn)
>   }
>   ```

---

### Q28: LeetCode SRE Pattern: Find Median of Two Sorted Arrays in $O(\log(\min(M,N)))$ for distributed latency metrics.
> **Deep Answer**:
> - **Binary Search on Partition Point**:
>   - Partition smaller array $A$ at index $i$ and larger array $B$ at index $j = (M + N + 1)/2 - i$.
>   - Validate partition: $\max(A_{\text{left}}, B_{\text{left}}) \le \min(A_{\text{right}}, B_{\text{right}})$.
>   - If $A_{\text{left}} > B_{\text{right}}$, move search left; else move right.
>   - Median is $\max(A_{\text{left}}, B_{\text{left}})$ (for odd total) or average of max-left and min-right (for even total).

---

### Q29: Compare `sync/atomic` operations vs `sync.Mutex`. How does CPU Cache Coherence (MESI) impact latency?
> **Deep Answer**:
> - **`sync.Mutex`**: Incurs OS context-switch overhead if lock contention occurs.
> - **`sync/atomic` (e.g. `atomic.AddInt64`)**:
>   - Uses CPU hardware instructions (`LOCK CMPXCHG` on x86).
>   - Does not context-switch threads ($< 5\text{ns}$ latency).
> - **MESI Protocol Cache-Line Bouncing**:
>   - If 32 CPU cores all call `atomic.AddInt64` on the same 64-bit integer, the cache line containing that integer is repeatedly invalidated across all CPU L1/L2 caches, causing bus saturation.
>   - **Remediation**: Use per-CPU striped counters (Counter Sharding) and sum across shards periodically.

---

### Q30: How do you configure a production-grade resilient HTTP Client in Go?
> **Deep Answer**:
> ```go
> var ResilientClient = &http.Client{
>     Timeout: 10 * time.Second,
>     Transport: &http.Transport{
>         DialContext: (&net.Dialer{
>             Timeout:   2 * time.Second,
>             KeepAlive: 30 * time.Second,
>         }).DialContext,
>         MaxIdleConns:        1000,
>         MaxIdleConnsPerHost: 100,
>         IdleConnTimeout:     90 * time.Second,
>         TLSHandshakeTimeout: 2 * time.Second,
>         ForceAttemptHTTP2:   true,
>     },
> }
> ```
> - Prevents socket exhaustion, connection leaks, and thread starvation under high traffic.
