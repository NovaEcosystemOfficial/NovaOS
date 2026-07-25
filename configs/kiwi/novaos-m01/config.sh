#!/bin/bash
# SPDX-License-Identifier: MIT
# Runs inside the image chroot during KIWI configure stage.
set -euxo pipefail

########################################
# Identity — NovaOS (not Fedora pretty name)
########################################
cat > /usr/lib/os-release <<'EOF'
NAME="NovaOS"
VERSION="0.1.0"
ID=novaos
ID_LIKE="fedora"
VERSION_ID="0.1"
PRETTY_NAME="NovaOS 0.1"
ANSI_COLOR="0;36"
HOME_URL="https://novaos.local"
DOCUMENTATION_URL="https://novaos.local"
SUPPORT_URL="https://novaos.local"
BUG_REPORT_URL="https://novaos.local"
LOGO="novaos"
VARIANT="Foundation"
VARIANT_ID="m01"
EOF
ln -sfn /usr/lib/os-release /etc/os-release

echo "NovaOS" > /etc/hostname

cat > /etc/issue <<'EOF'
NovaOS 0.1 (Foundation)
Kernel \r on an \m (\l)

EOF

cat > /etc/motd <<'EOF'
Welcome to NovaOS 0.1 — Foundation + Nova Identity (M1)
Public demo: autologin nova (Plasma X11). TTY: nova / novaos
VirtualBox: Graphics=VMSVGA, 3D Acceleration OFF.
VMware: VMware SVGA / open-vm-tools enabled.
Session log: /tmp/novaos-session.log and ~/.local/share/xorg/novaos-session.log
EOF

########################################
# Users — PUBLIC DEMO passwords (M0.1 only)
########################################
if ! id -u nova >/dev/null 2>&1; then
    useradd -m -U -G wheel,video,render,audio,input -s /bin/bash nova
else
    usermod -aG wheel,video,render,audio,input nova
fi

echo 'root:novaos' | chpasswd
echo 'nova:novaos' | chpasswd

mkdir -p /etc/sudoers.d
cat > /etc/sudoers.d/01-nova-wheel <<'EOF'
%wheel ALL=(ALL:ALL) ALL
EOF
chmod 440 /etc/sudoers.d/01-nova-wheel

chown -R nova:nova /home/nova
chmod 700 /home/nova
if command -v runuser >/dev/null 2>&1; then
    runuser -u nova -- xdg-user-dirs-update || true
else
    su -s /bin/bash nova -c 'xdg-user-dirs-update' || true
fi

# Runtime dir for uid 1000 (live images often race logind)
mkdir -p /etc/tmpfiles.d
cat > /etc/tmpfiles.d/novaos-runtime.conf <<'EOF'
d /run/user/1000 0700 nova nova -
EOF

########################################
# Graphics / session — VirtualBox & VMware
########################################
mkdir -p \
  /etc/xdg \
  /etc/xdg/plasma-workspace/env \
  /etc/profile.d \
  /etc/X11/xorg.conf.d \
  /etc/sddm.conf.d \
  /usr/local/libexec \
  /usr/share/xsessions \
  /etc/systemd/system/sddm.service.d \
  /etc/systemd/system \
  /var/lib/novaos \
  /etc/pam.d

chmod 755 /var/lib/novaos
chown nova:nova /var/lib/novaos || true

if [[ -f /etc/selinux/config ]]; then
    sed -i 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config || true
fi

# Bare-metal friendly defaults. VM soft-GL / QPainter is applied at *runtime*
# by novaos-safe-graphics.sh when systemd-detect-virt reports a hypervisor
# (config.sh runs in build chroot — cannot decide target HW here).
cat > /etc/xdg/kwinrc <<'EOF'
[Compositing]
Enabled=true
EOF

# M1 Nova Identity — branding defaults only (no session/graphics stack changes).
cat > /etc/xdg/kdeglobals <<'EOF'
[General]
ColorScheme=NovaOS

[KDE]
LookAndFeelPackage=org.novaos.desktop
EOF

