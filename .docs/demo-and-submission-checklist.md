# Demo Video Script — 2 minutes max

Gate 1 requires a 2-minute video explaining the solution and development journey.
Screenshots/video clips of the model running are also required in the repo/REPORT.

## Structure (120s budget)

### 1. Hook + problem (0:00–0:20)
- "Stroke kills and disables more people in sub-Saharan Africa than anywhere else, and
  the first hour decides the outcome."
- "In a rural health post there's no CT scanner, no neurologist, no internet — but there
  IS a laptop."
- "This is an offline AI clinical decision-support tool that runs entirely on that
  laptop, no cloud, no fees."

### 2. The demo — FAST triage (0:20–0:50)
- Show the model answering the FAST scenario prompt (record screen of a chat with the
  model via llama.cpp / llama-server web UI, or the llama-cli terminal).
- Highlight: step-by-step FAST assessment, urgency classification, prioritized actions
  (positioning, BP, urgent referral).
- Overlay caption: "Qwen2.5-1.5B GGUF — running locally on CPU, 8GB laptop profile."

### 3. The demo — CHW training (0:50–1:20)
- Show the second prompt: teaching a community health worker to train families.
- Highlight: plain-language explanation, FAST acronym, comprehension-check questions.
- Overlay caption: "Same model, second job: in-service training for health workers."

### 4. The engineering (1:20–1:45)
- "Why it works: a quantized Qwen2.5-1.5B (GGUF Q4_K_M) running through llama.cpp —
  CPU-only, 100% offline, peaks at 1.8 GB RAM of the 7 GB budget."
- Show the profiler output: speed ~10 tokens/s, peak RSS 1.8 GB, ARC-Easy 0.74.
- Show the bake-off table (3B vs 1.5B vs 135M) and why 1.5B was chosen.

### 5. Close (1:45–2:00)
- "A clinic's laptop becomes a 24/7 stroke advisor and trainer — private, free,
  always available."
- Name, team ID, repo URL (Laplace0xx/adtc-2026-hackathon).

## Recording checklist
- [ ] Record screen at 1080p, landscape; keep it under 2:00.
- [ ] Captions/overlays for all numbers (voice clarity in noisy settings).
- [ ] Filename: e.g. `adtc2026-demo.mp4` (GitHub repo or Google Drive link on DevPost).
- [ ] Also grab 2–3 still screenshots of model output for the DevPost gallery.

## Tools for the live demo
- `llama-server` (llama.cpp) gives an OpenAI-compatible API + simple web UI:
  `llama-server -m model/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 8080`
  then open http://localhost:8080 in a browser.
- Or capture the llama_cpp Python REPL output (as used in the quality check).

## DevPost submission checklist (Gate 1, due Aug 24 11:45pm PDT)
- [ ] Public GitHub repo URL: https://github.com/Laplace0xx/adtc-2026-hackathon (SET PUBLIC)
- [ ] metadata.json fully filled (no placeholders) — DONE
- [ ] download_model.sh works — DONE (verified idempotent)
- [ ] REPORT.md written — DONE
- [ ] submission.json produced by participant run — DONE (refresh SHA after commit)
- [ ] DevPost numeric fields: Sperf = 65.6, Seff = 74.4 (from final submission.json:
      Sperf = min(9.84/15,1)*100; Seff = (7168-1835)/7168*100). Enter one plain number
      per field. NOTE: the old 68.3 came from the pre-final 10.25 t/s bake-off run.
- [ ] 2-minute video — TO RECORD
- [ ] Screenshots / short clips — TO CAPTURE
- [ ] Bonus claims: budget laptop profile (true by default). African-language claim:
      NOT claimed (african_alpha_claim=false). African use case is argued in REPORT.md.
- [ ] Eligibility: Nigeria (resident) ✓, team ≤3 ✓, early stage ✓.