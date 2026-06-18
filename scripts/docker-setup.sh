#!/usr/bin/env bash
# Install/start Colima + Docker CLI in ~/.local (no Homebrew required).
# Usage: source scripts/docker-env.sh   OR   eval "$(bash scripts/docker-setup.sh --print-env)"
set -euo pipefail

LOCAL_BIN="${HOME}/.local/bin"
LIMA_DIR="${HOME}/.local/lima"
DOCKER_HOST_SOCK="${HOME}/.colima/default/docker.sock"

export PATH="${LIMA_DIR}/bin:${LOCAL_BIN}:${PATH}"

install_colima() {
  mkdir -p "${LOCAL_BIN}" "${LIMA_DIR}"
  if [[ ! -x "${LOCAL_BIN}/colima" ]]; then
    echo "Installing colima..."
    curl -fsSL -o "${LOCAL_BIN}/colima" \
      "https://github.com/abiosoft/colima/releases/download/v0.8.1/colima-Darwin-arm64"
    chmod +x "${LOCAL_BIN}/colima"
  fi
  if [[ ! -x "${LOCAL_BIN}/docker" ]]; then
    echo "Installing docker CLI..."
    curl -fsSL -o /tmp/docker.tgz \
      "https://download.docker.com/mac/static/stable/aarch64/docker-27.5.1.tgz"
    tar -xzf /tmp/docker.tgz -C /tmp
    cp /tmp/docker/docker "${LOCAL_BIN}/docker"
    chmod +x "${LOCAL_BIN}/docker"
  fi
  if [[ ! -x "${HOME}/.docker/cli-plugins/docker-compose" ]]; then
    echo "Installing docker compose plugin..."
    mkdir -p "${HOME}/.docker/cli-plugins"
    curl -fsSL -o "${HOME}/.docker/cli-plugins/docker-compose" \
      "https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-darwin-aarch64"
    chmod +x "${HOME}/.docker/cli-plugins/docker-compose"
  fi
  if [[ ! -x "${LIMA_DIR}/bin/limactl" ]]; then
    echo "Installing lima..."
    curl -fsSL -o "${LIMA_DIR}/lima.tgz" \
      "https://github.com/lima-vm/lima/releases/download/v2.1.2/lima-2.1.2-Darwin-arm64.tar.gz"
    tar -xzf "${LIMA_DIR}/lima.tgz" -C "${LIMA_DIR}"
  fi
}

fix_colima_certs() {
  if ! command -v colima >/dev/null 2>&1; then
    return 0
  fi
  if colima status 2>/dev/null | grep -q "Running"; then
    security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain \
      > /tmp/macos-certs.pem 2>/dev/null || true
    security find-certificate -a -p /Library/Keychains/System.keychain \
      >> /tmp/macos-certs.pem 2>/dev/null || true
    if [[ -s /tmp/macos-certs.pem ]]; then
      colima ssh -- sudo bash -c 'cat > /usr/local/share/ca-certificates/macos-extra.crt' \
        < /tmp/macos-certs.pem 2>/dev/null || true
      colima ssh -- sudo update-ca-certificates 2>/dev/null || true
      colima ssh -- sudo systemctl restart docker 2>/dev/null || true
    fi
  fi
}

start_colima() {
  if ! colima status 2>/dev/null | grep -q "Running"; then
    mkdir -p /tmp/colima
    echo "Starting colima (first run may take a few minutes)..."
    colima start --cpu 4 --memory 6 --disk 30
  fi
  export DOCKER_HOST="unix://${DOCKER_HOST_SOCK}"
}

install_colima
start_colima
fix_colima_certs

if [[ "${1:-}" == "--print-env" ]]; then
  printf 'export PATH="%s:%s:$PATH"\n' "${LIMA_DIR}/bin" "${LOCAL_BIN}"
  printf 'export DOCKER_HOST="unix://%s"\n' "${DOCKER_HOST_SOCK}"
  exit 0
fi

docker version --format 'Docker {{.Client.Version}} (colima {{.Server.Version}})'
echo "Docker ready. DOCKER_HOST=${DOCKER_HOST}"
