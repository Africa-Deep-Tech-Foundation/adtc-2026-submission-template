# ADTC 2026 — Build Log / Notes

Running documentation of everything done for the ADTC 2026 (Laptop LLM) Gate-1
submission. Successes, failures, and observations are recorded as they happen.

- **Goal:** Offline stroke CDSS (FAST triage + CHW education) for resource-constrained
  African primary health centers. English-only. African-use-case bonus.
- **Scoring target:** `Stotal = 0.50*Sacc + 0.30*Sperf + 0.20*Seff - Pthermal`
  (+10% budget profile). Hard constraint: peak RSS < 7 GB (OOM = DQ).
- **Domain:** `healthcare_medical` · **Team ID:** 1143733 · **Cross-disciplinary:** education/CHW training.
- **Gate 1 deadline:** Aug 24 2026 11:45pm PDT (Aug 25).
- **Rule reminder:** NEVER push to GitHub unless the user explicitly says so.

---

## Phase 0 — Environment setup & smoke test (2026-08-19)

### What was done
1. Verified environment:
   - `llama.cpp` built at `~/llama.cpp/build/bin/` (`llama-bench`, `llama-cli`).
   - `adtc-profiler` 0.1.0 installed (pip).
   - Accuracy stack imports OK: `llama_cpp` 0.3.35, `lm_eval` 0.4.12, numpy, psutil, jsonschema.
   - Python 3.14.5.
   - Machine: Fedora 43 (Workstation), Intel i5-8365U (4C/8T), 15.4 GB RAM, 17 GB free disk.
2. **Failure found:** `llama-bench` was NOT on PATH. The profiler's `_find_llama_bench()`
   only searches PATH, so the profiler would fail at the throughput stage.
   - **Fix:** `export PATH="$HOME/llama.cpp/build/bin:$PATH"` (must be set in every shell
     before running the profiler; or symlink `llama-bench` into a PATH dir).
   - **Observation:** the environment is Fedora, not the Ubuntu 22.04 audit target. This is
     fine for participant profiling (process-scoped RSS measurement), but the OS field in
     `submission.json` will differ from the audit VM — expected and tolerated.
3. Downloaded the starter 135M model via the template's `download_model.sh`
   (105 MB, `model/SmolLM2-135M-Instruct-Q4_K_M.gguf`). Download is idempotent (checks for
   existing file). OK.
4. **Schema fix:** template `metadata.json` had `"domain": "Healthcare"` which is INVALID —
   the profiler's JSON schema enforces a strict enum
   (`healthcare_medical`, `coding_assistants`, etc.). Changed to `healthcare_medical`.
   Without this the profiler exits with a schema validation error before benchmarking.
5. Ran the smoke test:
   ```
   adtc-profiler run --submission . --mode participant --output submission.json --skip-accuracy
   ```
   Result: ✓ wrote `submission.json` — schema-valid.

### Baseline numbers (SmolLM2-135M-Instruct Q4_K_M, CPU-pinned, this machine)
| Metric | Value |
|---|---|
| Generation speed | 65.05 t/s (Sperf would be 100 vs fixed 15 t/s reference) |
| First token latency | 2843.6 ms (512-token prompt, prompt-processing rate based) |
| Peak RSS | 200.8 MB (Seff ≈ 97) |
| Steady-state RSS | 185.5 MB |
| Peak temp | 71.0 °C (not throttled) |
| CPU p99 | 86.6% |
| Params check | pass (claimed 135M vs 134.5M actual, ±15% tolerance) |

### Notes for later
- `submission.json` is NOT in `.gitignore` — must be added before committing (Phase 3).
- `git_commit_sha` recorded from the repo (63ddc5422404); repo must be committed before
  final profiling so the SHA matches the submission.
- Accuracy block is empty when `--skip-accuracy` is used; the FINAL run must be a full run
  (no skip) so the report carries real accuracy telemetry.

---

## Phase 1 — Model bake-off (in progress)

### Candidates
1. Qwen2.5-3B-Instruct Q4_K_M (~1.9 GB) — primary
2. Qwen2.5-1.5B-Instruct Q4_K_M (~1.0 GB) — lighter alternative
3. SmolLM2-135M-Instruct Q4_K_M (already measured, control)

### Method
For each candidate:
- Download GGUF into `model/`.
- Point `metadata.json` `model.*` + `_runtime.model_path` at the candidate.
- Run `adtc-profiler run --mode participant` (FULL, includes ARC-Easy accuracy, 50 samples).
- Record results below. Sequential runs (CPU-bound; concurrent runs would skew memory/thermal).

### Downloads (2026-08-19)
- Qwen2.5-3B-Instruct Q4_K_M: `model/qwen2.5-3b-instruct-q4_k_m.gguf` — 2.1 GB.
  - First attempt hit the 5-min tool timeout mid-download (1.17 GB partial). Resumed with
    `curl -C -` and a 10-min window — completed cleanly. **Observation: full file transfers
    can exceed a default 5-min command timeout; always resume with `-C -` and longer limits.**
- Qwen2.5-1.5B-Instruct Q4_K_M: `model/qwen2.5-1.5b-instruct-q4_k_m.gguf` — 1.1 GB. OK.

