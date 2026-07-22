#!/usr/bin/env bash
# Static validation of the NovaOS build pipeline (no root, no network build).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

err=0
pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*" >&2; err=1; }

echo "==> validate-pipeline (static)"
echo "    root=${NOVAOS_ROOT}"
echo

# 1) Workspace lint
if bash "${NOVAOS_ROOT}/tools/lint/lint-workspace.sh"; then
  pass "lint-workspace"
else
  fail "lint-workspace"
fi

# 2) release.env
if novaos_load_release_env; then
  pass "release.env loads (profile=${NOVAOS_PROFILE} fedora=${FEDORA_VERSION})"
else
  fail "release.env"
  echo "validate-pipeline: FAILED"
  exit 1
fi

DESC="${NOVAOS_CONFIG_DIR}/kiwi/${NOVAOS_PROFILE}"

# 3) Profile directory matches release.env
if [[ ! -d "${DESC}" ]]; then
  fail "profile dir missing: ${DESC}"
else
  pass "profile dir ${NOVAOS_PROFILE}"
fi

# 4) XML
if command -v xmllint >/dev/null 2>&1; then
  if xmllint --noout "${DESC}/appliance.kiwi"; then
    pass "appliance.kiwi XML"
  else
    fail "appliance.kiwi XML"
  fi
else
  # Minimal tag balance check without xmllint
  if grep -q '<image ' "${DESC}/appliance.kiwi" && grep -q '</image>' "${DESC}/appliance.kiwi"; then
    pass "appliance.kiwi has image tags (xmllint unavailable)"
  else
    fail "appliance.kiwi structure"
  fi
fi

# 5) Cross refs inside appliance
for needle in iso-esp-excludes.yaml dracut-kiwi-live sddm plasma-desktop konsole plasma-systemsettings; do
  if grep -q "${needle}" "${DESC}/appliance.kiwi"; then
    pass "appliance contains ${needle}"
  else
    fail "appliance missing ${needle}"
  fi
done

# 6) Metalink pin script dry-run
tmp="$(mktemp)"
cp "${DESC}/appliance.kiwi" "${tmp}"
if python3 - "${tmp}" "${FEDORA_VERSION}" "${FEDORA_ARCH}" <<'PY'
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
    raise SystemExit(1)
open(path, "w", encoding="utf-8").write(text3)
PY
then
  pass "metalink pin logic"
else
  fail "metalink pin logic"
fi
rm -f "${tmp}"

# 7) config.sh sanity
if grep -q 'systemctl enable sddm' "${DESC}/config.sh" \
  && grep -q 'PRETTY_NAME="NovaOS' "${DESC}/config.sh" \
  && grep -q "chpasswd" "${DESC}/config.sh"; then
  pass "config.sh identity/session hooks"
else
  fail "config.sh incomplete"
fi

# 8) Scripts shebang + source common
for s in setup-build-host.sh check-env.sh build-iso.sh run-vm.sh clean-build.sh sha256-iso.sh; do
  f="${NOVAOS_ROOT}/scripts/${s}"
  if head -n1 "${f}" | grep -qE '^#!/(usr/)?bin/(env )?bash'; then
    pass "shebang ${s}"
  else
    fail "shebang ${s}"
  fi
done

for s in setup-build-host.sh check-env.sh build-iso.sh run-vm.sh clean-build.sh; do
  if grep -q 'scripts/lib/common.sh' "${NOVAOS_ROOT}/scripts/${s}"; then
    pass "sources common.sh: ${s}"
  else
    fail "missing common.sh source: ${s}"
  fi
done

# 9) Host package list: critical names
if grep -qx 'kiwi-systemdeps-iso-media' "${NOVAOS_CONFIG_DIR}/bootstrap/host-packages.txt"; then
  pass "host-packages has kiwi-systemdeps-iso-media"
else
  fail "host-packages must list kiwi-systemdeps-iso-media (not kiwi-systemdeps-iso)"
fi
if grep -qE '^kiwi-systemdeps-iso$' "${NOVAOS_CONFIG_DIR}/bootstrap/host-packages.txt"; then
  fail "host-packages still lists obsolete kiwi-systemdeps-iso"
fi

# 10) Makefile targets
for t in setup check iso vm clean lint validate; do
  if grep -qE "^${t}:" "${NOVAOS_ROOT}/Makefile"; then
    pass "Makefile target ${t}"
  else
    fail "Makefile missing target ${t}"
  fi
done

# 11) build-iso separates desc vs out dirs
if grep -q 'desc-\${PROFILE}' "${NOVAOS_ROOT}/scripts/build-iso.sh" \
  || grep -q 'desc-${PROFILE}' "${NOVAOS_ROOT}/scripts/build-iso.sh"; then
  pass "build-iso separates description workdir"
else
  # pattern in file is desc-${PROFILE}-${TS}
  if grep -q 'DESC_WORK=' "${NOVAOS_ROOT}/scripts/build-iso.sh" \
    && grep -q 'TARGET_DIR=' "${NOVAOS_ROOT}/scripts/build-iso.sh"; then
    pass "build-iso has DESC_WORK and TARGET_DIR"
  else
    fail "build-iso description/target separation"
  fi
fi

echo
if [[ "${err}" -ne 0 ]]; then
  echo "validate-pipeline: FAILED (${err} groups)"
  exit 1
fi
echo "validate-pipeline: PASSED — pipeline ready for first build on a Fedora host"
exit 0
