Name:           hello-nova-update
Version:        1.0.0
Release:        1%{?dist}
Summary:        Nova Update end-to-end test package
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS

%description
Pacchetto di prova per dimostrare aggiornamenti incrementali NovaOS
tramite repository RPM locale, senza ricostruire l'ISO.

%install
mkdir -p %{buildroot}/usr/share/hello-nova-update %{buildroot}/usr/bin
printf '%s\n' "hello-nova-update %{version}-%{release}" \
  > %{buildroot}/usr/share/hello-nova-update/VERSION
# Self-contained probe (works under test install-roots without chroot).
cat > %{buildroot}/usr/bin/hello-nova-update <<EOF
#!/bin/sh
echo "hello-nova-update %{version}-%{release}"
EOF
chmod 755 %{buildroot}/usr/bin/hello-nova-update

%files
/usr/share/hello-nova-update/VERSION
/usr/bin/hello-nova-update

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 1.0.0-1
- Initial test package for Nova Update e2e
