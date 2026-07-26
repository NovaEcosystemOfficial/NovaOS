#!/usr/bin/env bash
# End-to-end Nova Update flow against a local RPM repository (no ISO rebuild).
#
# Steps:
#   1) bootstrap tools (rpmbuild, createrepo_c)
#   2) build + publish hello-nova-update 1.0.0, install into test rootfs
#   3) build + publish 1.0.1
#   4) nova-updater check → detect → apply → verify VERSION
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="${ROOT}/build/work/update-test"
CHANNEL="${NOVA_UPDATE_TEST_CHANNEL:-stable}"
SOCK="${WORK}/run/update.sock"
STATE="${WORK}/state"
REPO="${WORK}/repo/channels"
INSTALL_ROOT="${WORK}/rootfs"
TOOLS_ENV="${NOVA_UPDATE_TEST_TOOLS:-${WORK}/host-tools}/env.sh"
PID=""

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

cleanup() {
  if [[ -n "${PID}" ]] && kill -0 "${PID}" 2>/dev/null; then
    kill "${PID}" 2>/dev/null || true
    wait "${PID}" 2>/dev/null || true
  fi
  rm -f "${SOCK}"
}
trap cleanup EXIT

echo "=============================================="
echo " Nova Update e2e — local RPM repo"
echo " workdir: ${WORK}"
echo "=============================================="

rm -rf "${WORK}/rootfs" "${WORK}/state" "${WORK}/run" "${WORK}/artifacts" "${WORK}/repo"
mkdir -p "${WORK}/run" "${STATE}" "${INSTALL_ROOT}"

bash "${ROOT}/scripts/update-test/bootstrap-update-test-tools.sh"
# shellcheck disable=SC1090
source "${TOOLS_ENV}"

########################################
# Phase A — baseline 1.0.0 in repo + rootfs
########################################
echo
echo "==> Phase A: baseline hello-nova-update 1.0.0"
RPM_A="$(bash "${ROOT}/scripts/update-test/build-test-package.sh" 1.0.0 1 "${CHANNEL}" | tail -1)"
bash "${ROOT}/scripts/update-test/publish-local-repo.sh" "${CHANNEL}" nova "${RPM_A}"

export NOVA_UPDATE_SOCKET="${SOCK}"
export NOVA_UPDATE_STATE_DIR="${STATE}"
export NOVA_UPDATE_BACKEND=localrpm
export NOVA_UPDATE_LOCAL_REPO="${REPO}"
export NOVA_UPDATE_INSTALL_ROOT="${INSTALL_ROOT}"
export NOVA_UPDATE_SIGNATURE_POLICY=warn

"${ROOT}/system/update/bin/nova-updated" \
  --backend localrpm --socket "${SOCK}" --foreground \
  >"${WORK}/nova-updated.log" 2>&1 &
PID=$!

for _ in $(seq 1 50); do
  [[ -S "${SOCK}" ]] && break
  sleep 0.1
done
[[ -S "${SOCK}" ]] || { cat "${WORK}/nova-updated.log" >&2; fail "daemon socket"; }
pass "nova-updated (localrpm) listening"

CLI=("${ROOT}/shell/nova-updater/nova-updater")
"${CLI[@]}" channel set "${CHANNEL}" >/dev/null
"${CLI[@]}" check >/dev/null
"${CLI[@]}" apply >/dev/null

BASELINE="$(cat "${INSTALL_ROOT}/usr/share/hello-nova-update/VERSION")"
[[ "${BASELINE}" == *"1.0.0"* ]] || fail "baseline VERSION='${BASELINE}'"
pass "baseline installed: ${BASELINE}"

# Confirm check is clean after install
CHECK_CLEAN="$("${CLI[@]}" check)"
echo "${CHECK_CLEAN}" | grep -q 'hello-nova-update' && fail "1.0.0 still reported as pending" || true
pass "check after baseline: no pending hello-nova-update"

########################################
# Phase B — publish 1.0.1 (no ISO rebuild)
########################################
echo
echo "==> Phase B: publish hello-nova-update 1.0.1 (incremental)"
RPM_B="$(bash "${ROOT}/scripts/update-test/build-test-package.sh" 1.0.1 1 "${CHANNEL}" | tail -1)"
# Keep 1.0.0 and add 1.0.1 in the same channel repo
bash "${ROOT}/scripts/update-test/publish-local-repo.sh" "${CHANNEL}" nova \
  "${WORK}/artifacts/hello-nova-update-1.0.0-1.nova.noarch.rpm" \
  "${RPM_B}"

########################################
# Phase C — check → detect → apply → verify
########################################
echo
echo "==> Phase C: check → detect → apply → verify"
CHECK_JSON="$("${CLI[@]}" check)"
echo "${CHECK_JSON}" | tee "${WORK}/check-1.0.1.json"
echo "${CHECK_JSON}" | grep -q '"name": "hello-nova-update"' || fail "update not detected"
echo "${CHECK_JSON}" | grep -q '"version": "1.0.1"' || fail "1.0.1 not detected"
pass "detected hello-nova-update 1.0.1"

APPLY_JSON="$("${CLI[@]}" apply)"
echo "${APPLY_JSON}" | tee "${WORK}/apply-1.0.1.json"
echo "${APPLY_JSON}" | grep -q 'hello-nova-update' || fail "apply did not mention package"
pass "apply completed"

FINAL="$(cat "${INSTALL_ROOT}/usr/share/hello-nova-update/VERSION")"
[[ "${FINAL}" == *"1.0.1"* ]] || fail "final VERSION='${FINAL}' (expected 1.0.1)"
pass "final VERSION: ${FINAL}"

RUN_OUT="$("${INSTALL_ROOT}/usr/bin/hello-nova-update")"
[[ "${RUN_OUT}" == *"1.0.1"* ]] || fail "binary output='${RUN_OUT}'"
pass "hello-nova-update binary reports ${RUN_OUT}"

STATUS="$("${CLI[@]}" status)"
echo "${STATUS}" | grep -q '"backend": "localrpm"' || fail "backend not localrpm"
pass "broker status ok"

echo
echo "=============================================="
echo " PASS — NovaOS updated without rebuilding ISO"
echo "   ${BASELINE}  →  ${FINAL}"
echo "   repo: ${REPO}/${CHANNEL}"
echo "=============================================="
