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
installer. This manual tarball flow requires LabPod v0.4.1 or newer; older
release tags do not provide all of the signed assets used below.

```bash
# Run the flow in a subshell so a failed verification stops the install
# without terminating an interactive shell.
(
set -e

TARBALL="labpod-linux-x86_64.tar.gz"

# Resolve "latest" to a concrete tag once, so every asset comes from the same
# release even if a new version is published mid-download. Set BASE yourself
# to pin a different release.
if [ -z "${BASE:-}" ]; then
  latest_url="$(curl -fsSL -o /dev/null -w '%{url_effective}' \
    https://github.com/LabPod/labpod/releases/latest)"
  BASE="https://github.com/LabPod/labpod/releases/download/${latest_url##*/}"
fi

curl -fLO "${BASE}/${TARBALL}"
curl -fLO "${BASE}/${TARBALL}.sig"
curl -fLO "${BASE}/SHA256SUMS"
curl -fLO "${BASE}/SHA256SUMS.sig"

cat > labpod-artifact-pub.pem <<'EOF'
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEki5c/1B4iOqb16m6ljKHjnbbq5EP
D8mP4mNRCYrqniXLDAkDFbpGaMw6WqPBiCQUVqyvDzyL+pADdJTAdxcUSw==
-----END PUBLIC KEY-----
EOF

# The signatures are the root of trust, so verify them before reading either
# file. Both the tarball and the asset manifest are signed with this key.
openssl dgst -sha256 \
  -verify labpod-artifact-pub.pem \
  -signature "${TARBALL}.sig" \
  "${TARBALL}"
openssl dgst -sha256 \
  -verify labpod-artifact-pub.pem \
  -signature SHA256SUMS.sig \
  SHA256SUMS

# SHA256SUMS also covers the CLI binaries, which this flow does not download.
# Read exactly the tarball's entry rather than running `sha256sum -c` over the
# whole file, so a manifest entry for an unrelated local asset cannot stand in
# for a missing tarball entry.
tarball_checksum="$(
  awk -v f="${TARBALL}" '
    {
      sub(/\r$/, "")
      name = $2
      sub(/^\*/, "", name)
      sub(/^.*\//, "", name)
      if (name == f) {
        if (count && $1 != hash) conflict = 1
        count++
        hash = $1
      }
    }
    END {
      if (!count) {
        print "SHA256SUMS has no entry for " f > "/dev/stderr"
        exit 1
      }
      if (conflict) {
        print "SHA256SUMS has conflicting checksums for " f > "/dev/stderr"
        exit 1
      }
      if (length(hash) != 64 || hash !~ /^[[:xdigit:]]+$/) {
        print "SHA256SUMS has a malformed SHA-256 for " f > "/dev/stderr"
        exit 1
      }
      print hash
    }
  ' SHA256SUMS
)" || exit 1
printf '%s  %s\n' "${tarball_checksum}" "${TARBALL}" | sha256sum -c -

# Extract into a new directory so files from an older release cannot survive
# next to the installer that is about to run.
mkdir labpod-release || {
  echo "labpod-release/ already exists; remove it before extracting" >&2
  exit 1
}
tar -xzf "${TARBALL}" -C labpod-release

sudo bash labpod-release/scripts/install.sh
)
```

To install a pinned version from tarball assets, set `BASE` to a versioned
release URL for v0.4.1 or newer before running the block above:

```bash
# Replace v0.4.1 with the desired tag (v0.4.1 or newer).
BASE=https://github.com/LabPod/labpod/releases/download/v0.4.1
```

The packaged installer accepts the host-setup options the curl installer passes
through, such as `--check`, `--skip-app`, `--skip-socket`, and `--with-hami`:

```bash
sudo bash labpod-release/scripts/install.sh --check
```

`--version` is not among them: the curl front-end consumes that flag itself to
choose which release to download, and a release tarball is already one specific
release — set `BASE` above to choose it. The packaged installer rejects unknown
options with `unknown arg: --version` and exit status 2. To assert which release
you are installing, v0.4.1 and newer accept `--expected-version`, which verifies
the bundled binary reports the requested tag:

```bash
sudo bash labpod-release/scripts/install.sh --expected-version v0.4.1
```

Run `sudo bash labpod-release/scripts/install.sh --help` for the full option
list.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
