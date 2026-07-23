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
Welcome to NovaOS 0.1 — Foundation Boot
Public demo: autologin nova (Plasma X11). TTY: nova / novaos
VirtualBox: Graphics=VMSVGA, 3D Acceleration OFF. VBoxDRMClient disabled in image.
Session log: ~/.local/share/xorg/novaos-session.log
EOF

########################################
# Users — PUBLIC DEMO passwords (M0.1 only)
########################################
# KIWI may create "nova" before this script runs (appliance.kiwi <users>).
# Always ensure groups: without video/render, X11/Plasma fails and SDDM loops.
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

########################################
# Graphics / session — VirtualBox & VMware black-screen mitigations
########################################
mkdir -p \
  /etc/xdg \
  /etc/xdg/plasma-workspace/env \
  /etc/profile.d \
  /etc/X11/xorg.conf.d \
  /etc/sddm.conf.d \
  /usr/local/libexec \
  /usr/share/xsessions \
  /etc/systemd/system/sddm.service.d

# SELinux permissive on live M0.1 (avoids session denials on overlay FS)
if [[ -f /etc/selinux/config ]]; then
    sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config || true
fi

# No OpenGL compositor — OpenGL paths black-screen in many VMs
cat > /etc/xdg/kwinrc <<'EOF'
[Compositing]
Enabled=false
OpenGLIsUnsafe=true
Backend=QPainter
EOF

# Default plasma look
cat > /etc/xdg/kdeglobals <<'EOF'
[General]
ColorScheme=BreezeLight

[KDE]
LookAndFeelPackage=org.kde.breeze.desktop
EOF

# Do not force an xorg Device section: AccelMethod=none broke user X sessions
# in VirtualBox while the greeter still worked.
rm -f /etc/X11/xorg.conf.d/10-novaos-vm.conf 2>/dev/null || true

cat > /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh <<'EOF'
#!/bin/sh
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QUICK_BACKEND=software
export QT_QPA_PLATFORM=xcb
export QT_XCB_GL_INTEGRATION=none
export KWIN_COMPOSE=N
EOF
chmod 755 /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh
cp /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh /etc/profile.d/novaos-safe-graphics.sh

# Session wrapper: log everything; fall back to xterm if Plasma dies
cat > /usr/local/libexec/novaos-plasma-x11 <<'EOF'
#!/bin/bash
set -u
LOGDIR="${HOME}/.local/share/xorg"
mkdir -p "${LOGDIR}"
LOG="${LOGDIR}/novaos-session.log"
cp_log() { cp -f "${LOG}" /tmp/novaos-session.log 2>/dev/null || true; }
exec >>"${LOG}" 2>&1
echo "======== novaos session $(date -Is) ========"
echo "USER=${USER:-?} HOME=${HOME:-?} DISPLAY=${DISPLAY:-?} XAUTH=${XAUTHORITY:-?} XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-?}"
# shellcheck disable=SC1091
source /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh
env | sort | grep -E '^(DISPLAY|XAUTHORITY|XDG_|QT_|KWIN_|LIBGL_|DBUS_)' || true
ls -la "${XAUTHORITY:-/nonexistent}" 2>&1 || true

if [[ -z "${DISPLAY:-}" ]]; then
  echo "ERROR: DISPLAY is empty — SDDM did not provide an X session"
  cp_log
  exit 1
fi

if [[ -x /usr/bin/startplasma-x11 ]]; then
  echo "Starting startplasma-x11..."
  /usr/bin/startplasma-x11
  rc=$?
  echo "startplasma-x11 exited rc=${rc}"
else
  echo "ERROR: /usr/bin/startplasma-x11 missing"
  rc=127
fi

echo "---- Xorg logs (tail) ----"
for f in "${HOME}/.local/share/xorg/Xorg."*.log /var/log/Xorg.*.log; do
  [[ -f "$f" ]] || continue
  echo "== $f =="
  tail -n 40 "$f" || true
done
cp_log

if [[ -x /usr/bin/xterm ]]; then
  echo "Starting xterm fallback..."
  exec /usr/bin/xterm -fa Monospace -fs 12 -geometry 120x40 \
    -T "NovaOS fallback (Plasma failed rc=${rc})" \
    -e bash -lc "echo Plasma failed rc=${rc}; echo Log: ${LOG}; echo; tail -n 80 ${LOG}; echo; exec bash"
