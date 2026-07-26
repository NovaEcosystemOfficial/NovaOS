Name:           novaos-update
Version:        0.2.3
Release:        1%{?dist}
Summary:        NovaOS Update Broker and CLI
License:        MIT
URL:            https://github.com/novaos/NovaOS
BuildArch:      noarch
Requires:       python3 >= 3.11
Requires:       systemd
Recommends:     dnf

%description
Official NovaOS update stack: nova-updated (system.update.v1), nova-updater CLI,
channel repo configs, GPG key material. GUI ships as nova-update-gui.
IPC socket /run/nova/update.sock is root:nova mode 0660 via systemd socket
activation; interactive users are members of group nova.

%install
install -d %{buildroot}/usr/libexec
install -d %{buildroot}/usr/bin
install -d %{buildroot}/usr/lib/nova/update
install -d %{buildroot}/etc/nova/update
install -d %{buildroot}/usr/lib/systemd/system
install -d %{buildroot}/usr/lib/systemd/system-preset
install -d %{buildroot}/usr/lib/sysusers.d
install -d %{buildroot}/etc/yum.repos.d
install -d %{buildroot}/etc/pki/novaos
install -d %{buildroot}/usr/share/doc/%{name}

cp -a %{_nova_root}/system/update/nova_update %{buildroot}/usr/lib/nova/update/
find %{buildroot}/usr/lib/nova/update -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
install -m 0755 %{_nova_root}/system/update/bin/nova-updated %{buildroot}/usr/libexec/nova-updated
install -m 0755 %{_nova_root}/system/update/bin/nova-updater %{buildroot}/usr/bin/nova-updater
install -m 0644 %{_nova_root}/system/update/conf/nova-update.conf %{buildroot}/etc/nova/update/nova-update.conf
install -m 0644 %{_nova_root}/system/update/systemd/nova-updated.service %{buildroot}/usr/lib/systemd/system/nova-updated.service
install -m 0644 %{_nova_root}/system/update/systemd/nova-updated.socket %{buildroot}/usr/lib/systemd/system/nova-updated.socket
install -m 0644 %{_nova_root}/system/update/systemd/80-novaos-update.preset \
  %{buildroot}/usr/lib/systemd/system-preset/80-novaos-update.preset
install -m 0644 %{_nova_root}/system/update/sysusers.d/nova.conf \
  %{buildroot}/usr/lib/sysusers.d/nova.conf
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
/usr/lib/systemd/system/nova-updated.socket
/usr/lib/systemd/system-preset/80-novaos-update.preset
/usr/lib/sysusers.d/nova.conf

%pre
# Ensure group exists before socket unit starts (RPM transaction).
if command -v systemd-sysusers >/dev/null 2>&1 && [ -f /usr/lib/sysusers.d/nova.conf ]; then
  systemd-sysusers nova.conf >/dev/null 2>&1 || :
elif ! getent group nova >/dev/null 2>&1; then
  groupadd -r nova >/dev/null 2>&1 || :
fi

%post
if command -v systemd-sysusers >/dev/null 2>&1; then
  systemd-sysusers nova.conf >/dev/null 2>&1 || :
fi
# Add interactive users so Nova Center / nova-updater work without sudo.
getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1}' | while read -r u; do
  usermod -aG nova "$u" >/dev/null 2>&1 || :
done
systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -eq 1 ]; then
  systemctl enable nova-updated.socket >/dev/null 2>&1 || :
  systemctl enable nova-updated.service >/dev/null 2>&1 || :
fi
systemctl restart nova-updated.socket >/dev/null 2>&1 || :
systemctl restart nova-updated.service >/dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ]; then
  systemctl --no-reload disable --now nova-updated.service nova-updated.socket >/dev/null 2>&1 || :
fi

%postun
systemctl daemon-reload >/dev/null 2>&1 || :

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.3-1
- localrpm: enable platform/update systemd units after live-root apply

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.2-1
- Socket activation root:nova 0660; sysusers group nova; no sudo for clients

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.1-1
- History API, system info, 0.2.1 release train
