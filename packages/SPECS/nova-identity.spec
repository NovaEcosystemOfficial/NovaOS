Name:           nova-identity
Version:        0.2.6
Release:        1%{?dist}
Summary:        NovaOS Identity — branding assets, terminal, and CLI tools
License:        MIT
URL:            https://github.com/novaos/NovaOS
BuildArch:      noarch
Requires:       python3 >= 3.11
Recommends:     nova-platform >= 0.2.5
Recommends:     nova-desktop
Recommends:     konsole
Provides:       nova-branding-assets = %{version}-%{release}

%description
Sprint 20 — Nova Identity. Centralizes NovaOS visual identity under
/usr/share/nova/assets (logo, icons, colors, fonts, wallpaper, splash),
customizes the terminal (prompt, Konsole profile, banner), and ships
nova-about / nova-info / nova-version / nova-health / nova-diagnose.
Distributed exclusively via Nova Update.

%install
ROOT=%{_nova_root}/desktop/nova-identity
install -d %{buildroot}/usr/bin
install -d %{buildroot}/usr/share/nova/assets
install -d %{buildroot}/usr/share/nova/identity
install -d %{buildroot}/usr/share/konsole
install -d %{buildroot}/usr/share/plymouth/themes
install -d %{buildroot}/usr/share/icons/hicolor
install -d %{buildroot}/usr/share/pixmaps
install -d %{buildroot}/usr/share/wallpapers
install -d %{buildroot}/usr/share/color-schemes
install -d %{buildroot}/etc/profile.d
install -d %{buildroot}/etc/bashrc.d
install -d %{buildroot}/etc/xdg
install -d %{buildroot}/etc/xdg/plasma-workspace/env
install -d %{buildroot}/etc/xdg/sddm
install -d %{buildroot}/etc/sddm.conf.d
install -d %{buildroot}/etc/plymouth
install -d %{buildroot}/etc/skel/.bashrc.d
install -d %{buildroot}/etc/skel/.config
install -d %{buildroot}/usr/share/doc/%{name}

# Canonical assets
cp -a ${ROOT}/assets/. %{buildroot}/usr/share/nova/assets/
# Library
cp -a ${ROOT}/lib/nova_identity %{buildroot}/usr/share/nova/identity/
find %{buildroot}/usr/share/nova -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# CLI
for cmd in nova-about nova-info nova-version nova-health nova-diagnose; do
  install -m 0755 ${ROOT}/bin/${cmd} %{buildroot}/usr/bin/${cmd}
done

# Terminal
install -m 0644 ${ROOT}/konsole/NovaOS.colorscheme %{buildroot}/usr/share/konsole/NovaOS.colorscheme
install -m 0644 ${ROOT}/konsole/NovaOS.profile %{buildroot}/usr/share/konsole/NovaOS.profile
install -m 0644 ${ROOT}/etc/profile.d/nova-identity.sh %{buildroot}/etc/profile.d/nova-identity.sh
install -m 0644 ${ROOT}/etc/profile.d/91-nova-banner.sh %{buildroot}/etc/profile.d/91-nova-banner.sh
install -m 0644 ${ROOT}/etc/bashrc.d/90-nova-banner.sh %{buildroot}/etc/bashrc.d/90-nova-banner.sh
install -m 0644 ${ROOT}/etc/bashrc.d/90-nova-banner.sh %{buildroot}/etc/skel/.bashrc.d/90-nova-banner.sh
install -m 0644 ${ROOT}/etc/xdg/konsolerc %{buildroot}/etc/xdg/konsolerc
install -m 0644 ${ROOT}/etc/skel/.config/konsolerc %{buildroot}/etc/skel/.config/konsolerc

# Branding XDG / About / Plasma
install -m 0644 ${ROOT}/etc/xdg/kcm-about-distrorc %{buildroot}/etc/xdg/kcm-about-distrorc
install -m 0644 ${ROOT}/etc/xdg/kdeglobals %{buildroot}/etc/xdg/kdeglobals
install -m 0755 ${ROOT}/etc/xdg/plasma-workspace/env/nova-identity-env.sh \
  %{buildroot}/etc/xdg/plasma-workspace/env/nova-identity-env.sh
