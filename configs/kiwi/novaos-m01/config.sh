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
Scope: bootable base (Plasma + SDDM). No Ryuk / Nova AI / Nova Shell product yet.
Default user: nova  password: novaos
EOF

########################################
# Users & credentials (dev / M0.1)
########################################
if ! id -u nova >/dev/null 2>&1; then
    useradd -m -U -G wheel,video,audio,input -s /bin/bash nova
fi

echo 'root:novaos' | chpasswd
echo 'nova:novaos' | chpasswd

mkdir -p /etc/sudoers.d
cat > /etc/sudoers.d/01-nova-wheel <<'EOF'
%wheel ALL=(ALL:ALL) ALL
EOF
chmod 440 /etc/sudoers.d/01-nova-wheel

########################################
# Session: SDDM + graphical target
########################################
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/novaos.conf <<'EOF'
[General]
DisplayServer=x11

[Theme]
Current=breeze

[Users]
MaximumUid=60000
EOF

systemctl enable sddm.service
systemctl enable NetworkManager.service
systemctl set-default graphical.target

########################################
# Locale
########################################
echo 'LANG=en_US.UTF-8' > /etc/locale.conf

########################################
# First-boot safety: no AI/Ryuk units (none shipped)
########################################
# Explicitly ensure we do not enable hypothetical future units
systemctl disable nova-ryuk.service 2>/dev/null || true
systemctl disable nova-ai-core.service 2>/dev/null || true

exit 0
