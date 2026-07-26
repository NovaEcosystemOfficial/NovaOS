Name:           novaos-update
Version:        0.2.1
Release:        1%{?dist}
Summary:        NovaOS Update Broker and CLI
License:        MIT
URL:            https://github.com/novaos/NovaOS
BuildArch:      noarch
Requires:       python3 >= 3.11
Recommends:     dnf

%description
Official NovaOS update stack: nova-updated (system.update.v1), nova-updater CLI,
channel repo configs, GPG key material. GUI ships as nova-update-gui.

%install
install -d %{buildroot}/usr/libexec
install -d %{buildroot}/usr/bin
install -d %{buildroot}/usr/lib/nova/update
install -d %{buildroot}/etc/nova/update
install -d %{buildroot}/usr/lib/systemd/system
install -d %{buildroot}/usr/lib/systemd/system-preset
install -d %{buildroot}/etc/yum.repos.d
install -d %{buildroot}/etc/pki/novaos
install -d %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/system/update/nova_update %{buildroot}/usr/lib/nova/update/
install -m 0755 %{_nova_root}/system/update/bin/nova-updated %{buildroot}/usr/libexec/nova-updated
install -m 0755 %{_nova_root}/system/update/bin/nova-updater %{buildroot}/usr/bin/nova-updater
install -m 0644 %{_nova_root}/system/update/conf/nova-update.conf %{buildroot}/etc/nova/update/nova-update.conf
install -m 0644 %{_nova_root}/system/update/systemd/nova-updated.service %{buildroot}/usr/lib/systemd/system/nova-updated.service
install -m 0644 %{_nova_root}/system/update/systemd/80-novaos-update.preset \
  %{buildroot}/usr/lib/systemd/system-preset/80-novaos-update.preset
install -m 0644 %{_nova_root}/packages/repo/conf/*.repo %{buildroot}/etc/yum.repos.d/
install -m 0644 %{_nova_root}/packages/repo/keys/RPM-GPG-KEY-novaos \
  %{buildroot}/etc/pki/novaos/RPM-GPG-KEY-novaos
install -m 0644 %{_nova_root}/system/update/README.md %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc /usr/share/doc/%{name}/README.md
/usr/lib/nova/update/
/usr/libexec/nova-updated
/usr/bin/nova-updater
%config(noreplace) /etc/nova/update/nova-update.conf
%config(noreplace) /etc/yum.repos.d/novaos-*.repo
/etc/pki/novaos/RPM-GPG-KEY-novaos
/usr/lib/systemd/system/nova-updated.service
/usr/lib/systemd/system-preset/80-novaos-update.preset

%post
if [ $1 -eq 1 ]; then
  systemctl daemon-reload >/dev/null 2>&1 || :
  systemctl enable nova-updated.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ]; then
  systemctl --no-reload disable --now nova-updated.service >/dev/null 2>&1 || :
fi

%postun
systemctl daemon-reload >/dev/null 2>&1 || :

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.1-1
- History API, system info, 0.2.1 release train
