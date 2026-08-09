# LabPod Releases

This repository publishes LabPod server release artifacts. Source code is
maintained separately.

LabPod is a single-node, multi-user GPU workspace manager for shared lab
workstations. Product documentation lives at https://docs.labpod.ai.

## Workspace images

Managed workspace image Dockerfiles, release automation, tag documentation,
and contribution guidance live in
[`LabPod/labpod-images`](https://github.com/LabPod/labpod-images). Public image
pull references remain under `ghcr.io/labpod/*`.

## Release assets

Every release publishes the server archive `labpod-linux-x86_64.tar.gz`, a
detached ECDSA-P256 signature for that archive, and a `SHA256SUMS` manifest
covering the release assets.

Standalone CLI binaries are published from v0.3.0 onward. A detached signature
for `SHA256SUMS` is published from v0.4.1 onward; in earlier releases the
manifest is unsigned, so the server archive is the only asset the signing key
authenticates. Verifying a downloaded asset is documented in the install guide.

## Installing

Run the public installer on the target Linux GPU workstation:

```bash
curl -fsSL https://labpod.ai/install.sh | sudo bash
```

It downloads a release from this repository, verifies it against a signing key
embedded in the script, and runs the packaged installer. Options, pinned
releases, and the change-control flow that avoids piping into a shell are
documented in the install guide: https://docs.labpod.ai/operators/install/

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
