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

## Review-first and offline installation

For v0.5.1 and newer, an operator can verify and extract a release as a regular
user before granting its installer root access. A fully offline host must have
the prerequisites from the install guide pre-provisioned, including rootless
Podman support and `nvidia-ctk` when an NVIDIA driver is present.

On a connected staging host, copy `https://labpod.ai/install.sh` and these four
assets from one release tag into `<mirror>/download/<tag>/`:

- `labpod-linux-x86_64.tar.gz`
- `labpod-linux-x86_64.tar.gz.sig`
- `SHA256SUMS`
- `SHA256SUMS.sig`

Transfer that mirror to the offline host, then verify and extract the exact tag
without root:

```bash
version=v0.5.1
mirror=/media/labpod-releases
review_dir="$PWD/labpod-$version"

LABPOD_BOOTSTRAP_RELEASES_BASE="file://$mirror" \
  bash "$mirror/install.sh" --version "$version" --extract-only "$review_dir"
```

Review the entire extracted tree, especially `scripts/install.sh` and
`deploy/`, before running it as root:

```bash
sudo "$review_dir/scripts/install.sh" --offline \
  --release-mirror "file://$mirror" --skip-gpu-verify
```

Omit `--skip-gpu-verify` only when the documented CUDA probe image is already
in the target user's local Podman store. `--release-mirror` is saved in the
root-owned install layout, so later in-app update applies use the same
versioned mirror. Release discovery is separate: leave automatic checks off on
an air-gapped host or configure the documented local metadata endpoint.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
