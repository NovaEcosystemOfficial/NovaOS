Name:           nova-desktop
Version:        0.2.4
Release:        1%{?dist}
Summary:        NovaOS Desktop Experience (login, branding, session, notifications)
License:        MIT and LGPLv2+
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       libnotify
Recommends:     novaos-update
Recommends:     nova-update-gui
Recommends:     nova-center
Recommends:     sddm

%description
Sprint 18 — Nova Desktop Experience. Disables the SDDM virtual keyboard,
applies NovaOS branding (look-and-feel, About System, wallpapers), improves
session autostart for Nova Update/Center, and provides native update
notifications. Distributed exclusively via Nova Update.

%install
ROOT=%{_nova_root}/desktop/nova-desktop
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/desktop
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/local/share/applications
mkdir -p %{buildroot}/usr/share/sddm/themes
mkdir -p %{buildroot}/usr/share/plasma/look-and-feel
mkdir -p %{buildroot}/usr/share/wallpapers
mkdir -p %{buildroot}/usr/share/color-schemes
mkdir -p %{buildroot}/usr/share/pixmaps
mkdir -p %{buildroot}/usr/share/icons/hicolor
mkdir -p %{buildroot}/etc/sddm.conf.d
mkdir -p %{buildroot}/etc/xdg
mkdir -p %{buildroot}/etc/xdg/autostart
mkdir -p %{buildroot}/etc/xdg/plasma-workspace/env
mkdir -p %{buildroot}/etc/skel/.config/autostart
mkdir -p %{buildroot}/usr/share/doc/%{name}

# Python package + helpers
cp -a ${ROOT}/nova_desktop %{buildroot}/usr/share/nova/desktop/
install -m 0755 ${ROOT}/bin/nova-notify-agent %{buildroot}/usr/bin/nova-notify-agent
install -m 0755 ${ROOT}/bin/nova-session-check %{buildroot}/usr/bin/nova-session-check

# SDDM theme (virtual keyboard removed)
cp -a ${ROOT}/sddm/novaos %{buildroot}/usr/share/sddm/themes/
install -m 0644 ${ROOT}/config/zzz-novaos-desktop.conf \
  %{buildroot}/etc/sddm.conf.d/zzz-novaos-desktop.conf

# Plasma look-and-feel + wallpaper + colors
cp -a ${ROOT}/look-and-feel/org.novaos.desktop %{buildroot}/usr/share/plasma/look-and-feel/
cp -a ${ROOT}/assets/wallpaper-NovaOS %{buildroot}/usr/share/wallpapers/NovaOS
install -m 0644 ${ROOT}/assets/NovaOS.colors %{buildroot}/usr/share/color-schemes/NovaOS.colors

# Branding icons
install -m 0644 ${ROOT}/icons/novaos.png %{buildroot}/usr/share/pixmaps/novaos.png
for s in 32 48 64 128 256; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/${s}x${s}/apps
  install -m 0644 ${ROOT}/icons/hicolor/${s}x${s}/apps/novaos.png \
    %{buildroot}/usr/share/icons/hicolor/${s}x${s}/apps/novaos.png
done

# XDG defaults (About System + look-and-feel)
install -m 0644 ${ROOT}/config/kcm-about-distrorc %{buildroot}/etc/xdg/kcm-about-distrorc
install -m 0644 ${ROOT}/config/kdeglobals %{buildroot}/etc/xdg/kdeglobals
install -m 0644 ${ROOT}/config/plasma-welcomerc %{buildroot}/etc/xdg/plasma-welcomerc
install -m 0755 ${ROOT}/config/novaos-desktop-env.sh \
  %{buildroot}/etc/xdg/plasma-workspace/env/novaos-desktop-env.sh

# Autostart (system + skel)
install -m 0644 ${ROOT}/autostart/org.novaos.Notify.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.Notify.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.SessionCheck.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.SessionCheck.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.Notify.desktop \
  %{buildroot}/etc/skel/.config/autostart/org.novaos.Notify.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.SessionCheck.desktop \
  %{buildroot}/etc/skel/.config/autostart/org.novaos.SessionCheck.desktop

# Launcher overrides (XDG_DATA_DIRS: /usr/local/share before /usr/share)
install -m 0644 ${ROOT}/applications/org.novaos.Center.desktop \
  %{buildroot}/usr/local/share/applications/org.novaos.Center.desktop
install -m 0644 ${ROOT}/applications/org.novaos.Update.desktop \
  %{buildroot}/usr/local/share/applications/org.novaos.Update.desktop

# Hide leftover Fedora menu entries when present (same desktop-id override)
mkdir -p %{buildroot}/usr/local/share/applications
for f in ${ROOT}/applications/hide/*.desktop; do
  install -m 0644 "$f" %{buildroot}/usr/local/share/applications/"$(basename "$f")"
done

install -m 0644 ${ROOT}/README.md %{buildroot}/usr/share/doc/%{name}/README.md

# Drop pycache from buildroot
find %{buildroot}/usr/share/nova/desktop -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/desktop -type f -name '*.pyc' -delete 2>/dev/null || true

%post
# Enable Update Broker socket when package is applied via Nova Update (root).
if [ -x /usr/bin/systemctl ]; then
  systemctl enable nova-updated.socket >/dev/null 2>&1 || true
  systemctl start nova-updated.socket >/dev/null 2>&1 || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -f /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
if [ -x /usr/bin/update-desktop-database ]; then
  update-desktop-database /usr/local/share/applications >/dev/null 2>&1 || true
fi
exit 0

%files
%doc %{_datadir}/doc/%{name}/README.md
%{_bindir}/nova-notify-agent
%{_bindir}/nova-session-check
%{_datadir}/nova/desktop/
%{_datadir}/sddm/themes/novaos/
%{_datadir}/plasma/look-and-feel/org.novaos.desktop/
%{_datadir}/wallpapers/NovaOS/
%{_datadir}/color-schemes/NovaOS.colors
%{_datadir}/pixmaps/novaos.png
%{_datadir}/icons/hicolor/*/apps/novaos.png
%config(noreplace) /etc/sddm.conf.d/zzz-novaos-desktop.conf
/etc/xdg/kcm-about-distrorc
/etc/xdg/kdeglobals
%config(noreplace) /etc/xdg/plasma-welcomerc
/etc/xdg/plasma-workspace/env/novaos-desktop-env.sh
/etc/xdg/autostart/org.novaos.Notify.desktop
/etc/xdg/autostart/org.novaos.SessionCheck.desktop
/etc/skel/.config/autostart/org.novaos.Notify.desktop
/etc/skel/.config/autostart/org.novaos.SessionCheck.desktop
/usr/local/share/applications/

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.4-1
- Sprint 18: login without virtual keyboard, Nova branding, session checks, notifications