cat > /etc/xdg/ksplashrc <<'EOF'
[KSplash]
Engine=KSplashQML
Theme=org.novaos.desktop
EOF

cat > /etc/xdg/baloofilerc <<'EOF'
[Basic Settings]
Indexing-Enabled=false
EOF

# Wallpaper comes from LookAndFeelPackage defaults (Image=NovaOS).
# Do not seed a truncated plasma-*.appletsrc — that can drop the stock panel.

# Seed demo user config so first-login Plasma/KWin cannot race empty homedir.
mkdir -p /home/nova/.config
cp -f /etc/xdg/kwinrc /home/nova/.config/kwinrc
cp -f /etc/xdg/kdeglobals /home/nova/.config/kdeglobals
cp -f /etc/xdg/ksplashrc /home/nova/.config/ksplashrc
cp -f /etc/xdg/baloofilerc /home/nova/.config/baloofilerc
chown -R nova:nova /home/nova/.config

rm -f /etc/X11/xorg.conf.d/10-novaos-vm.conf 2>/dev/null || true
cat > /etc/X11/xorg.conf.d/00-novaos-safe.conf <<'EOF'
Section "ServerFlags"
    Option "AutoAddGPU" "true"
EndSection
EOF

cat > /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh <<'EOF'
#!/bin/sh
# Runtime graphics policy:
# - Hypervisor (VirtualBox / VMware / QEMU): force software GL + QPainter-friendly env
# - Bare metal: leave Mesa/HW acceleration alone (M2 real-HW readiness)
export QT_QPA_PLATFORM=xcb
export KDE_FULL_SESSION=true
export XDG_CURRENT_DESKTOP=KDE
export XDG_SESSION_DESKTOP=KDE
export DESKTOP_SESSION=plasma

if command -v systemd-detect-virt >/dev/null 2>&1 && systemd-detect-virt -q 2>/dev/null; then
  export LIBGL_ALWAYS_SOFTWARE=1
  export GALLIUM_DRIVER=llvmpipe
  export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
  export KWIN_COMPOSE=Q
  export KWIN_OPENGL_IS_UNSAFE=1
fi
EOF
chmod 755 /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh
cp /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh /etc/profile.d/novaos-safe-graphics.sh

# Robust session wrapper:
# - log to /tmp FIRST (home may be late on live)
# - never re-exec $0 via dbus-run-session (that exited before any log)
# - ensure XDG_RUNTIME_DIR
# - keep X alive with xterm if Plasma dies
cat > /usr/local/libexec/novaos-plasma-x11 <<'EOF'
#!/bin/bash
# Early breadcrumb — must work even if HOME/XDG are broken.
echo "novaos-plasma-x11 invoke $(date -Is) uid=$(id -u) display=${DISPLAY:-<unset>} dbus=${DBUS_SESSION_BUS_ADDRESS:-<unset>}" >> /tmp/novaos-session.log 2>/dev/null || true

LOG_TMP=/tmp/novaos-session.log
LOG_HOME="${HOME:-/home/nova}/.local/share/xorg/novaos-session.log"
mkdir -p "${HOME:-/home/nova}/.local/share/xorg" 2>/dev/null || true
touch "${LOG_TMP}" 2>/dev/null || true
touch "${LOG_HOME}" 2>/dev/null || true

exec >>"${LOG_TMP}" 2>&1
echo "======== novaos session $(date -Is) ========"
echo "USER=$(id -un 2>/dev/null || echo ?) UID=$(id -u) HOME=${HOME:-?} SHELL=${SHELL:-?}"
echo "DISPLAY=${DISPLAY:-<unset>} XAUTHORITY=${XAUTHORITY:-<unset>}"
echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-?} XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-?}"
echo "DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-<unset>}"
id
ls -la "${XAUTHORITY:-/nonexistent}" 2>&1 || true

if [[ -z "${XDG_RUNTIME_DIR:-}" ]]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi
mkdir -p "${XDG_RUNTIME_DIR}" 2>/dev/null || true
chmod 700 "${XDG_RUNTIME_DIR}" 2>/dev/null || true

