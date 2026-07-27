Name:           nova-shell
Version:        0.2.9
Release:        1%{?dist}
Summary:        Nova Shell — NovaOS experience layer foundation
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       gtk3
Requires:       nova-platform >= 0.2.5
Requires:       nova-identity >= 0.2.6
Recommends:     nova-hub
Recommends:     nova-center
Recommends:     novaos-update
Recommends:     libwnck3

%description
Nova Shell foundation: Horizon Bar with TopBarManager auto-hide, Nova Launcher
with Quick Search, system widgets, and Dock API. Live status via platform.v1.
Internal APIs shell.v1 / shell.search.v1 / shell.dock.v1 / shell.topbar.v1.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/shell
mkdir -p %{buildroot}/usr/share/nova/shell/data
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/etc/xdg/autostart
mkdir -p %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/desktop/nova-shell/nova_shell %{buildroot}/usr/share/nova/shell/
install -m 0644 %{_nova_root}/desktop/nova-shell/data/catalog.json \
  %{buildroot}/usr/share/nova/shell/data/catalog.json
find %{buildroot}/usr/share/nova/shell -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/shell -type f -name '*.pyc' -delete 2>/dev/null || true
install -m 0755 %{_nova_root}/desktop/nova-shell/bin/nova-shell %{buildroot}/usr/bin/nova-shell
install -m 0644 %{_nova_root}/desktop/nova-shell/org.novaos.Shell.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Shell.desktop
install -m 0644 %{_nova_root}/desktop/nova-shell/autostart/org.novaos.Shell.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.Shell.desktop
install -m 0644 %{_nova_root}/desktop/nova-shell/README.md \
  %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc /usr/share/doc/%{name}/README.md
/usr/bin/nova-shell
/usr/share/nova/shell/
/usr/share/applications/org.novaos.Shell.desktop
/etc/xdg/autostart/org.novaos.Shell.desktop

%changelog
* Mon Jul 27 2026 NovaOS Team <dev@novaos.local> - 0.2.9-1
- Sprint 21.1: TopBarManager auto-hide, Impostazioni Nova bar modes

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.8-1
- Sprint 22: Horizon Bar, Launcher, Quick Search, Widgets, Dock API
