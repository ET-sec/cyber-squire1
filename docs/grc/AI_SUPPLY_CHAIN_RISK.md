# AI Supply Chain Risk Assessment

**Organization:** Organization Security Operations Platform
**Assessment Date:** 2026-03-12
**Assessor:** System Owner
**Methodology:** NIST SP 800-161r1 (C-SCRM), NIST AI RMF (MAP/MEASURE), OWASP LLM Top 10 (LLM03), MITRE ATLAS (AML.T0018, AML.T0043)
**NIST 800-53 Controls:** SA-12 (Supply Chain Protection), SR-1 (Supply Chain Risk Management Policy), SR-2 (Supply Chain Risk Management Plan), SR-3 (Supply Chain Controls and Processes), SR-11 (Component Authenticity)
**Classification:** Internal Use Only
**Version:** 1.0

---

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SCRM-AI-001 |
| Version | 1.0 |
| Status | Approved |
| Last Revised | 2026-03-12 |
| Next Review | 2026-09-12 |
| Author | Information Security Officer |
| Approver | System Owner |

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-03-12 | Information Security Officer | Initial AI supply chain risk assessment covering all three AI systems |

---

## 1. Purpose

AI supply chain risk is fundamentally different from traditional software supply chain risk. In traditional software, the supply chain is auditable: source code is inspectable, binaries are reproducible, and dependency trees are enumerable. AI models invert these properties. Model weights are opaque binary blobs that cannot be meaningfully inspected. Training data is unverifiable after the fact. Model behavior can change between versions without any visible change to the artifact. Model registries - the AI equivalent of package repositories - lack the signing infrastructure, provenance attestation, and reproducibility guarantees that the software ecosystem has built over decades.

This assessment evaluates the supply chain risk posture of all three AI systems within the Organization authorization boundary:

1. **AI-001** (svc-ai-gateway) - Claude Opus 4.7 via Anthropic API, a vendor-hosted model accessed over HTTPS where the Organization has zero visibility into model internals
2. **AI-002** (svc-llm) - Qwen 3 4B via Ollama registry, a self-hosted model pulled from a public registry and stored locally in llm-model-volume
3. **AI-003** (svc-transcription) - OpenAI Whisper, an open-weight model with weights baked into or downloaded by the Docker container image

Each system presents a distinct supply chain profile with different trust boundaries, verification capabilities, and failure modes. This document maps those differences, identifies gaps, and provides a prioritized remediation roadmap.

This assessment supports NIST SP 800-161r1 Cyber Supply Chain Risk Management (C-SCRM) practices and directly addresses OWASP LLM Top 10 category LLM03 (Supply Chain Vulnerabilities) and MITRE ATLAS techniques AML.T0018 (Backdoor ML Model) and AML.T0043 (Adversarial Data Injection). It complements the AI Threat Catalog (`AI_THREAT_CATALOG.md`, ATC-04) by providing deep supply chain decomposition that the catalog references but does not expand.

---

## 2. AI System Inventory

### 2.1 Supply Chain Metadata

| ID | System | Container | Model | Provider | Delivery Method | Update Frequency | License |
|----|--------|-----------|-------|----------|----------------|-----------------|---------|
| AI-001 | AI Agent Gateway | svc-ai-gateway (OpenClaw) | Claude Opus 4.7 | Anthropic PBC | REST API (provider-hosted) | Vendor-controlled (no notice) | Proprietary (API ToS) |
| AI-002 | Local LLM Inference | svc-llm (Ollama) | Qwen 3 4B | Alibaba Cloud (via Ollama registry) | Registry pull (self-hosted) | Manual (`ollama pull`) | Apache 2.0 |
| AI-003 | Voice Transcription | svc-transcription (Whisper) | OpenAI Whisper | OpenAI (via Docker image) | Baked into container image | Image rebuild | MIT |

### 2.2 Supply Chain Type Classification

| Type | Description | Applicable System | Verification Capability |
|------|-------------|-------------------|------------------------|
| **API-Hosted** | Model runs on vendor infrastructure; Organization sends data and receives outputs with no access to model internals | AI-001 | None - model is a black box behind an API endpoint |
| **Registry-Pulled** | Model binary pulled from a public registry and executed locally; Organization controls runtime but not the model artifact source | AI-002 | Partial - SHA256 hash at pull time; no cryptographic signature from model creator |
| **Image-Embedded** | Model weights are distributed as part of a Docker container image or downloaded at first startup | AI-003 | Partial - Docker image digest verification; weight file hashes must be manually checked |

---

## 3. Supply Chain Component Analysis

### 3.1 AI-001: Anthropic API (Claude Opus 4.7)

#### Supply Chain Profile

| Attribute | Detail |
|-----------|--------|
| **Vendor** | Anthropic PBC (San Francisco, CA) |
| **Delivery mechanism** | HTTPS REST API (`api.anthropic.com`) |
| **Authentication** | API key stored in secrets manager, injected at runtime via environment variable |
| **Transport security** | TLS 1.3, certificate validated by svc-ai-gateway HTTP client |
| **Model hosting** | Vendor-hosted; Organization has no access to inference infrastructure |
| **Data flow** | Prompts (containing operational context) sent to Anthropic; responses returned |
| **Data retention** | Per Anthropic API ToS - prompts may be retained for abuse monitoring; opt-out available |
| **Update model** | Vendor can update, deprecate, or change model behavior at any time |
| **Fallback** | None deployed; AI-002 is not a drop-in replacement (different capability tier) |

