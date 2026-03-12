#!/bin/bash

###############################################################################
# STOP.SH
# Script to stop Flask application and Docker containers
# for FIWARE Smart Store
###############################################################################

set -e

echo " [STOP] Stopping FIWARE Smart Store..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"
VENV_DIR="${VENV_DIR:-.venv}"

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 1. Stop Flask application
log "Stopping Flask application..."
# The Flask app should be running in the foreground, so we'll just let it be interrupted
# When this script is run, the Flask process should be terminated by the parent shell
echo ""
warn "Flask application will be stopped. Press Ctrl+C in the Flask terminal if it's still running."

# 2. Deactivate virtual environment (if sourced)
if [ -n "$VIRTUAL_ENV" ]; then
    log "Deactivating Python virtual environment..."
    deactivate 2>/dev/null || true
fi

# 3. Stop and remove Docker containers
log "Stopping and removing Docker containers..."
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    log "Docker containers stopped and removed"
else
    warn "docker-compose.yml not found, skipping Docker cleanup"
fi

log "FIWARE Smart Store stopped successfully"
