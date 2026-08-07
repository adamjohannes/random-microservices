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
  (cd "$dir" && docker compose down --remove-orphans) && ok "[$svc] stopped" || warn "[$svc] stop returned non-zero (may already be down)"
  echo ""
done

# Remove the shared network (force-disconnect any remaining containers first)
if docker network inspect services_net &>/dev/null 2>&1; then
  CONTAINERS=$(docker network inspect services_net --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
  for cname in $CONTAINERS; do
    docker network disconnect -f services_net "$cname" &>/dev/null || true
  done
  docker network rm services_net &>/dev/null && ok "services_net network removed" || warn "could not remove services_net"
fi

echo ""
echo -e "${BOLD}All services stopped.${RESET}"
