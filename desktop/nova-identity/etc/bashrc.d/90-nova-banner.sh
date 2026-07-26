# NovaOS interactive bash banner (once per shell)
# Installed to /etc/bashrc.d and /etc/skel/.bashrc.d

case $- in
  *i*) ;;
  *) return 0 2>/dev/null || exit 0 ;;
esac

if [ -n "${NOVA_BANNER_SHOWN:-}" ]; then
  return 0 2>/dev/null || true
fi
NOVA_BANNER_SHOWN=1

if command -v nova-version >/dev/null 2>&1; then
  _nova_ver="$(nova-version 2>/dev/null || true)"
else
  _nova_ver="NovaOS"
fi

printf '\n'
printf '  \033[1;36mNovaOS\033[0m — %s\n' "${_nova_ver}"
printf '  Digita \033[1mnova-about\033[0m per l’identità completa.\n'
printf '\n'
unset _nova_ver
