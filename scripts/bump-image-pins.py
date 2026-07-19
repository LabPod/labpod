#!/usr/bin/env python3
"""Bump the version pins that live in the image build workflow matrices.

Dependabot handles GitHub Actions and Dockerfile base-image tags, but it cannot
see the pip/torch/code-server versions embedded in the build matrices. This
script fetches the latest stable release of each and rewrites the pins in place,
so the scheduled bump-image-pins workflow can open a review PR. The PR-triggered
image builds validate (no publish), so a bad wheel/version combination is caught
before merge. See issue #875.

Handled pins:
  - torch / torchvision   -> build-pytorch-images.yml, build-pytorch-demo-images.yml
                             (only the newest shared pin; the cu121 old-driver
                             line stays put)
  - tensorflow            -> build-tensorflow-images.yml (tf_version)
  - code-server           -> images/pytorch-demo/Dockerfile (version + amd64/arm64 sha256)

No third-party imports: uses urllib + a tiny stable-version comparator so the
script runs on a bare runner.
"""

import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"
PYTORCH_WFS = [WF / "build-pytorch-images.yml", WF / "build-pytorch-demo-images.yml"]
TF_WF = WF / "build-tensorflow-images.yml"
DEMO_DOCKERFILE = ROOT / "images" / "pytorch-demo" / "Dockerfile"

_STABLE_RE = re.compile(r"^\d+(\.\d+)*$")


def version_key(v):
    return tuple(int(p) for p in v.split("."))


def is_stable(v):
    return bool(_STABLE_RE.match(v))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "labpod-bump-pins"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def latest_stable_pypi(pkg):
    data = json.loads(get(f"https://pypi.org/pypi/{pkg}/json"))
    stable = [v for v in data["releases"] if is_stable(v) and data["releases"][v]]
    return max(stable, key=version_key)


def latest_code_server():
    data = json.loads(get("https://api.github.com/repos/coder/code-server/releases/latest"))
    return data["tag_name"].lstrip("v")


def sha256_of(url):
    h = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "labpod-bump-pins"})
    with urllib.request.urlopen(req, timeout=300) as r:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def newest_pinned(files, key):
    """Highest stable value of `<key>: <ver>` across the given workflow files."""
    found = set()
    pat = re.compile(rf"\b{re.escape(key)}:\s*([0-9.]+)")
    for f in files:
        for m in pat.finditer(f.read_text()):
            if is_stable(m.group(1)):
                found.add(m.group(1))
    return max(found, key=version_key) if found else None


def replace_in(files, old_line_key, old, new):
    changed = []
    for f in files:
        txt = f.read_text()
        new_txt = re.sub(rf"(\b{re.escape(old_line_key)}:\s*){re.escape(old)}\b", rf"\g<1>{new}", txt)
        if new_txt != txt:
            f.write_text(new_txt)
            changed.append(f.relative_to(ROOT).as_posix())
    return changed


def main():
    changes = []

    # torch / torchvision (newest shared pin only; cu121 stays put).
    cur_torch = newest_pinned(PYTORCH_WFS, "torch")
    cur_tv = newest_pinned(PYTORCH_WFS, "torchvision")
    new_torch = latest_stable_pypi("torch")
    new_tv = latest_stable_pypi("torchvision")
    if cur_torch and version_key(new_torch) > version_key(cur_torch):
        files = replace_in(PYTORCH_WFS, "torch", cur_torch, new_torch)
        if files:
            changes.append(f"torch {cur_torch} -> {new_torch} ({', '.join(files)})")
    if cur_tv and version_key(new_tv) > version_key(cur_tv):
        files = replace_in(PYTORCH_WFS, "torchvision", cur_tv, new_tv)
        if files:
            changes.append(f"torchvision {cur_tv} -> {new_tv} ({', '.join(files)})")

    # TensorFlow (single matrix value).
    cur_tf = newest_pinned([TF_WF], "tf_version")
    new_tf = latest_stable_pypi("tensorflow")
    if cur_tf and version_key(new_tf) > version_key(cur_tf):
        files = replace_in([TF_WF], "tf_version", cur_tf, new_tf)
        if files:
            changes.append(f"tensorflow {cur_tf} -> {new_tf} ({', '.join(files)})")

    # code-server (Dockerfile ARG version + both arch sha256).
    df = DEMO_DOCKERFILE.read_text()
    cur_cs = re.search(r"CODE_SERVER_VERSION=([0-9.]+)", df).group(1)
    new_cs = latest_code_server()
    if is_stable(new_cs) and version_key(new_cs) > version_key(cur_cs):
        base = f"https://github.com/coder/code-server/releases/download/v{new_cs}"
        sha_amd64 = sha256_of(f"{base}/code-server_{new_cs}_amd64.deb")
        sha_arm64 = sha256_of(f"{base}/code-server_{new_cs}_arm64.deb")
        df = re.sub(r"(CODE_SERVER_VERSION=)[0-9.]+", rf"\g<1>{new_cs}", df)
        df = re.sub(r"(CODE_SERVER_SHA256_AMD64=)[0-9a-f]{64}", rf"\g<1>{sha_amd64}", df)
        df = re.sub(r"(CODE_SERVER_SHA256_ARM64=)[0-9a-f]{64}", rf"\g<1>{sha_arm64}", df)
        DEMO_DOCKERFILE.write_text(df)
        changes.append(f"code-server {cur_cs} -> {new_cs} (images/pytorch-demo/Dockerfile, sha256 recomputed)")

    summary = "\n".join(f"- {c}" for c in changes)
    print(summary if changes else "No pin updates available.")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"changed={'true' if changes else 'false'}\n")
            fh.write("summary<<EOF\n" + (summary or "No pin updates available.") + "\nEOF\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
