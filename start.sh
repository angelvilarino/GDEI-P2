#!/bin/bash

###############################################################################
# START.SH
# Script to start Docker containers and Flask application
# for FIWARE Smart Store
###############################################################################

set -e

echo " [START] Launching FIWARE Smart Store..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"
VENV_DIR="${VENV_DIR:-.venv}"
ORION_URL="${ORION_URL:-http://localhost:1026}"
MAX_RETRIES=30
RETRY_INTERVAL=2

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

# 1. Start Docker containers
log "Starting Docker containers..."
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    error "docker-compose.yml not found in current directory"
    exit 1
fi

docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
log "Docker containers started"

# 2. Wait for MongoDB to be healthy
log "Waiting for MongoDB to be healthy..."
for i in $(seq 1 $MAX_RETRIES); do
    if docker exec $(docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q mongo-db) \
        mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        log "MongoDB is healthy"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        error "MongoDB failed to become healthy after ${MAX_RETRIES} retries"
        exit 1
    fi
    warn "MongoDB health check attempt $i/$MAX_RETRIES..."
    sleep $RETRY_INTERVAL
done

# 3. Wait for Orion to be healthy
log "Waiting for Orion to be healthy..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s "${ORION_URL}/version" &>/dev/null; then
        log "Orion is healthy"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        warn "Orion took too long to start, continuing anyway..."
        break
    fi
    warn "Orion health check attempt $i/$MAX_RETRIES..."
    sleep $RETRY_INTERVAL
done

# 4. Create Python virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 5. Activate virtual environment and install dependencies
log "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel &>/dev/null
pip install -r requirements.txt &>/dev/null

# 6. Run import-data only when Orion has no entities
if [ -f "import-data" ]; then
    if [ ! -x "import-data" ]; then
        log "Making import-data executable..."
        chmod +x import-data
    fi

    log "Checking if Orion already contains entities..."
    entities_json="$(curl -s "${ORION_URL}/v2/entities?limit=1")"

    if echo "$entities_json" | grep -Eq '^\s*\[\s*\]\s*$'; then
        log "Orion is empty. Running import-data script..."
        ORION_URL="$ORION_URL" ./import-data || warn "import-data script failed"
    else
        log "Orion already has data. Skipping import-data."
    fi
else
    warn "import-data script not found, skipping initial data load"
fi

# 7. Start Flask application
log "Starting Flask application..."
export FLASK_ENV=development
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000

python app.py
