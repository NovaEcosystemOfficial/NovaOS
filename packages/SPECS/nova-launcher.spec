Name:           nova-launcher
Version:        0.2.10
Release:        1%{?dist}
Summary:        Nova Launcher — official NovaOS application launcher
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       gtk3
Requires:       nova-identity >= 0.2.6
Recommends:     nova-hub
Recommends:     nova-center
Recommends:     nova-shell
Recommends:     nova-update-gui

%description
Official NovaOS launcher window with instant search over .desktop apps,
favorites, recent documents, and quick actions. Runs alongside the KDE
menu (not a replacement yet). API launcher.v1 / launcher.search.v1 for Ryuk.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/launcher
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/kglobalaccel
mkdir -p %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/desktop/nova-launcher/nova_launcher %{buildroot}/usr/share/nova/launcher/
find %{buildroot}/usr/share/nova/launcher -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/launcher -type f -name '*.pyc' -delete 2>/dev/null || true
install -m 0755 %{_nova_root}/desktop/nova-launcher/bin/nova-launcher %{buildroot}/usr/bin/nova-launcher
install -m 0644 %{_nova_root}/desktop/nova-launcher/org.novaos.Launcher.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Launcher.desktop
install -m 0644 %{_nova_root}/desktop/nova-launcher/kglobalaccel/org.novaos.Launcher.desktop \
  %{buildroot}/usr/share/kglobalaccel/org.novaos.Launcher.desktop
install -m 0644 %{_nova_root}/desktop/nova-launcher/README.md \
  %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc /usr/share/doc/%{name}/README.md
/usr/bin/nova-launcher
/usr/share/nova/launcher/
/usr/share/applications/org.novaos.Launcher.desktop
/usr/share/kglobalaccel/org.novaos.Launcher.desktop

%changelog
* Mon Jul 27 2026 NovaOS Team <dev@novaos.local> - 0.2.10-1
- Sprint 22: official Nova Launcher parallel to KDE menu