install -m 0644 ${ROOT}/etc/sddm.conf.d/zzz-novaos-identity.conf \
  %{buildroot}/etc/sddm.conf.d/zzz-novaos-identity.conf

# Plymouth theme (optional at runtime)
cp -a ${ROOT}/plymouth/novaos %{buildroot}/usr/share/plymouth/themes/
install -m 0644 ${ROOT}/etc/plymouth/plymouthd.conf %{buildroot}/etc/plymouth/plymouthd.conf

# Also publish wallpaper/colors/icons into traditional locations (identity owns)
cp -a ${ROOT}/assets/wallpaper/NovaOS %{buildroot}/usr/share/wallpapers/NovaOS
install -m 0644 ${ROOT}/assets/colors/NovaOS.colors %{buildroot}/usr/share/color-schemes/NovaOS.colors
install -m 0644 ${ROOT}/assets/logo/novaos.png %{buildroot}/usr/share/pixmaps/novaos.png
for s in 32 48 64 128 256; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/${s}x${s}/apps
  if [ -f ${ROOT}/assets/icons/hicolor/${s}x${s}/apps/novaos.png ]; then
    install -m 0644 ${ROOT}/assets/icons/hicolor/${s}x${s}/apps/novaos.png \
      %{buildroot}/usr/share/icons/hicolor/${s}x${s}/apps/novaos.png
  else
    install -m 0644 ${ROOT}/assets/logo/novaos.png \
      %{buildroot}/usr/share/icons/hicolor/${s}x${s}/apps/novaos.png
  fi
done

# Enhanced Plasma splash (look-and-feel)
install -d %{buildroot}/usr/share/plasma/look-and-feel
cp -a ${ROOT}/look-and-feel/org.novaos.desktop %{buildroot}/usr/share/plasma/look-and-feel/

install -m 0644 ${ROOT}/README.md %{buildroot}/usr/share/doc/%{name}/README.md

%post
# Point SDDM novaos theme at shared assets when theme is present
if [ -d /usr/share/sddm/themes/novaos ] && [ -f /usr/share/nova/assets/sddm/theme.conf ]; then
  cp -f /usr/share/nova/assets/sddm/theme.conf /usr/share/sddm/themes/novaos/theme.conf 2>/dev/null || :
fi
if command -v plymouth-set-default-theme >/dev/null 2>&1; then
  plymouth-set-default-theme novaos >/dev/null 2>&1 || :
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -f /usr/share/icons/hicolor >/dev/null 2>&1 || :
fi
# Ensure interactive bash sources /etc/bashrc.d on Fedora-like images
if [ -f /etc/bashrc ] && ! grep -q 'bashrc.d' /etc/bashrc 2>/dev/null; then
  :
fi
exit 0

%files
%doc /usr/share/doc/%{name}/README.md
/usr/share/nova/assets/
/usr/share/nova/identity/
/usr/bin/nova-about
/usr/bin/nova-info
/usr/bin/nova-version
/usr/bin/nova-health
/usr/bin/nova-diagnose
/usr/share/konsole/NovaOS.colorscheme
/usr/share/konsole/NovaOS.profile
/usr/share/plymouth/themes/novaos/
/usr/share/wallpapers/NovaOS/
/usr/share/color-schemes/NovaOS.colors
/usr/share/pixmaps/novaos.png
/usr/share/icons/hicolor/*/apps/novaos.png
/usr/share/plasma/look-and-feel/org.novaos.desktop/
/etc/profile.d/nova-identity.sh
/etc/profile.d/91-nova-banner.sh
/etc/bashrc.d/90-nova-banner.sh
/etc/skel/.bashrc.d/90-nova-banner.sh
/etc/skel/.config/konsolerc
/etc/xdg/konsolerc
/etc/xdg/kcm-about-distrorc
/etc/xdg/kdeglobals
/etc/xdg/plasma-workspace/env/nova-identity-env.sh
/etc/sddm.conf.d/zzz-novaos-identity.conf
%config(noreplace) /etc/plymouth/plymouthd.conf

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.6-1
- Sprint 20: shared Nova assets, terminal identity, nova-about and CLI tools