if [[ -f /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh ]]; then
  # shellcheck disable=SC1091
  source /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh
fi

env | sort | grep -E '^(DISPLAY|XAUTHORITY|XDG_|QT_|KWIN_|LIBGL_|DBUS_|GALLIUM_)' || true

if [[ -z "${DISPLAY:-}" ]]; then
  echo "ERROR: DISPLAY is empty — SDDM did not provide an X session"
  echo "FAIL:no-display $(date -Is)" > /var/lib/novaos/desktop.status 2>/dev/null || true
  cp -f "${LOG_TMP}" "${LOG_HOME}" 2>/dev/null || true
  cp -f "${LOG_TMP}" /var/lib/novaos/novaos-session.log 2>/dev/null || true
  exit 1
fi

# pam_systemd should set this; repair if a race left it empty.
if [[ -z "${DBUS_SESSION_BUS_ADDRESS:-}" && -S "${XDG_RUNTIME_DIR}/bus" ]]; then
  export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
  echo "Repaired DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS}"
fi

# Keep a lightweight heartbeat while Plasma is up (proves session liveness in logs).
(
  for _i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    sleep 2
    printf 'heartbeat t+%ss plasmashell=%s kwin=%s\n' "$((_i * 2))" \
      "$(pgrep -x plasmashell >/dev/null && echo yes || echo no)" \
      "$(pgrep -x kwin_x11 >/dev/null && echo yes || echo no)"
  done
) >>"${LOG_TMP}" 2>&1 &
hb_pid=$!

rc=127
if [[ -x /usr/bin/startplasma-x11 ]]; then
  echo "Starting startplasma-x11..."
  # Prefer stock binary; capture all output into the session log (already redirected).
  /usr/bin/startplasma-x11
  rc=$?
  echo "startplasma-x11 exited rc=${rc}"
else
  echo "ERROR: /usr/bin/startplasma-x11 missing"
fi
kill "${hb_pid}" 2>/dev/null || true
echo "---- pgrep after plasma exit ----"
pgrep -a -u "$(id -u)" || true
echo "---- journalctl user (plasma/kwin) ----"
journalctl --user -b --no-pager -n 120 2>&1 || true
journalctl -b --user-unit='plasma*' --no-pager -n 60 2>&1 || true
journalctl -b _UID="$(id -u)" --no-pager -p warning -n 80 2>&1 || true

echo "---- Xorg logs (tail) ----"
for f in "${HOME:-/home/nova}/.local/share/xorg/Xorg."*.log /var/log/Xorg.*.log; do
  [[ -f "$f" ]] || continue
  echo "== $f =="
  tail -n 80 "$f" || true
done

cp -f "${LOG_TMP}" "${LOG_HOME}" 2>/dev/null || true
cp -f "${LOG_TMP}" /var/lib/novaos/novaos-session.log 2>/dev/null || true

if [[ -x /usr/bin/xterm ]]; then
  echo "FAIL:plasma-exit-${rc} $(date -Is)" > /var/lib/novaos/desktop.status 2>/dev/null || true
  echo "Starting xterm fallback to retain graphical session..."
  # Mirror log to home again after fallback starts
  cp -f "${LOG_TMP}" "${LOG_HOME}" 2>/dev/null || true
  exec /usr/bin/xterm -fa Monospace -fs 12 -geometry 120x40 \
    -T "NovaOS fallback (Plasma failed rc=${rc})" \
    -e bash -lc "echo Plasma failed rc=${rc}; echo Log: ${LOG_TMP}; echo; tail -n 80 ${LOG_TMP}; echo; exec bash"
fi

echo "FAIL:no-fallback $(date -Is)" > /var/lib/novaos/desktop.status 2>/dev/null || true
exit "${rc}"
EOF
chmod 755 /usr/local/libexec/novaos-plasma-x11

