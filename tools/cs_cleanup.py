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
@file cs_cleanup.py
@brief System Resource Sanitization Tool for ChronoSense.
"""

import os
import subprocess
import getpass

/**
 * @file cs_cleanup.py
 * @brief System Resource Sanitization Tool for ChronoSense.
 * * @details This script performs a deep cleanup of the system environment to prevent
 * resource leaks between performance tests. It specifically targets orphaned 
 * Nginx processes, lingering ChronoSense threads, and System V Shared Memory segments.
 */

def clean_by_ipcs():
    """
    @brief Identifies and purges all ChronoSense-related resources from the system.
    
    @details The procedure follows a three-step safety protocol:
    1. Termination of active processes (Nginx/ChronoSense) to release memory handles.
    2. Enumeration and removal of IPC Shared Memory segments owned by the current user.
    3. Recursive permission reset on the project directory to fix sudo-induced ownership locks.
    """
    current_user = getpass.getuser()
    cs_home = os.environ.get("CS_HOME")

    print(f"[🛡️] Cleaning System V Shared Memory for user: {current_user}")

    # 1. Kill processes first to release attachments
    # Forcefully terminates any process matching 'nginx' or 'chronosense' to unlock SHM segments.
    subprocess.run(["sudo", "pkill", "-9", "-i", "nginx"], stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "pkill", "-9", "-f", "chronosense"], stderr=subprocess.DEVNULL)

    # 2. Identify and remove System V SHM segments
    # This command finds all segments owned by the user and removes them one by one.
    # Essential for preventing "ghost" memory allocation errors during successive builds.
    os.system("ipcs -m | grep " + current_user + " | awk '{print $2}' | xargs -I {} sudo ipcrm -m {}")

    # 3. Fix Folder Permissions (CS_HOME/chronosense/tests)
    # Resets ownership to the current user, rectifying permissions after 'sudo make install' operations.
    if cs_home:
        print(f"[📂] Resetting ownership on {cs_home}")
        subprocess.run(["sudo", "chown", "-R", f"{current_user}:{current_user}", cs_home])
    
    print("[✔] Done. No more 'ghost' segments should remain.")

if __name__ == "__main__":
    clean_by_ipcs()