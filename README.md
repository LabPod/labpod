# LabPod Releases

This repository publishes LabPod binary release artifacts. Source code is maintained separately.

LabPod is a single-node, multi-user GPU workspace manager for shared lab workstations. Product
docs live at https://docs.labpod.ai.

## Container images

LabPod publishes JupyterLab workspace images to the GitHub Container Registry.

### PyTorch + JupyterLab

Browse image versions, manifests, and pull instructions on the
[pytorch-jupyter package page](https://github.com/LabPod/labpod/pkgs/container/pytorch-jupyter).

```bash
podman pull ghcr.io/labpod/pytorch-jupyter:cu129
```

Available CUDA tags are `cu121`, `cu126`, and `cu129`. Images are published for
Linux `amd64`; the host supplies the compatible NVIDIA driver. See the
[image README](images/pytorch-jupyter/README.md) for the CUDA, PyTorch,
architecture, and minimum-driver compatibility matrix.

### TensorFlow + JupyterLab

Browse image versions, manifests, and pull instructions on the
[tensorflow-jupyter package page](https://github.com/LabPod/labpod/pkgs/container/tensorflow-jupyter).

```bash
podman pull ghcr.io/labpod/tensorflow-jupyter:cu125
```

`tensorflow[and-cuda]` bundles its own CUDA user-space, so the driver coupling is
looser than PyTorch's — a single `cu125` tag runs on host driver `>= 525.60.13`.
Images are published for Linux `amd64`; the host supplies the compatible NVIDIA
driver. See the [image README](images/tensorflow-jupyter/README.md) for the
CUDA, TensorFlow, architecture, and minimum-driver compatibility matrix.

### SciPy data science + JupyterLab (CPU)

Browse image versions, manifests, and pull instructions on the
[scipy-jupyter package page](https://github.com/LabPod/labpod/pkgs/container/scipy-jupyter).

```bash
podman pull ghcr.io/labpod/scipy-jupyter:py312
```

A **CPU-only** data-science image (NumPy/SciPy/pandas/scikit-learn/matplotlib/
seaborn/bokeh + JupyterLab) — no CUDA, no host-driver requirement. Published for
Linux `amd64`. See the [image README](images/scipy-jupyter/README.md) for the
stack and Python line.

### PyTorch Demo (kitchen-sink showcase)

Browse image versions, manifests, and pull instructions on the
[pytorch-demo package page](https://github.com/LabPod/labpod/pkgs/container/pytorch-demo).

```bash
podman pull ghcr.io/labpod/pytorch-demo:cpu
```

The image behind LabPod's "PyTorch Demo Workspace" template — JupyterLab,
TensorBoard, code-server, terminal, MLflow, and Aim in one workspace. The `cpu`
tag runs on any host with no driver requirement (fast demo default); `cu121`,
`cu126`, and `cu129` tags demo GPU allocation + monitoring. Published for Linux
`amd64`. See the [image README](images/pytorch-demo/README.md) for the tag matrix.

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

The installer sets up host prerequisites, Podman rootless support, the LabPod binary, systemd
units, and the GPU container stack. It does not install the NVIDIA GPU driver itself.

## Install from the release tarball

If your change-control process does not allow `curl | bash`, download the release assets first,
verify them, extract the tarball, then run the packaged installer:

```bash
BASE="https://github.com/LabPod/labpod/releases/latest/download"

curl -fLO "${BASE}/labpod-linux-x86_64.tar.gz"
curl -fLO "${BASE}/labpod-linux-x86_64.tar.gz.sig"
curl -fLO "${BASE}/SHA256SUMS"

sha256sum -c SHA256SUMS

cat > labpod-artifact-pub.pem <<'EOF'
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEki5c/1B4iOqb16m6ljKHjnbbq5EP
D8mP4mNRCYrqniXLDAkDFbpGaMw6WqPBiCQUVqyvDzyL+pADdJTAdxcUSw==
-----END PUBLIC KEY-----
EOF

openssl dgst -sha256 \
  -verify labpod-artifact-pub.pem \
  -signature labpod-linux-x86_64.tar.gz.sig \
  labpod-linux-x86_64.tar.gz

mkdir labpod-release
tar -xzf labpod-linux-x86_64.tar.gz -C labpod-release

sudo bash labpod-release/scripts/install.sh
```

To install a pinned version from tarball assets, set `BASE` to a versioned release URL such as
`https://github.com/LabPod/labpod/releases/download/v0.1.0`.

You can pass the same installer options after the script path, for example:

```bash
sudo bash labpod-release/scripts/install.sh --check
```

## More documentation

- Install guide: https://docs.labpod.ai/operators/install/
- Requirements: https://docs.labpod.ai/start/requirements/