fi
exit "${rc}"
EOF
chmod 755 /usr/local/libexec/novaos-plasma-x11

cat > /usr/share/xsessions/novaos-plasma.desktop <<'EOF'
[Desktop Entry]
Type=XSession
Exec=/usr/local/libexec/novaos-plasma-x11
TryExec=/usr/local/libexec/novaos-plasma-x11
DesktopNames=KDE
Name=NovaOS Plasma (X11)
Comment=Plasma X11 with VM-safe graphics and session logging
EOF

# Hide Wayland Plasma (greeter was offering "Plasma" = Wayland)
mkdir -p /usr/share/wayland-sessions/disabled
if [[ -f /usr/share/wayland-sessions/plasma.desktop ]]; then
    mv -f /usr/share/wayland-sessions/plasma.desktop \
          /usr/share/wayland-sessions/disabled/plasma.desktop
fi
rm -f /usr/share/sddm/scripts/wayland-session 2>/dev/null || true

cat > /etc/sddm.conf.d/novaos.conf <<'EOF'
[Autologin]
User=nova
Session=novaos-plasma.desktop
Relogin=false

[General]
DisplayServer=x11
GreeterEnvironment=LIBGL_ALWAYS_SOFTWARE=1,QT_QUICK_BACKEND=software,QT_QPA_PLATFORM=xcb,QT_XCB_GL_INTEGRATION=none

[Theme]
Current=breeze

[X11]
Session=novaos-plasma.desktop
ServerArguments=-nolisten tcp -dpi 96

[Users]
MaximumUid=60000
EOF

# Give DRM/modeset a moment before greeter/autologin
mkdir -p /etc/systemd/system/sddm.service.d
cat > /etc/systemd/system/sddm.service.d/novaos-delay.conf <<'EOF'
[Service]
ExecStartPre=/bin/sleep 2
EOF

########################################
# Services
########################################
systemctl enable sddm.service
systemctl enable NetworkManager.service
systemctl set-default graphical.target

# serial-getty flaps without a serial port and floods VT audit noise
systemctl disable serial-getty@ttyS0.service 2>/dev/null || true
systemctl mask serial-getty@ttyS0.service 2>/dev/null || true

systemctl enable vmtoolsd.service 2>/dev/null || true
systemctl enable vgauthd.service 2>/dev/null || true
systemctl enable open-vm-tools.service 2>/dev/null || true
systemctl enable spice-vdagentd.service 2>/dev/null || true

# VirtualBox: keep VBoxService; disable VBoxClient/VBoxDRMClient (black screen)
systemctl enable vboxservice.service 2>/dev/null || true
systemctl disable vboxclient.service 2>/dev/null || true
systemctl mask vboxclient.service 2>/dev/null || true
rm -f /etc/xdg/autostart/vboxclient.desktop 2>/dev/null || true
if [[ -f /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh ]]; then
    cat > /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh <<'EOF'
#!/bin/sh
# NovaOS M0.1: VBoxClient/VBoxDRMClient disabled (VERR_INVALID_PARAMETER black screen).
exit 0
EOF
    chmod 755 /etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh
fi
if [[ -x /usr/bin/VBoxDRMClient ]]; then
    mkdir -p /usr/local/bin
    cat > /usr/local/bin/VBoxDRMClient <<'EOF'
#!/bin/sh
# Stubbed: real VBoxDRMClient causes VirtualBox display black-screens on this image.
exit 0
EOF
    chmod 755 /usr/local/bin/VBoxDRMClient
fi
if [[ -x /usr/bin/VBoxClient ]]; then
    mkdir -p /usr/local/bin
    cat > /usr/local/bin/VBoxClient <<'EOF'
#!/bin/sh
# Stubbed for M0.1 live: skip all VBoxClient features including DRM display pushes.
exit 0
EOF
    chmod 755 /usr/local/bin/VBoxClient
fi
if [[ -x /usr/bin/VBoxClient-all ]]; then
    mkdir -p /usr/local/bin
    cat > /usr/local/bin/VBoxClient-all <<'EOF'
#!/bin/sh
exit 0
EOF
    chmod 755 /usr/local/bin/VBoxClient-all
fi

echo 'LANG=en_US.UTF-8' > /etc/locale.conf

systemctl disable nova-ryuk.service 2>/dev/null || true
systemctl disable nova-ai-core.service 2>/dev/null || true

exit 0