### GGUF header verification (via profiler `gguf.extract_metadata`)
| Model | Arch | Context | Actual params | Claim → fraud check |
|---|---|---|---|---|
| Qwen2.5-3B | qwen2 | 32768 | 3,397,103,616 | "3B" → PASS (within ±15%: 2.55–3.45B) |
| Qwen2.5-1.5B | qwen2 | 32768 | 1,777,088,000 | "1.5B" → **FAIL** (1.777B > 1.725B upper bound) |
| SmolLM2-135M | llama | 8192 | 134,515,008 | "135M" → PASS |

**Failure/observation:** The "1.5B" model actually has 1.78B params. Claiming `1.5B` in
`parameters_estimate` triggers the profiler's fraud check (params_match: false). The metadata
for that candidate must use `1.8B` (or `1.7B`) to pass. For the 3B, `3B` is fine.

### Runs
- **Run 1 — Qwen2.5-3B-Instruct Q4_K_M:** full participant run (ARC-Easy, 50 samples).
  - Accuracy: **0.80 acc_norm** (50 samples) — solid for 3B.
  - Peak RSS: **3467 MB** → Seff ≈ 50.4. VMS 4395 MB.
  - **Throughput 5.04 t/s — POLLUTED.** llama-bench ran during heavy system load
    (load avg 13, 6.3 GB swap used, Chrome/VS Code/2×opencode running). First-token
    latency 39.9 s is absurd. These numbers are NOT usable.
  - Thermal: 75.0 °C peak, not throttled. CPU p99 99.2%.
  - Params match: PASS (3.397B vs "3B").
  - **Lesson learned:** never run benchmarks during system load; check `loadavg`/`free`
    first. Re-run throughput cleanly.
- **Run 2 — Qwen2.5-3B (CLEAN re-run):** `--skip-accuracy` for trustworthy speed/memory.
  - **TPS 4.46 t/s, TTFT 37.7 s (512-token prompt).** Peak RSS 3467 MB. Temp 76 °C, not throttled.
  - Sperf = 29.7 (min(4.46/15,1)×100) · Seff = 51.6.
  - **MAJOR STRATEGIC FINDING:** the i5-8365U (8th-gen Ultrabook, 4C/8T) is too slow for a
    3B Q4. Live-judge chat would take ~60+ s per answer; Sperf is capped at ~30/100 on the
    speed axis. A 3B only wins if its Sacc advantage outweighs losing ~45 pts on Sperf and
    ~46 pts on Seff vs a 1.5B. Decision hinges on the 1.5B numbers.
  - est Stotal (using real Sperf=29.7, Seff=51.6, Sacc≈80): **59.2**
- **Run 3 — Qwen2.5-1.5B-Instruct Q4_K_M (claimed 1.8B):** `--accuracy-limit 10`.
  - TPS 8.55 t/s → Sperf = 57.0 · Peak RSS 1835 MB → Seff = 74.4 · TTFT 20.5 s.
  - Acc (10 samples) 0.50 acc_norm → Sacc proxy 50 (NOISY — only 10 samples).
  - params_match PASS with "1.8B" claim (actual 1.777B).
  - est Stotal ≈ 0.5×50 + 0.3×57 + 0.2×74.4 = **57.0** (Sacc estimate unreliable).
  - **Observation:** "1.8B" label fix works; accuracy sample size matters a lot — the 50-sample
    3B score (0.80) is far more trustworthy than this 10-sample 0.50.
- **Run 4 — SmolLM2-135M (control):** `--accuracy-limit 10`.
  - results below

### Results
<!-- filled in as runs complete -->

### Decision (2026-08-19)
**COMMITTED TO Qwen2.5-1.5B-Instruct Q4_K_M.** Rationale:
- Final 50-sample numbers (quiet machine): TPS 10.25, peak RSS 1835 MB, **ARC-Easy 0.74 acc_norm**,
  params_match PASS, temp 76 °C.
- est Stotal = 0.5×74 + 0.3×68.3 + 0.2×74.4 = **72.4** (vs 3B: 59.2; vs 135M: ~64.4 on noisy proxies).
- The 1.5B captures ~93% of the 3B's measured accuracy (0.74 vs 0.80) at 2.3× the speed and half the
  RAM — a dominant tradeoff on this hardware class. The 135M fails the accuracy axis (0.30) which is
  50% of the score, and is qualitatively unusable for clinical chat.

### Quality check (llama_cpp chat, temp=0)
- **tp_001 (FAST triage):** excellent — step-by-step FAST with findings/meaning/urgency, High urgency
  classification, prioritized actions (positioning, BP measurement, urgent referral, re-assess in
  15 min). Clinically sound.
- **tp_002 (CHW training):** excellent — plain-language stroke explanation, risk factors, prevention,
  FAST acronym, ends with 3 comprehension-check questions as requested.
- **CLI lesson:** `llama-cli -p ...` enters REPL by default in new builds and with stdin closed it
  spins printing `>` prompts (wrote a 1.7 GB junk file — deleted). Use `-no-cnv` + `--simple-io`
  (still flaky) or the llama_cpp Python API for scripted testing.
- Generation ≈ 10 t/s live (345 tokens in ~54 s including ~10 s model load).

### Final run (submission.json)
- Full 50-sample ARC-Easy run on the FINAL metadata (team 1143733, stroke prompts, 1.8B claim).
  → **Sperf 68.3 · Seff 74.4 · Sacc 74.0 · estStotal 72.4** (pre-bonus; +10% budget multiplier applies).
- NOTE: this run was made BEFORE the local commit; SHA will be refreshed by a post-commit re-run.