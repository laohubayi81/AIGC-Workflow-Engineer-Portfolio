# Default base is a Docker Hub mirror (docker.io is often unreachable in CN / IPv6).
# base 比 cudnn-runtime 小一截；PyTorch cu124 轮子自带 CUDA。
ARG CUDA_IMAGE=docker.m.daocloud.io/nvidia/cuda:12.4.1-base-ubuntu22.04
FROM ${CUDA_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    GIT_TERMINAL_PROMPT=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git python3 python3-pip \
        libgl1 libglib2.0-0 libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

# GitHub is flaky; gitclone.com was used successfully on this machine for other repos.
WORKDIR /opt
RUN git clone --depth 1 https://gitclone.com/github.com/comfyanonymous/ComfyUI.git \
    || git clone --depth 1 https://ghfast.top/https://github.com/comfyanonymous/ComfyUI.git \
    || git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /opt/ComfyUI

RUN python -m pip install --break-system-packages --upgrade pip \
    && python -m pip install --break-system-packages \
        torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 \
    && python -m pip install --break-system-packages -r requirements.txt \
        opencv-python-headless onnxruntime-gpu

RUN mkdir -p custom_nodes \
    && git clone --depth 1 https://gitclone.com/github.com/Fannovel16/comfyui_controlnet_aux.git custom_nodes/comfyui_controlnet_aux \
    && git clone --depth 1 https://gitclone.com/github.com/facok/comfyui-krea2-controlnet.git custom_nodes/comfyui-krea2-controlnet \
    && git clone --depth 1 https://gitclone.com/github.com/lbouaraba/comfyui-krea2edit.git custom_nodes/comfyui-krea2edit

COPY custom-nodes/comfyui-delivery-gate /opt/ComfyUI/custom_nodes/comfyui-delivery-gate
COPY deploy/docker/extra_model_paths.yaml /opt/ComfyUI/extra_model_paths.yaml

RUN mkdir -p /models /input /output

EXPOSE 8188
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188", \
     "--extra-model-paths-config", "/opt/ComfyUI/extra_model_paths.yaml", \
     "--input-directory", "/input", "--output-directory", "/output"]
