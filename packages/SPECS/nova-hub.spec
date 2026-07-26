Name:           nova-hub
Version:        0.2.7
Release:        1%{?dist}
Summary:        Nova Hub — official NovaOS home
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       gtk3
Requires:       nova-platform >= 0.2.5
Requires:       nova-identity >= 0.2.6
Recommends:     nova-center >= 0.2.5
Recommends:     novaos-update
Recommends:     nova-update-gui

%description
Official NovaOS home (Applications menu). Dashboard, quick actions,
ecosystem placeholders, local news, and system status via platform.v1.
Shares Platform/Update bridges with Nova Center when co-installed.
Internal API hub.v1.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/hub
mkdir -p %{buildroot}/usr/share/nova/hub/data
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/desktop/nova-hub/nova_hub %{buildroot}/usr/share/nova/hub/
install -m 0644 %{_nova_root}/desktop/nova-hub/data/news.json \
  %{buildroot}/usr/share/nova/hub/data/news.json
find %{buildroot}/usr/share/nova/hub -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova/hub -type f -name '*.pyc' -delete 2>/dev/null || true
install -m 0755 %{_nova_root}/desktop/nova-hub/bin/nova-hub %{buildroot}/usr/bin/nova-hub
install -m 0644 %{_nova_root}/desktop/nova-hub/org.novaos.Hub.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Hub.desktop
install -m 0644 %{_nova_root}/desktop/nova-hub/README.md \
  %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc /usr/share/doc/%{name}/README.md
/usr/bin/nova-hub
/usr/share/nova/hub/
/usr/share/applications/org.novaos.Hub.desktop

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.7-1
- Sprint 21: Nova Hub home — dashboard, actions, ecosystem, news, system
