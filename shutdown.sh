#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RESET='\033[0m'

info() { echo -e "${BOLD}[shutdown]${RESET} $*"; }
ok()   { echo -e "${GREEN}[  ok  ]${RESET} $*"; }
warn() { echo -e "${YELLOW}[ warn ]${RESET} $*"; }

SERVICES=(web notifications connections course account)

echo ""
info "Stopping all services…"
echo ""

for svc in "${SERVICES[@]}"; do
  dir="$ROOT/$svc"
  if [ ! -f "$dir/docker-compose.yaml" ]; then
    warn "[$svc] no docker-compose.yaml found, skipping"
    continue
  fi
  info "[$svc] docker compose down"
  (cd "$dir" && docker compose down) && ok "[$svc] stopped" || warn "[$svc] stop returned non-zero (may already be down)"
  echo ""
done

# Remove the shared network if it exists and is now empty
if docker network inspect services_net &>/dev/null 2>&1; then
  CONTAINERS=$(docker network inspect services_net --format '{{len .Containers}}' 2>/dev/null || echo "0")
  if [ "$CONTAINERS" -eq 0 ]; then
    docker network rm services_net &>/dev/null && ok "services_net network removed"
  else
    warn "services_net still has $CONTAINERS container(s) attached — not removed"
  fi
fi

echo ""
echo -e "${BOLD}All services stopped.${RESET}"
