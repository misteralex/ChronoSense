# ChronoSense: Pipeline Injection Strategy

---

Executive Summary: The ChronoSense Strategy

This document defines the ChronoSense Injection Strategy, a hybrid framework designed to bridge the gap between static code analysis and real-time observability. Unlike traditional monitoring, ChronoSense does not merely log data; it identifies and instrumentates the "neural centers" of a C-based application (such as Nginx) through a deterministic 7-step pipeline.

The strategy is built on three core pillars:

- Contextual Intelligence: By combining Clang-based AST analysis with Perf dynamic profiling, the pipeline identifies functions that are not only structurally complex but also operationally critical in real-world execution scenarios.

- AI-Enhanced Quantization: The system leverages Groq’s high-speed inference to move beyond simple heuristics. AI-driven sensitivity analysis ensures that the most "information-dense" variables are prioritized for monitoring.

- Agnostic Decoupling: Through an automated injection process, the monitor remains decoupled from the source code. It uses an 8x8 matrix of agnostic probes, ensuring zero-copy data transfer and minimal overhead on the target system’s performance.

- This pipeline ensures that every probe injected is mathematically justified, architecturally significant, and optimized for high-performance Edge environments.

---

## Phase 1: Contextual & Structural Mapping

### Step 1: Node Mapping & Ranking (`cs_step1_node_map_sealed.py`)
The pipeline begins by scanning the target source code (e.g., Nginx) using the Clang AST (Abstract Syntax Tree).
- **Function Discovery:** Identifies all functions, signatures, and locations.
- **Structural Metrics:** Calculates Cyclomatic Complexity (CCN), call counts, and reference counts.
- **Initial Ranking:** Assigns a `final_score` to each function based on its "operational mass"—rewarding logical complexity and connectivity.

### Step 2: Logical Aggregation (`cs_step2_logical_map_sealed.py`)
To prevent statistical fragmentation, physical functions spread across different files are consolidated.
- **Name-Based Clustering:** Groups functions with identical names into a single **Logical Node**.
- **Dual Identity:** Maintains a mapping between the physical implementation and the logical monitor entity.

---

## Phase 2: Variable Analysis & Weighting

### Step 3: Active Variable Extraction (`cs_step3_active_vars_sealed.py`)
Deep analysis of the variables within the certified nodes.
- **Filtering:** Automatically discards trivial iterators (e.g., `i`, `j`, `rc`).
- **Typing & Scoring:** Detects data types (structs, pointers, primitives). Pointers and complex structures receive higher "interest" scores.

### Step 4: Hierarchical Quantization (`cs_step4_final_quantization_sealed.py`)
Normalizes the importance of variables to ensure a balanced monitoring distribution.
- **Percent Rank:** Applies a hierarchical weight ranging from **0.15 to 0.95**.
- **Quantization:** Categorizes variables into HIGH, MID, and LOW priority buckets, ensuring the monitor focuses on the most impactful data points.

---

## Phase 3: Topological Selection & Cataloging

### Step 5: Topological Delta T (`cs_step5_topological_dt_sealed.py`)
Identifies critical pairs for Differential Tracking (DT).
- **Divergence Algorithm:** Uses Levenshtein distance on function signatures to find the 4 pairs of nodes with the highest logical divergence.
- **Significance Score:** Ensures that the selected DT pairs are architecturally relevant for detecting drifts.

### Step 6: Agnostic Catalog Generation (`cs_step6_agnostic_group_generator.py`)
Organizes the 64 best candidates into a structured format.
- **8x8 Architecture:** Maps variables into 8 groups of 8 probes each.
- **Macro Assignment:** Generates agnostic names (e.g., `CS_G0_P0_NODE_A`) to decouple the monitor logic from the source code.

---

## Phase 4: Execution & Injection

### Step 7: Automated Injector (`cs_step7_injector.py`)
The final operational act where the theory meets the code.
- **Pilot Project Creation:** Clones the source into a dedicated lab environment (`nginx-cs-lab`).
- **Interface Generation:** Creates `cs_interface.h`, mapping agnostic macros to real Shared Memory IDs.
- **Physical Injection:** Uses regex to insert probe macros directly into the function entry points and manages `#include` dependencies.

---

