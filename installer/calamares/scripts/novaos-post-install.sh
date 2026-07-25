#!/bin/bash
# SPDX-License-Identifier: MIT
# Runs inside the *target* system chroot during Calamares exec.
# Makes the installed system distinct from the live demo personality.
set -euo pipefail

log() { printf 'novaos-post-install: %s\n' "$*"; }

log "start"

########################################
# Marker: installed (not live)
########################################
mkdir -p /etc/novaos /var/lib/novaos
cat > /etc/novaos/install-state <<'EOF'
mode=installed
installer=calamares
milestone=0.2
EOF
chmod 644 /etc/novaos/install-state

########################################
# Identity — bump VARIANT for installed systems
########################################
if [[ -f /usr/lib/os-release ]]; then
  sed -i \
    -e 's/^VARIANT=.*/VARIANT="Installable"/' \
    -e 's/^VARIANT_ID=.*/VARIANT_ID="m02"/' \
    /usr/lib/os-release || true
  ln -sfn /usr/lib/os-release /etc/os-release
fi

########################################
# SDDM — no autologin; X11 Plasma session
########################################
mkdir -p /etc/sddm.conf.d
rm -f /etc/sddm.conf.d/zz-novaos.conf
cat > /etc/sddm.conf.d/zz-novaos-installed.conf <<'EOF'
[Autologin]
User=
Session=
Relogin=false

[General]
DisplayServer=x11
Numlock=none

[Theme]
Current=breeze

[X11]
SessionCommand=/usr/share/sddm/scripts/Xsession
Session=novaos-plasma.desktop
ServerArguments=-nolisten tcp
EOF
chmod 644 /etc/sddm.conf.d/zz-novaos-installed.conf

########################################
# Disable live-only smoke verifier
########################################
systemctl disable novaos-desktop-verify.service 2>/dev/null || true
systemctl mask novaos-desktop-verify.service 2>/dev/null || true
rm -f /etc/systemd/system/graphical.target.wants/novaos-desktop-verify.service 2>/dev/null || true

########################################
# Dual-boot: always run os-prober from grub-mkconfig
########################################
mkdir -p /etc/default/grub.d
cat > /etc/default/grub.d/40-novaos-os-prober.cfg <<'EOF'
# NovaOS: detect other OS (Windows, other Linux) for dual-boot menus.
GRUB_DISABLE_OS_PROBER=false
EOF
chmod 644 /etc/default/grub.d/40-novaos-os-prober.cfg

if [[ -f /etc/default/grub ]]; then
  if grep -q '^GRUB_DISABLE_OS_PROBER=' /etc/default/grub; then
    sed -i 's/^GRUB_DISABLE_OS_PROBER=.*/GRUB_DISABLE_OS_PROBER=false/' /etc/default/grub
  else
    echo 'GRUB_DISABLE_OS_PROBER=false' >> /etc/default/grub
  fi
fi

########################################
# Bare-metal graphics: drop forced software GL
# (Live ISO keeps VM-safe overrides; installed systems use real GPU.)
########################################
rm -f /etc/xdg/plasma-workspace/env/novaos-safe-graphics.sh
rm -f /etc/profile.d/novaos-safe-graphics.sh
if [[ -f /etc/xdg/kwinrc ]]; then
  sed -i \
    -e 's/^OpenGLIsUnsafe=.*/OpenGLIsUnsafe=false/' \
    -e 's/^Backend=.*/Backend=OpenGL/' \
    /etc/xdg/kwinrc || true
fi

########################################
# MOTD / issue for installed systems
########################################
cat > /etc/motd <<'EOF'
Welcome to NovaOS (installed)
Use your installer account. Development tools: gcc, make, git, cmake.
EOF

cat > /etc/issue <<'EOF'
NovaOS \S
Kernel \r on an \m (\l)

EOF

########################################
# Remove live demo leftovers if still present
########################################
if id -u nova >/dev/null 2>&1; then
  log "removing leftover demo user nova"
  userdel -r nova 2>/dev/null || userdel nova 2>/dev/null || true
fi
rm -f /etc/tmpfiles.d/novaos-runtime.conf 2>/dev/null || true

########################################
# Remove installer packages from target (offline-safe)
########################################
if command -v rpm >/dev/null 2>&1; then
  rpm -e --nodeps calamares calamares-libs 2>/dev/null || true
fi
rm -rf /etc/calamares /usr/share/calamares/branding/novaos 2>/dev/null || true
rm -f /usr/share/applications/novaos-installer.desktop 2>/dev/null || true
rm -f /usr/share/applications/calamares.desktop 2>/dev/null || true
rm -f /usr/sbin/novaos-post-install.sh 2>/dev/null || true

########################################
# Ensure critical services
########################################
systemctl enable NetworkManager.service 2>/dev/null || true
systemctl enable sddm.service 2>/dev/null || true
systemctl set-default graphical.target 2>/dev/null || true

log "done"
exit 0
