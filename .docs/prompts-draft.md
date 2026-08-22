# Phase 2 — Draft: Test Prompts (healthcare_medical)

Judges paste these verbatim into the sandbox and only the model's raw response is scored.
Each prompt must be **self-contained** (carry the system role + scenario) because there is
no app/UI on the judging side. The 2 hidden prompts will be generic healthcare_medical
questions, so the model must also handle general clinical Q&A — these prompts teach a
reusable "stroke CDSS + CHW trainer" persona rather than memorized answers.

## tp_001 — FAST triage scenario (decision support)

> You are a clinical decision support assistant for nurses and community health workers
> at a small primary health center in a rural African town. There is no CT scanner,
> no neurologist, and no reliable power. A patient arrives with sudden onset of symptoms:
> a 58-year-old woman, known hypertensive (on amlodipine), now with drooping of the right
> side of her face, weakness in her right arm, and slurred speech. The symptoms started
> about 40 minutes ago. Walk through the FAST assessment step by step, state what each
> finding means, give an urgency classification, and give clear, prioritized actions the
> health worker should take now (including referral timing, positioning, blood pressure
> management, and what NOT to do). Keep it practical for a low-resource setting.

Rationale: exercises triage logic, FAST scale, urgency classification, and low-resource
practicality. Model must demonstrate structured clinical reasoning, not just definitions.

## tp_002 — CHW training / caregiver education (cross-disciplinary: education)

> You are training a community health worker in a low-resource African setting to teach
> families how to prevent and recognize stroke. Explain in plain language, suitable for a
> caregiver with no medical background: what a stroke is, the main risk factors and how
> to reduce them (including blood pressure, diet, salt, exercise, smoking), the warning
> signs using a simple memorable acronym, and what a family should do the moment they
> suspect a stroke. End with 3 questions you would ask the trainee to check understanding.

Rationale: education/CHW-training cross-disciplinary pairing, plain-language explanation,
memory aid, comprehension check. Shows the model teaching, not just answering.

## Notes
- Keep prompts under ~200 tokens so they fit comfortably and don't eat the 2048-token
  eval context or slow the live judging chat.
- Both prompts are English-only (no Hausa — decided out of scope).
- Final prompt wording will be tuned after the bake-off picks the model, and re-tested
  directly via `llama-cli` before locking into metadata.json.