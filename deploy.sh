#!/usr/bin/env bash
set -e

COMPOSE_FILE="docker-compose.full.yml"

prompt_env_var() {
  read -r -p "Enter value for $1 (leave blank to exit): " value
  [ -z "$value" ] && exit 1
  export "$1=$value"
}

read_env() {
  if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    prompt_env_var TELEGRAM_BOT_TOKEN
  fi
  if [ -z "$BACKEND_API_URL" ]; then
    prompt_env_var BACKEND_API_URL
  fi
  if [ -z "$LOGS_DIR" ]; then
    read -r -p "Enter logs directory (blank for ./logs): " value
    [ -z "$value" ] && export LOGS_DIR="./logs" || export LOGS_DIR="$value"
  fi
}
read_env

start() {
  echo "🔨 Building Docker images..."
  docker compose -f "$COMPOSE_FILE" build
  echo "🚀 Starting services in detached mode..."
  docker compose -f "$COMPOSE_FILE" up -d
  echo "⏳ Waiting for all services to report healthy..."
  SERVICES=("supervisor_backend" "bot" "planner" "scraper" "file_writer" "scheduler")
  for SERVICE in "${SERVICES[@]}"; do
    for attempt in $(seq 1 30); do
      echo "⏳ Checking $SERVICE health ($attempt/30)..."
      if docker compose -f "$COMPOSE_FILE" exec "$SERVICE" curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ $SERVICE is healthy"
        break
      fi
      sleep 4
    done
    if ! docker compose -f "$COMPOSE_FILE" exec "$SERVICE" curl -s http://localhost:8000/health > /dev/null 2>&1; then
      echo "❌ $SERVICE did not become healthy in time"
      exit 1
    fi
  done
  echo "🎉 All services are up and healthy."
}

status() {
  echo "📊 Container status:"
  docker compose -f "$COMPOSE_FILE" ps
}

stop() {
  echo "🛑 Stopping services..."
  docker compose -f "$COMPOSE_FILE" down
  echo "✅ Stack stopped."
}

logs() {
  echo "📄 Tailing logs..."
  docker compose -f "$COMPOSE_FILE" logs -f
}

case "$1" in
  start) start ;;
  status) status ;;
  stop) stop ;;
  logs) logs ;;
  *) echo "Usage: $0 {start|status|stop|logs}" ;;
esac
