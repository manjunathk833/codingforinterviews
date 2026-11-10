---
slug: cs-04-concurrency-mutexes-and-lock-free-cas
course_id: 08-core-cs-internals
track: core-cs
volume: "08. Core CS: OS, Networking & Storage"
module_number: 1
module_title: "Module 1: Kernel Memory, Concurrency & Network Wire Internals"
chapter_number: 4
level_tag: "Senior → Staff Systems"
title: "Hardware Concurrency: MESI Cache Coherency, Memory Barriers, Deadlocks & Lock-Free CAS"
summary: "From CPU store buffers, MESI cache-line false sharing (64B), and Java/C++ happens-before fences to Coffman's 4 Deadlock conditions, Linux futexes, lock-free CAS loops, and the ABA problem."
reading_time_minutes: 23
visualizer_id: "cs-concurrency-epoll-cas"
lab_path: "frameworks/sdet-system-design/01-distributed-concurrency-isolation"
tags: ["core-cs", "concurrency", "mesi", "memory-barriers", "deadlock", "lock-free", "cas", "false-sharing"]
---

# Hardware Concurrency: MESI Cache Coherency, Memory Barriers, Deadlocks & Lock-Free CAS

```json pretraining
[
  {
    "term": "MESI & 64B False Sharing",
    "formula": "CacheLine = 64 Bytes (Modified/Exclusive/Shared/Invalid)",
    "meaning": "CPUs coherence-lock entire 64-byte L1 cache lines—never single variables! Two threads mutating adjacent independent 8-byte longs ping-pong the same cache line across cores."
  },
  {
    "term": "Happens-Before Fence (`volatile`)",
    "formula": "Store-Release ≺ Load-Acquire",
    "meaning": "Prevents compiler & CPU store-buffer instruction reordering so all writes prior to a `volatile` write are guaranteed visible after another thread's `volatile` read."
  },
  {
    "term": "Coffman's 4 Deadlock Conditions",
    "formula": "Mutex ∧ Hold&Wait ∧ NoPreempt ∧ CircularWait",
    "meaning": "Deadlock occurs iff ALL 4 hold simultaneously; imposing a strict global lock-acquisition order (`id(L1) < id(L2)`) mathematically eliminates Circular Wait."
  },
  {
    "term": "CAS & The ABA Problem",
    "formula": "CAS(ptr, A → B → A) ⇒ Versioned Stamp (ptr, stamp+1)",
    "meaning": "Hardware `LOCK CMPXCHG` checks only if memory equals `A`, missing that `A` was freed, recycled, and reallocated; solved by `AtomicStampedReference`."
  }
]
```

```json poe
{
  "question": "In Java (or C++ without `std::atomic`), Thread 1 executes `config = loadConfig(); ready = true;` where `ready` is a plain non-`volatile` `boolean`, while Thread 2 spins on `while (!ready) {}` and then calls `config.port()`. How can Thread 2 crash with a `NullPointerException` or infinite loop in production even on x86_64?",
  "options": [
    "Booleans occupy 9 bytes on 64-bit CPUs, causing torn reads",
    "Without a `volatile` / Acquire-Release happens-before memory barrier, the JIT compiler legally hoists `!ready` out of the `while` loop (`if (!ready) while(true){}` -> infinite spin!) AND may reorder writes/reads so `ready = true` becomes visible before `config`'s fields finish initializing!",
    "Only ARM CPUs ever reorder instructions; JIT compilers never hoist reads",
    "Adding `Thread.yield()` inside the loop establishes a full JMM happens-before edge"
  ],
  "answerIndex": 1,
    "explanation": "Even on x86's strong Total Store Order (TSO) hardware, the JVM C2 JIT compiler legally hoists plain non-volatile loop-invariant reads into a CPU register forever and reorders non-volatile stores! Declaring `volatile boolean ready` emits both compiler barriers and hardware store-load fences."
}
```

## Part I — Silicon Reality: Store Buffers, `MESI` & `64-Byte` False Sharing

