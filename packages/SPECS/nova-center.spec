Name:           nova-center
Version:        0.2.2
Release:        1%{?dist}
Summary:        Nova Center — official NovaOS control panel
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       gtk3
Recommends:     novaos-update
Recommends:     nova-update-gui

%description
Official NovaOS control panel (Applications menu). Reads live system data
for dashboard, hardware, network, system paths, Nova services, and Nova
Update status. Internal API center.v1; Ryuk integration is stubbed for a
future sprint.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/center
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/desktop/nova-center/nova_center %{buildroot}/usr/share/nova/center/
# Do not ship bytecode caches from the build host
find %{buildroot}/usr/share/nova/center -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/center -type f -name '*.pyc' -delete 2>/dev/null || true
install -m 0755 %{_nova_root}/desktop/nova-center/bin/nova-center %{buildroot}/usr/bin/nova-center
install -m 0644 %{_nova_root}/desktop/nova-center/org.novaos.Center.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Center.desktop
install -m 0644 %{_nova_root}/desktop/nova-center/README.md %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc %{_datadir}/doc/%{name}/README.md
%{_bindir}/nova-center
%{_datadir}/nova/center/
%{_datadir}/applications/org.novaos.Center.desktop

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.2-1
- First official Nova Center control panel (Sprint 16)
