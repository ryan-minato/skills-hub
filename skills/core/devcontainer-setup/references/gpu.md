# GPU dev containers

Read this before writing any configuration that needs GPU access, or whose
base image comes from `nvcr.io`.

Both vendors share two facts:

- `hostRequirements.gpu` is vendor-neutral metadata for tools that pick
  hosts: `true` (require), `"optional"` (use if present), or an object like
  `{ "cores": 1, "memory": "16gb" }`. Default to `"optional"` so the config
  still opens on GPU-less machines; use `true` only when the project is
  unusable without a GPU.
- Actual GPU exposure happens through `runArgs` (raw `docker run`
  arguments) — there is no first-class GPU property beyond the two above.

## NVIDIA (primary path, inside the trusted sources)

Use an NGC image (`nvcr.io/nvidia/*`) when the project needs a
GPU-accelerated framework preinstalled; they ship matched CUDA/cuDNN/
framework stacks that are painful to assemble by hand.

- Framework images: `nvcr.io/nvidia/pytorch`, `nvcr.io/nvidia/tensorflow`
  — batteries included, large.
- Bare toolkit: `nvcr.io/nvidia/cuda` — when the project installs its own
  frameworks (e.g. via `uv`/`conda`) and only needs the CUDA runtime.
- Tags are date-based (`yy.mm`, e.g. `25.03-py3`) and `latest` often does
  not exist. List them first and pin one:

  ```bash
  uv run scripts/list_sources.py --tags nvcr.io/nvidia/pytorch --limit 40
  ```

NGC images are **not** devcontainer-prebuilt, so the baseline features
rule applies with no exceptions: without `common-utils` there is no
non-root user or shell baseline, and user creation, `remoteUser`, and
other features misbehave. A known-good starting point:

```jsonc
{
  "name": "gpu-training",
  "image": "nvcr.io/nvidia/pytorch:<yy.mm>-py3", // pin from --tags output
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {
      "username": "vscode"
    },
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/git-lfs:1": {}
  },
  "remoteUser": "vscode",
  "runArgs": ["--gpus", "all"],
  "hostRequirements": { "gpu": "optional" }
}
```

Notes on this shape:

- `common-utils` creates the `vscode` user; `updateRemoteUserUID` (default
  true) then aligns it with the local UID on Linux. Running as root is
  acceptable only for throwaway experiments the user says are throwaway.
- Restrict `--gpus` when sharing a multi-GPU host:
  `["--gpus", "device=0"]`.
- CUDA on a non-NGC trusted image is also possible: add
  `ghcr.io/devcontainers/features/nvidia-cuda:3` on top of an
  `mcr.microsoft.com/devcontainers/*` image when the user needs only the
  toolkit, not a full NGC stack.

Host prerequisites (tell the user; not checkable from inside a config):
an NVIDIA driver and the NVIDIA Container Toolkit on the Docker host.
Smoke test after the container starts:

```bash
nvidia-smi          # must list the GPU(s)
python -c "import torch; print(torch.cuda.is_available())"  # frameworks
```

## AMD (ROCm — outside the default trusted sources)

AMD GPUs are exposed by device passthrough, not `--gpus` (that flag is
NVIDIA-runtime-specific):

```jsonc
{
  "runArgs": [
    "--device=/dev/kfd",
    "--device=/dev/dri",
    "--group-add", "video",
    "--group-add", "render"
  ],
  "hostRequirements": { "gpu": "optional" }
}
```

ROCm images (Docker Hub `rocm/*`, e.g. `rocm/pytorch`, `rocm/dev-ubuntu-22.04`)
are **not** in this skill's trusted sources. Two compliant routes:

1. Preferred: ask the user to explicitly approve the ROCm image (the
   policy's escape hatch), then treat it like any non-prebuilt image —
   baseline features (`common-utils` + `git`, usually `git-lfs`) still
   apply.
2. Alternative: start from a trusted `mcr.microsoft.com/devcontainers/*`
   image and install ROCm userspace in a Dockerfile — only worth it when
   the ROCm stack needed is small; full framework stacks are better served
   by route 1.

Host prerequisites: `amdgpu` kernel driver and ROCm on the host. Smoke
test inside the container: `rocminfo` or `rocm-smi` must list the GPU;
frameworks report via `torch.cuda.is_available()` (ROCm builds reuse the
CUDA API surface).

## Companion features for GPU workflows

From `ghcr.io/stacit-ai/devcontainer-features/*` (trusted): `uv`,
`micromamba`, `miniforge` for Python environment management on top of
framework images; `huggingface` + `hf-mount` for model/dataset access;
`ollama` and `llama-cpp` for local LLM serving. List current options with:

```bash
uv run scripts/list_sources.py --kind features --format json
```