Software engineers often imagine multi-core CPUs reading and writing directly to a single shared RAM array. In physical silicon, a RAM fetch costs $\sim 80\text{ ns}$ ($\sim 250$ clock cycles), whereas an L1 cache hit costs $\sim 1\text{ ns}$ ($3–4$ cycles). Each core therefore sits behind a private **Store Buffer** + **L1/L2 Cache** synchronized via the **`MESI` (`Modified`, `Exclusive`, `Shared`, `Invalid`)** coherence protocol at **$64\text{-byte}$ Cache-Line granularity** (`128B` on Apple Silicon M-series!).

Two subtle hardware traps immediately emerge:
1. **Visibility & Reordering Bugs**: Core 0 writes `ready = true` into its local **Store Buffer** before invalidation ACKs return, or the JIT compiler reorders independent memory operations unless constrained by **`Acquire` / `Release` / `SeqCst` (`volatile`) Memory Barriers**.
2. **False Sharing ($10\times$ Throughput Collapse)**: Suppose `WorkerStats` stores `volatile long worker0Count` and `volatile long worker1Count` side-by-side (`16` bytes total). Both variables land inside **the exact same $64\text{-byte}$ L1 cache line**! Every increment by Core 0 broadcasts an `Invalidate` message stalling Core 1's L1 cache—destroying scalability even though the two threads touch **zero logically shared variables**! Padding each counter to its own `64B`/`128B` cache line (`@Contended` in JVM / `LongAdder` striped cells / `alignas(64)` in C++) restores linear multi-core scaling.

```mermaid
flowchart LR
  Uncontended["Uncontended Lock / Atomic"] -->|User-Space CAS (~5ns)| Fast["Fast Path: Zero Syscall (Linux Futex / Atomic)"]
  Uncontended -->|CAS Contention| Spin["Adaptive Short Spin / Striped Cells (LongAdder)"]
  Spin -->|Sustained Contention| Kernel["Slow Path: futex(FUTEX_WAIT) Park Thread (~2µs)"]
  Kernel -->|Lock Order id_A < id_B| Safe["Deadlock-Free Wakeup (FUTEX_WAKE)"]
```

---

## Part II — Mutexes (`futex`), Deadlock Prevention & Lock-Free `CAS` (`ABA`)

1. **How Modern Mutexes (`pthread_mutex`, JVM `synchronized` / `ReentrantLock`) Actually Work**: They do **not** trap into the Linux kernel on uncontended calls! A **Linux `futex` (*Fast Userspace Mutex*)** executes a single user-space atomic `CAS` (`0 -> 1`, $\sim 5\text{ ns}$); it invokes the `sys_futex` kernel syscall to park the OS thread **only when contention actually occurs**.
2. **Eliminating Deadlocks Deterministically**: Coffman proved a deadlock requires **all 4 conditions** (*Mutual Exclusion*, *Hold-and-Wait*, *No Preemption*, *Circular Wait*). When transferring funds between `Account A` and `Account B`, locking `(from, to)` deadlocks the instant Thread 1 transfers `A -> B` while Thread 2 transfers `B -> A`. Breaking **Circular Wait** by always acquiring locks sorted by canonical ID (`min(idA, idB)` then `max(idA, idB)`) makes deadlocks **mathematically impossible**!
3. **Lock-Free `Compare-And-Swap` (`CAS`) & The `ABA` Trap**: Hardware `CMPXCHG` atomically updates `*addr = newVal` iff `*addr == expected`. In a lock-free Treiber stack (`Top -> A -> B`), if Thread 1 reads `Top = A` (with `next = B`) and pauses while Thread 2 pops `A`, pops `B`, and pushes a recycled node at address `A` (`Top -> A -> C`), Thread 1's `CAS(Top, A, B)` **succeeds**—pointing `Top` at freed/corrupted node `B`! Attaching a monotonic **version stamp** `(ptr, stamp)` (`AtomicStampedReference`) turns `A@v1` into `A@v3`, defeating `ABA` completely.

