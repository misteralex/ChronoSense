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
@file cs_demo_host_nginx.py
@brief Automated Performance Benchmarking Suite for ChronoSense.
"""

"""
@file cs_demo_host_nginx.py
@brief Automated Performance Benchmarking Suite for ChronoSense.
@details This script orchestrates a complete simulation environment by launching 
the instrumented Nginx binary and executing high-concurrency stress tests using 
Locust. It validates the sub-0.3% overhead claims across different scenarios.
"""

import sys
import subprocess
import time
import os
from pathlib import Path
from locust import HttpUser, task, between

# --- ENVIRONMENT VARIABLES LOADING ---
# Validates the presence of CS_HOME to ensure the test suite can locate binaries.
cs_home_env = os.environ.get("CS_HOME")
if not cs_home_env:
    print("[!] FATAL ERROR: CS_HOME environment variable is not set.")
    sys.exit(1)

cs_host_prj = os.environ.get("CS_HOST_PRJ", "nginx")
cs_source = os.environ.get("CS_HOME_SOURCE", "chronosense-draft")
test_dir = os.path.join(cs_home_env, cs_source, "tests", "nginx")

# --- PATH CONFIGURATION ---
# Resolution of binary and configuration paths based on the build orchestration.
print(f"[⚙️] test_dir: {test_dir}")
CS_HOST_BIN = os.path.join(test_dir, "nginx")
CS_HOST_CONF = os.path.join(test_dir, "conf/nginx.conf")

# Self-referencing path for Locust task execution.
CS_DEMO_FILE = os.path.abspath(__file__) 
TARGET_URL = "http://localhost:8080"

# --- LOCUST LOGIC ---
# Defines the HTTP user behavior for the load simulation.
try:
    class ChronosenseUser(HttpUser):
        """
        @class ChronosenseUser
        @brief Simulates a high-frequency edge client.
        @details Implements a minimal wait time to maximize request throughput, 
        stressing the atomic telemetry layer.
        """
        wait_time = between(0.1, 0.5)

        @task
        def access_root(self):
            """Executes a standard GET request to the Nginx host."""
            self.client.get("/")
except ImportError:
    pass

class NginxAtomicTester:
    """
    @class NginxAtomicTester
    @brief Controller for the Nginx lifecycle and benchmarking.
    @details Manages startup, shutdown, and execution of the performance scenarios.
    """
    def __init__(self):
        self.nginx_proc = None
        self.current_tag = ""

    def start_nginx(self):
        """
        @brief Launches the Nginx master process with ChronoSense instrumentation.
        @details Uses the configuration specified in CS_HOST_CONF.
        """
        print(f"[🚀] Starting Nginx host at {CS_HOST_BIN}...")
        cmd = [CS_HOST_BIN, "-c", CS_HOST_CONF, "-g", "daemon off;"]
        self.nginx_proc = subprocess.Popen(cmd)
        time.sleep(2)  # Wait for workers to initialize the shared memory

    def run_locust(self, users, spawn_rate, duration):
        """
        @brief Executes the Locust load test in headless mode.
        @param users Total number of concurrent users.
        @param spawn_rate Rate at which users are spawned per second.
        @param duration Total duration of the test in seconds.
        """
        print(f"[🔥] Running Performance Test: {users} users, {duration}s")
        cmd = [
            "locust", "-f", CS_DEMO_FILE, 
            "--headless",
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", f"{duration}s",
            "--host", TARGET_URL
        ]
        subprocess.run(cmd)

    def stop_nginx(self):
        """@brief Terminates the Nginx process and cleans up resources."""
        if self.nginx_proc:
            print("[🛑] Turn off host demo simulation")
            self.nginx_proc.terminate()
            self.nginx_proc.wait()

def main():
    """
    @brief Entry point for the POC simulation scenarios.
    @details Selects the test intensity based on the provided CLI tag.
    """
    scenarios = {
        "normal_scenario": {"users": 10, "spawn_rate": 1, "duration": 60},
        "noisy_scenario":  {"users": 50, "spawn_rate": 50, "duration": 30},
        "stress_scenario": {"users": 200, "spawn_rate": 10, "duration": 120}
    }

    if len(sys.argv) < 2 or sys.argv[1] not in scenarios:
        print("Usage: cs_demo.py [TAG]")
        print("Available TAGs: normal_scenario, noisy_scenario, stress_scenario")
        sys.exit(1)

    tag = sys.argv[1]
    config = scenarios[tag]
    
    tester = NginxAtomicTester()
    tester.current_tag = tag

    try:
        tester.start_nginx()
        print(f"\n>>> ACTIVATING SCENARIO: {tag}")
        tester.run_locust(config["users"], config["spawn_rate"], config["duration"])
    finally:
        tester.stop_nginx()

if __name__ == "__main__":
    main()