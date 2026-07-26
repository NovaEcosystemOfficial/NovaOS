#!/usr/bin/env bash
# Publish RPMs into the local Nova Update channel repo and refresh repodata.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHANNEL="${1:-stable}"
CLASS="${2:-nova}"  # os | nova | apps
shift 2 || true
RPMS=("$@")

WORK="${ROOT}/build/work/update-test"
TOOLS_ENV="${NOVA_UPDATE_TEST_TOOLS:-${WORK}/host-tools}/env.sh"
REPO_CHANNEL="${WORK}/repo/channels/${CHANNEL}"
DEST="${REPO_CHANNEL}/${CLASS}/x86_64"

if [[ ! -f "${TOOLS_ENV}" ]]; then
  bash "${ROOT}/scripts/update-test/bootstrap-update-test-tools.sh"
fi
# shellcheck disable=SC1090
source "${TOOLS_ENV}"

if [[ ${#RPMS[@]} -eq 0 ]]; then
  mapfile -t RPMS < <(find "${WORK}/artifacts" -name '*.rpm' 2>/dev/null | sort)
fi
[[ ${#RPMS[@]} -gt 0 ]] || { echo "ERROR: no RPMs to publish" >&2; exit 1; }

mkdir -p "${DEST}" "${REPO_CHANNEL}/os/x86_64" "${REPO_CHANNEL}/apps/x86_64"
echo "==> Publishing ${#RPMS[@]} RPM(s) → ${DEST}"
for rpm in "${RPMS[@]}"; do
  cp -f "${rpm}" "${DEST}/"
  echo "    + $(basename "${rpm}")"
done

echo "==> createrepo_c ${REPO_CHANNEL}"
rm -rf "${REPO_CHANNEL}/.repodata" "${REPO_CHANNEL}/repodata"
createrepo_c "${REPO_CHANNEL}"

# Drop a file:// repo snippet for humans / optional DNF use
CONF_DIR="${WORK}/yum.repos.d"
mkdir -p "${CONF_DIR}"
cat >"${CONF_DIR}/novaos-${CHANNEL}-local.repo" <<EOF
[novaos-${CHANNEL}-local]
name=NovaOS local test repo (${CHANNEL})
baseurl=file://${REPO_CHANNEL}
enabled=1
gpgcheck=0
metadata_expire=60
EOF

echo "PASS — repo published at ${REPO_CHANNEL}"
ls -la "${DEST}"
ls "${REPO_CHANNEL}/repodata" | head