```json contrast
{
  "title": "High-Concurrency Shared State Engineering (32 Cores)",
  "naiveTitle": "Coarse `synchronized` / Ad-Hoc Dual Locks",
  "naiveMetric": "Deadlocks on Bi-Directional Calls · 12x Cache Stall",
  "naivePoints": [
    "Acquires locks in caller-argument order lock(from) -> lock(to), deadlocking under A<->B transfers",
    "Packs 32 worker progress counters into a contiguous `long[32]` array (severe 64B False Sharing!)",
    "Uses broken Double-Checked Locking (`if (inst == null)`) without declaring the reference `volatile`",
    "Shares a single `AtomicLong` under 64-core contention, causing 95% CAS retry spin waste"
  ],
  "staffTitle": "Canonical Lock Ordering + Striped `LongAdder` + Stamped CAS",
  "staffMetric": "Zero Deadlocks · Linear 32-Core Scaling",
  "staffPoints": [
    "Enforces global total order on multi-lock acquisition (`accountA.id < accountB.id`) + bounded `tryLock`",
    "Uses JVM `LongAdder` (striped `@Contended` 64B-padded cells) instead of single-hotspot `AtomicLong`",
    "Enforces strict JMM Happens-Before visibility via `final` immutable records or `volatile` references",
    "Pairs lock-free pointer CAS structures with monotonic epoch/version stamps (`AtomicStampedReference`)"
  ]
}
```

### Concurrency Primitive Trade-Off Matrix

| Primitive | Uncontended Cost | High-Contention (32-Core) Behavior | Starvation / Liveness | Ideal Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Mutex / `ReentrantLock`** | $\sim 5–15\text{ ns}$ (Userspace futex CAS) | Kernel context-switch queueing ($\sim 1.5–3\ \mu\text{s}$) | Blocking (convoying if lock-holder hits GC/page fault) | Multi-variable invariant updates, I/O guards |
| **Single `AtomicLong` (`CAS` loop)** | $\sim 5\text{ ns}$ | **Degrades** due to MESI cache-line ping-pong + retry spins | Lock-free (at least 1 thread advances per cycle) | Low-to-moderate contention sequence generators, flags |
| **Striped `LongAdder`** | $\sim 5\text{ ns}$ | **Scales linearly** across 64+ cores (hashes threads to padded cells) | Wait-free / Lock-free | High-throughput telemetry counters, request metrics (`sum()` sums cells) |
| **Read-Write / `StampedLock`** | $\sim 10\text{ ns}$ (Optimistic read: $1\text{ ns}$!) | Zero cache invalidation across concurrent readers | Optimistic read requires `validate(stamp)` | Read-dominated (`99%` read) routing tables & config caches |

---

## Part III — Production Implementation Blueprints (Python 3 & Java 17)

### Python 3 Blueprint: Canonical Total-Order Multi-Lock Transfer (Deadlock-Free!)
```python
from dataclasses import dataclass, field
import threading


@dataclass
class BankAccount:
    account_id: str
    balance_cents: int
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


def transfer_deadlock_free(source: BankAccount, dest: BankAccount, amount_cents: int) -> bool:
    """
    Breaks Coffman's Circular-Wait condition by acquiring locks in strict lexicographical account_id order.
    Concurrent transfer(A, B) and transfer(B, A) BOTH lock min(A,B) first, then max(A,B) — 0% deadlock!
    """
    if source.account_id == dest.account_id:
        return amount_cents >= 0

    first, second = (
        (source, dest) if source.account_id < dest.account_id else (dest, source)
    )
    with first.lock:
        with second.lock:
            if source.balance_cents < amount_cents:
                return False
            source.balance_cents -= amount_cents
            dest.balance_cents += amount_cents
            return True
```

### Java 17 Blueprint: ABA-Safe Versioned `AtomicStampedReference` Stack & Deadlock-Free Lock Order
```java
import java.util.concurrent.atomic.AtomicStampedReference;

public final class LockFreeStampedStack<E> {
    private record Node<E>(E item, Node<E> next) {}

    // Pairs top pointer with a monotonically increasing integer stamp to defeat ABA!
    private final AtomicStampedReference<Node<E>> top = new AtomicStampedReference<>(null, 0);

    public void push(E item) {
        int[] stampHolder = new int[1];
        while (true) {
            Node<E> oldHead = top.get(stampHolder);
            int oldStamp = stampHolder[0];
            Node<E> newHead = new Node<>(item, oldHead);
            if (top.compareAndSet(oldHead, newHead, oldStamp, oldStamp + 1)) {
                return;
            }
        }
    }

    public E pop() {
        int[] stampHolder = new int[1];
        while (true) {
            Node<E> oldHead = top.get(stampHolder);
            int oldStamp = stampHolder[0];
            if (oldHead == null) {
                return null;
            }
            if (top.compareAndSet(oldHead, oldHead.next(), oldStamp, oldStamp + 1)) {
                return oldHead.item();
            }
        }
    }
}
```

