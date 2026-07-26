Name:           nova-desktop
Version:        0.2.6
Release:        1%{?dist}
Summary:        NovaOS Desktop Experience (login, session, notifications)
License:        MIT and LGPLv2+
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       libnotify
Requires:       nova-identity >= 0.2.6
Recommends:     novaos-update
Recommends:     nova-update-gui
Recommends:     nova-center
Recommends:     sddm

%description
Sprint 18+ desktop experience: SDDM novaos theme (no virtual keyboard),
session checks, and update notifications. Visual branding assets are owned
by nova-identity under /usr/share/nova/assets.

%install
ROOT=%{_nova_root}/desktop/nova-desktop
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/desktop
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/local/share/applications
mkdir -p %{buildroot}/usr/share/sddm/themes
mkdir -p %{buildroot}/etc/sddm.conf.d
mkdir -p %{buildroot}/etc/xdg/autostart
mkdir -p %{buildroot}/etc/xdg/plasma-workspace/env
mkdir -p %{buildroot}/etc/skel/.config/autostart
mkdir -p %{buildroot}/usr/share/doc/%{name}
mkdir -p %{buildroot}/etc/xdg

cp -a ${ROOT}/nova_desktop %{buildroot}/usr/share/nova/desktop/
install -m 0755 ${ROOT}/bin/nova-notify-agent %{buildroot}/usr/bin/nova-notify-agent
install -m 0755 ${ROOT}/bin/nova-session-check %{buildroot}/usr/bin/nova-session-check

cp -a ${ROOT}/sddm/novaos %{buildroot}/usr/share/sddm/themes/
# Prefer shared identity assets for logo/wallpaper
if [ -f %{_nova_root}/desktop/nova-identity/assets/sddm/theme.conf ]; then
  install -m 0644 %{_nova_root}/desktop/nova-identity/assets/sddm/theme.conf \
    %{buildroot}/usr/share/sddm/themes/novaos/theme.conf
fi
install -m 0644 ${ROOT}/config/zzz-novaos-desktop.conf \
  %{buildroot}/etc/sddm.conf.d/zzz-novaos-desktop.conf

install -m 0644 ${ROOT}/config/plasma-welcomerc %{buildroot}/etc/xdg/plasma-welcomerc
install -m 0755 ${ROOT}/config/novaos-desktop-env.sh \
  %{buildroot}/etc/xdg/plasma-workspace/env/novaos-desktop-env.sh

install -m 0644 ${ROOT}/autostart/org.novaos.Notify.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.Notify.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.SessionCheck.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.SessionCheck.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.Notify.desktop \
  %{buildroot}/etc/skel/.config/autostart/org.novaos.Notify.desktop
install -m 0644 ${ROOT}/autostart/org.novaos.SessionCheck.desktop \
  %{buildroot}/etc/skel/.config/autostart/org.novaos.SessionCheck.desktop

install -m 0644 ${ROOT}/applications/org.novaos.Center.desktop \
  %{buildroot}/usr/local/share/applications/org.novaos.Center.desktop
install -m 0644 ${ROOT}/applications/org.novaos.Update.desktop \
  %{buildroot}/usr/local/share/applications/org.novaos.Update.desktop
for f in ${ROOT}/applications/hide/*.desktop; do
  install -m 0644 "$f" %{buildroot}/usr/local/share/applications/"$(basename "$f")"
done

install -m 0644 ${ROOT}/README.md %{buildroot}/usr/share/doc/%{name}/README.md
find %{buildroot}/usr/share/nova/desktop -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/desktop -type f -name '*.pyc' -delete 2>/dev/null || true

%post
if [ -x /usr/bin/systemctl ]; then
  systemctl enable nova-updated.socket >/dev/null 2>&1 || true
  systemctl start nova-updated.socket >/dev/null 2>&1 || true
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
%config(noreplace) /etc/sddm.conf.d/zzz-novaos-desktop.conf
%config(noreplace) /etc/xdg/plasma-welcomerc
/etc/xdg/plasma-workspace/env/novaos-desktop-env.sh
/etc/xdg/autostart/org.novaos.Notify.desktop
/etc/xdg/autostart/org.novaos.SessionCheck.desktop
/etc/skel/.config/autostart/org.novaos.Notify.desktop
/etc/skel/.config/autostart/org.novaos.SessionCheck.desktop
/usr/local/share/applications/

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.6-1
- Branding assets moved to nova-identity; SDDM theme uses shared paths

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.4-1
- Sprint 18: login without virtual keyboard, Nova branding, session checks, notifications