# Breadcrumb for EVERY X session (runs before desktop Exec)
mkdir -p /etc/X11/xinit/xinitrc.d
cat > /etc/X11/xinit/xinitrc.d/00-novaos-breadcrumb.sh <<'EOF'
#!/bin/sh
mkdir -p /var/lib/novaos 2>/dev/null || true
echo "xinitrc $(date -Is) user=$(id -un) uid=$(id -u) display=${DISPLAY:-?} runtime=${XDG_RUNTIME_DIR:-?} dbus=${DBUS_SESSION_BUS_ADDRESS:-?}" \
  >> /var/lib/novaos/xinitrc.log 2>/dev/null || true
# Ensure runtime dir even if pam_systemd raced
if [ -z "${XDG_RUNTIME_DIR:-}" ]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
  mkdir -p "$XDG_RUNTIME_DIR" 2>/dev/null || true
  chmod 700 "$XDG_RUNTIME_DIR" 2>/dev/null || true
fi
EOF
chmod 755 /etc/X11/xinit/xinitrc.d/00-novaos-breadcrumb.sh

# Prefer stock Plasma Exec path (more reliable through SDDM Xsession than a custom wrapper).
# Keep wrapper available as novaos-plasma.desktop for manual selection / fallback.
cat > /usr/share/xsessions/novaos-plasma.desktop <<'EOF'
[Desktop Entry]
Type=XSession
Exec=/usr/local/libexec/novaos-plasma-x11
TryExec=/usr/local/libexec/novaos-plasma-x11
DesktopNames=KDE
Name=NovaOS Plasma (X11)
Comment=Plasma X11 with VM-safe graphics and session logging
EOF

# Hide Wayland Plasma
mkdir -p /usr/share/wayland-sessions/disabled
if [[ -f /usr/share/wayland-sessions/plasma.desktop ]]; then
    mv -f /usr/share/wayland-sessions/plasma.desktop \
          /usr/share/wayland-sessions/disabled/plasma.desktop
fi
rm -f /usr/share/sddm/scripts/wayland-session 2>/dev/null || true

# Ensure pam_systemd creates a proper user session (XDG_RUNTIME_DIR / logind)
for pamf in /etc/pam.d/sddm /etc/pam.d/sddm-autologin /etc/pam.d/sddm-greeter; do
  if [[ -f "${pamf}" ]] && ! grep -q 'pam_systemd.so' "${pamf}"; then
    echo 'session optional pam_systemd.so' >> "${pamf}"
  fi
done

# Fedora ships plasma-wayland.conf forcing Wayland greeter — breaks X11 VM sessions.
rm -f /usr/lib/sddm/sddm.conf.d/plasma-wayland.conf
# zz- prefix wins last-merge against other drop-ins
cat > /etc/sddm.conf.d/zz-novaos.conf <<'EOF'
[Autologin]
User=nova
Session=novaos-plasma.desktop
Relogin=false

[General]
DisplayServer=x11
Numlock=none
# Greeter keeps software GL for VM stability; user session is runtime-gated.
GreeterEnvironment=LIBGL_ALWAYS_SOFTWARE=1,QT_QPA_PLATFORM=xcb,GALLIUM_DRIVER=llvmpipe,KWIN_COMPOSE=Q

[Theme]
Current=novaos

[X11]
SessionCommand=/usr/share/sddm/scripts/Xsession
Session=novaos-plasma.desktop
ServerArguments=-nolisten tcp
DisplayCommand=/usr/share/sddm/scripts/Xsetup
DisplayStopCommand=/usr/share/sddm/scripts/Xstop

[Users]
MaximumUid=60000

[Wayland]
SessionCommand=/usr/share/sddm/scripts/wayland-session
EOF
rm -f /etc/sddm.conf.d/novaos.conf

cat > /usr/local/libexec/novaos-wait-graphics <<'EOF'
#!/bin/bash
# Wait for a usable DRM node or framebuffer so logind can create seat0.
for _ in $(seq 1 40); do
  if compgen -G '/dev/dri/card*' >/dev/null || compgen -G '/dev/dri/render*' >/dev/null || [[ -e /dev/fb0 ]]; then
    exit 0
  fi
  sleep 1