> [!WARNING]
> **Staff Interview Gotcha — Why Broken Double-Checked Locking (`Singleton`) Fails Without `volatile` AND What CPython's `GIL` Does NOT Protect**:
> 1. In Java, `instance = new Helper()` compiles into `(a) alloc memory`, `(b) run constructor`, `(c) assign pointer to instance`. Without `private static volatile Helper instance`, `(b)` and `(c)` can reorder—so Thread 2 sees `instance != null` and reads half-initialized zeroed fields!
> 2. In CPython, developers falsely assume *"The GIL makes Python dictionaries/counters thread-safe."* The GIL only protects internal C reference counts between bytecodes—`counter += 1` (`LOAD_FAST`, `BINARY_ADD`, `STORE_FAST`) can be preempted mid-bytecode, losing increments without `threading.Lock`!

---

## Part IV — End-of-Chapter Mastery Check

```json quiz
[
  {
    "id": "cs-04-q1",
    "question": "Two threads run on separate CPU cores: Thread 0 increments `stats.slot0` in a tight loop while Thread 1 increments `stats.slot1`. Neither thread ever touches the other's variable, yet throughput drops 9x compared to local stack variables! What hardware mechanism caused this, and how do you fix it?",
    "options": [
      "TLB page-table exhaustion; solved by enabling swap",
      "False Sharing across a single 64-byte L1 MESI cache line: because `slot0` and `slot1` sit within the same 64B cache line, every store by Core 0 invalidates Core 1's L1 cache line; solved by 64B/128B cache-line padding (`@Contended` or `LongAdder`)",
      "Coffman Circular Wait deadlock",
      "Branch prediction flush caused by UTF-8 encoding"
    ],
    "answerIndex": 1,
    "explanation": "MESI cache coherence operates on 64-byte (or 128-byte) cache lines, not individual 8-byte longs. Co-locating independent hot-write counters forces continuous cross-core L1 invalidation traffic."
  },
  {
    "id": "cs-04-q2",
    "question": "Which of Coffman's 4 necessary Deadlock conditions is broken when you enforce a strict global ordering (`lock(minId)` before `lock(maxId)`) across all multi-resource transactions?",
    "options": [
      "Mutual Exclusion",
      "Circular Wait — because a directed dependency cycle `T1 -> T2 -> ... -> T1` cannot exist on a strict total order (`id_1 < id_2 < ... < id_1` is impossible!)",
      "No Preemption",
      "Memory Alignment"
    ],
    "answerIndex": 1,
    "explanation": "A cycle in a wait-for graph would imply an entity ID is strictly less than itself—a mathematical contradiction—making deadlocks impossible without giving up mutual exclusion."
  },
  {
    "id": "cs-04-q3",
    "question": "What is the 'ABA Problem' in lock-free Compare-And-Swap (`CAS`) algorithms, and how does `AtomicStampedReference` prevent it?",
    "options": [
      "Two threads have names starting with 'A' and 'B'",
      "Memory at a target address changes from A to B and back to A (e.g., a popped node's address is recycled while another thread's interior `next` pointer is stale), tricking a plain value-only `CAS(expected=A)` into succeeding; pairing the pointer with a monotonic version stamp `(A, v1) != (A, v3)` causes the stale CAS to fail safely",
      "CAS instructions fail whenever integers are negative",
      "Lock-free queues reverse FIFO order into LIFO"
    ],
    "answerIndex": 1,
    "explanation": "Monotonic version/epoch tagging ensures that even if the exact same pointer/value A reappears, the incremented stamp exposes the intermediate state mutations."
  }
]
```
