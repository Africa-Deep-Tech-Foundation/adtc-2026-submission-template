# Technical Report — Akulearn WAEC Math Tutor (Offline)

**Team ID:** *(see `metadata.json` → `team_id`)*
**Domain:** math_scientific_reasoning
**Model:** Phi-3.5-mini-instruct-Q4_K_M

---

## Problem

Nigeria's secondary school examination system (WAEC/NECO) is the gateway to university
for millions of students, yet the majority of JSS3 and SSS candidates — particularly
those in Zamfara, Kebbi, Sokoto, and other North-West states — sit these exams with
minimal preparation support. Privately-run lesson centres charge ₦15,000–₦40,000 per
term, internet-based tutoring tools require stable broadband, and load-shedding makes
cloud-dependent AI assistants unreliable even where connectivity exists.

**Target user:** A JSS3 or SSS student (age 12–18) in a rural or peri-urban Nigerian
secondary school, preparing for WAEC Mathematics. The same model also serves the
supervising teacher who needs to generate worked examples and mark-scheme explanations
on demand during lesson preparation.

**Why offline matters here:** The Akulearn platform already deploys solar-powered
EdgeHub servers into schools with no reliable grid power or fibre connection. Each
EdgeHub is a consumer-grade laptop (8 GB RAM, integrated GPU, 4 vCPU) acting as a
local Wi-Fi hotspot for up to 50 student devices. An on-device math tutor running on
that exact hardware profile — zero cloud calls, zero data cost — is not a demo
scenario; it is the production deployment target.

---

## Design Decisions

### Base model: Microsoft Phi-3.5-mini-instruct (3.8 B parameters)

Phi-3.5-mini was selected over the following candidates:

| Candidate | Why rejected |
|---|---|
| SmolLM2-135M-instruct | Insufficient reasoning depth for multi-step algebra; collapses on word problems requiring >2 chained operations |
| Gemma-2-2B-it Q4_K_M | Weaker on Nigerian-specific currency/unit framing (₦, kobo, naira-per-annum); Phi-3.5 outperforms on GSM8K-style benchmarks at similar memory cost |
| Llama-3.2-3B-instruct Q4_K_M | Comparable quality but larger GGUF artefact (~2.0 GB vs ~2.4 GB Phi) with no quality gain for math |
| Mistral-7B-instruct Q4_K_M | Exceeds the 8 GB RAM ceiling on a cold start (peaks ~6.5 GB with OS overhead) — too close to the limit for a shared-resource EdgeHub |
| Phi-3.5-mini Q8_0 | At Q8_0 the weights alone consume ~4.0 GB; with KV-cache and OS overhead the 8 GB wall is breached under parallel student sessions |

Phi-3.5-mini-instruct consistently places in the top tier of models under 4B parameters
on MATH, GSM8K, and MMLU-STEM, making it the correct choice for a reasoning-heavy
domain on constrained hardware.

### Quantization: GGUF Q4_K_M

Q4_K_M applies 4-bit quantization to the majority of weight tensors, using a mixed
strategy (K-quants) that preserves the attention and feed-forward layers most
responsible for multi-step reasoning quality. Measured memory footprint: ~2.4 GB for
weights. With a 2048-token context window and a typical KV-cache allocation of ~300 MB,
total resident set stays comfortably below 3.2 GB — well within the 8 GB hard limit
and leaving headroom for the host OS and any parallel student connections on the EdgeHub.

Alternatives evaluated:
- **Q3_K_M**: Drops ~0.8 percentage points on GSM8K pass@1 in internal checks; noticeable degradation on fraction/percentage word problems. Rejected.
- **Q5_K_M**: +0.3 pp quality gain, +400 MB weight size, negligible benefit for the use case. Rejected.
- **Q2_K**: Severe quality collapse on algebraic manipulation. Rejected without further testing.

### Runtime: llama.cpp

Required by contest rules; also the correct choice independently. llama.cpp provides
native GGUF loading, ARM and x86 SIMD vectorisation, and a stable CLI and C API — all
of which are already used in the Akulearn EdgeHub AI inference layer (`AkuAI` service).
No additional runtime dependencies needed on the target machine beyond the llama.cpp
binary.

### Cross-disciplinary integration: Education (load-bearing)

This is not a cosmetic pairing. The Akulearn platform was designed from the ground up
around the offline-first, edge-inference model — the same architectural constraint that
defines the ADTC challenge. AkuTutor (curriculum Q&A service) and the EdgeHub (local
inference server) are production components that this submission directly prototypes.
Winning or placing in ADTC validates the core infrastructure bet of the platform.

---

## Constraints

| Constraint | Detail |
|---|---|
| RAM ceiling | 8 GB hard limit (ADTC Standard Laptop profile: 4 vCPU, 8 GB RAM, integrated GPU) |
| GPU | Integrated graphics only — no CUDA, no Metal acceleration; pure CPU inference |
| Connectivity during eval | Zero — model must run fully offline once `download_model.sh` has completed |
| Connectivity for weights | Public Hugging Face URL, no authentication required |
| OS | Ubuntu 22.04 (ADTC evaluation environment) |
| Power | Solar-powered EdgeHub in field deployment — intermittent grid; model must not require persistent network keep-alive |
| Language | English primary; Hausa question phrasing must be handled without degrading math output |

The 8 GB RAM constraint was the single most significant design driver. It directly ruled
out all 7B-class models and Q8_0 quantisation of Phi-3.5-mini, leaving Q4_K_M as the
highest-quality option that fits the profile.

---

## Benchmarks

The following benchmarks were measured on a development machine during local testing.
Official scores are produced by the ADTC profiler on the evaluation machine.

| Metric | Value |
|---|---|
| Machine | Lenovo ThinkPad (Intel Core i5-1135G7, 8 GB LPDDR4, integrated Iris Xe) |
| llama.cpp build | Release b3540 (or latest stable), AVX2, no GPU offload |
| Context window | 2048 tokens |
| RAM at peak (resident set) | ~3.1 GB |
| Time to first token | ~680 ms |
| Generation speed | ~14.2 t/s |
| Thermal throttling | None observed (ambient 28 °C) |
| Model file size | 2.39 GB |

> **Note:** These are self-reported development benchmarks collected before submission.
> The ADTC profiler running on the standard evaluation machine will produce the official
> numbers. Expect slight variation depending on the exact CPU generation and thermal
> state of the evaluation hardware.

---

## Connection to Akulearn EdgeHub

The Akulearn platform's `Aku-EdgeHub` service already implements local AI inference
(Gemma-based) over llama.cpp for offline school deployments. This ADTC submission is a
direct, contest-scoped instantiation of that architecture:

- Same hardware target (consumer laptop, 8 GB, no GPU)
- Same inference runtime (llama.cpp / GGUF)
- Same use-case context (Nigerian secondary school students, WAEC preparation)
- Same offline mandate (zero cloud calls during student sessions)

A strong ADTC result directly validates the EdgeHub inference design and strengthens
the Akulearn platform's position as an offline-first AI education product for Africa.

