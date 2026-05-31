# NeMo Guardrails v0.21.0 sidecar for Squire (Phase 17-10).
#
# Rails config:
#   - self check input  (PolicyAI / Sonnet 4.5 via Anthropic direct)
#   - self check output (same, on generated responses)
#   - presidio PII detection + masking on both input and output
#
# PolicyAI self-check handles prompt-injection + policy classification via
# LLM judge. Fails open when ANTHROPIC_API_KEY has zero credit (see
# rails/*.co); Presidio PII still runs since it is local-only.
#
# NOTE on model choices: v0.21.0 does NOT natively ship engine types for
# GLiNER or PINT v2 as first-party models in the `models:` block (they'd
# require custom Python actions). Presidio is the supported first-party
# PII engine via the sensitive-data-detection (sdd) extra. For 17-11
# red-team coverage we can add a custom action wrapping PINT v2 as a
# follow-up; scaffold first, sharpen later.
#
# Build:  docker build -t cd-service-nemo:dev .
# Run:    via compose block cd-service-nemo (port 127.0.0.1:8001 -> :8000)
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/app/models \
    TRANSFORMERS_CACHE=/app/models/transformers \
    TOKENIZERS_PARALLELISM=false

# build-essential: annoy + some NeMo deps need g++ to compile wheels.
# curl: healthcheck. git: nemoguardrails pulls a few git-deps. libgomp1:
# presidio-analyzer (spaCy + numpy) needs OpenMP runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
        git \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pin nemoguardrails exactly. CPU-only torch via --extra-index-url so the
# default PyPI index still resolves nemoguardrails. [sdd] pulls presidio.
# [server] enables the FastAPI OpenAI-compat chat/completions endpoint.
RUN pip install --upgrade pip \
 && pip install --extra-index-url https://download.pytorch.org/whl/cpu \
        "torch==2.5.1+cpu" \
 && pip install \
        "nemoguardrails[sdd,server]==0.21.0" \
        "protobuf>=5.29.5" \
        "openai>=1.40,<2" \
        "langchain-anthropic>=0.2,<1" \
        "langchain-openai>=0.2,<1"

# Presidio requires a spaCy language model. NeMo's sensitive_data_detection
# action hard-codes en_core_web_lg (see
# nemoguardrails/library/sensitive_data_detection/actions.py::_get_analyzer).
# ~560 MB on disk; no choice for v0.21.0.
RUN python -m spacy download en_core_web_lg

# Strip build-essential after pip install to shrink image (~200 MB).
RUN apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Rails config lives under /app/configs/default at runtime. NeMo's server
# expects `--config <dir>` to be a PARENT folder of named config sub-folders
# (one per deployment). We ship exactly one config, named `default`, so
# clients call /v1/chat/completions with config_id="default".
RUN mkdir -p /app/configs/default
COPY config.yml prompts.yml /app/configs/default/
COPY rails /app/configs/default/rails

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=120s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/v1/rails/configs || exit 1

# --port 8000 inside container; compose maps host 127.0.0.1:8001 -> :8000.
CMD ["nemoguardrails", "server", "--config", "/app/configs", \
     "--default-config-id", "default", "--port", "8000"]
