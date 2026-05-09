# 🛡️ ChronoSense Overview

This document defines the ChronoSense Injection Strategy, a hybrid framework designed to bridge the gap between static code analysis and real-time observability. Unlike traditional monitoring, ChronoSense does not merely log data; it identifies and instrumentates the "neural centers" of a C-based application (such as Nginx) through a deterministic pipeline.

## Current strategy:

- Contextual Intelligence: By combining Clang-based AST analysis with Perf profiling, the pipeline identifies functions that are both structurally complex and operationally critical. AI-Enhanced Quantization leverages Groq’s high-speed inference to prioritize "information-dense" variables for monitoring. This work is currently a work in progress; the `cs_catalog.json` acts as an initial roadmap for further Perf explorations. 

- Agnostic Decoupling: Through an automated injection process, the monitor remains decoupled from the source code. At this stage, the **8 probes** have been manually inserted into the host source code to guide the final automation.

## 🛰️ Chronosense: Technical Core & Statistical Monitoring

>ChronoSense is a developer-centric telemetry framework designed for direct embedding into a host application's lifecycle via targeted probes on critical functions. Unlike external observers, ChronoSense operates internally, providing high-fidelity statistical oversight with negligible overhead. The current implementation utilizes four pairs of probes, enabling simultaneous monitoring of state variables and the execution timing (Delta-T) between capture points.

- Direct Source-Level Integration
Chronosense is not a sidecar process; it is a deeply integrated library.
- Host Embedding: The library is installed directly into the host project (e.g., Nginx) via the cs_interface.h header.
- Virtual Patching: Probes are injected into the source code as macros. This allows the compiler to optimize the monitoring code alongside the business logic, often resulting in "zero-cost" abstractions.
- Atomic Shared Memory: Data is moved from the host application to the Chronosense core via a specialized Shared Memory (SHM) area. This ensures that the monitor and the host are decoupled in terms of execution but tightly coupled in terms of data visibility.

## Technical Summary: The Mathematical Engine
The system establishes a behavioral baseline during a Warm-up period (typically 60 samples).

The architecture is built upon three mathematical pillars and a mapping entity:
- Welford’s Method (Slow Baseline): Computes mean and variance in a single pass (recursive). It represents the system's deep, historical memory.
- EMA - Exponential Moving Average (Fast Baseline): A reactive filter that tracks present fluctuations. It represents the system's immediate reflex.
- Z-Score (Normalizer): Converts the deviation between the EMA and Welford’s baseline into a universal unit of measurement ($\sigma$). This allows for the comparison of physically different signals (e.g., volts, degrees, bars) on a standardized scale.

  | Z-Score Value | System State | TensorFlow Action |
  | :--- | :--- | :--- |
  | **< 0.50** | Optimal / Nominal | Stable Training Phase |
  | **0.50 - 1.50** | Network/Load Fluctuation | Bias Monitoring |
  | **> 3.00** | Anomaly / Packet Loss | Data Alignment Intervention |

> Statistics is not merely a module within ChronoSense: it is its central nervous system. For a client, this must be presented as the filter that transforms data chaos into actionable business decisions.

#### Core Expectations & System Characteristics

- Drift Detection: By comparing real-time DT signatures against the statistical mean, Chronosense can detect "micro-anomalies"—small timing drifts that often precede catastrophic failures or resource exhaustion.
- Statistical Sentinel Characteristics
Non-Blocking Telemetry: All probe operations are lock-free and atomic, ensuring the host application's concurrency model is never compromised.
- High-Frequency Sampling: Optimized for Edge environments where sub-millisecond precision is required to capture transient state changes.
- Deterministic Reliability: Because the probes are part of the compiled binary, the monitoring is deterministic; if the code runs, the telemetry is guaranteed to fire.

## Summary of Impact
- Memory Footprint: Fixed and pre-allocated SHM.
- Performance: Sub-1% CPU Impact (Zero-cost abstraction via -O3 inlining).
- Deployment: Direct injection into the build system (e.g., make, cmake).

### Strategic Note: 
Chronosense transitions the host project from a "black box" to a self-aware system capable of reporting its own internal statistical health.

---
<br></br>
# Data Repository & Simulation Output (/data)

- `src/`: Contains the core C/C++ implementation and the strategic interface.
- `tools/`: A full suite of automation scripts (Step 1-7) for static analysis, AI-driven quantization (Groq), and automated code injection.
- `docs/`: Detailed documentation including the pipeline_injection_strategy.md, which defines the mathematical and AI-driven logic behind probe placement.
- `data/`: Serves as the Statistical Repository of the Chronosense framework. It contains the raw and processed datasets generated during simulation and stress-test cycles, stored in the high-performance Apache Parquet format.
  
  The `data/` directory contains the analytical output of the system in Apache Parquet format:
    - `chronosense-normal.parquet`: Baseline signatures representing healthy system states.
    - `chronosense-stress.parquet` / `chronosense-noisy.parquet`: Data captured during high-load and interference scenarios to calibrate anomaly detection thresholds.
