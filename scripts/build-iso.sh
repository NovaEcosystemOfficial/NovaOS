#!/usr/bin/env bash
# Build the NovaOS live ISO with KIWI NG.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_require_root
novaos_load_release_env
novaos_ensure_linux_build_fs
novaos_require_cmd dnf python3 find

KIWI_BIN="$(novaos_kiwi_bin)" || {
  echo "ERROR: kiwi-ng not found. Run: sudo scripts/setup-build-host.sh" >&2
  exit 1
}

PROFILE="${NOVAOS_PROFILE}"
DESC_DIR="${NOVAOS_CONFIG_DIR}/kiwi/${PROFILE}"
TS="$(novaos_timestamp)"
DESC_WORK="${NOVAOS_BUILD_DIR}/work/desc-${PROFILE}-${TS}"
TARGET_DIR="${NOVAOS_BUILD_DIR}/work/out-${PROFILE}-${TS}"
LOG_FILE="${NOVAOS_BUILD_DIR}/logs/build-iso-${TS}.log"
ISO_BASENAME="${NOVAOS_ISO_NAME}"
RELEASE_DIR="${NOVAOS_ISO_DIR}/releases"
LATEST_DIR="${NOVAOS_ISO_DIR}/latest"
ROOT_ISO="${NOVAOS_ISO_DIR}/${ISO_BASENAME}.iso"

if [[ ! -f "${DESC_DIR}/appliance.kiwi" ]]; then
  echo "ERROR: missing ${DESC_DIR}/appliance.kiwi" >&2
  exit 1
fi
if [[ ! -f "${DESC_DIR}/config.sh" ]]; then
  echo "ERROR: missing ${DESC_DIR}/config.sh" >&2
  exit 1
fi
if [[ ! -f "${DESC_DIR}/iso-esp-excludes.yaml" ]]; then
  echo "ERROR: missing ${DESC_DIR}/iso-esp-excludes.yaml" >&2
  exit 1
fi

chmod +x "${DESC_DIR}/config.sh"

mkdir -p \
  "${NOVAOS_BUILD_DIR}/logs" \
  "${NOVAOS_BUILD_DIR}/cache" \
  "${RELEASE_DIR}" \
  "${LATEST_DIR}"

FEDORA_REPO="https://mirrors.fedoraproject.org/metalink?repo=fedora-${FEDORA_VERSION}&arch=${FEDORA_ARCH}"
UPDATES_REPO="https://mirrors.fedoraproject.org/metalink?repo=updates-released-f${FEDORA_VERSION}&arch=${FEDORA_ARCH}"

echo "==> NovaOS ISO build"
echo "    kiwi:     ${KIWI_BIN} ($(${KIWI_BIN} --version 2>/dev/null | head -n1 || echo unknown))"
echo "    profile:  ${PROFILE}"
echo "    fedora:   ${FEDORA_VERSION}/${FEDORA_ARCH}"
echo "    desc:     ${DESC_DIR}"
echo "    target:   ${TARGET_DIR}"
echo "    output:   ${ROOT_ISO}"
echo "    log:      ${LOG_FILE}"
echo "    metalink: ${FEDORA_REPO}"
echo "    updates:  ${UPDATES_REPO}"
echo

rm -rf "${DESC_WORK}" "${TARGET_DIR}"
mkdir -p "${DESC_WORK}" "${TARGET_DIR}"
cp -a "${DESC_DIR}/." "${DESC_WORK}/"
chmod +x "${DESC_WORK}/config.sh"

rm -f "${DESC_WORK}/README.md" \
      "${DESC_WORK}/PUBLIC_DEMO_CREDENTIALS.txt" \
      "${DESC_WORK}/CREDENTIALS.txt" \
      "${DESC_WORK}/.gitkeep"

python3 - "${DESC_WORK}/appliance.kiwi" "${FEDORA_VERSION}" "${FEDORA_ARCH}" <<'PY'
import re, sys
path, ver, arch = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path, encoding="utf-8").read()
text2, n1 = re.subn(
    r"metalink\?repo=fedora-\d+&amp;arch=[a-z0-9_]+",
    f"metalink?repo=fedora-{ver}&amp;arch={arch}",
    text,
)
text3, n2 = re.subn(
    r"metalink\?repo=updates-released-f\d+&amp;arch=[a-z0-9_]+",
    f"metalink?repo=updates-released-f{ver}&amp;arch={arch}",
    text2,
)
if n1 < 1 or n2 < 1:
    raise SystemExit(
        f"Failed to pin metalink repos (fedora={n1}, updates={n2}). Check appliance.kiwi."
    )
