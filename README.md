# ADTC 2026 — Submission Template

This is the official template repository for the **Africa Deep Tech Challenge 2026** Laptop LLM track.

Fork this repository, fill in the required files, and submit your repository URL via [adtc-2026.devpost.com](https://adtc-2026.devpost.com).

---

## ✅ Submission Checklist

Before submitting, confirm every item:

- [ ] Your repository is **public** on GitHub
- [ ] `metadata.json` is fully filled in — no placeholder values remain
- [ ] `metadata.json` contains exactly **2 test prompts** in the `test_prompts` array, written for your chosen domain
- [ ] `download_model.sh` has only `MODEL_FILE` and `MODEL_URL` edited — no `[YOUR_...]` placeholders remain, and nothing else in the file was changed
- [ ] `MODEL_URL` points to an exact, pinned commit/release — not a mutable branch like `main`
- [ ] `download_model.sh` successfully downloads your model to `model/`
- [ ] The downloaded file is a valid **GGUF format** (`.gguf`) weight file
- [ ] `model/*.gguf` is listed in `.gitignore` — do **not** commit large weight files
- [ ] `REPORT.md` is filled in with your technical writeup, including the **Model Provenance** section
- [ ] Running `bash download_model.sh` completes without errors
- [ ] Your model runs entirely **offline** — zero external network calls during inference
- [ ] **Gate 2 only:** `metadata.json`'s `provenance` object is fully filled in — base model source, base model commit SHA, fine-tuning method, and training datasets (see [Model Provenance](#-model-provenance-gate-2) below)
- [ ] **Gate 2 only:** if `provenance.fine_tuning_method` is `lora`, `qlora`, or `full_fine_tune`, a `provenance/` folder is included with your adapter weights or training scripts, loss logs, dataset info + checksums, and merge/quantization docs

---

## 📁 Required File Structure

```
your-submission/
├── metadata.json          ← Required. Team, model, provenance, and test prompt metadata.
├── download_model.sh      ← Required. Downloads your .gguf model weight file.
├── REPORT.md              ← Required. Technical writeup (problem, design, provenance, benchmarks).
├── model/
│   └── your-model.gguf   ← Downloaded by the script above. Do NOT commit.
├── provenance/             ← Required ONLY if you fine-tuned your model (LoRA/QLoRA/full fine-tune).
│   ├── adapter_model.safetensors  ← Or your training scripts, if you did a full fine-tune.
│   ├── training_log.txt           ← Loss curve / training log.
│   └── dataset_info.md            ← Dataset name(s), source(s), and checksums.
└── .gitignore             ← Must exclude *.gguf and model/ from version control.
```

> If your model is a stock/off-the-shelf model used as-is (no fine-tuning), you do **not** need a `provenance/` folder — just fill in `provenance.base_model_source` and `provenance.base_model_commit_sha` in `metadata.json` and set `provenance.fine_tuning_method` to `"none"`.

---

## 📝 metadata.json

Fill in every field. No field should remain at its placeholder value.

```json
{
  "team_id": "your-team-id",
  "domain": "coding_assistants",
  "language_scope": ["en"],
  "african_alpha_claim": false,
  "budget_laptop_claim": true,
  "submitter": {
    "name": "your-name",
    "email": "your-email@domain.com",
    "github_handle": "your-github"
  },
  "cross_disciplinary_pairing": {
    "discipline": "education",
    "load_bearing": true,
    "description": "Brief description of how your model serves a real-world domain."
  },
  "provenance": {
    "base_model_source": "huggingface:org/base-model-name",
    "base_model_commit_sha": "the-exact-commit-sha-you-started-from",
    "fine_tuning_method": "none",
    "training_datasets": []
  },
  "test_prompts": [
    {
      "prompt_id": "tp_001",
      "prompt": "Your first test prompt, written for your chosen domain."
    },
    {
      "prompt_id": "tp_002",
      "prompt": "Your second test prompt, written for your chosen domain."
    }
  ],
  "model": {
    "name": "YourModel-Q4_K_M",
    "runtime": "llama.cpp",
    "quantization": "GGUF Q4_K_M",
    "parameters_estimate": "1.1B",
    "packaging": "binary_bundle"
  },
  "_runtime": {
    "model_path": "model/your-model.gguf"
  }
}
```

### Field Reference

| Field | Required | Description |
|---|---|---|
| `team_id` | ✅ | Your unique team ID as registered on the ADTF portal |
| `domain` | ✅ | Your challenge track. One of: `math_scientific_reasoning`, `healthcare_medical`, `agriculture`, `creative_writing`, `coding_assistants`, `corporate_enterprise`, `autonomous_ai_agents` |
| `language_scope` | ✅ | Array of BCP-47 language codes. Must include at least one. |
| `african_alpha_claim` | ✅ | `true` only if claiming the African Use Case Bonus |
| `budget_laptop_claim` | ✅ | Must be `true` — all submissions target the 8 GB RAM laptop profile |
| `submitter.name` | ✅ | Full name of the team member submitting the run |
| `submitter.email` | ✅ | Valid email address linked to the registered team |
| `submitter.github_handle` | ✅ | Verifiable GitHub username |
| `cross_disciplinary_pairing.discipline` | ✅ | The deep-tech discipline your model serves |
| `cross_disciplinary_pairing.load_bearing` | ✅ | `true` if the pairing is integral to the submission, not cosmetic |
| `provenance.base_model_source` | Gate 2 | Where your base model came from, e.g. `huggingface:microsoft/Phi-3-mini-4k-instruct-gguf`. If you trained from scratch, use the URL of your training repo instead. |
| `provenance.base_model_commit_sha` | Gate 2 | The exact commit SHA of the base model repo/file you started from. **This is not necessarily the same value as the commit you pin in `download_model.sh`'s `MODEL_URL`** — see [Model Provenance](#-model-provenance-gate-2) below for the distinction. |
| `provenance.fine_tuning_method` | Gate 2 | One of: `none` (stock model used as-is), `prompt_engineering` (no weight changes), `lora`, `qlora`, `full_fine_tune` |
| `provenance.training_datasets` | Gate 2 | Array of dataset names/URLs used for fine-tuning. Use `[]` if `fine_tuning_method` is `none` or `prompt_engineering`. |
| `test_prompts` | ✅ | **Exactly 2 prompts** in your chosen domain. Organizers will add 2 hidden prompts to test for overfitting. |
| `model.runtime` | ✅ | Must be `llama.cpp`. No other runtime is accepted. |
| `model.quantization` | ✅ | Must be a GGUF quantization format (e.g. `GGUF Q4_K_M`, `GGUF Q5_K_M`) |
| `model.parameters_estimate` | ✅ | Approximate parameter count (e.g. `135M`, `1.1B`, `7B`) |
| `model.packaging` | ✅ | How the model is packaged. One of: `docker_image`, `docker_build_from_repo`, `binary_bundle` |
| `_runtime.model_path` | ✅ | Relative path from repo root to your `.gguf` file (e.g. `model/my-model.gguf`) |

---

## 🔍 Model Provenance (Gate 2)

If you advance past Gate 1, semifinalists must fully disclose where their model came from. This is tracked in two places: the `provenance` object in `metadata.json` (structured facts) and the **Model Provenance** section of `REPORT.md` (narrative explanation, including a before/after comparison if you fine-tuned).

The entire `provenance` object — like everything above marked "Gate 2" — is optional at the schema level: a missing or incomplete `provenance` object never blocks a profiler run. It's a required item on the Gate 2 submission checklist, checked manually as part of that review, not something the tool enforces automatically.

**A note on the two "commit SHA" fields in this template — they answer different questions:**

- `download_model.sh`'s `MODEL_URL` commit pin (existing requirement, unchanged) exists so the *exact file the evaluator downloads* can never silently change after judging begins.
- `provenance.base_model_commit_sha` (new) identifies the *upstream base model version you started from*. For a stock model used as-is, these are usually the same commit. If you fine-tuned a base model and then hosted the resulting weights somewhere else (e.g. your own Hugging Face repo), they will differ — `base_model_commit_sha` points to the original base model's commit, not your fine-tuned repo's commit.

⚠️ **Neither of these is `reproducibility.git_commit_sha`** — that field doesn't belong in `metadata.json` at all; it's generated automatically by the profiler and appears only in the output report (`submission.json`/`audit.json`) it produces, tracking *your submission repo's own* commit, not your model's. Adding a `git_commit_sha` key directly to `metadata.json` will fail schema validation and abort the profiler run before any benchmark executes.

If `provenance.fine_tuning_method` is `none` (you used a stock/off-the-shelf model without modification), you only need to fill in `base_model_source` and `base_model_commit_sha` — no `provenance/` folder is required, and this is a fully legitimate submission path. It will, however, affect your originality score; see the challenge rules for how originality is scored.

If you did fine-tune (`lora`, `qlora`, or `full_fine_tune`), include a `provenance/` folder at your repo root containing:
- Your adapter weights (LoRA/QLoRA) or training scripts (full fine-tune)
- A training/loss log
- Dataset name(s), source(s), and checksums for any data used
- Notes on any merge or quantization steps applied after training

---

## 📥 download_model.sh

This script **must** download your model weight file to the `model/` directory.

Only edit the `MODEL_FILE` and `MODEL_URL` values near the top of the file — replace `[YOUR_MODEL_FILE_NAME]` and `[YOUR_MODEL_URL]` with your own. Every other line (the idempotency check, the download/retry logic) must stay exactly as provided. The evaluator reads this script's literal `MODEL_URL` assignment directly — it never executes your script on judging hardware — so changes outside those two values, or anything that isn't a plain, static string (shell commands, variables, string concatenation), will make your submission fail to prepare.

Rules:
- Must be idempotent — safe to run multiple times without re-downloading.
- Must work without any credentials — your weights must be publicly accessible.
- The downloaded file path must exactly match `_runtime.model_path` in `metadata.json`.
- `MODEL_URL` must point to an exact, immutable file — pin it to a specific commit or release, never a mutable branch/tag like `main` or `latest`. On Hugging Face, replace `main` in the URL with the exact commit SHA from your repo's file history (click "History" on the file, copy the commit hash). This guarantees the file you submitted can never change after judging begins.

Recommended hosting options for your weights:
- [Hugging Face](https://huggingface.co) — public model repos (free, best for GGUF files)
- GitHub Release Assets — attach the `.gguf` file to a GitHub Release (already immutable once published — no separate pinning needed)
- Any stable public URL (GCS public bucket, S3 public object, etc.)

---

## 📄 REPORT.md

Your technical writeup. Judges and the LLM-based audit system will read this to understand your submission. Cover:

1. **Problem** — What problem are you solving? Who is the target user in an African context?
2. **Design Decisions** — What model did you start from? Why that quantization level? What alternatives did you evaluate?
3. **Model Provenance** — Base model source and commit, fine-tuning methodology (if any), training datasets used, and a before/after comparison showing what your fine-tuning changed (if `provenance.fine_tuning_method` is not `none`).
4. **Constraints** — What hardware, connectivity, or data constraints shaped your approach?
5. **Benchmarks** — What inference speed and memory numbers did you observe on your development machine?

Keep it factual and specific. One to three pages is ideal.

---

## 🧪 Local Testing

The ADTC profiler is open source. Install it directly from the official repository:

```bash
pip install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"
```

Then run a local smoke test before submitting:

```bash
# 1. Download your weights
bash download_model.sh

# 2. Run the profiler in participant mode
adtc-profiler run \
  --submission . \
  --mode participant \
  --output submission.json \
  --skip-accuracy

# 3. Review your report
cat submission.json
```

A valid run produces a `submission.json` with `"measured_on": "participant_laptop"`.

The profiler source code, including the thermal monitoring logic and scoring formulas, is publicly readable at:
[github.com/Africa-Deep-Tech-Foundation/adtc-profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler)

---

## ⚠️ Rules

1. **Public repository required.** Your repository must be public at the time of evaluation.
2. **No model weights in git.** Add `*.gguf` and `model/` to your `.gitignore`. The evaluator downloads weights fresh via `download_model.sh`.
3. **100% offline during evaluation.** Your model must run with zero external network dependencies during our testing window. `download_model.sh` runs before the profiler starts, but once profiling begins, no outbound requests are permitted.
4. **llama.cpp only.** All models must use GGUF weights and run through `llama.cpp`. No other runtime is supported by our evaluation framework.
5. **8 GB RAM limit.** Your model must run within the standard laptop profile (4 vCPU, 8 GB RAM, integrated GPU only). Out-of-memory errors during evaluation result in automatic disqualification.
6. **No size restriction.** There is no parameter count or file size cap — but the 8 GB RAM constraint is strict. Plan your quantization level accordingly.
7. **Two test prompts required.** Your `metadata.json` must include exactly 2 prompts in the `test_prompts` array. Organizers will generate 2 additional hidden prompts within your domain. All 4 are used for scoring.

---

## 🆘 Support

Open an issue in this repository or contact the ADTF team at challenge@africadeeptech.org.

View the full eligibility rules at [adtc-2026.devpost.com/rules](https://adtc-2026.devpost.com/rules).

---

## 📄 License

This template is licensed under the terms of the [GNU GPL v3 License](LICENSE).

