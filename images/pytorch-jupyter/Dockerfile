# LabPod PyTorch + JupyterLab composite image (public, pull-only).
#
# Built and pushed to ghcr.io/labpod/pytorch-jupyter:<cuda-tag> by
# .github/workflows/build-pytorch-images.yml. Replaces the upstream
# jovyan-based quay.io/jupyter/pytorch-notebook for LabPod's default
# "PyTorch JupyterLab" template: no baked USER (runs as the workspace
# owner under rootless Podman), no /home/jovyan remnants, WORKDIR /work.
#
# CUDA/torch pairing is supplied per tag by the build matrix:
#   cu121 -> CUDA 12.1 / Ubuntu 22.04 base, torch cu121 wheels (sm_50--sm_90)
#   cu126 -> CUDA 12.6 / Ubuntu 24.04 base, torch cu126 wheels (sm_50--sm_90)
#   cu129 -> CUDA 12.9 / Ubuntu 24.04 base, torch cu129 wheels (sm_70--sm_120)
# torch cu128/cu129 wheels dropped pre-Volta support; those tags need sm_70+.
# Verify the torch/torchvision pins against the wheel index the first CI
# run (older tags cap out at older torch: cu121 -> torch 2.5.1).
ARG CUDA_BASE_IMAGE=docker.io/nvidia/cuda:12.6.3-runtime-ubuntu24.04
FROM ${CUDA_BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"
ARG TORCH_CUDA=cu126
ARG TORCH_VERSION=2.8.0
ARG TORCHVISION_VERSION=0.23.0

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

# PyTorch pinned to the matching wheel index so the bundled CUDA libs
# track the image's CUDA base instead of floating with PyPI defaults.
RUN uv pip install --no-cache \
        --index-url "https://download.pytorch.org/whl/${TORCH_CUDA}" \
        "torch==${TORCH_VERSION}" \
        "torchvision==${TORCHVISION_VERSION}"

RUN uv pip install --no-cache \
        jupyterlab \
        ipywidgets \
        jupyter-resource-usage \
        tensorboard \
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