#### Supply Chain Dependencies

```
svc-ai-gateway (OpenClaw container)
├── Docker image: openclaw:v2026.3.8 (custom build, no Docker Hub)
│   ├── Base image: [vendor-provided, not inspected]
│   ├── Runtime: Node.js / Python (per OpenClaw)
│   └── Skills: tavily-search, browser, python-interpreter, notion, gemini, github
├── Network dependency: HTTPS to api.anthropic.com (external)
├── Authentication: API key (ANTHROPIC_API_KEY from secrets manager)
└── Model: Claude Opus 4.7 (hosted by Anthropic - no local artifact)
```

#### Identified Risks

| Risk | Description | MITRE ATLAS |
|------|-------------|-------------|
| **Vendor model change** | Anthropic can update Claude Opus 4.7 behavior, capabilities, or safety filters without notice. A model update could alter response quality, introduce new failure modes, or change the model's handling of edge cases the Organization depends on. | - |
| **API endpoint compromise** | Man-in-the-middle attack on the API endpoint, DNS hijacking of `api.anthropic.com`, or BGP route manipulation could redirect API traffic to an attacker-controlled endpoint. | AML.T0043 |
| **Vendor data breach** | Prompts sent to Anthropic contain operational context. A breach of Anthropic's infrastructure could expose Organization operational data. | - |
| **Vendor business continuity** | Anthropic is a venture-funded company. Service discontinuation, pricing changes, or API deprecation would eliminate the Organization's primary AI capability. | - |
| **API key compromise** | Stolen API key allows unauthorized use of the Organization's Anthropic account, including billing abuse and prompt/response history access (if available via API). | - |

#### Trust Assessment

The Anthropic API supply chain is a **pure trust relationship**. The Organization cannot inspect model weights, verify training data, audit model changes, or confirm that the model served today is the same model served yesterday. TLS protects transport integrity, and the API key authenticates the Organization to Anthropic, but there is no mechanism for the Organization to authenticate the model to itself. Behavioral baseline testing (Section 7.3) is the only available integrity verification method.

**Risk Rating: Medium** - High vendor dependency offset by Anthropic's market position, SOC 2 compliance, and the Organization's air-gapped AI-002 as a degraded fallback.

---

### 3.2 AI-002: Ollama Registry (Qwen 3 4B)

#### Supply Chain Profile

| Attribute | Detail |
|-----------|--------|
| **Model creator** | Alibaba Cloud (Qwen team) |
| **Registry** | registry.ollama.ai (operated by Ollama Inc.) |
| **Delivery mechanism** | `ollama pull qwen3:4b` - downloads GGUF model binary to llm-model-volume |
| **Container image** | `ollama/ollama` from Docker Hub |
| **Model format** | GGUF (GPT-Generated Unified Format) - single binary file containing weights and metadata |
| **Runtime network** | net-ai (`internal: true`) - no internet access at inference time |
| **Model signing** | None - Ollama registry does not support cryptographic model signatures |
| **Hash verification** | SHA256 hash computed at pull time and stored in Ollama manifest |
| **Update model** | Manual only - requires explicit `ollama pull` with internet access |
| **License** | Apache 2.0 (Qwen 3) |

#### Supply Chain Dependencies

```
svc-llm (Ollama container)
├── Docker image: ollama/ollama (Docker Hub)
│   ├── Base image: Ubuntu/Alpine (vendor-specified)
│   ├── Runtime: Go binary (Ollama server)
│   └── Inference engine: llama.cpp (compiled into Ollama)
├── Model artifact: qwen3:4b
│   ├── Source: registry.ollama.ai
│   ├── Format: GGUF binary
│   ├── Creator: Alibaba Cloud / Qwen team
│   ├── Intermediate: Ollama registry (repackages HuggingFace upload)
│   └── Storage: llm-model-volume (persistent Docker volume)
├── Network (runtime): net-ai (internal: true - no egress)
└── Network (pull-time): requires internet access to registry.ollama.ai
```

#### Identified Risks

| Risk | Description | MITRE ATLAS |
|------|-------------|-------------|
| **Registry compromise (model swap)** | An attacker who compromises registry.ollama.ai could replace the `qwen3:4b` manifest with a backdoored model. The next `ollama pull` would download the malicious artifact. | AML.T0018 |
| **Model poisoning at source** | The Qwen model is created by Alibaba Cloud. A state-level adversary or insider could introduce backdoors or biased behavior during training that persists through quantization and distribution. | AML.T0018, AML.T0043 |
| **GGUF format manipulation** | GGUF files contain both weights and metadata. A crafted GGUF file could exploit parsing vulnerabilities in llama.cpp (the inference engine compiled into Ollama) to achieve code execution. | AML.T0018 |
| **Ollama container image compromise** | The `ollama/ollama` Docker image is pulled from Docker Hub. A compromised Docker Hub account or build pipeline could inject malicious code into the Ollama runtime itself. | - |
| **No model signing** | Ollama's registry has no model signature verification. Unlike Docker Content Trust or Sigstore for container images, there is no cryptographic chain from the model creator (Alibaba Cloud) through the registry to the local artifact. | AML.T0018 |
| **Stale model with known vulnerabilities** | Manual update process means the Organization may run a model version with known jailbreak bypasses or safety issues that have been patched in newer releases. | - |

