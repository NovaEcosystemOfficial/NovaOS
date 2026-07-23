# Security policy — NovaOS

## What may be in this repository

- **Public demo credentials** for Milestone 0.1 development / live ISO images  
  (`configs/kiwi/novaos-m01/PUBLIC_DEMO_CREDENTIALS.txt`: user `nova` / password `novaos`)  
  These are **not secrets**. They exist so engineers can boot and test the image.

## What must NEVER be committed

- API keys, OAuth tokens, GitHub PATs, cloud credentials
- Private keys (`.pem`, `.key`, SSH, TLS)
- `.env` files with real secrets
- Production passwords or customer data
- Service-account JSON / signing keys for release infrastructure

Use local untracked files (see `.gitignore`: `secrets/`, `credentials/`, `.env`, `configs/bootstrap/env.sh`).

## Why we did not rewrite git history

The only passwords previously published were these **trivial public demo ISO logins**.  
Rewriting `main` history and force-pushing would add operational risk for almost no security benefit (the values were never high-value secrets).

If a **real** secret is ever committed by mistake: rotate it immediately, then request a coordinated history purge.

## Production images

Before any external / production distribution, replace demo passwords with a secure first-boot or installer flow. Do not ship `novaos` as a default on real systems.
