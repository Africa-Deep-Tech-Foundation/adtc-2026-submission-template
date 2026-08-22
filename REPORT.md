# Technical Report — Offline Stroke Clinical Decision Support for Low-Resource Primary Health Centers

**Team ID:** 1143733
**Domain:** healthcare_medical
**Model:** Qwen2.5-1.5B-Instruct (GGUF Q4_K_M, 1.8B params)
**Runtime:** llama.cpp (CPU-only, fully offline)
**Cross-disciplinary pairing:** Education / Community Health Worker training

---

## Problem

**Who is the user:** Nurses, community health workers (CHWs), and caregivers at small primary health centers in rural and peri-urban Africa — settings with no CT scanner, no neurologist, unreliable power, and intermittent or absent internet connectivity.

**What problem:** Stroke is a leading cause of adult disability and death in Sub-Saharan Africa. Early recognition and rapid referral are the single biggest levers on outcomes, yet the clinical knowledge needed to apply structured triage (the FAST protocol: Face, Arms, Speech, Time) and to manage hypertension and other risk factors is often concentrated in urban specialists. At the same time, the nurses and CHWs on the front line are responsible for both triage and patient/caregiver education, with little access to continuing training.

**Why local/offline matters:** Cloud-hosted LLMs require API fees, stable fibre, and sustained electricity — blockers for a district health post. A model that runs entirely on the laptop already sitting on the clinic desk (8 GB RAM, integrated graphics, no GPU) gives these facilities a private, zero-connectivity, zero-cost clinical advisor: it supports a triage decision at the point of care, and it trains the health worker at the same time. This directly matches the ADTC 2026 vision: "AI that belongs to you, running on the hardware you already have."

**Target user scenario:** A CHW at a rural health post, faced with a 58-year-old hypertensive patient with sudden facial droop, arm weakness, and slurred speech, uses the tool on a shared clinic laptop to walk through the FAST assessment, receive an urgency classification and prioritized actions, and then teach the patient's family how to recognize and respond to stroke in the future.

---

## Design Decisions

### Base model
We evaluated three candidates on the target hardware class (8th-gen Intel i5, 4C/8T, CPU-only inference):

| Model (GGUF Q4_K_M) | File size | Generation speed | Peak RSS | ARC-Easy acc |
|---|---|---|---|---|
| SmolLM2-135M-Instruct | 105 MB | 48.4 t/s | 201 MB | 0.30 |
| **Qwen2.5-1.5B-Instruct** | **1.1 GB** | **9.84 t/s** | **1.84 GB** | **0.74 (50 smp)** |
| Qwen2.5-3B-Instruct | 2.1 GB | 4.46 t/s | 3.47 GB | 0.80 (50 smp) |

**Why Qwen2.5-1.5B-Instruct:**
- The 3B model's reasoning quality is measurably best (0.80 ARC-Easy) but its generation speed on the target hardware class is only ~4.5 t/s — a live judge or clinician would wait 30–40 s per response (first-token latency for a 512-token prompt was ~38 s). At the fixed 15 t/s speed reference this caps its speed score near 30/100 and makes the in-person demo experience poor.
- The 135M model is extremely fast (48 t/s, 100/100 speed, ~97/100 efficiency) but its answer quality (0.30 ARC-Easy, and qualitatively very weak on open clinical questions) fails the 50%-weighted accuracy axis that dominates the score.
- The 1.5B model is the balance point: responsive enough for an interactive clinical chat (~10 t/s, ~2 s first token on a short prompt), uses only 1.84 GB of the 7 GB budget, and retains usable clinical reasoning for structured triage and plain-language education.

### Quantization
- **Q4_K_M** chosen for quality/size/speed balance — it preserves accuracy well versus Q4_0 and is ~1/2 the size of Q8_0. At ~1.1 GB it leaves >5 GB headroom under the 7 GB evaluation ceiling, removing OOM risk entirely.
- Alternative quantizations rejected: Q8_0 (unnecessary memory cost with no meaningful gain at this size for the use case); Q2_K/Q3_K_M (measurable quality degradation on clinical reasoning tasks, and Q4_K_M already fits comfortably).

### Why llama.cpp / GGUF
Mandated by the challenge and correct for the target: llama.cpp is the only accepted runtime, runs pure CPU inference efficiently on commodity x86 laptops, and the GGUF format is the de facto standard for quantized local deployment.

### Runtime packaging
`binary_bundle` — the model is a single self-contained GGUF file downloaded by `download_model.sh`; llama.cpp (server/CLI) is the runtime.

---

## Constraints

- **Hardware target:** 8 GB RAM (7 GB effective budget), Intel i5 10th–12th gen, integrated graphics only, Ubuntu 22.04 LTS. Evaluated on an equivalent-profile development machine (Intel i5-8365U, 4C/8T, 16 GB RAM, CPU-only).
- **Offline requirement:** zero network dependencies during evaluation; model runs 100% locally. `download_model.sh` fetches weights before profiling begins; no runtime call-outs.
- **Memory ceiling:** 7 GB peak RSS — disqualification if exceeded. This model peaks at 1.84 GB, a large safety margin.
- **Thermal:** no throttling observed; peak core temperature 71 °C on the development machine (below the 85 °C penalty threshold).
- **Data/privacy:** in a clinic context, patient data never leaves the device — a decisive advantage of on-device inference in health settings with weak data-protection enforcement.

---

## Benchmarks

Measured with the official ADTC profiler (`adtc-profiler run --mode participant`, CPU-pinned via llama-bench `-ngl 0`).

| Metric | Value |
|---|---|
| Machine | Dell Latitude 7400 — Intel Core i5-8365U @ 1.60 GHz, 4C/8T, 16 GB RAM, Fedora 43 (CPU-only) |
| Generation speed | 9.84 t/s |
| First-token latency (512-token prompt) | 22.9 s |
| Peak RAM (RSS) | 1.84 GB |
| Steady-state RAM (RSS) | 1.75 GB |
| Peak core temperature | 71.0 °C (no throttling) |
| CPU utilization (p99) | 95.2% during generation |
| Accuracy (ARC-Easy, 50 samples) | 0.74 acc_norm |
| Params check (GGUF header vs claim) | PASS (1.78 B vs "1.8B", within ±15%) |

These are self-reported development benchmarks. Official scores are measured by the ADTC profiler on the standard evaluation machine. Expected deltas on the audit VM (i5 10th–12th gen) are within the competition's ±15% memory / ±25% throughput comparison tolerances.

---

## African Context & Use Case

- Stroke burden in Sub-Saharan Africa is high and rising, driven largely by undiagnosed/untreated hypertension; awareness and structured triage are the most cost-effective interventions available without advanced imaging.
- The system is designed for facilities with no specialists and no connectivity: it works on the clinic's existing laptop, needs no power backup beyond the device, and stores nothing in the cloud.
- The cross-disciplinary pairing with **education** is load-bearing, not cosmetic: the same interaction both supports a triage decision and teaches the CHW/caregiver — the model's second test prompt is a structured CHW training exercise with a comprehension check, making the clinical tool a continuous in-service training device.

---

## Notes on Scope

This submission is a proof-of-concept focused on the model itself (as the challenge requires): the GGUF model, its offline llama.cpp runtime, the prompts that elicit reliable clinical behavior, and measured telemetry. A production deployment would wrap this model in a simple offline web app (llama-server) with a FAST checklist UI and a printable referral summary for the patient file.

**Disclaimer:** This tool is intended to support and train health workers in structured triage and education. It is not a replacement for clinical judgment or formal diagnosis; final decisions remain with qualified health professionals.