## Quality Assurance: The Integrity Pipeline
All steps are governed by `cs_test_pipeline.py`, which validates:
- **Population:** No empty tables or missing nodes.
- **Variety:** No hierarchical collapse (ensuring scores are diverse).
- **Mapping:** Total synchronization between the database and the injected macros.
<br></br>
# ChronoSense: Pipeline Injection Strategy

This document outlines the end-to-end automated workflow (Step 1 to Step 7) used by ChronoSense to transform raw C source code into a statistically monitored system. The pipeline integrates static analysis, dynamic profiling, hierarchical quantization assisted by AI, and automated code injection.

---

## Phase 1: Contextual, Structural & Dynamic Mapping

### Step 1: Node Mapping & Ranking (`cs_step1_node_map_sealed.py`)
The pipeline begins by scanning the target source code using the Clang AST (Abstract Syntax Tree).
- **Function Discovery:** Identifies all functions, signatures, and locations.
- **Structural Metrics:** Calculates Cyclomatic Complexity (CCN), call counts, and reference counts.
- **Initial Ranking:** Assigns a `final_score` based on "operational mass"—rewarding logical complexity and connectivity.

### Step 2: Logical Aggregation & Dynamic Sync (`cs_step2_logical_map_sealed.py`)
To prevent statistical fragmentation, physical functions are consolidated into **Logical Nodes**.
- **Perf Integration:** The static analysis is now integrated with dynamic profiling data from **Perf**. This ensures that the consolidation reflects actual runtime behavior and operative function usage within the specific project scenarios hosting ChronoSense.
- **Dual Identity:** Maintains a mapping between the physical implementation and the logically aggregated entity, validated by real-world execution paths.

---

## Phase 2: Variable Analysis & AI-Enhanced Weighting

### Step 3: Active Variable Extraction (`cs_step3_active_vars_sealed.py`)
Deep analysis of the variables within the certified nodes.
- **Filtering:** Automatically discards trivial iterators (e.g., `i`, `j`, `rc`).
- **Typing & Scoring:** Detects data types (structs, pointers, primitives). Pointers and complex structures receive higher "interest" scores.

### Step 4: Hierarchical Quantization & AI Sensitivity (`cs_step4_final_quantization_sealed.py`)
Normalizes the importance of variables to ensure a balanced monitoring distribution.
- **Groq AI Support:** The quantization process is enhanced by **Groq**, which provides high-speed AI inference to identify highly sensitive variables within functions that static heuristics might overlook.
- **Percent Rank:** Applies a hierarchical weight ranging from **0.15 to 0.95**.
- **Quantization:** Categorizes variables into HIGH, MID, and LOW priority buckets based on combined structural and AI-driven sensitivity metrics.

---

## Phase 3: Topological Selection & Cataloging

### Step 5: Topological Delta T (`cs_step5_topological_dt_sealed.py`)
Identifies critical pairs for Differential Tracking (DT).
- **Divergence Algorithm:** Uses Levenshtein distance on function signatures to find the 4 pairs of nodes with the highest logical divergence.
- **Significance Score:** Ensures that the selected DT pairs are architecturally relevant for detecting drifts.

### Step 6: Agnostic Catalog Generation (`cs_step6_agnostic_group_generator.py`)
Organizes the 64 best candidates into a structured format.
- **8x8 Architecture:** Maps variables into 8 groups of 8 probes each.
- **Macro Assignment:** to minitor logic using a probe (e.g., `CS_P0_NODE_A`).

---

## Phase 4: Execution & Injection

### Step 7: Automated Injector (`cs_step7_injector.py`)
The final operational act where the theory meets the code.
- **Pilot Project Creation:** Clones the source into a dedicated lab environment.
- **Interface Generation:** Creates `cs_interface.h`, mapping agnostic macros to real Shared Memory IDs.
- **Physical Injection:** Uses regex to insert probe macros directly into the function entry points and manages `#include` dependencies.

---

## Quality Assurance: The Integrity Pipeline
All steps are governed by `cs_test_pipeline.py`, which validates:
- **Population:** No empty tables or missing nodes.
- **Variety:** No hierarchical collapse (ensuring scores are diverse).
- **Mapping:** Total synchronization between the database, dynamic profiles, and the injected macros.

---
*ChronoSense: Native Intelligence, Deterministic Resilience. Developed by Alex FARACI*