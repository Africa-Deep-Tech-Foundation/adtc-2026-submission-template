# ADTC 2026 — Submission Template

This is the official template repository for the **Africa Deep Tech Challenge 2026** Laptop LLM track.

Fork this repository, fill in the required files, and submit your repository URL to the ADTF evaluation portal.

---

## ✅ Submission Checklist

Before submitting, make sure all of these are true:

- [ ] Your repository is **public** on GitHub
- [ ] `metadata.json` is filled in with your team's real information
- [ ] `download_model.sh` successfully downloads your model to `model/`
- [ ] Your model file is a valid **GGUF format** (`.gguf`) weight file
- [ ] `model/*.gguf` files are listed in `.gitignore` (do not commit large weights)
- [ ] Running `download_model.sh` then `adtc-profiler` locally passes without errors

---

## 📁 Required Structure

Your repository must contain exactly these files:

```
your-submission/
├── metadata.json          ← Required. Team and model metadata.
├── download_model.sh      ← Required. Downloads your .gguf model weight file.
├── model/
│   └── your-model.gguf   ← Downloaded by the script above. Do NOT commit this.
└── .gitignore             ← Must exclude *.gguf files.
```

---

## 📝 metadata.json

Fill in every field. Do not leave any field blank.

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
  "model": {
    "name": "YourModel-Q4_K_M",
    "runtime": "llama.cpp",
    "quantization": "GGUF Q4_K_M",
    "parameters_estimate": "1.1B",
    "packaging": "binary_bundle"
  },
  "_runtime": {
    "model_path": "model/your-model.gguf",
    "docker_image": "your-team/model:latest"
  }
}
```

### Field Reference

| Field | Description |
|---|---|
| `team_id` | Your unique team ID as registered on the ADTF portal |
| `domain` | Your challenge track. One of: `coding_assistants`, `education`, `agriculture`, `health` |
| `language_scope` | Array of BCP-47 language codes. Must include at least one. |
| `african_alpha_claim` | Set to `true` only if you are claiming the African Language Bonus |
| `budget_laptop_claim` | Must be `true`. All submissions target the 8GB RAM laptop profile. |
| `model.runtime` | Must be `llama.cpp`. All models must run through llama.cpp. |
| `model.quantization` | Must be a GGUF quantization (e.g. `GGUF Q4_K_M`, `GGUF Q5_K_M`) |
| `_runtime.model_path` | Relative path from the repo root to your `.gguf` file |

---

## 📥 download_model.sh

This script **must** download your model weight file to the `model/` directory before the evaluator runs.

Rules:
- Must be idempotent (safe to run multiple times).
- Must work without any credentials (your weights must be publicly accessible).
- The downloaded file path must match `_runtime.model_path` in `metadata.json`.

Recommended hosting options for your weights:
- [Hugging Face](https://huggingface.co) — public model repos (free)
- GitHub Release Assets — attach the `.gguf` file to a GitHub Release
- Any public URL (GCS, S3, etc.)

---

## 🧪 Local Testing

Install the profiler and run a local smoke test before submitting:

```bash
pip install adtc-profiler   # or: uv pip install adtc-profiler

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

A valid run will produce a `submission.json` with `"measured_on": "participant_laptop"`.

---

## ⚠️ Rules

1. **Public repository required.** Your repository must be public at the time of evaluation.
2. **No model weights in git.** Add `*.gguf` and `model/` to your `.gitignore`.
3. **No internet access during evaluation.** Your `download_model.sh` runs before the profiler in a controlled environment, but the profiler itself runs without external network access.
4. **llama.cpp only.** All models must run through `llama.cpp` using GGUF weights.
5. **8 GB RAM limit.** Your model must run within the standard laptop profile (4 vCPU, 8 GB RAM, no GPU).

---

## 🆘 Support

Open an issue in this repository or contact the ADTF team at challenge@africadeeptech.org.
