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

## Install from the release tarball

If your change-control process does not allow `curl | bash`, download the
release assets first, verify them, extract the tarball, then run the packaged
installer:

```bash
BASE="https://github.com/LabPod/labpod/releases/latest/download"

curl -fLO "${BASE}/labpod-linux-x86_64.tar.gz"
curl -fLO "${BASE}/labpod-linux-x86_64.tar.gz.sig"
curl -fLO "${BASE}/SHA256SUMS"

cat > labpod-artifact-pub.pem <<'EOF'
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEki5c/1B4iOqb16m6ljKHjnbbq5EP
D8mP4mNRCYrqniXLDAkDFbpGaMw6WqPBiCQUVqyvDzyL+pADdJTAdxcUSw==
-----END PUBLIC KEY-----
EOF

# The signature is the root of trust for the tarball, so verify it first.
openssl dgst -sha256 \
  -verify labpod-artifact-pub.pem \
  -signature labpod-linux-x86_64.tar.gz.sig \
  labpod-linux-x86_64.tar.gz

# SHA256SUMS also covers the CLI binaries, which this flow does not download.
# --ignore-missing scopes the check to the files you actually fetched; it still
# fails if the tarball's hash is wrong or its entry is absent.
sha256sum --ignore-missing -c SHA256SUMS

mkdir -p labpod-release
tar -xzf labpod-linux-x86_64.tar.gz -C labpod-release

sudo bash labpod-release/scripts/install.sh
```

To install a pinned version from tarball assets, set `BASE` to a versioned
release URL such as
`https://github.com/LabPod/labpod/releases/download/v0.4.1`.

The packaged installer accepts the same host-setup options as the curl
installer, for example:

```bash
sudo bash labpod-release/scripts/install.sh --check
```

`--version` is not one of them. It is consumed by the curl front-end, which
uses it to choose which release to download; a release tarball is already a
pinned version, so the packaged installer has nothing to resolve. Run
`sudo bash labpod-release/scripts/install.sh --help` for its full option list.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