#### Trust Assessment

The Ollama supply chain has a **two-hop trust problem**: the Organization trusts Ollama's registry, which in turn trusts the model uploaded by Alibaba Cloud's Qwen team. Neither hop has cryptographic provenance verification. The strongest control is the air-gapped runtime on net-ai - even if the model were compromised, it cannot exfiltrate data or receive command-and-control instructions at inference time. SHA256 hashes provide tamper detection after initial pull but not provenance attestation.

**Risk Rating: Medium** - Registry trust gap offset by air-gapped runtime (no internet at inference), manual update cadence (no auto-pull), and SHA256 hash verification at pull time.

---

### 3.3 AI-003: Whisper (Open-Weight)

#### Supply Chain Profile

| Attribute | Detail |
|-----------|--------|
| **Model creator** | OpenAI |
| **Delivery mechanism** | Model weights embedded in or downloaded by the Docker container image at first startup |
| **Container image** | Whisper container (specific image tag maintained by container packager) |
| **Model format** | PyTorch (.pt / .bin) checkpoint files |
| **Runtime framework** | Python, PyTorch, potentially CUDA/CPU-specific libraries |
| **Runtime network** | net-ai (`internal: true`) - no internet access at inference time |
| **Model signing** | None - OpenAI does not sign Whisper model weight files |
| **Hash verification** | Manual - compare weight file SHA256 against OpenAI's published hashes (if available) |
| **Update model** | Container image rebuild/repull |
| **License** | MIT |

#### Supply Chain Dependencies

```
svc-transcription (Whisper container)
├── Docker image: [whisper image] (Docker Hub or custom build)
│   ├── Base image: python:3.x or nvidia/cuda
│   ├── Framework: PyTorch (pip install)
│   │   ├── numpy, scipy, tokenizers, transformers
│   │   └── ~150+ transitive Python dependencies
│   ├── Whisper library: openai-whisper (pip package)
│   └── Model weights: downloaded at build/first-run
│       ├── Source: OpenAI GitHub releases or HuggingFace
│       ├── Format: PyTorch checkpoint (.pt)
│       └── Storage: transcription-model-volume or baked into image layer
├── Network (runtime): net-ai (internal: true - no egress)
└── Network (build-time): requires internet for pip install + model download
```

#### Identified Risks

| Risk | Description | MITRE ATLAS |
|------|-------------|-------------|
| **Docker image compromise** | The container image includes the full Python + PyTorch stack. A compromised base image, malicious PyPI package, or dependency confusion attack could inject code that runs alongside or instead of the Whisper model. | - |
| **PyTorch dependency chain** | Whisper depends on PyTorch, which depends on ~150+ transitive Python packages. Any of these packages could be compromised via supply chain attack (typosquatting, maintainer account takeover, malicious release). This is the deepest dependency tree of all three AI systems. | - |
| **Weight file tampering** | PyTorch checkpoint files (.pt) use Python's `pickle` for serialization. Pickle deserialization is inherently unsafe - a crafted .pt file can execute arbitrary Python code when loaded. This is the most critical supply chain vector for Whisper. | AML.T0018 |
| **Model source ambiguity** | Whisper weights may be sourced from OpenAI's GitHub, HuggingFace, or a third-party mirror depending on the container image's Dockerfile. The actual provenance depends on which image was used and when it was built. | AML.T0018 |
| **Stale dependencies** | The Python dependency tree is frozen at image build time. Known CVEs in PyTorch, numpy, or other dependencies will persist until the image is rebuilt. | - |

#### Trust Assessment

Whisper has the **deepest and most fragile supply chain** of the three AI systems. The PyTorch pickle deserialization vector means that a compromised weight file is equivalent to arbitrary code execution - not just model behavior manipulation. The ~150+ transitive Python dependencies create a broad attack surface that no amount of model-level verification can address. However, the air-gapped runtime on net-ai prevents exploitation from reaching external infrastructure, and the limited capability of the Whisper model (audio-to-text only) constrains the impact of a behavior-only compromise.

**Risk Rating: Medium-High** - Pickle deserialization risk and deep dependency tree offset by air-gapped runtime and limited model capability scope (transcription only, no autonomous actions).

---

## 4. Dependency Tree Analysis

### 4.1 Integrity Verification Coverage

The following table maps where integrity verification exists in each AI system's supply chain and where gaps remain.

| Layer | AI-001 (Anthropic API) | AI-002 (Ollama/Qwen) | AI-003 (Whisper) |
|-------|----------------------|---------------------|-----------------|
| **Transport** | TLS 1.3 (verified) | TLS to registry (verified) | TLS to Docker Hub/PyPI (verified) |
| **Container image** | N/A (standalone) | Docker image digest (available, not pinned) | Docker image digest (available, not pinned) |
| **Container signing** | N/A | Cosign signature (not verified at pull) | Cosign signature (not verified at pull) |
| **Model binary** | N/A (vendor-hosted) | SHA256 hash at pull (Ollama built-in) | No automated verification |
| **Model signing** | N/A | Not available (Ollama has no signing) | Not available (OpenAI does not sign weights) |
| **Training data provenance** | Unverifiable | Unverifiable | Partially documented (Whisper paper) |
| **Runtime dependencies** | N/A | Compiled into Go binary (minimal) | ~150+ Python packages (no lock file audit) |
| **SBOM** | N/A | Container SBOM via CI/CD (Implemented) | Container SBOM via CI/CD (Implemented) |
| **Model BOM** | Not applicable | Not generated | Not generated |