done
exit 0
EOF
chmod 755 /usr/local/libexec/novaos-wait-graphics

cat > /etc/systemd/system/sddm.service.d/novaos-delay.conf <<'EOF'
[Unit]
After=systemd-user-sessions.service
Wants=systemd-user-sessions.service

[Service]
# Wait for DRM/fb; hard Wants=dev-dri-card0 breaks when vmwgfx fails to bind.
ExecStartPre=/usr/local/libexec/novaos-wait-graphics
ExecStartPre=/bin/sleep 3
EOF

########################################
# Automated desktop verifier (serial + status file)
########################################
cat > /usr/local/libexec/novaos-desktop-verify <<'EOF'
#!/bin/bash
set -u
STATUS_DIR=/var/lib/novaos
mkdir -p "${STATUS_DIR}"
SERIAL=/dev/ttyS0
deadline=$((SECONDS + 180))
result=FAIL
detail=timeout

serial_line() {
  local line=$1
  printf '%s\n' "${line}" >> "${STATUS_DIR}/verify.log" 2>/dev/null || true
  printf '%s\n' "${line}" > "${SERIAL}" 2>/dev/null || true
  printf '%s\n' "${line}"
}

serial_line "NOVAOS_SMOKE_BEGIN $(date -Is)"

while (( SECONDS < deadline )); do
  if pgrep -u nova -x plasmashell >/dev/null 2>&1; then
    result=PASS
    detail=plasmashell
    break
  fi
  if pgrep -u nova -x kwin_x11 >/dev/null 2>&1 && pgrep -u nova -f 'plasma|startplasma' >/dev/null 2>&1; then
    result=PASS
    detail=kwin-plasma
    break
  fi
  if pgrep -u nova -x xterm >/dev/null 2>&1; then
    # Graphical session retained; Plasma failed — still FAIL for milestone, but classified.
    result=FAIL
    detail=xterm-fallback
    break
  fi
  if [[ -f /var/lib/novaos/novaos-session.log ]] && grep -q 'startplasma-x11 exited' /var/lib/novaos/novaos-session.log 2>/dev/null; then
    detail=plasma-exited
  elif [[ -f /tmp/novaos-session.log ]] && grep -q '======== novaos session' /tmp/novaos-session.log 2>/dev/null; then
    detail=session-script-ran
  elif [[ -f /var/lib/novaos/xinitrc.log ]]; then
    detail=xinitrc-ran
  fi
  sleep 2
done

{
  echo "result=${result}"
  echo "detail=${detail}"
  echo "date=$(date -Is)"
  echo "--- processes ---"
  ps -u nova -o pid,cmd 2>/dev/null || true
  echo "--- loginctl ---"
  loginctl list-sessions 2>/dev/null || true
  echo "--- sddm journal ---"
  journalctl -b -u sddm --no-pager -n 100 2>/dev/null || true
  echo "--- /tmp/novaos-session.log ---"
  if [[ -f /tmp/novaos-session.log ]]; then
    cat /tmp/novaos-session.log || true
  else
    echo "(missing)"
  fi
  echo "--- home session log ---"
  if [[ -f /home/nova/.local/share/xorg/novaos-session.log ]]; then
    cat /home/nova/.local/share/xorg/novaos-session.log || true
  else
    echo "(missing)"
  fi
  echo "--- xsession-errors ---"
  for f in /home/nova/.xsession-errors /home/nova/.cache/xsession-errors \
           /home/nova/.local/share/sddm/xorg-session.log; do
    [[ -f "$f" ]] || continue
    echo "== $f =="
    cat "$f" || true
  done
  echo "--- xinitrc breadcrumb ---"
  if [[ -f /var/lib/novaos/xinitrc.log ]]; then
    cat /var/lib/novaos/xinitrc.log || true
  else
    echo "(missing)"
  fi
  echo "--- journal nova uid ---"
  journalctl -b _UID=1000 --no-pager -n 80 2>/dev/null || true
  echo "--- sddm journal (autologin) ---"
  journalctl -b -u sddm --no-pager 2>/dev/null | grep -E 'autologin|Starting X11|nova|FAILED|Greeter' | tail -n 40 || true
  echo "--- Xorg ---"
  for f in /home/nova/.local/share/xorg/Xorg.*.log /var/log/Xorg.*.log /tmp/Xorg.*.log; do
    [[ -f "$f" ]] || continue
    echo "== $f =="
    tail -n 100 "$f" || true
  done
} > "${STATUS_DIR}/verify-report.txt" 2>&1 || true

