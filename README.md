# ADTC 2026 — Submission Template

This is the official template repository for the **Africa Deep Tech Challenge 2026** Laptop LLM track.

Fork this repository, fill in the required files, and submit your repository URL via [adtc-2026.devpost.com](https://adtc-2026.devpost.com).

---

## ✅ Submission Checklist

Before submitting, confirm every item:

- [ ] Your repository is **public** on GitHub
- [ ] `metadata.json` is fully filled in — no placeholder values remain
- [ ] `metadata.json` contains exactly **2 test prompts** in the `test_prompts` array, written for your chosen domain
- [ ] `download_model.sh` successfully downloads your model to `model/`
- [ ] The downloaded file is a valid **GGUF format** (`.gguf`) weight file
- [ ] `model/*.gguf` is listed in `.gitignore` — do **not** commit large weight files
- [ ] `REPORT.md` is filled in with your technical writeup
- [ ] Running `bash download_model.sh` completes without errors
- [ ] Your model runs entirely **offline** — zero external network calls during inference

---

## 📁 Required File Structure

```
your-submission/
├── metadata.json          ← Required. Team, model, and test prompt metadata.
├── download_model.sh      ← Required. Downloads your .gguf model weight file.
├── REPORT.md              ← Required. Technical writeup (problem, design, benchmarks).
├── model/
│   └── your-model.gguf   ← Downloaded by the script above. Do NOT commit.
└── .gitignore             ← Must exclude *.gguf and model/ from version control.
```

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
  "cross_disciplinary_pairing": {
    "discipline": "education",
    "load_bearing": true,
    "description": "Brief description of how your model serves a real-world domain."
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
    "parameters_estimate": "1.1B"
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
| `cross_disciplinary_pairing.discipline` | ✅ | The deep-tech discipline your model serves |
| `cross_disciplinary_pairing.load_bearing` | ✅ | `true` if the pairing is integral to the submission, not cosmetic |
| `test_prompts` | ✅ | **Exactly 2 prompts** in your chosen domain. Organizers will add 2 hidden prompts to test for overfitting. |
| `model.runtime` | ✅ | Must be `llama.cpp`. No other runtime is accepted. |
| `model.quantization` | ✅ | Must be a GGUF quantization format (e.g. `GGUF Q4_K_M`, `GGUF Q5_K_M`) |
| `model.parameters_estimate` | ✅ | Approximate parameter count (e.g. `135M`, `1.1B`, `7B`) |
| `_runtime.model_path` | ✅ | Relative path from repo root to your `.gguf` file (e.g. `model/my-model.gguf`) |

---

## 📥 download_model.sh

This script **must** download your model weight file to the `model/` directory.

Rules:
- Must be idempotent — safe to run multiple times without re-downloading.
- Must work without any credentials — your weights must be publicly accessible.
- The downloaded file path must exactly match `_runtime.model_path` in `metadata.json`.

Recommended hosting options for your weights:
- [Hugging Face](https://huggingface.co) — public model repos (free, best for GGUF files)
- GitHub Release Assets — attach the `.gguf` file to a GitHub Release
- Any stable public URL (GCS public bucket, S3 public object, etc.)

---

## 📄 REPORT.md

Your technical writeup. Judges and the LLM-based audit system will read this to understand your submission. Cover:

1. **Problem** — What problem are you solving? Who is the target user in an African context?
2. **Design Decisions** — What model did you start from? Why that quantization level? What alternatives did you evaluate?
3. **Constraints** — What hardware, connectivity, or data constraints shaped your approach?
4. **Benchmarks** — What inference speed and memory numbers did you observe on your development machine?

Keep it factual and specific. One to three pages is ideal.

---

## 🧪 Local Testing

The ADTC profiler is open source. Install it directly from the official repository:

```bash
pip install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-profiler.git#subdirectory=profiler"
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
[github.com/Africa-Deep-Tech-Foundation/adtc-2026-profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-profiler)

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