### 4.2 Gap Summary

| Gap ID | Description | Affected Systems | Severity |
|--------|-------------|-----------------|----------|
| SCG-01 | No Docker Content Trust verification at pull time | AI-002, AI-003 | Medium |
| SCG-02 | No cryptographic model signing from model creator to local artifact | AI-002, AI-003 | High |
| SCG-03 | No ML Bill of Materials (ML-BOM) generated or maintained | AI-002, AI-003 | Medium |
| SCG-04 | No automated model hash verification on cron | AI-002, AI-003 | Medium |
| SCG-05 | No behavioral baseline testing for API-hosted model | AI-001 | Medium |
| SCG-06 | Container images not pinned to digest (use mutable tags) | AI-002, AI-003 | Medium |
| SCG-07 | PyTorch pickle deserialization not mitigated | AI-003 | High |
| SCG-08 | No Python dependency audit or lock file verification | AI-003 | Medium |
| SCG-09 | No vendor incident notification SLA documented | AI-001 | Low |
| SCG-10 | No model update approval workflow | AI-002, AI-003 | Medium |

---

## 5. Risk Matrix

### 5.1 Scoring Methodology

Risk scores use the same 5x5 matrix defined in the Risk Assessment (`RISK_ASSESSMENT.md`, Section 2):

- **Likelihood:** 1 (Very Low) through 5 (Very High)
- **Impact:** 1 (Very Low) through 5 (Very High)
- **Risk Score:** Likelihood x Impact
- **Thresholds:** Low (1-6), Moderate (7-14), High (15-19), Critical (20-25)

### 5.2 Supply Chain Risk Register

| Risk ID | Description | System | Likelihood | Impact | Score | Rating | Existing Controls | Residual Risk |
|---------|-------------|--------|-----------|--------|-------|--------|-------------------|---------------|
| SCR-01 | Ollama registry compromise - malicious model served on next pull | AI-002 | 2 (Low) | 4 (High) | 8 | Moderate | SHA256 hash at pull; manual update cadence; air-gapped runtime | Medium |
| SCR-02 | Anthropic model behavior change without notice - degraded or altered output quality | AI-001 | 4 (High) | 3 (Moderate) | 12 | Moderate | None - no behavioral baseline testing | High |
| SCR-03 | PyTorch pickle deserialization exploit in Whisper weight file | AI-003 | 2 (Low) | 5 (Very High) | 10 | Moderate | Air-gapped runtime; container resource limits; Falco monitoring | Medium |
| SCR-04 | Docker Hub image compromise - malicious code in ollama/ollama or whisper base image | AI-002, AI-003 | 2 (Low) | 4 (High) | 8 | Moderate | Trivy CVE scanning in CI/CD; SBOM generation; Cosign (not enforced) | Medium |
| SCR-05 | Qwen model poisoning at source (Alibaba Cloud insider or state-level threat) | AI-002 | 1 (Very Low) | 4 (High) | 4 | Low | Air-gapped runtime; limited use scope (internal workflows only) | Low |
| SCR-06 | Anthropic API key compromise - unauthorized billing and data access | AI-001 | 2 (Low) | 4 (High) | 8 | Moderate | Key stored in secrets manager; key rotation policy; API spend alerts | Low |
| SCR-07 | Python dependency chain compromise (typosquatting, maintainer takeover) in Whisper stack | AI-003 | 3 (Moderate) | 3 (Moderate) | 9 | Moderate | Trivy scanning; air-gapped runtime | Medium |
| SCR-08 | GGUF parsing vulnerability in llama.cpp leads to code execution on svc-llm | AI-002 | 2 (Low) | 4 (High) | 8 | Moderate | Air-gapped on net-ai; no internet egress; Falco shell spawn detection | Medium |
| SCR-09 | Anthropic vendor discontinuation - service termination or prohibitive pricing change | AI-001 | 2 (Low) | 4 (High) | 8 | Moderate | AI-002 as degraded fallback; no auto-migration capability | Medium |
| SCR-10 | Stale model running with known jailbreak or safety bypass | AI-002 | 3 (Moderate) | 2 (Low) | 6 | Low | Manual update review; svc-llm restricted to internal use | Low |
| SCR-11 | Man-in-the-middle on Anthropic API endpoint (DNS hijack, BGP manipulation) | AI-001 | 1 (Very Low) | 5 (Very High) | 5 | Low | TLS certificate validation; edge security provider DNS protection | Low |
| SCR-12 | Model weight file replaced on disk (post-pull local tampering) | AI-002, AI-003 | 1 (Very Low) | 4 (High) | 4 | Low | Volume permissions; host access restricted; no model hash re-verification on startup | Low |
| SCR-13 | Whisper model sourced from unofficial mirror (provenance ambiguity) | AI-003 | 2 (Low) | 3 (Moderate) | 6 | Low | Dockerfile inspection; image rebuild from known source | Low |
| SCR-14 | OpenClaw gateway container includes undisclosed dependencies or capabilities | AI-001 | 2 (Low) | 3 (Moderate) | 6 | Low | SBOM generation; Trivy scanning; container resource monitoring | Low |
| SCR-15 | Coordinated supply chain attack targeting multiple AI providers simultaneously | All | 1 (Very Low) | 5 (Very High) | 5 | Low | System diversity (3 different providers/sources); no single-source dependency for all AI | Low |

