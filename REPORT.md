# Technical Report — [Your Submission Title]

**Team ID:** your-team-id  
**Domain:** coding_assistants  
**Model:** YourModel-Q4_K_M

---

## Problem

<!-- What problem are you solving? Who is the target user? Why does this matter in an African context? -->

Describe the problem your model addresses, the target user group, and why running this model locally (offline, on consumer hardware) is important for this use case.

---

## Design Decisions

<!-- What model did you start from? Why that base model and quantization? What alternatives did you consider and reject? -->

- **Base model:** e.g. Llama 3.2 1B, Mistral 7B, Phi-3 mini, etc.
- **Quantization:** e.g. Q4_K_M chosen for balance of quality and memory footprint
- **Alternatives considered:** e.g. Q8_0 exceeded 8 GB limit; Q2_K degraded output quality too aggressively

---

## Constraints

<!-- What hardware, connectivity, power, or data constraints shaped your choices? -->

- Target: 8 GB RAM, integrated GPU, Ubuntu 22.04
- No GPU acceleration — pure CPU inference via llama.cpp
- Any specific connectivity or data availability constraints relevant to your domain

---

## Benchmarks

<!-- What inference speed and memory numbers did you observe on your development machine? -->

| Metric | Value |
|---|---|
| Machine | e.g. MacBook Air M2 / ThinkPad X1 i5 |
| RAM at peak | e.g. 3.8 GB |
| Time to first token | e.g. 420 ms |
| Generation speed | e.g. 18.4 t/s |
| Thermal throttling | e.g. None observed |

These are self-reported development benchmarks. Official scores are measured by the ADTC profiler on the standard evaluation machine.
