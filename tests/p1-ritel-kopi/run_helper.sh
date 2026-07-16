#!/usr/bin/env bash
# Helper for P1 scenario execution — run from repo root
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

reset_memory() {
  docker compose exec -T pgsql-agent psql -U cba_agent -d agent_memory -c \
    "TRUNCATE chat_histories, short_memories, state_transitions RESTART IDENTITY;" >/dev/null
  echo "Memory reset OK"
}

get_latest_thread_id() {
  docker compose exec -T pgsql-agent psql -U cba_agent -d agent_memory -t -A -c \
    "SELECT thread_id FROM state_transitions ORDER BY turn_num DESC, sequence_num DESC LIMIT 1;" \
    | tr -d '[:space:]'
}

run_stream() {
  local input="$1"
  local outfile="$2"
  local timeout_sec="${3:-600}"
  echo "=== STREAM: $input ===" | tee "$outfile"
  curl -N -s --max-time "$timeout_sec" -X POST 'http://localhost:8000/agent/stream' \
    -H 'Content-Type: application/json' \
    -d "$(jq -n --arg i "$input" '{input: $i}')" 2>&1 | tee -a "$outfile"
  echo "" | tee -a "$outfile"
}

run_resume() {
  local thread_id="$1"
  local input="$2"
  local outfile="$3"
  local timeout_sec="${4:-600}"
  echo "=== RESUME ($thread_id): $input ===" | tee -a "$outfile"
  curl -N -s --max-time "$timeout_sec" -X POST 'http://localhost:8000/agent/resume' \
    -H 'Content-Type: application/json' \
    -d "$(jq -n --arg t "$thread_id" --arg i "$input" '{thread_id: $t, input: $i}')" 2>&1 | tee -a "$outfile"
  echo "" | tee -a "$outfile"
}

extract_event_types() {
  grep -o '"type": *"[^"]*"' "$1" | sed 's/"type": *"//;s/"$//' | sort | uniq -c
}

extract_thread_from_interrupt() {
  grep -o '"thread_id": *"[^"]*"' "$1" | head -1 | sed 's/"thread_id": *"//;s/"$//'
}

get_audit_nodes() {
  local thread_id="$1"
  curl -s "http://localhost:8000/agent/audit/${thread_id}" | jq -r '.[] | "\(.sequence_num)\t\(.node_name)\t\(.event_type)"'
}

get_chat_history() {
  curl -s 'http://localhost:8000/chat/history' | jq .
}

wait_health() {
  for i in $(seq 1 30); do
    if curl -s --max-time 5 http://localhost:8000/health | grep -q ok; then
      echo "Health OK"
      return 0
    fi
    sleep 2
  done
  echo "Health check failed" >&2
  return 1
}

set_harness() {
  local s5="${1:-false}"
  local s6="${2:-false}"
  local s7="${3:-false}"
  local env_file="$REPO_ROOT/.env"
  sed -i "s/^SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=.*/SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=${s5}/" "$env_file"
  sed -i "s/^SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=.*/SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=${s6}/" "$env_file"
  sed -i "s/^SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=.*/SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=${s7}/" "$env_file"
  docker compose up -d agent-api --force-recreate >/dev/null
  wait_health
  echo "Harness: S5=$s5 S6=$s6 S7=$s7"
}