### 5.3 Risk Distribution

| Rating | Count | Risk IDs |
|--------|-------|----------|
| **Critical** | 0 | - |
| **High** | 0 | - |
| **Moderate** | 8 | SCR-01, SCR-02, SCR-03, SCR-04, SCR-06, SCR-07, SCR-08, SCR-09 |
| **Low** | 7 | SCR-05, SCR-10, SCR-11, SCR-12, SCR-13, SCR-14, SCR-15 |

---

## 6. ML Bill of Materials (ML-BOM)

An ML Bill of Materials extends the concept of a Software Bill of Materials (SBOM) to cover model-specific artifacts that traditional SBOMs cannot enumerate. While the CI/CD pipeline generates container SBOMs (via Trivy and SBOM workflows), model weights, training data provenance, and model-specific metadata are not captured. This section defines the ML-BOM for each AI system.

### 6.1 AI-001: Claude Opus 4.7 (Anthropic API)

| Field | Value |
|-------|-------|
| **Model name** | Claude Opus 4.7 |
| **Model version** | Vendor-managed (no version pinning available to consumer) |
| **Model format** | API-hosted (no local artifact) |
| **Model creator** | Anthropic PBC |
| **Model license** | Proprietary (Anthropic API Terms of Service) |
| **Training data** | Undisclosed; Anthropic publishes high-level descriptions but not datasets |
| **Training data provenance** | **Unknown** - not verifiable by consumer |
| **Container image** | openclaw:v2026.3.8 (custom) |
| **Container digest** | Not pinned (standalone container, not Compose-managed) |
| **Runtime dependencies** | OpenClaw runtime (Node.js / Python) |
| **API endpoint** | api.anthropic.com |
| **Authentication** | ANTHROPIC_API_KEY (secrets manager) |
| **Last verified** | 2026-03-11 (API connectivity and response test) |
| **Model hash** | N/A - vendor-hosted, no local artifact to hash |
| **SBOM coverage** | Container SBOM only; model internals not enumerable |

### 6.2 AI-002: Qwen 3 4B (Ollama)

| Field | Value |
|-------|-------|
| **Model name** | Qwen 3 4B |
| **Model version** | qwen3:4b (Ollama tag) |
| **Model format** | GGUF (GPT-Generated Unified Format) |
| **Model creator** | Alibaba Cloud (Qwen team) |
| **Model license** | Apache 2.0 |
| **Training data** | Undisclosed; Qwen technical report describes data categories but not specific datasets |
| **Training data provenance** | **Partially documented** - training methodology published; specific data sources not disclosed |
| **Container image** | ollama/ollama |
| **Container tag** | latest (mutable - should pin to digest) |
| **Runtime dependencies** | Go binary, llama.cpp (compiled into Ollama) |
| **Model storage** | llm-model-volume (persistent Docker volume on alpha-node) |
| **Model hash (SHA256)** | Stored in Ollama manifest (`ollama show qwen3:4b --modelfile`) |
| **Last verified** | 2026-03-11 (pull and hash recorded) |
| **SBOM coverage** | Container SBOM generated; model weights not in SBOM |

### 6.3 AI-003: OpenAI Whisper

| Field | Value |
|-------|-------|
| **Model name** | OpenAI Whisper |
| **Model version** | Determined by container image tag |
| **Model format** | PyTorch checkpoint (.pt / .bin) |
| **Model creator** | OpenAI |
| **Model license** | MIT |
| **Training data** | 680,000 hours of web audio (documented in Whisper paper, arXiv:2212.04356) |
| **Training data provenance** | **Partially documented** - aggregate statistics published; specific audio sources not itemized |
| **Container image** | Whisper container image (Docker Hub) |
| **Container tag** | Mutable tag (should pin to digest) |
| **Runtime dependencies** | Python 3.x, PyTorch, numpy, scipy, tokenizers, transformers, ffmpeg |
| **Model storage** | transcription-model-volume or baked into image layer |
| **Model hash (SHA256)** | Not currently recorded |
| **Last verified** | 2026-03-11 (container health check) |
| **SBOM coverage** | Container SBOM generated; Python dependency tree partially covered; model weights not in SBOM |

### 6.4 ML-BOM Gap Analysis

| Gap | Description | Remediation |
|-----|-------------|-------------|
| No model weights in SBOM | Current SBOM tools (Trivy, Syft) enumerate OS packages and language dependencies but do not index model weight files as components | Extend SBOM generation to include model file paths, hashes, and metadata |
| No training data attestation | None of the three model providers offer machine-readable training data provenance attestations | Monitor industry adoption of NIST AI RMF MAP 1.1 attestation formats |
| No model version pinning (AI-001) | Anthropic API does not expose a model version identifier that consumers can pin to | Implement behavioral baseline testing to detect version changes |
| Mutable container tags (AI-002, AI-003) | Container images referenced by mutable tag rather than immutable digest | Pin images to SHA256 digest in Docker Compose / run commands |

