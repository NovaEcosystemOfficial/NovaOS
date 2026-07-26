#!/usr/bin/env bash
# Build hello-nova-update RPM (version from arg or 1.0.0).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-1.0.0}"
RELEASE="${2:-1}"
CHANNEL="${3:-stable}"

WORK="${ROOT}/build/work/update-test"
TOP="${WORK}/rpmbuild"
SPEC_SRC="${ROOT}/packages/test/hello-nova-update/hello-nova-update.spec"
TOOLS_ENV="${NOVA_UPDATE_TEST_TOOLS:-${WORK}/host-tools}/env.sh"

if [[ ! -f "${TOOLS_ENV}" ]]; then
  bash "${ROOT}/scripts/update-test/bootstrap-update-test-tools.sh"
fi
# shellcheck disable=SC1090
source "${TOOLS_ENV}"

mkdir -p "${TOP}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
SPEC="${TOP}/SPECS/hello-nova-update.spec"
cp -f "${SPEC_SRC}" "${SPEC}"
# Pin version/release for this build
sed -i \
  -e "s/^Version:.*/Version:        ${VERSION}/" \
  -e "s/^Release:.*/Release:        ${RELEASE}%{?dist}/" \
  "${SPEC}"

echo "==> Building hello-nova-update-${VERSION}-${RELEASE}"
rpmbuild \
  --define "_topdir ${TOP}" \
  --define "dist .nova" \
  --define "_build_id_links none" \
  --define "__brp_compress %{nil}" \
  --define "__brp_strip %{nil}" \
  --define "__brp_strip_static_archive %{nil}" \
  --define "__brp_strip_comment_note %{nil}" \
  --define "__brp_remove_la_files %{nil}" \
  ${NOVA_RPMCONFIGDIR:+--define "_rpmconfigdir ${NOVA_RPMCONFIGDIR}"} \
  -bb "${SPEC}"

RPM="$(find "${TOP}/RPMS" -name "hello-nova-update-${VERSION}-${RELEASE}*.rpm" | head -1)"
[[ -n "${RPM}" && -f "${RPM}" ]] || { echo "ERROR: rpm not produced" >&2; exit 1; }
rpm -qp "${RPM}" >/dev/null

OUT_DIR="${WORK}/artifacts"
mkdir -p "${OUT_DIR}"
cp -f "${RPM}" "${OUT_DIR}/"
echo "PASS — built ${RPM}"
echo "${RPM}"
