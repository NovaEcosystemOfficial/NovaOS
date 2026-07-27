# NovaOS identity environment for Plasma sessions
export NOVA_ASSETS=/usr/share/nova/assets
export NOVA_IDENTITY_VERSION=0.2.7
# Ensure About / branding helpers see Nova assets first
export XDG_DATA_DIRS="/usr/share/nova:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
