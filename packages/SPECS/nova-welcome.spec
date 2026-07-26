Name:           nova-welcome
Version:        0.2.3
Release:        1%{?dist}
Summary:        Nova Welcome — NovaOS first-boot experience
License:        MIT
BuildArch:      noarch
URL:            https://github.com/novaos/NovaOS
Requires:       python3 >= 3.11
Requires:       python3-pyside6
Recommends:     nova-center

%description
Official NovaOS first-boot wizard (Nova Welcome). Qt/PySide6 onboarding that
runs once per user via XDG autostart, then writes
~/.config/nova/welcome-completed and can open Nova Center. Ships shared
nova_shared helpers for hostname/theme preferences (desktop.shared.v1).

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/nova/welcome
mkdir -p %{buildroot}/usr/share/nova/shared
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/etc/xdg/autostart
mkdir -p %{buildroot}/usr/share/doc/%{name}
mkdir -p %{buildroot}/etc/skel/.config/autostart

cp -a %{_nova_root}/desktop/nova-welcome/nova_welcome %{buildroot}/usr/share/nova/welcome/
cp -a %{_nova_root}/desktop/nova-shared/nova_shared %{buildroot}/usr/share/nova/shared/
find %{buildroot}/usr/share/nova -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}/usr/share/nova -type f -name '*.pyc' -delete 2>/dev/null || true

install -m 0755 %{_nova_root}/desktop/nova-welcome/bin/nova-welcome %{buildroot}/usr/bin/nova-welcome
install -m 0644 %{_nova_root}/desktop/nova-welcome/org.novaos.Welcome.desktop \
  %{buildroot}/usr/share/applications/org.novaos.Welcome.desktop
install -m 0644 %{_nova_root}/desktop/nova-welcome/org.novaos.Welcome.autostart.desktop \
  %{buildroot}/etc/xdg/autostart/org.novaos.Welcome.desktop
# Also seed new user homes (Calamares/useradd skel)
install -m 0644 %{_nova_root}/desktop/nova-welcome/org.novaos.Welcome.autostart.desktop \
  %{buildroot}/etc/skel/.config/autostart/org.novaos.Welcome.desktop
install -m 0644 %{_nova_root}/desktop/nova-welcome/README.md %{buildroot}/usr/share/doc/%{name}/README.md

%files
%doc %{_datadir}/doc/%{name}/README.md
%{_bindir}/nova-welcome
%{_datadir}/nova/welcome/
%{_datadir}/nova/shared/
%{_datadir}/applications/org.novaos.Welcome.desktop
/etc/xdg/autostart/org.novaos.Welcome.desktop
/etc/skel/.config/autostart/org.novaos.Welcome.desktop

%changelog
* Sun Jul 26 2026 NovaOS Team <dev@novaos.local> - 0.2.3-1
- First Nova Welcome first-boot wizard (Sprint 17)