echo "${result}:${detail}" > "${STATUS_DIR}/desktop.status"
serial_line "NOVAOS_SMOKE_RESULT ${result} detail=${detail}"
if [[ -r "${STATUS_DIR}/verify-report.txt" ]]; then
  serial_line "NOVAOS_SMOKE_REPORT_BEGIN"
  while IFS= read -r line || [[ -n "${line}" ]]; do
    serial_line "${line}"
  done < "${STATUS_DIR}/verify-report.txt"
  serial_line "NOVAOS_SMOKE_REPORT_END"
fi
serial_line "NOVAOS_SMOKE_END ${result}"

[[ "${result}" == "PASS" ]]
EOF
chmod 755 /usr/local/libexec/novaos-desktop-verify

cat > /etc/systemd/system/novaos-desktop-verify.service <<'EOF'
[Unit]
Description=NovaOS desktop smoke verifier
After=display-manager.service graphical.target
Wants=display-manager.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 10
ExecStart=/usr/local/libexec/novaos-desktop-verify
RemainAfterExit=yes
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=graphical.target
EOF
systemctl enable novaos-desktop-verify.service

########################################
# Services / VT ownership
########################################
systemctl enable sddm.service
systemctl enable NetworkManager.service
systemctl enable bluetooth.service 2>/dev/null || true
systemctl enable upower.service 2>/dev/null || true
systemctl enable power-profiles-daemon.service 2>/dev/null || true
systemctl set-default graphical.target

# Do NOT mask getty@tty1 — that can prevent logind from creating a graphical seat0,
# which makes SDDM skip autologin. SDDM already Conflicts=getty@tty1.service.
systemctl disable serial-getty@ttyS0.service 2>/dev/null || true
systemctl mask serial-getty@ttyS0.service 2>/dev/null || true

systemctl enable vmtoolsd.service 2>/dev/null || true
systemctl enable vgauthd.service 2>/dev/null || true
systemctl enable open-vm-tools.service 2>/dev/null || true
systemctl enable spice-vdagentd.service 2>/dev/null || true

systemctl enable vboxservice.service 2>/dev/null || true
systemctl disable vboxclient.service 2>/dev/null || true
systemctl mask vboxclient.service 2>/dev/null || true
rm -f /etc/xdg/autostart/vboxclient.desktop 2>/dev/null || true
# CRITICAL: Xsession *sources* xinitrc.d scripts. A bare `exit` here aborts the
# whole session before Exec= (Plasma never starts → return to greeter/console).
if [[ -f /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh ]]; then
    cat > /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh <<'EOF'
#!/bin/sh
# NovaOS: do not start VBoxClient; never `exit` (this file is sourced).
return 0 2>/dev/null || true
EOF
    chmod 755 /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh
