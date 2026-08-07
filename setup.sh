#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[0;33m'; GREEN='\033[0;32m'; BOLD='\033[1m'; RESET='\033[0m'

info()  { echo -e "${BOLD}[setup]${RESET} $*"; }
ok()    { echo -e "${GREEN}[  ok  ]${RESET} $*"; }
warn()  { echo -e "${YELLOW}[ warn ]${RESET} $*"; }
fail()  { echo -e "${RED}[FAIL  ]${RESET} $*" >&2; }

ERRORS=0
err() { fail "$*"; (( ERRORS++ )) || true; }

# ── dependency checks ─────────────────────────────────────────────────────────
info "Checking required dependencies…"

check_cmd() {
  local cmd="$1" hint="${2:-}"
  if command -v "$cmd" &>/dev/null; then
    ok "$cmd  ($(command -v "$cmd"))"
  else
    err "$cmd not found${hint:+ — $hint}"
  fi
}

check_docker_running() {
  if ! docker info &>/dev/null 2>&1; then
    err "Docker daemon is not running — start Docker Desktop or dockerd"
  else
    ok "Docker daemon is running"
  fi
}

check_docker_compose_v2() {
  if docker compose version &>/dev/null 2>&1; then
    ok "docker compose (plugin)  ($(docker compose version --short 2>/dev/null || echo 'ok'))"
  else
    err "docker compose plugin not found — upgrade Docker Desktop or install the compose plugin"
  fi
}

check_cmd docker "install Docker Desktop from https://docker.com"
check_docker_running
check_docker_compose_v2

# ── environment variable notes ────────────────────────────────────────────────
info "Checking environment variables…"
ok "JWT_SECRET and M2M_SECRET use 'change-me-in-production' for local dev (hardcoded in compose files)"
warn "Set JWT_SECRET and M2M_SECRET to strong secrets before deploying to production"

# ── warn about hardcoded secrets in compose files ────────────────────────────
info "Checking for hardcoded secrets in docker-compose files…"
for f in "$ROOT"/account/docker-compose.yaml "$ROOT"/course/docker-compose.yaml "$ROOT"/connections/docker-compose.yaml; do
  if grep -q "change-me-in-production" "$f" 2>/dev/null; then
    warn "$(basename "$(dirname "$f")")/docker-compose.yaml contains JWT_SECRET: change-me-in-production — safe for local dev only"
  fi
done

# ── bail if any hard errors ───────────────────────────────────────────────────
if (( ERRORS > 0 )); then
  echo ""
  fail "$ERRORS error(s) found. Fix the issues above and re-run."
  exit 1
fi

# ── port conflict check ───────────────────────────────────────────────────────
info "Checking for port conflicts…"
PORTS=(8080 8081 8082 8083 5173 5672 15672 8025 1025 7474 7687)
PORT_CONFLICTS=0
for port in "${PORTS[@]}"; do
  if lsof -iTCP:"$port" -sTCP:LISTEN -t &>/dev/null 2>&1; then
    warn "Port $port is already in use — a service may fail to bind"
    (( PORT_CONFLICTS++ )) || true
  fi
done
if (( PORT_CONFLICTS == 0 )); then
  ok "All ports are free"
fi

# ── shared Docker network ─────────────────────────────────────────────────────
info "Ensuring shared Docker network 'services_net' exists…"
if docker network inspect services_net &>/dev/null 2>&1; then
  ok "services_net already exists"
else
  docker network create services_net
  ok "services_net created"
fi

# ── boot services ─────────────────────────────────────────────────────────────
echo ""
info "Starting all services with docker compose…"
echo ""

SERVICES=(account course connections notifications web)

for svc in "${SERVICES[@]}"; do
  info "[$svc] docker compose up --build -d"
  (
    cd "$ROOT/$svc"
    docker compose up --build -d
  )
  ok "[$svc] started"
  echo ""
done

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}All services launched.${RESET}"
echo ""
echo "  Service       URL"
echo "  ──────────────────────────────────────────"
echo "  account       http://localhost:8080"
echo "  course        http://localhost:8081"
echo "  connections   http://localhost:8082"
echo "  notifications http://localhost:8083/health"
echo "  web           http://localhost:5173"
echo "  RabbitMQ UI   http://localhost:15672  (guest / guest)"
echo "  MailHog UI    http://localhost:8025"
echo "  Neo4j UI      http://localhost:7474"
echo ""
info "To tail logs: docker compose -f <service>/docker-compose.yaml logs -f"
info "To stop all:  for s in account course connections notifications web; do (cd \$s && docker compose down); done"
