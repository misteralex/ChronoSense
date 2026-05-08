#!/bin/sh

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

/**
 * @file cs-build-host-project.sh
 * @brief ChronoSense High-Performance Build & Integration Orchestrator.
 */

/**
 * @file cs-build-host-project.sh
 * @brief ChronoSense High-Performance Build & Integration Orchestrator.
 * * @details This script automates the full lifecycle of the ChronoSense-instrumented 
 * Nginx build. It performs environment sanitization, dependency injection (C Core), 
 * compiler optimization targeting (O3/LTO logic via Nginx auto-configure), 
 * and local deployment for benchmarking.
 */

# --- ENVIRONMENT CONFIGURATION ---
# @note Ensure CS_HOME points to your local development root.
export CS_HOME="/your/path/to/chronosense"  # Update this to your actual ChronoSense home directory
export CS_HOST_PRJ=nginx

CS_SOURCE=chronosense
CS_NGINX_TESTS="$CS_HOME/$CS_SOURCE/tests/$CS_HOST_PRJ"
CS_HOST_BIN="$CS_HOME/$CS_HOST_PRJ/objs/src/chronosense"

/**
 * @section step1 Source Injection
 * Copies the proprietary C core and interface headers into the host project tree.
 * This enables the 'Binary Fusion' during the compilation phase.
 */
cp -fv $CS_HOME/$CS_SOURCE/src/core/cs_core.c \
      $CS_HOME/$CS_SOURCE/src/include/cs_core.h \
      $CS_HOME/$CS_SOURCE/src/include/cs_interface.h \
      $CS_HOME/$CS_HOST_PRJ/src/chronosense/

/**
 * @section step2 Workspace Sanitization
 * Removes previous build artifacts and localized test environments 
 * to ensure a deterministic compilation state.
 */
echo "Cleaning build environment..."
if [ -n "$CS_NGINX_TESTS" ] && [ -d "$CS_NGINX_TESTS" ]; then
    echo "Cleaning up Chronosense Nginx tests at: $CS_NGINX_TESTS"
    sudo rm -rf "$CS_NGINX_TESTS"
else
    echo "Error: CS_NGINX_TESTS is not set or not a directory. Aborting to prevent disaster."
    exit 1
fi
cd $CS_HOME/$CS_HOST_PRJ
make clean

/**
 * @section step3 IPC Reset
 * Explicitly removes the shared memory segment to prevent stale data 
 * or permission conflicts in the atomic telemetry layer.
 */
echo "Removing existing shared memory file..."
sudo rm -rf /dev/shm/chronosense_db

/**
 * @section step4 Nginx Configuration
 * Patches Nginx with ChronoSense-specific compiler flags.
 * @link --with-cc-opt Includes the chronosense source directory.
 * @link --with-ld-opt Links necessary mathematical libraries.
 */
echo "Reconfigure source code"
./auto/configure --prefix=$CS_NGINX_TESTS --sbin-path=$CS_NGINX_TESTS/nginx \
--conf-path=$CS_NGINX_TESTS/nginx.conf --pid-path=$CS_NGINX_TESTS/logs/nginx.pid \
--error-log-path=$CS_NGINX_TESTS/logs/error.log --http-log-path=$CS_NGINX_TESTS/logs/access.log \
--with-http_ssl_module  --with-cc-opt="-I src/chronosense" --with-ld-opt="-lm"

/**
 * @section step5 Compilation
 * Executes multi-threaded build using all available CPU cores.
 */
echo "Building the project..."
mkdir -p $CS_HOST_BIN
sudo chown -R $USER:$USER $CS_NGINX_TESTS $CS_HOME/$CS_HOST_PRJ
make -j$(nproc)
echo -e "\e[32m[✔] Build completed successfully!\e[0m"

/**
 * @section step6 Local Deployment
 * Installs the instrumented binary and synchronizes configuration files
 * (nginx.conf, mime.types) to the isolated test directory.
 */
echo "Installing nginx to target directory..."
sudo make install

# Restore permissions
# sudo is needed here to reclaim files created by 'sudo make install'
sudo chown -R $USER:$USER "$CS_NGINX_TESTS"
mkdir -p "$CS_NGINX_TESTS/conf"
cp -fv "$CS_HOME/$CS_HOST_PRJ/conf/nginx.conf" "$CS_NGINX_TESTS/conf"
cp -fv "$CS_HOME/$CS_HOST_PRJ/conf/mime.types" "$CS_NGINX_TESTS/conf"