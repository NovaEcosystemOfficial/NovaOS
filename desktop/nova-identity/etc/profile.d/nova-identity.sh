# NovaOS interactive shell identity (bash / zsh via profile.d)
# Sourced for login shells; bashrc.d handles interactive non-login.

if [ -n "${NOVA_IDENTITY_LOADED:-}" ]; then
  return 0 2>/dev/null || true
fi
NOVA_IDENTITY_LOADED=1

export NOVA_ASSETS="${NOVA_ASSETS:-/usr/share/nova/assets}"
export NOVA_IDENTITY_VERSION="${NOVA_IDENTITY_VERSION:-0.2.7}"

# Prefer NovaOS hostname in prompts
_nova_host="$(hostname -s 2>/dev/null || echo novaos)"

# Bash / generic PS1 — Nova branded
if [ -n "${BASH_VERSION:-}" ]; then
  # shellcheck disable=SC2154
  PS1='\[\e[1;36m\]NovaOS\[\e[0m\] \[\e[1;34m\]\u@'"${_nova_host}"'\[\e[0m\] \[\e[1;32m\]\w\[\e[0m\] \$ '
  export PS1
elif [ -n "${ZSH_VERSION:-}" ]; then
  PROMPT='%F{cyan}NovaOS%f %F{blue}%n@'"${_nova_host}"'%f %F{green}%~%f %# '
  export PROMPT
fi
