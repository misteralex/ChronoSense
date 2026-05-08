#!/usr/bin/env python3

# Copyright 2026 Alex FARACI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
@file cs_trace.py
@brief ChronoSense monitoring and historical analysis tool.
"""

import sys
import os
import time
import mmap
import pandas as pd
import duckdb
import signal
from cffi import FFI

##
# @file cs_trace.py
# @brief ChronoSense monitoring and historical analysis tool.
# @details This script maps shared memory to monitor real-time probes and 
# provides historical analysis using DuckDB and Parquet storage.
#

ffi = FFI()

##
# @brief CFFI Definition for ChronoSense data structures.
# @details Defines 64-byte aligned structures for probes and the main database.
#
ffi.cdef("""
    typedef struct {
        uint64_t tsc_cycles;   
        uint32_t n_l;          
        uint16_t id;           
        uint16_t pad0;         
        float    mean_l;       
        float    m2_l;         
        float    mean_s;       
        float    alpha_s;      
        float    last_value;   
        float    sigma;        
        float    z_score;      
        uint32_t glitches;         
        uint32_t last_n_l;      
        uint64_t last_tsc;      
        float    throughput;    
    } cs_probe_t;

    typedef struct {
        uint32_t magic;
        uint32_t n_slots;
        uint64_t global_tick; 
        uint16_t sample_counters[64]; 
        cs_probe_t probes[64]; 
    } cs_db_t;
""")

## 
# @var SHM_PATH
# @brief Path to the POSIX Shared Memory file used by the ChronoSense Nginx module.
SHM_PATH = "/dev/shm/chronosense_db"

## 
# @var WARMUP_SAMPLES
# @brief Number of initial samples ignored or highlighted during the system warmup phase.
WARMUP_SAMPLES = 60

# --- Environment and Storage Configuration ---
# Derived from CS_HOME environment variable, falling back to current directory.
CS_HOME = os.environ.get("CS_HOME", ".")
CS_SOURCE = "chronosense-draft"
PARQUET_FILE = os.path.join(CS_HOME, CS_SOURCE, "data", "chronosense.parquet")

# Ensure the 'data' directory exists to avoid FileNotFoundError during flush
os.makedirs(os.path.dirname(PARQUET_FILE), exist_ok=True)

data_log = []

##
# @brief Handles graceful shutdown and emergency data flush.
# @param sig Signal number.
# @param frame Current stack frame.
#
def save_and_exit(sig, frame):
    if len(data_log) > 0:
        print(f"\nEmergency flush: saving {len(data_log)} residual samples...")
        pd.DataFrame(data_log).to_parquet(PARQUET_FILE, engine='pyarrow', index=False)
    sys.exit(0)

signal.signal(signal.SIGINT, save_and_exit)

##
# @brief Performs advanced statistical analysis on historical data.
# @param file_path Path to the .parquet file containing recorded samples.
# @details Uses DuckDB to compute aggregate metrics with dynamic formatting for small values.
#
def analyze_historical(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"\n{'='*115}")
    print(f" CHRONOSENSE - HISTORICAL ANALYSIS & GLITCH REPORT: {file_path}")
    print(f"{'='*115}")
    
    try:
        con = duckdb.connect(database=':memory:')
        query = f"""
        SELECT 
            id as "ID",
            count(*) as "Samples",
            min(val) as "Min",
            max(val) as "Max",
            avg(val) as "Media",
            avg(throughput) as "THR (Avg)",
            count(*) FILTER (WHERE abs(z_score) > 3.0) as "Glitches",
            round(count(*) FILTER (WHERE abs(z_score) > 3.0) * 100.0 / count(*), 2) as "Anomaly (%)",
            max(abs(z_score)) as "Max_Z"
        FROM read_parquet('{file_path}')
        GROUP BY id ORDER BY id
        """
        stats_df = con.execute(query).df()

        ##
        # @brief Formats float values dynamically.
        # @details Uses scientific notation for values smaller than 0.0001 to ensure visibility.
        #
        def dynamic_format(x):
            if isinstance(x, float) and 0 < abs(x) < 0.0001:
                return f"{x:.4e}"
            return f"{x:.4f}"

        print(stats_df.to_string(index=False, float_format=dynamic_format))
        print(f"{'='*115}\n")
    except Exception as e:
        print(f"DuckDB Error: {e}")

##
# @brief Retrieves the inode of the shared memory file.
# @return The inode number or None if not found.
#
def get_shm_inode():
    try: return os.stat(SHM_PATH).st_ino
    except FileNotFoundError: return None

##
# @brief Main loop for real-time monitoring and data collection.
# @details Maps Shared Memory, prints a live dashboard, and buffers data for Parquet persistence.
#    
def run_trace():
    global data_log
    last_seen_tick = -1

    while True:
        current_inode = get_shm_inode()
        if current_inode is None:
            print(f"Waiting for {SHM_PATH}...", end="\r")
            time.sleep(1)
            continue

        try:
            fd = os.open(SHM_PATH, os.O_RDONLY)
            mm = mmap.mmap(fd, os.path.getsize(SHM_PATH), access=mmap.ACCESS_READ)
            db = ffi.cast("cs_db_t *", ffi.from_buffer(mm))
            last_inode = current_inode

            while True:
                if get_shm_inode() != last_inode: break
                
                current_tick = db.global_tick
                if current_tick == last_seen_tick:
                    time.sleep(0.1)
                    continue

                last_seen_tick = current_tick
                current_buffer = len(data_log)
                
                print("\033[H\033[J", end="") 
                print(f"CHRONOSENSE DASHBOARD | TICK: {current_tick} | SYNC: {current_buffer}/600")
                print(f"PATH: {PARQUET_FILE}")
                print("-" * 115)
                print(f"{'SLOT':<5} | {'ID':<6} | {'VALUE':<10} | {'L-MEAN':<10} | {'SIGMA':<8} | {'Z-SCORE':<8} | {'GLITCHES':<8} | {'THR':<10} | {'SAMPLES'}")
                print("-" * 115)

                snapshot_time = time.time()
                for i in range(12): 
                    p = db.probes[i]
                    z = p.z_score
                    thr_val = p.throughput
                    
                    color = "\033[91m" if abs(z) > 3.0 else "\033[92m"
                    thr_str = f"{thr_val:.2e}" if 0 < thr_val < 0.001 else f"{thr_val:10.4f}"

                    print(f"{i:<5} | {p.id:<6} | {p.last_value:10.2f} | {p.mean_l:10.2f} | "
                        f"{p.sigma:8.2f} | {color}{z:8.2f}\033[0m | {p.glitches:<8} | {thr_str:<10} | {p.n_l}")

                    data_log.append({
                        'timestamp': snapshot_time, 'tick': current_tick, 'id': p.id, 
                        'val': p.last_value, 'z_score': p.z_score, 'n_samples': p.n_l,
                        'glitches': p.glitches, 'throughput': thr_val
                    })

                if len(data_log) >= 600:
                    pd.DataFrame(data_log).to_parquet(PARQUET_FILE, engine='pyarrow', index=False)
                    data_log = [] 
                
                time.sleep(0.1)

        except (FileNotFoundError, OSError, mmap.error):
            time.sleep(0.5)
        finally:
            if 'mm' in locals(): mm.close()
            if 'fd' in locals(): os.close(fd)
            
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith('.parquet'):
        analyze_historical(sys.argv[1])
    else:
        run_trace()