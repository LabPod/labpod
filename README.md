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
public bootstrap to a file, verify it, review it, then execute it. It performs
the same signature, checksum, archive-member, and temporary-extraction checks
as the piped installer and the in-app updater.

```bash
curl -fsSL https://labpod.ai/install.sh -o labpod-install.sh
```

The bootstrap carries the release signing key, and everything it verifies is
anchored to that key. Confirm the copy you downloaded carries the expected one
before running it:

```bash
awk '/BEGIN PUBLIC KEY/{p=1} p{print} /END PUBLIC KEY/{if(p) exit}' labpod-install.sh \
  | sed 's/^[^-]*-----BEGIN/-----BEGIN/; s/-----END PUBLIC KEY-----.*/-----END PUBLIC KEY-----/' \
  | openssl pkey -pubin -outform DER \
  | sha256sum
```

That must print:

```
811dcb94b2641574e62931782fafa93f863f608018d099d118b6d38f3b69024e
```

A different value means the script did not come from us — stop, and do not run
it. Then review and run:

```bash
# Review the complete script with your normal editor or pager.
less labpod-install.sh

# Check what the installer would do without changing the host.
sudo bash ./labpod-install.sh --version v0.x.y --check

# Install that same release.
sudo bash ./labpod-install.sh --version v0.x.y
```

Pass the same `--version` to both commands. Without it each run independently
resolves the latest release, so a release published between the two would be
installed without its dry run ever having been reviewed. Omit `--version`
entirely only if installing whatever is current is acceptable.

Any other option is passed through to the packaged installer, for example:

```bash
sudo bash ./labpod-install.sh --skip-app
```

Run `sudo bash ./labpod-install.sh --help` for the full option list.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