open(path, "w", encoding="utf-8").write(text3)
print(f"Pinned metalink repos to Fedora {ver}/{arch}")
PY

python3 - "${DESC_WORK}/config.sh" "${NOVAOS_VERSION}" "${NOVAOS_MILESTONE:-0.1}" <<'PY'
import sys
path, version, milestone = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path, encoding="utf-8").read()
text = text.replace('VERSION="0.1.0"', f'VERSION="{version}"')
text = text.replace('VERSION_ID="0.1"', f'VERSION_ID="{milestone}"')
text = text.replace('PRETTY_NAME="NovaOS 0.1"', f'PRETTY_NAME="NovaOS {milestone}"')
text = text.replace("NovaOS 0.1 (Foundation)", f"NovaOS {milestone} (Foundation)")
text = text.replace("Welcome to NovaOS 0.1", f"Welcome to NovaOS {milestone}")
open(path, "w", encoding="utf-8").write(text)
print(f"Synced config.sh version strings to {version} / milestone {milestone}")
PY

echo "==> Running KIWI (this takes a long time)..."
set +e
set -x
"${KIWI_BIN}" --debug system build \
  --description "${DESC_WORK}" \
  --target-dir "${TARGET_DIR}" \
  2>&1 | tee "${LOG_FILE}"
kiwi_rc=${PIPESTATUS[0]}
set +x
set -e

if [[ "${kiwi_rc}" -ne 0 ]]; then
  echo "ERROR: kiwi build failed with exit code ${kiwi_rc}" >&2
  echo "See log: ${LOG_FILE}" >&2
  tail -n 80 "${LOG_FILE}" >&2 || true
  exit "${kiwi_rc}"
fi

mapfile -t ISOS < <(find "${TARGET_DIR}" -type f -name '*.iso' | sort)
if [[ "${#ISOS[@]}" -eq 0 ]]; then
  echo "ERROR: build finished but no .iso found under ${TARGET_DIR}" >&2
  echo "See log: ${LOG_FILE}" >&2
  ls -laR "${TARGET_DIR}" >&2 || true
  exit 1
fi

SRC_ISO="${ISOS[$((${#ISOS[@]} - 1))]}"
DEST_ISO="${RELEASE_DIR}/${ISO_BASENAME}.iso"
cp -f "${SRC_ISO}" "${DEST_ISO}"
cp -f "${DEST_ISO}" "${ROOT_ISO}"
"${ROOT}/scripts/sha256-iso.sh" "${DEST_ISO}"
cp -f "${DEST_ISO}.sha256" "${ROOT_ISO}.sha256"

cp -f "${DEST_ISO}" "${LATEST_DIR}/novaos-current.iso"
cp -f "${DEST_ISO}.sha256" "${LATEST_DIR}/novaos-current.iso.sha256"

cat > "${RELEASE_DIR}/${ISO_BASENAME}.buildinfo" <<EOF
novaos_version=${NOVAOS_VERSION}
fedora_version=${FEDORA_VERSION}
arch=${FEDORA_ARCH}
profile=${PROFILE}
built_at=${TS}
source_iso=${SRC_ISO}
dest_iso=${DEST_ISO}
root_iso=${ROOT_ISO}
log=${LOG_FILE}
kiwi=$(${KIWI_BIN} --version 2>/dev/null | head -n1 || echo unknown)
size_bytes=$(stat -c%s "${DEST_ISO}" 2>/dev/null || stat -f%z "${DEST_ISO}" 2>/dev/null || echo unknown)
EOF

echo
echo "==> BUILD OK"
echo "    ISO:  ${ROOT_ISO}"
echo "    COPY: ${DEST_ISO}"
echo "    SUM:  ${ROOT_ISO}.sha256"
echo "    LATE: ${LATEST_DIR}/novaos-current.iso"
echo "    Next: scripts/run-vm.sh ${ROOT_ISO}"
