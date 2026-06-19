#!/bin/bash

# ==============================================================================
# start_redis.sh
#
# Starts a Redis server instance by loading configuration from a .env.redis file.
# If the port is already in use by another Redis server, it will stop the
# old instance before starting the new one (effectively restarting it).
#
# Usage:
#   ./start_redis.sh
#
# Prerequisites:
#   - redis-server, lsof, and ps must be installed and accessible in the PATH.
#   - A .env.redis file must exist in the same directory.
# ==============================================================================

# --- Configuration File ---
# The name of the environment file to read settings from.
ENV_FILE=".env.redis"

# --- Pre-flight Checks ---
# 1. Check if the redis-server command is available.
if ! command -v redis-server &> /dev/null; then
    echo "Error: 'redis-server' command not found."
    echo "Please install Redis and ensure 'redis-server' is in your PATH."
    exit 1
fi

# 2. Check if the lsof command is available (for port checking).
if ! command -v lsof &> /dev/null; then
    echo "Error: 'lsof' command not found. It is required to check if the port is in use."
    echo "Please install 'lsof' (e.g., 'sudo apt-get install lsof' or 'sudo yum install lsof')."
    exit 1
fi

# 3. Check if the configuration file exists.
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Configuration file '$ENV_FILE' not found."
    echo "Please create a .env.redis file with your Redis settings."
    exit 1
fi

# --- Load Environment Variables ---
# We source the .env file to load the variables into the script's environment.
# 'set -a' exports them, making them available to subprocesses.
echo "Loading configuration from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

# --- Validate Required Variables ---
# Ensure that the essential variables are set in the .env file.
if [ -z "$REDIS_HOST" ] || [ -z "$REDIS_PORT" ]; then
    echo "Error: REDIS_HOST and REDIS_PORT must be defined in $ENV_FILE."
    exit 1
fi

# --- Check Port and Restart if Necessary ---
echo "Checking status of port $REDIS_PORT..."
# Find the PID of the process listening on the specified port.
# We check both IPv4 and IPv6 explicitly to avoid ambiguity with 'localhost'.
# Stderr is redirected to /dev/null to suppress errors if lsof finds no process.
PID_V4=$(lsof -t -i 4 -a -i :$REDIS_PORT -s TCP:LISTEN 2>/dev/null)
PID_V6=$(lsof -t -i 6 -a -i :$REDIS_PORT -s TCP:LISTEN 2>/dev/null)

# Combine PIDs from both checks and trim whitespace.
PID=$(echo "$PID_V4 $PID_V6" | xargs)


if [ -n "$PID" ]; then
    echo "Port $REDIS_PORT is currently in use by process with PID: $PID."
    
    # Check if the process is actually a redis-server before killing it.
    # We check the command for each PID found.
    PROCESS_NAME=$(ps -p $PID -o comm=)

    if [[ "$PROCESS_NAME" == *"redis-server"* ]]; then
        echo "Process is an existing Redis server. Attempting to stop it..."
        kill $PID
        # Wait for the OS to release the port. This loop is more reliable than a fixed sleep.
        echo "Waiting for port $REDIS_PORT to become free..."
        for i in {1..5}; do
            # Check both IPv4 and IPv6 again to confirm the port is free
            if ! lsof -t -i 4 -a -i :$REDIS_PORT -s TCP:LISTEN &>/dev/null && ! lsof -t -i 6 -a -i :$REDIS_PORT -s TCP:LISTEN &>/dev/null; then
                echo "Port is now free."
                break
            fi
            if [ "$i" -eq 5 ]; then
                echo "Error: Timed out waiting for port $REDIS_PORT to be released."
                exit 1
            fi
            sleep 1
        done
    else
        echo "Error: Port $REDIS_PORT is used by '$PROCESS_NAME' (PID: $PID), which is not a Redis server."
        echo "Aborting to avoid disrupting another application."
        exit 1
    fi
else
    echo "Port $REDIS_PORT appears to be free."
fi

# --- Build the Redis Server Command ---
# We construct the command-line arguments for redis-server.
# The --daemonize no flag is added to keep Redis running in the foreground,
# which is standard practice for services managed by scripts or process managers.
# Remove it if you want Redis to fork into the background.
CMD="redis-server --bind $REDIS_HOST --port $REDIS_PORT --daemonize no"

# Append the password argument only if the REDIS_PASSWORD variable is not empty.
if [ -n "$REDIS_PASSWORD" ]; then
    # Note: It's better to set the password via a redis.conf file for security.
    # This method can expose the password in the process list.
    CMD="$CMD --requirepass \"$REDIS_PASSWORD\""
fi

# --- Execute the Command ---
echo "Starting Redis server on redis://$REDIS_HOST:$REDIS_PORT"
echo "To stop the server, press Ctrl+C."
echo "----------------------------------------------------"

# We use eval to ensure that the command string, especially the potentially
# quoted password, is parsed correctly by the shell.
eval $CMD
