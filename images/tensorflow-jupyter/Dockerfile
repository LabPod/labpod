# LabPod TensorFlow + JupyterLab composite image (public, pull-only).
#
# Built and pushed to ghcr.io/labpod/tensorflow-jupyter:<cuda-tag> by
# .github/workflows/build-tensorflow-images.yml. Replaces the upstream
# jovyan-based quay.io/jupyter/tensorflow-notebook for LabPod's default
# "TensorFlow JupyterLab" template: no baked USER (runs as the workspace
# owner under rootless Podman), no /home/jovyan remnants, WORKDIR /work.
#
# CUDA pairing differs from the PyTorch image: tensorflow[and-cuda] bundles
# its CUDA user-space through pip nvidia-* wheels, so the effective CUDA
# runtime is pinned by the TensorFlow version, not by a per-CUDA wheel index.
# The nvidia/cuda base only supplies a consistent system + forward-compat
# layout; TensorFlow loads its own bundled CUDA 12.x libs from the venv.
# The tag names the CUDA floor those wheels require:
#   cu125 -> TensorFlow 2.21 / and-cuda wheels (CUDA 12.5+, cuDNN 9.3), Ubuntu 24.04 base
# tensorflow[and-cuda] supports host driver >= 525.60.13 via CUDA 12 minor-
# version compatibility, so a single tag covers older driver lines (e.g. 535).
# Verify the TensorFlow pin against PyPI on the first CI run.
ARG CUDA_BASE_IMAGE=docker.io/nvidia/cuda:12.5.1-runtime-ubuntu24.04
FROM ${CUDA_BASE_IMAGE}

LABEL org.opencontainers.image.description="LabPod TensorFlow + JupyterLab workspace image with CUDA, TensorBoard, and common scientific Python tools."

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"
ARG TF_VERSION=2.21.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        htop \
        iproute2 \
        jq \
        less \
        nano \
        openssh-client \
        python3 \
        python3-venv \
        rsync \
        tmux \
        tree \
        unzip \
        vim \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv "$VIRTUAL_ENV" \
    && python3 -m pip install --no-cache-dir uv \
    && uv --version

# TensorFlow's and-cuda extra pulls the matching nvidia-* CUDA wheels, so the
# bundled CUDA runtime tracks the TensorFlow version instead of PyPI defaults.
RUN uv pip install --no-cache "tensorflow[and-cuda]==${TF_VERSION}"

# TensorBoard ships with TensorFlow, so it is not installed separately.
RUN uv pip install --no-cache \
        jupyterlab \
        ipywidgets \
        jupyter-resource-usage \
        numpy \
        pandas \
        scikit-learn \
        matplotlib

WORKDIR /work
EXPOSE 8888 6006

# Stay-alive composite: LabPod starts JupyterLab / TensorBoard on demand
# via `podman exec`, so PID 1 just stays alive. LabPod runs every
# workspace with `podman run --init`, so zombie reaping is handled by
# catatonit injected at runtime — the image doesn't bundle its own init.
ENTRYPOINT ["sleep", "infinity"]