fi
# Guard any other xinitrc.d snippets that might `exit` when sourced.
for _xs in /etc/X11/xinit/xinitrc.d/*; do
  [[ -f "${_xs}" ]] || continue
  if grep -qE '^[[:space:]]*exit([[:space:]]|$)' "${_xs}" 2>/dev/null; then
    sed -i -E 's/^[[:space:]]*exit([[:space:]]+.*)?$/return 0 2>\/dev\/null || true/' "${_xs}" || true
  fi
done
for stub in VBoxDRMClient VBoxClient VBoxClient-all; do
  if [[ -x "/usr/bin/${stub}" ]]; then
    mkdir -p /usr/local/bin
    cat > "/usr/local/bin/${stub}" <<'EOF'
#!/bin/sh
exit 0
EOF
    chmod 755 "/usr/local/bin/${stub}"
  fi
done

echo 'LANG=en_US.UTF-8' > /etc/locale.conf

systemctl disable nova-ryuk.service 2>/dev/null || true
systemctl disable nova-ai-core.service 2>/dev/null || true

# Hard requirement: without pam_systemd, SDDM sessions have no XDG_RUNTIME_DIR/D-Bus.
if [[ ! -e /usr/lib64/security/pam_systemd.so && ! -e /lib64/security/pam_systemd.so ]]; then
    echo "ERROR: pam_systemd.so missing — install systemd-pam" >&2
    exit 1
fi
if ! command -v dbus-launch >/dev/null 2>&1 && [[ ! -x /usr/bin/dbus-launch ]]; then
    echo "ERROR: dbus-launch missing — install dbus-x11" >&2
    exit 1
fi

########################################
# M2.2 Developer Edition — workspace / browser (reversible overlay + seeds)
########################################
chmod 755 /usr/local/bin/setup-dev.sh 2>/dev/null || true
chmod 755 /usr/local/libexec/novaos-seed-dev-favorites 2>/dev/null || true

# System-wide MIME defaults are in /etc/xdg/mimeapps.list (overlay).
# Seed per-user copy + Desktop launcher so menu/panel/desktop all expose Firefox.
mkdir -p /home/nova/.config /home/nova/Desktop /etc/skel/Desktop /etc/skel/.config
if [[ -f /etc/xdg/mimeapps.list ]]; then
    cp -f /etc/xdg/mimeapps.list /home/nova/.config/mimeapps.list
    cp -f /etc/xdg/mimeapps.list /etc/skel/.config/mimeapps.list
fi
if [[ -f /usr/share/applications/firefox.desktop ]]; then
    cp -f /usr/share/applications/firefox.desktop /home/nova/Desktop/firefox.desktop
    cp -f /usr/share/applications/firefox.desktop /etc/skel/Desktop/firefox.desktop
    chmod 755 /home/nova/Desktop/firefox.desktop /etc/skel/Desktop/firefox.desktop
fi

if command -v flatpak >/dev/null 2>&1; then
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
fi

# OpenSSH available for developer remotes (password login remains demo-only).
systemctl enable sshd.service 2>/dev/null || true

if command -v runuser >/dev/null 2>&1; then
    runuser -u nova -- bash -lc 'xdg-settings set default-web-browser firefox.desktop' 2>/dev/null || true
    runuser -u nova -- /usr/local/bin/setup-dev.sh || true
else
    su -s /bin/bash nova -c 'xdg-settings set default-web-browser firefox.desktop' 2>/dev/null || true
    su -s /bin/bash nova -c '/usr/local/bin/setup-dev.sh' || true
fi

# Convenience: neofetch → fastfetch when only fastfetch is shipped.
if [[ ! -e /usr/local/bin/neofetch ]] && command -v fastfetch >/dev/null 2>&1; then
    ln -sfn "$(command -v fastfetch)" /usr/local/bin/neofetch
fi

chown -R nova:nova /home/nova

# Static presence checks (fail image build if toolchain incomplete).
for cmd in firefox git ssh curl wget unzip zip gcc g++ make cmake python3 \
           node npm flatpak htop fastfetch; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "ERROR: M2.2 required command missing: ${cmd}" >&2
        exit 1
    fi
done
if ! command -v pip3 >/dev/null 2>&1 && ! command -v pip >/dev/null 2>&1; then
    if ! python3 -m pip --version >/dev/null 2>&1; then
        echo "ERROR: M2.2 required command missing: pip/pip3" >&2
        exit 1
    fi
fi
test -d /home/nova/NovaWorkspace/NovaOS
test -x /usr/local/bin/setup-dev.sh

exit 0
