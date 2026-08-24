# VECTOR Afya MVP

VECTOR Afya is an offline healthcare information and education assistant built around a local Qwen2.5-3B-Instruct GGUF model and llama.cpp-compatible inference.

## MVP architecture

1. User selects a mode or chooses Auto-detect.
2. A deterministic router confirms one of four ADTC healthcare categories:
   - Clinical Information
   - Medical Q&A
   - Triage Support
   - Patient Education
3. A cross-cutting Safety / Assessment & Escalation layer checks for predefined urgent signals and supplies safety constraints.
4. Category instructions and global safety instructions are sent to the local model.
5. A post-generation safety check ensures urgent cases contain explicit escalation language.

Assessment & Escalation is intentionally a safety capability, not a fifth user-facing ADTC category.

## Run

The model must exist at `model/Qwen2.5-3B-Instruct-Q4_K_M.gguf`. Run `./download_model.sh` first when the model is absent.

Then, from the project root:

```bash
python -m vector_afya.app
```

For a non-interactive test:

```bash
python -m vector_afya.app --mode patient_education --question "Explain high blood pressure in simple language."
```

## Tests

```bash
python -m pytest -q
```

## Safety scope

The safety layer is deliberately conservative and limited. It is not a clinical decision engine, does not diagnose, and cannot replace professional assessment. Red-flag matching is a deterministic pre-generation guardrail; the model remains responsible for the educational response within the supplied constraints.