---

## 7. Integrity Verification Procedures

### 7.1 AI-002: Ollama Model Verification

**Current state:** SHA256 hash computed at pull time and stored in Ollama's local manifest.

**Verification command:**
```bash
# Show model manifest including layer hashes
ollama show qwen3:4b --modelfile

# List all model layers with SHA256 digests
ollama show qwen3:4b --format json | jq '.layers[].digest'

# Compare against previously recorded baseline hash
BASELINE_HASH="<recorded_sha256>"
CURRENT_HASH=$(ollama show qwen3:4b --format json | jq -r '.layers[] | select(.mediaType == "application/vnd.ollama.image.model") | .digest')
if [ "$BASELINE_HASH" != "$CURRENT_HASH" ]; then
    echo "ALERT: Model hash mismatch - potential supply chain compromise"
fi
```

**Recommended cron verification (not yet implemented):**
```bash
# /etc/cron.d/model-integrity-check (daily at 03:00 UTC)
0 3 * * * root docker exec svc-llm ollama show qwen3:4b --format json \
  | jq -r '.layers[] | select(.mediaType == "application/vnd.ollama.image.model") | .digest' \
  | diff - /opt/platform/model-baselines/qwen3-8b.sha256 \
  || curl -X POST https://example-ops.com/webhook/master-cmd \
     -H "Content-Type: application/json" \
     -d '{"action":"telegram","chat_id":"OPERATOR","text":"ALERT: Ollama model hash mismatch detected"}'
```

### 7.2 AI-003: Whisper Model Verification

**Current state:** No automated weight file verification.

**Verification procedure:**
```bash
# Identify weight file location inside container
docker exec svc-transcription find / -name "*.pt" -o -name "*.bin" 2>/dev/null

# Compute SHA256 of weight files
docker exec svc-transcription sha256sum /path/to/model/weights.pt

# Compare against OpenAI published hashes (from GitHub release or model card)
# Note: OpenAI publishes expected hashes for each Whisper model size

# Verify container image digest
docker inspect svc-transcription --format '{{.Image}}'
```

**Docker image pinning (recommended):**
```yaml
# docker-compose.yaml - pin to digest instead of mutable tag
services:
  svc-transcription:
    image: whisper-image@sha256:<immutable_digest>
```

### 7.3 AI-001: Anthropic API Behavioral Baseline

Since the Organization cannot inspect the Anthropic model, behavioral baseline testing is the only verification method. This detects model changes that alter outputs for known test inputs.

**Baseline test suite (recommended implementation):**
```python
# behavioral_baseline.py - run weekly or after suspected model changes
BASELINE_PROMPTS = [
    {
        "prompt": "Classify the following log entry as BENIGN or SUSPICIOUS: "
                  "Failed password for root from 10.0.0.1 port 22 ssh2",
        "expected_classification": "SUSPICIOUS",
        "tolerance": "exact_match"
    },
    {
        "prompt": "Summarize in one sentence: The firewall blocked 3,421 "
                  "connection attempts from 192.168.1.0/24 to port 443.",
        "expected_keywords": ["blocked", "firewall", "connection", "443"],
        "tolerance": "keyword_presence"
    },
    {
        "prompt": "What is 2 + 2?",
        "expected_answer": "4",
        "tolerance": "contains"
    }
]

# Compare responses against baseline
# Alert if > 20% of prompts fail their tolerance check
# Log all results to monitoring platform for trend analysis
```

**What to monitor:**
- Response latency changes (>50% deviation from baseline)
- Response format changes (structured output suddenly unstructured)
- Safety filter behavior changes (previously allowed prompts now refused, or vice versa)
- API version headers in HTTP responses (if Anthropic adds versioning)

### 7.4 Monitoring and Alerting

| Signal | Source | Alert Condition | Severity |
|--------|--------|----------------|----------|
| Model hash change (AI-002) | Cron job | Hash differs from baseline file | Critical |
| Weight file hash change (AI-003) | Cron job | Hash differs from recorded value | Critical |
| Anthropic API behavioral deviation | Weekly test | >20% baseline prompt failures | High |
| Container image digest change | Docker inspect | Digest differs after restart without planned update | High |
| Ollama auto-update detected | Process monitoring | `ollama pull` executed outside maintenance window | Medium |
| API endpoint certificate change | TLS monitoring | Certificate fingerprint changed | Medium |
| Unexpected network egress from net-ai | Falco | Any outbound connection from svc-llm or svc-transcription | Critical |

---

## 8. Vendor Risk Assessment

### 8.1 Anthropic PBC

| Category | Assessment |
|----------|-----------|
| **Company type** | Private (venture-funded); Series D ($4B+ raised) |
| **Business continuity risk** | **Low-Medium** - well-funded with strong market position, but not yet profitable; dependent on continued funding and market demand |
| **Data handling** | SOC 2 Type II certified; data processing agreement available; opt-out for training on API inputs |
| **Incident notification** | Per ToS - no specific SLA for security incident notification to API consumers |
| **Model change notification** | **None** - model updates can occur without consumer notification; no changelog or versioning exposed to API consumers |
| **Geographic risk** | US-based; data processed in US data centers (per current infrastructure) |
| **Regulatory compliance** | SOC 2, voluntary AI safety commitments; not FedRAMP authorized |
| **Lock-in risk** | **Medium** - Claude-specific prompt engineering and behavioral patterns not portable to other providers |
| **Alternative providers** | OpenAI (GPT-4), Google (Gemini), Mistral, open-weight models (AI-002 as degraded fallback) |
| **Contract/ToS review** | Annual review of API Terms of Service and Acceptable Use Policy |