- `tests/`: Validation Sandbox where the Chronosense library meets the host application (i.e. `nginx`). It is designed not just to test the library in isolation, but to verify the integrity of the integrated system after the injection process.

---

# Documentation & Artifacts Registry
The repository includes a comprehensive set of documents and POC evidences:

- `architecture.md`: Technical details on the C++ core and IPC mechanisms ([System Architecture](docs/architecture.md))

- `pipeline_injestion_strategy.md`: Detailed guide on the 7-step analysis and injection process (Clang AST, Perf, and Groq AI). ([Pipeline Injection Stategy](docs/pipeline_injection_strategy.md))

- `interface_and_strategic_overview.md`: Documentation for developers on using the library interface. ([Interface and Strategic Overviewy](docs/interface_and_strategic_overview.md))

- `artifacts/`: Contains the cs_catalog.json mapping and the Nginx-CS-Patch (the actual modified source files like ngx_http_core_module.c).

  - **Demos: Video evidence (.mp4)**
 showing the system detecting drifts in "Normal" vs "Noisy/Stress" scenarios.
    - cs_demo_normal_scenario_with_optimization.mp4
    - cs_demo_normal_scenario.mp4
    - cs_demo_noisy_stress_scenario.mp4

  - **Demos: Virtual Patches (.c)**

    - docs / artifacts / ngx_http_core_module.c <br> `CS_P0_NODE_A`
    - docs / artifacts / ngx_http_index_module.c <br> `CS_P0_NODE_B` <br></br>

    - docs / artifacts / ngx_rbtree.c <br> `CS_P1_NODE_A`
    - docs / artifacts / ngx_http_rewrite_module.c <br> `CS_P1_NODE_B` <br></br>

    - docs / artifacts / ngx_epoll_module.c <br> `CS_P2_NODE_A`
    - docs / artifacts / ngx_http_log_module.c <br> `CS_P2_NODE_B` <br></br>

    - docs / artifacts / ngx_open_file_cache.c 
      <br> `CS_P3_NODE_A` <br> `CS_P3_NODE_B`

<br></br>
## 📂 ChronoSense - Full Device Tree

```
.
├── data/                                   # High-fidelity datasets (Parquet format)
│   ├── chronosense-demo.parquet            # Consolidated sample for quick analysis
│   ├── chronosense-noisy.parquet           # Jitter and noise simulation metrics
│   ├── chronosense-normal.parquet          # Baseline operational telemetry
│   └── chronosense-stress.parquet          # Edge-case high-concurrency results
│
├── docs/                                   # Technical specifications & IP documentation
│   ├── architecture.md                 
│   ├── pipeline_injection_strategy.md
│   ├── interface_and_strategic_overview.md
│   └── artifacts/                          # Validation proofs and binary patches
│       ├── cs_catalog.json                 # Data discovery & profiling metadata
│       ├── cs_demo_noisy_stress.mp4        # Visual proof: Stress scenario stability
│       ├── cs_demo_normal.mp4              # Visual proof: Standard operation
│       ├── cs_demo_optimized.mp4           # Performance comparison: O0 vs O3 Fusion
│       └── nginx-cs-patch/                 # Instrumented Nginx core modules
│           ├── ngx_epoll_module.c          # Event-loop level telemetry injection
│           └── ngx_http_core_module.c      # Request lifecycle atomic hooks
│
├── tools/                                  # System orchestration & benchmarking
│   ├── cs-build-host-project.sh            # Automated Build & Binary Fusion orchestrator
│   ├── cs_demo_host_nginx.py               # Locust-based performance test suite
│   ├── cs_trace.py                         # Real-time visualization for probes and statistics
│   └── cs_cleanup.py                       # System V IPC & Shared Memory sanitizer
│
└── src/                                    # Core ChronoSense Engine (Proprietary)
    ├── core      
    │   └── cs_core.c                       # Atomic implementation & SHM logic
    └── include
        ├── cs_core.h                       # Internal engine definitions
        └── cs_interface.h                  # Public API / Contract for host integration
```
---

## POC Limitations:

Some core implementation files are provided as headers-only or stubs to protect proprietary atomic synchronization logic.

Performance benchmarks are verified using the full binary fusion build (see video demo).

---

*ChronoSense: Native Intelligence, Deterministic Resilience. Developed by Alex FARACI*

---

## ⚖️ License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for the full text.