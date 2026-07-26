"""Package signature verification foundation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SignatureReport:
    policy: str
    ok: bool
    checked: int
    missing_keys: list[str]
    unverified: list[str]
    message: str


def discover_keys(keys_dir: Path) -> list[Path]:
    if not keys_dir.is_dir():
        return []
    keys: list[Path] = []
    for pattern in ("*.gpg", "*.asc", "*.pub", "*.pem"):
        keys.extend(sorted(keys_dir.glob(pattern)))
    return keys


def verify_updates(
    package_names: list[str],
    *,
    keys_dir: Path,
    policy: str = "warn",
) -> SignatureReport:
    """Foundation verifier.

    Production will invoke rpm/gpg/sigstore. Here we gate on key material presence
    and treat packages as verified when keys exist and policy is not enforce-without-keys.
    """
    policy = (policy or "warn").lower()
    if policy == "off":
        return SignatureReport(
            policy=policy,
            ok=True,
            checked=len(package_names),
            missing_keys=[],
            unverified=[],
            message="signature verification disabled",
        )

    keys = discover_keys(keys_dir)
    # Placeholder production key names must not count as real trust anchors.
    real_keys = [
        k
        for k in keys
        if "placeholder" not in k.name.lower() and "example" not in k.name.lower()
    ]

    if not real_keys:
        msg = (
            f"no production NovaOS signing keys in {keys_dir}; "
            "using placeholder/dev trust path"
        )
        if policy == "enforce":
            return SignatureReport(
                policy=policy,
                ok=False,
                checked=len(package_names),
                missing_keys=["novaos-release"],
                unverified=list(package_names),
                message=msg,
            )
        return SignatureReport(
            policy=policy,
            ok=True,
            checked=len(package_names),
            missing_keys=["novaos-release"],
            unverified=[],
            message=msg + " (policy=warn)",
        )

    return SignatureReport(
        policy=policy,
        ok=True,
        checked=len(package_names),
        missing_keys=[],
        unverified=[],
        message=f"keys present ({len(real_keys)}); rpm --checksig integration pending",
    )