### 8.2 Ollama Inc. / Alibaba Cloud (Qwen)

| Category | Assessment |
|----------|-----------|
| **Ollama - Company type** | Open-source project with venture funding |
| **Ollama - Business continuity** | **Medium** - registry could go offline; model files are self-hosted after pull (reduces dependency) |
| **Ollama - Data handling** | Registry metadata only; model served locally; no inference data sent to Ollama |
| **Alibaba Cloud - Company type** | Public company (NYSE: BABA); large enterprise with AI research division |
| **Alibaba Cloud - Model provenance** | Model weights published to HuggingFace and Ollama registry; training methodology documented in technical report |
| **Alibaba Cloud - Geographic risk** | **Medium-High** - Chinese company; potential regulatory pressure or export control impacts on model availability |
| **Incident notification** | None - open-source distribution model; no SLA for vulnerability or compromise notification |
| **Model integrity** | No cryptographic signing; relies on registry trust and SHA256 hash at pull |
| **Alternative providers** | Mistral, Llama (Meta), Phi (Microsoft) - all available via Ollama registry in GGUF format |
| **Lock-in risk** | **Very Low** - GGUF is a standard format; Ollama supports dozens of models; switching is trivial |

### 8.3 OpenAI (Whisper)

| Category | Assessment |
|----------|-----------|
| **Company type** | Private (venture-funded); capped-profit structure |
| **Business continuity risk** | **Very Low for Whisper** - model weights are MIT-licensed and self-hosted; OpenAI's business continuity does not affect locally deployed Whisper |
| **Data handling** | No data sent to OpenAI (local inference only) |
| **Model updates** | Whisper is a released artifact; OpenAI is unlikely to update the existing Whisper model (superseded by newer products) |
| **Incident notification** | N/A - open-source release; security issues tracked via GitHub |
| **Model integrity** | Weights published on GitHub with hashes; no cryptographic signing |
| **Alternative providers** | faster-whisper, whisper.cpp, Distil-Whisper - drop-in alternatives with the same model architecture |
| **Lock-in risk** | **Very Low** - MIT license, standard model format, multiple re-implementations available |

---

## 9. Remediation Roadmap

### 9.1 Prioritized Actions

| Priority | Action | Risk(s) Addressed | Gap(s) | Effort | Target Date | Owner |
|----------|--------|-------------------|--------|--------|-------------|-------|
| **P1** | Implement model hash verification cron job for AI-002 and AI-003 | SCR-01, SCR-12 | SCG-04 | Low | 2026-04-15 | Information Security Officer |
| **P2** | Pin container images to SHA256 digest in Compose and run commands | SCR-04, SCR-08 | SCG-06 | Low | 2026-04-15 | Platform Administrator |
| **P3** | Create ML-BOM baseline document with all model hashes, versions, and sources | SCR-01, SCR-03, SCR-13 | SCG-03 | Medium | 2026-05-01 | Information Security Officer |
| **P4** | Deploy Anthropic API behavioral baseline test suite (weekly cron) | SCR-02 | SCG-05 | Medium | 2026-05-15 | Information Security Officer |
| **P5** | Audit Whisper container Dockerfile for weight source and dependency pinning | SCR-03, SCR-07 | SCG-07, SCG-08 | Medium | 2026-05-15 | Platform Administrator |
| **P6** | Enable Docker Content Trust in CI/CD (aligns with POAM-003) | SCR-04 | SCG-01 | Medium | 2026-06-09 | Platform Administrator |
| **P7** | Implement model update approval workflow (manual pull + review + hash record) | SCR-01, SCR-10 | SCG-10 | Low | 2026-06-15 | Information Security Officer |
| **P8** | Evaluate Sigstore/Cosign for model signing (monitor ecosystem adoption) | SCR-01, SCR-03 | SCG-02 | Low (monitoring) | 2026-09-12 | Information Security Officer |
| **P9** | Document Anthropic vendor incident notification expectations in contract review | SCR-06, SCR-09 | SCG-09 | Low | 2026-06-15 | System Owner |
| **P10** | Investigate PyTorch SafeTensors migration for Whisper (eliminates pickle risk) | SCR-03 | SCG-07 | High | 2026-09-12 | Information Security Officer |

### 9.2 Quick Wins (Achievable Within 30 Days)

1. **Record current model hashes** - Run `ollama show qwen3:4b --format json` and `sha256sum` on Whisper weight files. Store in `/opt/platform/model-baselines/` on alpha-node.
2. **Pin Ollama image** - Change `ollama/ollama` to `ollama/ollama@sha256:<current_digest>` in docker-compose.yaml.
3. **Document model update procedure** - Add a section to the Change Management Policy requiring hash verification before and after any `ollama pull` or image rebuild.

### 9.3 Long-Term Initiatives

