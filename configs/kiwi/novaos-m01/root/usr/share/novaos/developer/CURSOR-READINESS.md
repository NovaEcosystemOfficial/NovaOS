# Cursor readiness on NovaOS Developer Edition

Cursor is **not** pre-installed. This image ships dependencies so a Cursor
`.AppImage` / `.rpm` / official installer can run on NovaOS (X11 session).

## Provided

| Area | Packages / notes |
|------|------------------|
| Electron runtime libs | `nss`, `atk`, `at-spi2-atk`, `gtk3`, `libXScrnSaver`, `libXrandr`, `alsa-lib`, `libdrm`, `libxkbcommon`, `mesa-libgbm` |
| Portals | `xdg-desktop-portal`, `xdg-desktop-portal-kde`, `xdg-desktop-portal-gtk` |
| Fonts | `google-noto-sans-fonts`, `google-noto-sans-mono-fonts`, `liberation-fonts-all`, `dejavu-sans-fonts` |
| Graphics | Mesa DRI/Vulkan; on bare metal HW GL enabled (M2); VMs keep software GL |
| Terminal / git | `konsole`, `git`, `openssh-clients` |

## Install Cursor (manual)

1. Download from https://cursor.com (Linux x64 AppImage or RPM).
2. AppImage: `chmod +x Cursor-*.AppImage && ./Cursor-*.AppImage`
3. Or install the RPM with `sudo rpm -Uvh` / `sudo dnf install ./cursor*.rpm`
4. Optional: place a desktop entry under `~/.local/share/applications/`

## Known limits

- Session is Plasma **X11** (Foundation/VM-safe). Cursor on Wayland is untested here.
- Secure Boot may block unsigned AppImages — disable SB for M2 (see M2 checklist).
- Do not vendor Cursor binaries into the NovaOS ISO (license / update surface).
