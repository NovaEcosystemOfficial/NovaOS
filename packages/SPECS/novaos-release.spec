Name:           novaos-release
Version:        0.2.4
Release:        1%{?dist}
Summary:        NovaOS release identity (/etc/os-release)
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS

%description
NovaOS distribution identity files. Updating this package is the official
way to bump the OS version without rebuilding the ISO (via Nova Update).

%install
mkdir -p %{buildroot}/usr/lib %{buildroot}/etc/novaos %{buildroot}/usr/share/doc/%{name}
cat > %{buildroot}/usr/lib/os-release <<'EOF'
NAME="NovaOS"
VERSION="0.2.4"
ID=novaos
ID_LIKE="fedora"
VERSION_ID="0.2.4"
PRETTY_NAME="NovaOS 0.2.4"
ANSI_COLOR="0;36"
HOME_URL="https://novaos.local"
DOCUMENTATION_URL="https://novaos.local"
SUPPORT_URL="https://novaos.local"
BUG_REPORT_URL="https://novaos.local"
LOGO="novaos"
VARIANT="Installable"
VARIANT_ID="m02"
EOF
ln -sfn ../usr/lib/os-release %{buildroot}/etc/os-release
printf '%s\n' '0.2.4' > %{buildroot}/etc/novaos/version
printf '%s\n' 'milestone=0.2.4' 'channel=stable' 'delivered_by=nova-update' \
  > %{buildroot}/etc/novaos/release-info
install -m 0644 %{_nova_root}/packages/novaos-release/README.md \
  %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc %{_datadir}/doc/%{name}/README.md
/usr/lib/os-release
/etc/os-release
%config(noreplace) /etc/novaos/version
%config(noreplace) /etc/novaos/release-info

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.4-1
- NovaOS v0.2.4 identity (Desktop Experience train)

* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.1-1
- Official NovaOS 0.2.1 identity via Nova Update