1. **Sigstore for ML** - The Sigstore project (sigstore.dev) is extending its signing framework to cover ML model artifacts. When model registries (Ollama, HuggingFace) support Sigstore attestations, adopt verification as a mandatory step in the model update workflow.
2. **SafeTensors adoption** - HuggingFace's SafeTensors format eliminates the pickle deserialization risk inherent in PyTorch checkpoint files. Monitor Whisper ecosystem for SafeTensors support.
3. **ML-BOM automation** - As tools like CycloneDX ML-BOM and SPDX AI Profile mature, integrate automated ML-BOM generation into the CI/CD pipeline alongside existing SBOM generation.
4. **Model behavioral regression CI** - Integrate behavioral baseline tests into the CI/CD pipeline so that any model-related change (container rebuild, explicit pull) triggers automated behavioral validation before deployment.

---

## 10. Cross-References

### 10.1 GRC Document Mapping

| Document | Relationship to This Assessment |
|----------|--------------------------------|
| [AI_THREAT_CATALOG.md](AI_THREAT_CATALOG.md) | ATC-04 (Model Supply Chain Compromise) - this assessment expands the supply chain analysis referenced in ATC-04 |
| [THREAT_MODEL_STRIDE.md](THREAT_MODEL_STRIDE.md) | T-02 (Tampering - container/model integrity), T-05 (Tampering - supply chain) |
| [ATTACK_TREE_AI_PIPELINE.md](ATTACK_TREE_AI_PIPELINE.md) | Path 2 (Supply Chain Compromise) - all nodes |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | AI-R03 (Model Integrity), AI-R08 (Supply Chain) |
| [SSP_SYSTEM_SECURITY_PLAN.md](SSP_SYSTEM_SECURITY_PLAN.md) | SA-12, SI-7, SA-22 control implementations |
| [POAM_PLAN_OF_ACTION.md](POAM_PLAN_OF_ACTION.md) | POAM-003 (Docker Content Trust), POAM-005 (svc-ai-gateway hardening) |
| [POLICY_AI_GOVERNANCE.md](POLICY_AI_GOVERNANCE.md) | Section 11 (Third-Party AI Risk), AI-T06 (Supply Chain Threat) |
| [POLICY_CHANGE_MANAGEMENT.md](POLICY_CHANGE_MANAGEMENT.md) | Model update approval process alignment |
| [CIS_RISK_REGISTER.md](CIS_RISK_REGISTER.md) | CIS 4.5 (Docker Content Trust finding) |

### 10.2 Framework Mapping

| Framework | Reference | Coverage in This Assessment |
|-----------|-----------|----------------------------|
| NIST SP 800-161r1 | C-SCRM Level 3 (Operational) | Sections 3, 4, 5, 7, 8 |
| NIST AI RMF | MAP 1.1, MAP 2.3, MEASURE 2.1, MANAGE 1.1 | Sections 2, 3, 6, 7 |
| NIST 800-53 Rev. 5 | SA-12, SR-1, SR-2, SR-3, SR-11, SI-7, CM-14 | Sections 3, 4, 7, 9 |
| OWASP LLM Top 10 | LLM03 (Supply Chain Vulnerabilities) | Entire document |
| MITRE ATLAS | AML.T0018 (Backdoor ML Model), AML.T0043 (Adversarial Data Injection) | Sections 3, 5 |
| ISO/IEC 42001:2023 | A.6 (AI System Lifecycle), A.10 (Third-Party Relationships) | Sections 3, 8 |

### 10.3 POAM Entries Generated by This Assessment

The following new POA&M entries are recommended based on findings in this assessment:

| Proposed POA&M ID | Finding | Risk Level | Source | Target Date |
|-------------------|---------|------------|--------|-------------|
| POAM-NEW-01 | No automated model hash verification for AI-002 and AI-003 | Medium | SCRM-AI-001, SCG-04 | 2026-04-15 |
| POAM-NEW-02 | No behavioral baseline testing for AI-001 API-hosted model | Medium | SCRM-AI-001, SCG-05 | 2026-05-15 |
| POAM-NEW-03 | ML-BOM not generated for any AI system | Medium | SCRM-AI-001, SCG-03 | 2026-05-01 |
| POAM-NEW-04 | PyTorch pickle deserialization risk in AI-003 weight files | Medium | SCRM-AI-001, SCG-07 | 2026-09-12 |

---

## 11. Review Schedule and Ownership

| Activity | Frequency | Next Date | Owner |
|----------|-----------|-----------|-------|
| Full supply chain risk reassessment | Semi-annual | 2026-09-12 | Information Security Officer |
| Model hash verification audit | Monthly | 2026-04-12 | Platform Administrator |
| Vendor risk profile update | Annual (or upon material vendor change) | 2027-03-12 | Information Security Officer |
| ML-BOM refresh | Quarterly (or upon model update) | 2026-06-12 | Information Security Officer |
| Container image digest audit | Monthly | 2026-04-12 | Platform Administrator |
| Behavioral baseline test review | Monthly | 2026-04-12 | Information Security Officer |
| Remediation roadmap progress check | Quarterly | 2026-06-12 | System Owner |

---

*This AI supply chain risk assessment is a living document. It SHALL be updated when new AI models are deployed, existing models are updated or replaced, new supply chain vulnerabilities are disclosed affecting any AI dependency, or after any security incident involving AI model integrity. The next scheduled review is 2026-09-12.*
