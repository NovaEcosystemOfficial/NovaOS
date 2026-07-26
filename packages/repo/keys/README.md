# NovaOS RPM signing key

| File | Role |
|------|------|
| `RPM-GPG-KEY-novaos` | Canonical key installed at `/etc/pki/novaos/RPM-GPG-KEY-novaos` |
| `novaos-rpm-placeholder.gpg` | Same material (dev alias); do not use as alternate install path |

Referenced by `packages/repo/conf/novaos-*.repo` (`gpgkey=file:///etc/pki/novaos/RPM-GPG-KEY-novaos`).

**Before public release:** replace both files with the production signing public key.
Until then the key is a placeholder trust anchor (policy `warn` in nova-update.conf).
