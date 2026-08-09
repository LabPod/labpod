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

## Install with curl

Run the public installer on the target Linux GPU workstation:

```bash
# Check what the installer would do without changing the host
curl -fsSL https://labpod.ai/install.sh | sudo bash -s -- --check

# Install the latest release
curl -fsSL https://labpod.ai/install.sh | sudo bash
```

To install a pinned release instead of the latest release, pass a version tag:

```bash
curl -fsSL https://labpod.ai/install.sh | sudo bash -s -- --version v0.x.y
```

The installer sets up host prerequisites, Podman rootless support, the LabPod
binary, systemd units, and the GPU container stack. It does not install the
NVIDIA GPU driver itself.

## Install without piping to bash

If your change-control process does not allow `curl | bash`, download the
public bootstrap to a file, review that file, then execute it. This uses the
same signature, checksum, archive-member, and temporary-extraction checks as
the piped installer and the in-app updater, without maintaining a second copy
of the signing key or verification logic in this README.

```bash
curl -fsSL https://labpod.ai/install.sh -o labpod-install.sh

# Review the complete script with your normal editor or pager.
less labpod-install.sh

# Check what the installer would do without changing the host.
sudo bash ./labpod-install.sh --check

# Install the latest release.
sudo bash ./labpod-install.sh
```

To install a pinned release or pass a host-setup option, add it after the
script path:

```bash
sudo bash ./labpod-install.sh --version v0.4.1
sudo bash ./labpod-install.sh --skip-app
```

## Install from an offline release mirror

For an air-gapped workstation, stage the bootstrap and its four signed release
assets on a connected Linux machine. Use a concrete tag so every file belongs
to one immutable release:

```bash
TAG=v0.4.1
MIRROR=labpod-offline
ASSET_DIR="${MIRROR}/download/${TAG}"
BASE="https://github.com/LabPod/labpod/releases/download/${TAG}"

mkdir -p "${ASSET_DIR}"
curl -fsSL https://labpod.ai/install.sh -o "${MIRROR}/install.sh"
for asset in \
  labpod-linux-x86_64.tar.gz \
  labpod-linux-x86_64.tar.gz.sig \
  SHA256SUMS \
  SHA256SUMS.sig
do
  curl -fL "${BASE}/${asset}" -o "${ASSET_DIR}/${asset}"
done
```

Transfer the whole `labpod-offline/` directory to the workstation, review
`install.sh`, then point that same bootstrap at the local mirror:

```bash
TAG=v0.4.1
MIRROR="$(realpath labpod-offline)"

sudo env LABPOD_BOOTSTRAP_RELEASES_BASE="file://${MIRROR}" \
  bash "${MIRROR}/install.sh" --version "${TAG}"
```

The bootstrap verifies both detached ECDSA-P256 signatures before relying on
`SHA256SUMS`, checks the archive against the authenticated manifest, validates
archive members, extracts into a temporary directory, and only then runs the
packaged installer.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
