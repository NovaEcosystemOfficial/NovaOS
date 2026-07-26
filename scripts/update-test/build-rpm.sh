#!/usr/bin/env bash
# Build an RPM from packages/SPECS/<name>.spec using update-test rpmbuild toolchain.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_NAME="${1:?usage: build-rpm.sh <spec-basename> [version]}"
VERSION_OVERRIDE="${2:-}"

WORK="${ROOT}/build/work/update-test"
TOP="${WORK}/rpmbuild"
TOOLS_ENV="${NOVA_UPDATE_TEST_TOOLS:-${WORK}/host-tools}/env.sh"
SPEC_SRC="${ROOT}/packages/SPECS/${SPEC_NAME}.spec"

[[ -f "${SPEC_SRC}" ]] || { echo "ERROR: missing ${SPEC_SRC}" >&2; exit 1; }

if [[ ! -f "${TOOLS_ENV}" ]]; then
  bash "${ROOT}/scripts/update-test/bootstrap-update-test-tools.sh"
fi
# shellcheck disable=SC1090
source "${TOOLS_ENV}"

mkdir -p "${TOP}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
SPEC="${TOP}/SPECS/${SPEC_NAME}.spec"
cp -f "${SPEC_SRC}" "${SPEC}"
if [[ -n "${VERSION_OVERRIDE}" ]]; then
  sed -i -e "s/^Version:.*/Version:        ${VERSION_OVERRIDE}/" "${SPEC}"
fi

echo "==> rpmbuild ${SPEC_NAME}"
rpmbuild \
  --define "_topdir ${TOP}" \
  --define "_nova_root ${ROOT}" \
  --define "dist .nova" \
  --define "_build_id_links none" \
  --define "__brp_compress %{nil}" \
  --define "__brp_strip %{nil}" \
  --define "__brp_strip_static_archive %{nil}" \
  --define "__brp_strip_comment_note %{nil}" \
  --define "__brp_remove_la_files %{nil}" \
  ${NOVA_RPMCONFIGDIR:+--define "_rpmconfigdir ${NOVA_RPMCONFIGDIR}"} \
  -bb "${SPEC}"

RPM="$(find "${TOP}/RPMS" -name "${SPEC_NAME}-*.rpm" | sort | tail -1)"
[[ -n "${RPM}" && -f "${RPM}" ]] || { echo "ERROR: rpm not produced" >&2; exit 1; }
mkdir -p "${WORK}/artifacts"
cp -f "${RPM}" "${WORK}/artifacts/"
echo "PASS — ${RPM}"
echo "${RPM}"
