Name:           nova-platform
Version:        0.2.5
Release:        1%{?dist}
Summary:        NovaOS Platform Service (nova-platformd) and Python client
License:        MIT
URL:            https://github.com/novaos/NovaOS
BuildArch:      noarch
Requires:       python3 >= 3.11
Requires:       systemd
Recommends:     NetworkManager
Provides:       nova-platform-python = %{version}-%{release}

%description
Sprint 19 — Nova Platform Foundation. Proprietary platform layer for NovaOS:
nova-platformd (platform.v1 over /run/nova/platform.sock), nova-platformctl CLI,
and the shared Python library nova_platform (Provides: nova-platform-python).
Logs under /var/log/nova/. Distributed exclusively via Nova Update.

%install
ROOT=%{_nova_root}/system/platform
install -d %{buildroot}/usr/libexec
install -d %{buildroot}/usr/bin
install -d %{buildroot}/usr/lib/nova/platform
install -d %{buildroot}/etc/nova/platform
install -d %{buildroot}/usr/lib/systemd/system
install -d %{buildroot}/usr/lib/systemd/system-preset
install -d %{buildroot}/usr/lib/tmpfiles.d
install -d %{buildroot}/usr/share/doc/%{name}
install -d %{buildroot}/var/log/nova

cp -a ${ROOT}/nova_platform %{buildroot}/usr/lib/nova/platform/
find %{buildroot}/usr/lib/nova/platform -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/lib/nova/platform -type f -name '*.pyc' -delete 2>/dev/null || true

install -m 0755 ${ROOT}/bin/nova-platformd %{buildroot}/usr/libexec/nova-platformd
install -m 0755 ${ROOT}/bin/nova-platformctl %{buildroot}/usr/bin/nova-platformctl
install -m 0644 ${ROOT}/conf/nova-platform.conf %{buildroot}/etc/nova/platform/nova-platform.conf
install -m 0644 ${ROOT}/systemd/nova-platformd.service %{buildroot}/usr/lib/systemd/system/nova-platformd.service
install -m 0644 ${ROOT}/systemd/nova-platformd.socket %{buildroot}/usr/lib/systemd/system/nova-platformd.socket
install -m 0644 ${ROOT}/systemd/80-nova-platform.preset \
  %{buildroot}/usr/lib/systemd/system-preset/80-nova-platform.preset
install -m 0644 ${ROOT}/tmpfiles.d/nova-platform.conf \
  %{buildroot}/usr/lib/tmpfiles.d/nova-platform.conf
install -m 0644 ${ROOT}/README.md %{buildroot}/usr/share/doc/%{name}/README.md
# Log directory (files created at runtime by the daemon / tmpfiles)
install -d -m 0755 %{buildroot}/var/log/nova

%files
%doc /usr/share/doc/%{name}/README.md
/usr/lib/nova/platform/
/usr/libexec/nova-platformd
/usr/bin/nova-platformctl
%config(noreplace) /etc/nova/platform/nova-platform.conf
/usr/lib/systemd/system/nova-platformd.service
/usr/lib/systemd/system/nova-platformd.socket
/usr/lib/systemd/system-preset/80-nova-platform.preset
/usr/lib/tmpfiles.d/nova-platform.conf
%dir /var/log/nova

%pre
if command -v systemd-sysusers >/dev/null 2>&1 && [ -f /usr/lib/sysusers.d/nova.conf ]; then
  systemd-sysusers nova.conf >/dev/null 2>&1 || :
elif ! getent group nova >/dev/null 2>&1; then
  groupadd -r nova >/dev/null 2>&1 || :
fi

%post
if command -v systemd-tmpfiles >/dev/null 2>&1; then
  systemd-tmpfiles --create /usr/lib/tmpfiles.d/nova-platform.conf >/dev/null 2>&1 || :
fi
getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1}' | while read -r u; do
  usermod -aG nova "$u" >/dev/null 2>&1 || :
done
systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -eq 1 ]; then
  systemctl enable nova-platformd.socket >/dev/null 2>&1 || :
  systemctl enable nova-platformd.service >/dev/null 2>&1 || :
fi
systemctl restart nova-platformd.socket >/dev/null 2>&1 || :
systemctl restart nova-platformd.service >/dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ]; then
  systemctl --no-reload disable --now nova-platformd.service nova-platformd.socket >/dev/null 2>&1 || :
fi

%postun
systemctl daemon-reload >/dev/null 2>&1 || :

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.5-1
- Sprint 19: nova-platformd, platform.v1, nova-platformctl health, logging
