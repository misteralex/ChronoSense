/*
 * Copyright 2026 Alex FARACI
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @file cs_interface.h
 * @brief ChronoSense POC Final Interface.
 * * Provides macros and function declarations for non-invasive monitoring 
 * of critical variables and execution timing (Differential Tracking).
 */

#ifndef _CS_INTERFACE_H_INCLUDED_
#define _CS_INTERFACE_H_INCLUDED_

#include <stdint.h>
#include <stddef.h>

/**
 * @brief Agnostic Data Transfer - Zero-Copy Version macro.
 * * @param id       Probe slot index (0-7).
 * @param var_ptr  Address of the variable to monitor.
 * @param size     Size of the data (using sizeof).
 * @param pair_id  Differential Tracking pair ID (0-3).
 */
#define CS_UPDATE(id, var_ptr, size, pair_id) \
    cs_var_transfer((id), (const void *)(var_ptr), (size), (pair_id))

/**
 * @brief Core function for transferring probe data to shared memory.
 * * @param shm_idx      Shared memory slot index.
 * @param source_addr  Pointer to the source variable.
 * @param size         Data size in bytes.
 * @param pair         Differential Tracking pair identifier.
 */
void cs_var_transfer(uint32_t shm_idx, const void *source_addr, size_t size, uint8_t pair);

/* -------------------------------------------------------------------------- */
/* Differential Tracking: Node A/B Definitions for 4 Monitoring Pairs         */
/* -------------------------------------------------------------------------- */

/** @name Pair 0 - Temporal Anchor */
/**@{*/
#define CS_P0_NODE_A(ptr, size)  CS_UPDATE(0, ptr, size, 0)
#define CS_P0_NODE_B(ptr, size)  CS_UPDATE(1, ptr, size, 0)
/**@}*/

/** @name Pair 1 - Temporal Anchor */
/**@{*/
#define CS_P1_NODE_A(ptr, size)  CS_UPDATE(2, ptr, size, 1)
#define CS_P1_NODE_B(ptr, size)  CS_UPDATE(3, ptr, size, 1)
/**@}*/

/** @name Pair 2 - Temporal Anchor */
/**@{*/
#define CS_P2_NODE_A(ptr, size)  CS_UPDATE(4, ptr, size, 2)
#define CS_P2_NODE_B(ptr, size)  CS_UPDATE(5, ptr, size, 2)
/**@}*/

/** @name Pair 3 - Temporal Anchor */
/**@{*/
#define CS_P3_NODE_A(ptr, size)  CS_UPDATE(6, ptr, size, 3)
#define CS_P3_NODE_B(ptr, size)  CS_UPDATE(7, ptr, size, 3)
/**@}*/

#endif /* _CS_INTERFACE_H_INCLUDED_ */