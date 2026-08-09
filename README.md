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

Every release publishes the server archive `labpod-linux-x86_64.tar.gz`, the
standalone CLI binaries, a `SHA256SUMS` manifest, and detached ECDSA-P256
signatures.

## Installing

Run the public installer on the target Linux GPU workstation:

```bash
curl -fsSL https://labpod.ai/install.sh | sudo bash
```

It downloads a release from this repository, verifies it against a signing key
embedded in the script, and runs the packaged installer. Options, pinned
releases, and the change-control flow that avoids piping into a shell are
documented in the install guide: https://docs.labpod.ai/operators/install/

## Verifying the installer

The signing key that anchors every artifact published here is carried inside
that installer, so a substituted installer would carry a substituted key. This
repository is a separate channel from the site serving the script, which is
what makes the check below meaningful. Confirm the copy you downloaded before
running it:

```bash
curl -fsSL https://labpod.ai/install.sh -o labpod-install.sh

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
it.

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
