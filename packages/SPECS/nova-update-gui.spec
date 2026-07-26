Name:           nova-update-gui
Version:        0.2.6
Release:        1%{?dist}
Summary:        Nova Update graphical client for NovaOS
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
# Soft requirement: novaos-update package may be delivered as overlay files
# before the first RPM install. Do not hard-Requires to avoid chicken/egg.
Requires:       python3 >= 3.11
Requires:       python3-gobject
Requires:       gtk3
Recommends:     novaos-update

%description
Official Nova Update GUI (Applications menu). Talks to nova-updated via
system.update.v1 and shows version, channel, check/install, service status
and update history.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/update/gui
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/desktop/nova-update/nova_update_gui %{buildroot}/usr/share/nova/update/gui/
install -m 0755 %{_nova_root}/desktop/nova-update/bin/nova-update-gui %{buildroot}/usr/bin/nova-update-gui
install -m 0644 %{_nova_root}/desktop/nova-update/org.novaos.Update.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Update.desktop
install -m 0644 %{_nova_root}/desktop/nova-update/README.md %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc %{_datadir}/doc/%{name}/README.md
%{_bindir}/nova-update-gui
%{_datadir}/nova/update/gui/
%{_datadir}/applications/org.novaos.Update.desktop

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.6-1
- Launcher icon novaos (shared Identity assets)

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.3-1
- Move Controlla/Installa above lists so Install is always visible
- Enable Installa only when pending updates exist

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.1-1
- First official Nova Update GUI (v0.2.1)
