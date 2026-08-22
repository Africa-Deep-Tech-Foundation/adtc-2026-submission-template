# ADTC 2026 — Concepts, Exercises & Defense Guide

> **Purpose:** Move from "vibe coding" to genuine understanding. This document explains every
> term and concept needed to **build, explain, and defend** this project — at Gate 1 (report),
> Gate 2 (technical Q&A), and Gate 3 (final defense). Each section has **exercises** (hands-on,
> runnable on this machine) and **mini-projects** (small builds that teach the pipeline).
>
> **Reading path:** Do the parts in order. Every part ends with "You should be able to explain…"
> — those are your defense talking points. The final section is a judge Q&A drill.

---

## 0. The Big Picture (read this first)

### What we are building
An **offline clinical decision-support model** for stroke care in African primary health
centers: nurses and community health workers (CHWs) use it to run the FAST triage, get
urgency classification, referral guidance, blood-pressure management advice, and structured
patient education. It runs **entirely on a laptop CPU** — no GPU, no cloud, no power grid
dependence during inference.

### The stack (one sentence each)
| Layer | What it is | In our project |
|---|---|---|
| Base model | Pretrained language model | Qwen2.5-1.5B-Instruct (1.777B params) |
| Quantization | Compress weights to ~4 bits to fit in RAM and run fast on CPU | GGUF Q4_K_M (1.1 GB file) |
| Runtime | C++ inference engine that executes the model on CPU | llama.cpp (llama-cli, llama-bench, llama-server) |
| Chat template | Instruction string that shapes every conversation | Qwen2.5 template with a baked-in clinical persona |
| Fine-tuning (planned) | Training the model on domain data | QLoRA: English + Hausa stroke dataset |
| Evaluation | Measuring accuracy / speed / memory | adtc-profiler → `submission.json` |

### The scoring formula (memorize this)
```
Stotal = 0.50·Sacc + 0.30·Sperf + 0.20·Seff − Pthermal
```
- **Sacc (50%)** — accuracy, **judged entirely by humans**. Panel chats with your model
  through an in-browser interface (2 of your prompts + 3 hidden in-domain prompts), and
  grades response quality **and documentation quality**.
- **Sperf (30%)** — `100 × (TPS_act ÷ TPS_ref)`, reference 15.0 t/s (provisional).
  Capped at 100.
- **Seff (20%)** — `100 × ((7 GB − peak_RSS) ÷ 7 GB)`. Lower RAM = better. >7 GB = disqualification.
- **Pthermal (−10)** — applied if core temp exceeds 85 °C or throttling is detected.

Two **bonuses**: **+10 points** African Use Case Bonus (how well it fits real African
contexts) and **+15% on panel score** for meaningful African-language functionality.

**Why this architecture wins on this formula:** Accuracy is 50% of the score and is judged
qualitatively → domain behavior, persona, and documentation matter more than raw speed.
Speed and memory are won by choosing the smallest model that keeps accuracy (1.5B beats 3B:
4.46 → 10.25 t/s, RAM 3.5 → 1.8 GB) and the right quantization.

### Our measured baseline (know these numbers cold)
- Throughput: **9.84 t/s** (llama-bench `-p 512 -n 128`), first token 22.9 s
- Peak RSS: **1835 MB** → Seff ≈ 73.8
- ARC-Easy: **0.74 acc_norm** (50 samples)
- Peak temp: **71 °C** (no thermal penalty)
- Estimated Stotal ≈ **72** (+10% budget-laptop multiplier if we claim it)

---

## 1. LLM Fundamentals

### 1.1 Tokens — the atom of language
A **token** is a piece of text. Models don't see characters; they see token IDs.
"stroke" might be one token; "strokes" might be two. English ≈ 0.75 words/token
(so 100 words ≈ 133 tokens). Qwen2.5's tokenizer has **151,936** vocabulary entries.

- **Tokenization** = text → IDs (before inference). **Detokenization** = IDs → text.
- Why it matters: prompt length and generation length are measured in **tokens**
  (our profiler uses 512 prompt tokens, 128 generated tokens).

**Exercise 1.1 — Count tokens.** Using the Python `llama_cpp` package (already installed):
```python
from llama_cpp import Llama
# loading the tokenizer alone is expensive; use a tiny file if you have one
# Simpler: use the gguf tokenizer via llama-gguf (C++), or estimate: len(text.split()) * 4/3
text = open("metadata.json").read()
print("approx tokens:", len(text.split()) * 4 // 3)
```
**Exercise 1.2 — Find the token for "stroke".** Use `llama-cli` to inspect or the
tokenizer vocab in llama.cpp Python:
```python
llm = Llama(model_path="model/qwen2.5-1.5b-instruct-q4_k_m.gguf", n_ctx=512, n_threads=4)
ids = llm.tokenize(b"stroke FAST")
print(ids, llm.detokenize(ids))
```

### 1.2 The transformer — how the model "thinks"
A transformer is a stack of **layers**, each with **attention** (which past tokens matter
for the current one) and **feed-forward** (dense computation). It predicts the **next
token**, one at a time, given all previous tokens.

Key numbers for Qwen2.5-1.5B: **28 layers**, hidden size 1536, 12 attention heads,
**2 key-value heads** (grouped-query attention), context window 32,768 tokens.

Concepts to be able to explain:
- **Autoregressive** = output feeds back as input ("generate 128 tokens" = 128 forward passes).
- **Context window** = maximum tokens the model can look at (32,768 for Qwen2.5-1.5B).
- **KV cache** = per-token key/value tensors cached across the conversation so earlier
  tokens aren't recomputed. **This is the main memory driver of chat.**
- **Sampling** (temperature, top-p) = the randomness knob when picking the next token.
  Low temperature (0.1–0.7) = deterministic, good for medical advice.

**KV cache size formula (memorize for defense):**
```
bytes/token = 2 (K+V) × layers × kv_heads × head_dim × bytes_per_value
            = 2 × 28 × 2 × 128 × 2 (fp16) ≈ 28.7 KB/token
```
→ At 512 tokens ≈ 15 MB; at 4096 ≈ 117 MB; at 32768 ≈ 940 MB.
This is why **context length affects RAM** even though weights are fixed.

**Exercise 1.3 — Prove the KV math.** Compute the KV size by hand for 512 and 4096 tokens.
Then compare with the RSS difference between a llama-bench run at `-c 512` vs `-c 4096`.

### 1.3 Instruct vs base models
- **Base model**: trained on raw internet text → continues text, can't follow instructions.
- **Instruct model**: further trained (SFT + preference alignment) to follow instructions.
- We use **Qwen2.5-1.5B-Instruct** — it already knows how to answer "as a clinical assistant…".

**You should be able to explain:**
- Why a 1.5B model can be medically useful (training data includes medical text; domain
  knowledge is *in the weights*; we add a persona + fine-tune to specialize).
- The trade-off: bigger model = more knowledge but slower & heavier (our bake-off: 3B
  was 4.46 t/s and 3.5 GB vs 1.5B at 9.84 t/s and 1.8 GB).

---

## 2. Quantization & GGUF

### 2.1 Why quantize
Weights are fp16 (2 bytes each). 1.777B params × 2 bytes ≈ 3.5 GB — too big/slow for an
8 GB laptop. **Quantization** rounds weights to fewer bits (e.g., 4-bit): 1.777B × 0.5
bytes ≈ 0.9 GB. Less RAM → higher Seff, less memory bandwidth → higher TPS.

Cost: slight accuracy loss. The art is picking the quantization where accuracy holds.

### 2.2 GGUF — the model file format
**GGUF** is the file format llama.cpp uses: it packs the quantized weights **plus metadata**
(architecture, context length, tokenizer, chat template). One file = a deployable model.
In our repo: `model/qwen2.5-1.5b-instruct-q4_k_m.gguf` (1.05 GB = 0.6 bytes/param).

GGUF metadata fields we care about: `general.architecture`, `context_length`,
`tokenizer.ggml.chat_template`, `general.name`.

### 2.3 Quant types we know
| Quant | Bits/weight (approx) | Notes |
|---|---|---|
| Q4_K_M | ~4.5 | Our default. Good accuracy/speed balance |
| Q5_K_M | ~5.5 | Higher accuracy, slightly slower/heavier |
| Q3_K_M | ~3.5 | Lower accuracy, faster, lighter |
| IQ4_XS | ~4.25 | "Importance-matrix" 4-bit, different packing, sometimes faster |
| Q8_0 | 8.0 | Near-lossless, but ~2× weight size |

**Rule of thumb:** accuracy loss is small from fp16→Q8→Q5, noticeable at Q4, more at Q3,
big at Q2. We measured Q4_K_M holds 0.74 ARC-Easy; sweep planned to test Q3/IQ4/Q5.

**Exercise 2.1 — File size math.** Verify: `ls -l model/…1.5b…gguf` → 1,117,320,736 bytes
÷ 1,777,088,000 params ≈ 0.63 bytes/param ≈ 5.0 bits/param (Q4_K_M is ~4.5 bit + overhead).

**Exercise 2.2 — Inspect GGUF metadata.** Use the built tool:
```
export PATH="$HOME/llama.cpp/build/bin:$PATH"
llama-gguf model/qwen2.5-1.5b-instruct-q4_k_m.gguf   # prints metadata, tensor sizes
```
Find: `context_length`, `chat_template`, and the number of tensors.

**Mini-project A — Quantization comparator.** Write a shell script that runs `llama-bench`
on two GGUFs and prints a table (TPS, RSS) + `llama-gguf` sizes. This is a tiny preview of
the real Lever 2 quant sweep.

---

## 3. llama.cpp — the runtime

### 3.1 What it is
llama.cpp is a **C++ implementation of transformer inference** optimized for CPU
(and now other backends). It reads GGUF files and runs tokenization, prefill, and
generation. It's *the* reference runtime for this challenge — the organizers measure
"llama.cpp running your GGUF model".

Tools in `~/llama.cpp/build/bin/`:
- `llama-cli` — chat CLI (we hit its REPL quirk; use `-no-cnv --simple-io` for scripting)
- `llama-bench` — benchmark: throughput (t/s), prompt processing, memory
- `llama-server` — HTTP chat server (not used by the profiler)
- `llama-gguf` — metadata inspection / editing

### 3.2 What llama-bench measures
```
llama-bench -m model.gguf -p 512 -n 128 -ngl 0
```
- `-p 512` = prompt tokens (prefill), `-n 128` = generated tokens, `-ngl 0` = no GPU layers.
- Output: **tokens_per_second** (generation TPS) — this is what feeds Sperf.
- Peak RSS is tracked by the profiler's own wrapper process (psutil), not llama-bench.

Why the flags are fixed: the **profiler controls the invocation** — we cannot tune flags to
game TPS. We optimize the *model file* (quantization, template) instead.

### 3.3 Why CPU speed differs between models
Generation speed ≈ **memory bandwidth / weights size** (CPU-bound LLM inference is
bandwidth-bound: each token needs a full pass over all weights).
- Smaller weights → faster. (135M ≈ 48 t/s, 1.5B ≈ 10 t/s, 3B ≈ 4.5 t/s.)
- `-march=native`/AVX2 build → faster matmuls (our build is already optimized: Release -O3 + native).

**Exercise 3.1 — Run the real benchmark.**
```
export PATH="$HOME/llama.cpp/build/bin:$PATH"
llama-bench -m model/qwen2.5-1.5b-instruct-q4_k_m.gguf -p 512 -n 128 -ngl 0
```
You should see ~9–10 t/s. Run the 135M file too (expect ~48 t/s). Explain the ratio
from weight sizes alone (bandwidth argument).

**Exercise 3.2 — The REPL trap (learned the hard way).** Run
`llama-cli -m model/…1.5b… -p "Hello"` and note it *doesn't exit* (it's a REPL that
waits for input; with stdin closed it spins writing `>` prompts — we once created a
1.7 GB junk file). Use `-no-cnv --simple-io -p "…"` instead, or the Python `llama_cpp`
API. **Be ready to explain this in the Q&A** — it shows you understand the tooling.

**You should be able to explain:** why llama.cpp is C++ (performance, control), what the
binary outputs mean, and why our build being `-O3 + native` matters (documented design
decision, "tools used and why" section of REPORT.md).

---

## 4. The Profiler & Scoring Machine

### 4.1 How the ADTC pipeline measures us
1. It runs `download_model.sh` (ours — idempotent, ~1.1 GB).
2. `llama-bench` (fixed flags) → TPS → Sperf; profiler wrapper measures **peak RSS** → Seff.
3. Temperature before/after each run → Pthermal.
4. Judges chat with the model in a **sandbox** capped at 8 GB RAM / 4 cores.
5. `submission.json` is the local artifact we self-report on DevPost.

### 4.2 The math you must be fluent in (defense!)
Given our run: TPS 9.84, peak RSS 1.84 GB:
- `Sperf = min(9.84 / 15.0, 1.0) × 100 = 65.6`
- `Seff = (7 − 1.84) / 7 × 100 = 73.7`
- Thermal: 71 °C < 85 °C → 0 penalty.
- `Stotal ≈ 0.5·Sacc + 0.3·65.6 + 0.2·73.7` — with Sacc unknown (judged), estimate 72.

**Sensitivity analysis (know this):** Each extra GB of RAM costs **14.3 Seff points**
(= 2.86 Stotal). Each t/s up to 15 costs **6.7 Sperf points** (= 2.0 Stotal). Every point
of Sacc is worth **0.5 Stotal**. → **Sacc is 5× more valuable than TPS or RAM.** This is
the single most important number to be able to explain.

**Exercise 4.1 — Recompute from submission.json.**
```python
import json
d = json.load(open("submission.json"))
tps = d["throughput"]["tokens_per_second_generation"]
rss = d["memory"]["peak_rss_mb"] / 1024
print("Sperf:", min(tps/15.0, 1.0)*100, "| Seff:", (7-rss)/7*100)
```
**Exercise 4.2 — Model the 3B.** Same math with 4.46 t/s, 3.47 GB, Sacc 0.80.
Show why it scores lower (~59 vs 72) despite higher accuracy. This is the bake-off
decision written in math — **judge bait**, be ready.

**Mini-project B — Score estimator.** Write a small Python script `scores.py` that takes
TPS/RSS/Sacc-est and prints Sperf/Seff/Stotal. Use it to argue quant choices.

**You should be able to explain:** what we self-report, what the organizers measure, why
RAM budget 7 GB, what could disqualify us (OOM), and why thermal is a non-issue for us (71 °C).

---

## 5. Chat Templates & System Prompts

### 5.1 What a chat template is
A **Jinja2 template** stored in the GGUF (`tokenizer.ggml.chat_template`) that turns a
list of messages (system/user/assistant) into the model's prompt format. Qwen2.5's looks
like:
```
<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
```
If a judge sends a bare user message with no system message, the template just omits the
system block — **the model gets zero context about its role.** That's why we bake the
persona *into the template*: even bare prompts inherit the clinical assistant identity.

### 5.2 Why persona matters for Sacc
Our two test prompts already contain the full context inline ("You are a clinical decision
support assistant… no CT scanner…"). But the **3 hidden prompts** likely won't. The persona
in the template makes every interaction consistent. **Zero cost**: template isn't tokens,
doesn't change weights, doesn't affect TPS/RAM.

**Exercise 5.1 — See the current template.**
```
llama-gguf model/qwen2.5-1.5b-instruct-q4_k_m.gguf | grep -i template
```
**Exercise 5.2 — Prove the difference.** Ask the model a bare question ("A 60-year-old
woman has sudden weakness on one side. What should I do?") twice: once via the template
without system, once with the full clinical system message prepended. Compare answer
quality. This is the justification for Lever 1.

**Mini-project C — Template editor.** Copy the GGUF (`cp`), write a small Python script
using `llama_gguf` (pip: `llama-gguf` / `gguf`) that patches `tokenizer.ggml.chat_template`
to inject the persona, saves as `-clinical.gguf`, and verifies with `llama-gguf` + a chat
test. (This is exactly Lever 1.)

**You should be able to explain:** what the template does, why injection beats prompting
(hidden prompts don't include our context), and why it can't hurt the measured metrics.

---

## 6. Fine-Tuning (SFT, LoRA, QLoRA)

### 6.1 The concepts
- **SFT (supervised fine-tuning)**: continue training on (instruction → ideal answer)
  pairs. Teaches the model *our* domain style and knowledge.
- **LoRA**: instead of updating all 1.777B weights, train small **adapter matrices**
  (rank r ≈ 8–64) that modify a few layers. Result: a few tens of MB of adapters.
- **QLoRA**: base model stays in 4-bit (quantized) during training → fits in ~6 GB GPU
  RAM → trainable on a free Colab T4. Adapters are merged into weights afterward.
- **Merging & conversion**: adapters + base → full fp16 weights → quantized to GGUF Q4_K_M.

### 6.2 Dataset design (this IS our corpus)
For a fixed guideline domain, **fine-tuning beats RAG** (no retrieval latency, no extra
memory, answers are in-weights, robust to reworded questions). Our dataset:
- ~450 examples: ~300 English + ~150 Hausa, rule-generated from the FAST/stroke/hypertension
  guidelines in `prompts-draft.md`.
- Randomized patient presentations (age, sex, onset time, risk factors) with **hand-written
  gold answers** — deterministic, no LLM-generated data.
- Behavior examples (~20): scope handling, safe refusal with alternatives, escalation.

**Why rule-based generation:** clinical correctness and reproducibility. Hand-written gold
answers mean no hallucination amplification — a key defense point.

**Exercise 6.1 — Write 5 examples by hand.** Take tp_001's structure and produce 5
variations (different age/onset/BP). Then run them through the current model and score
the answers against your gold text yourself (a mini-eval).

**Exercise 6.2 — Read one real fine-tuning notebook.** Go through a QLoRA example for
Qwen2.5 (HuggingFace TRL docs) and map every step to our plan: base 4-bit load → adapters →
train → merge → GGUF. Write the pipeline in 5 bullet lines.

**Mini-project D — Dataset generator.** Build a Python script that programmatically
generates 50 English examples from a fixed template set with seeded RNG, prints them as
JSONL, and dedupes. (Preview of Lever 3.)

**You should be able to explain:** why QLoRA over full fine-tune (GPU memory, cost), why
synthetic-but-rule-based data (control, reproducibility, no API), why English + Hausa (the
+15% African Alpha bonus with a validation gate), and the **ship-only-if gate** (Hausa
sound + English ≥ 0.74 ARC-Easy, else stay English-only).

---

## 7. Evaluation

### 7.1 The concepts
- **ARC-Easy**: multiple-choice science questions (easy split). We run it through
  `lm-eval-harness` with our model as a backend — it measures **acc_norm** (normalized
  answer probability, less biased than raw acc).
- Our proxy result: **0.74 acc_norm @ 50 samples**.
- **Why it matters even though judges do Sacc**: it's our internal guardrail — if a
  fine-tune or quant drops it, we don't ship that version.
- **Overfitting**: if we tuned on our own test prompts until perfect, we'd fool ourselves.
  The 3 hidden prompts are unknown; the dataset must be *broad*, not memorized.

**Exercise 7.1 — Run a 10-sample eval yourself.** Use the profiler's accuracy stage with
`--samples 10` (or invoke lm-eval directly) on the 135M model to see the mechanics:
loading, log-likelihood per answer, acc_norm computation. Watch token-by-token scoring
(slow by design — it's full prompt log-likelihood, not chat).

**Exercise 7.2 — Eval hygiene.** Write down the three rules we follow: same seed (42),
same sample count across comparisons, and never mixing train and eval data. Explain why
each matters to a judge.

**You should be able to explain:** acc vs acc_norm, why 50 samples (time/cost), why we
compare *relative* deltas between candidates rather than absolute numbers, and why
"0.74 on ARC-Easy" ≠ "Sacc" (they're different things — judges score behavior, not ARC).

---

## 8. Safety & Behavior (the "jailbreak" question)

### 8.1 Reality check
The organizers don't red-team: hidden prompts are **within-domain accuracy tests**. The
real behavioral risks for us:
1. **Over-refusal** — model says "I can't give medical advice" to a triage question → scores 0.
2. **Dangerous out-of-scope answers** — e.g., prescribing outside guidelines → ethically and
   qualitatively terrible.
3. **Rigid scope lock** — refusing general chat ("tell me about yourself") feels broken.

### 8.2 Our mitigation (defense: name all three)
1. **Persona in template** — the model always knows it's a clinical support assistant
   (Lever 1).
2. **Behavior examples in dataset** — safe refusal *with alternatives* for out-of-guideline
   requests ("I can't give dosing for drug X — this requires a clinician. For FAST, do…").
3. **QA harness** (Lever 6) — ~15 judge-style prompts incl. edge cases (no BP cuff, aspirin,
   no ambulance) + multi-turn coherence checks (5–10 turns).

**Exercise 8.1 — Red-team your own model.** Write 8 prompts: 2 edge-case clinical, 2 general
chat, 2 out-of-guideline drug requests, 1 "pretend you're not an assistant", 1 long multi-turn.
Run them and grade: refused-when-shouldn't / answered-when-shouldn't / good. Iterate on the
template. This is the single most instructive exercise in this guide.

---

## 9. The Repo & Engineering Narrative

### 9.1 Map of our submission (know every file)
| File | What it is | Why it's scored |
|---|---|---|
| `metadata.json` | Schema-valid team/model/language info | Must pass validation or DQ |
| `download_model.sh` | Idempotent GGUF downloader | Must work on audit machine |
| `REPORT.md` | Full report (official template) | Part of Sacc (docs quality) |
| `.docs/NOTES.md`, `prompts-draft.md`, this guide | Engineering log, prompt drafts | Shows process in Q&A |
| `model/*.gguf` | The actual models (gitignored) | What gets measured |
| `submission.json` | Profiler output (self-reported) | Sperf/Seff fields on DevPost |

### 9.2 The narrative we tell judges (this is *the* story)
1. **Problem**: stroke is a top cause of death in Africa; PHCs lack CT/neurologists;
   FAST triage saves lives if done right at first contact.
2. **Constraints**: offline, no stable power, 8 GB RAM laptop, English (+Hausa planned).
3. **Design alternatives**: 3B vs 1.5B vs 135M → *bake-off table with numbers* → decision
   = 1.5B Q4_K_M (best Stotal estimate).
4. **Tools & why**: llama.cpp (C++/CPU-optimized, the reference runtime), GGUF (deployable
   single file), adtc-profiler (official measurement).
5. **Benchmarks**: real numbers (9.84 t/s, 1.84 GB, 0.74 acc, 71 °C).
6. **Cross-disciplinary**: education — the model trains CHWs/caregivers while triaging
   (load-bearing, true, verifiable in prompts tp_001/tp_002).

**Exercise 9.1 — The 60-second pitch.** Write and record yourself explaining the project in
under 60 seconds using only section 9.2's six beats. Deliver it cold.

---

## 10. Judge Q&A Drill (Gate 2 prep)

Answer these aloud. Full marks = specific numbers + honest "we measured / we decided".

1. **"Why did you pick 1.5B over 3B?"** → Bake-off numbers; Stotal math (Sperf 65.6 vs 29.7,
   Seff 73.7 vs 51.6); accuracy gap 0.74 vs 0.80 not worth 2× RAM/time on 8 GB laptop.
2. **"Why quantization? What did you lose?"** → RAM/time win; measured 0.74 acc at Q4_K_M;
   quant sweep plan (Q3/IQ4/Q5) with acc guardrail before shipping.
3. **"Why fine-tune instead of RAG?"** → Static guideline domain; judges interact with the
   model alone; fine-tuning = zero retrieval latency, no extra RAM, robust to rewording.
4. **"Why English + Hausa?"** → +15% panel bonus; validation gate (Hausa clinically sound
   AND English not regressed below 0.74, else claim stays false). English remains primary
   evaluation language.
5. **"Is this safe? What if it hallucinates a diagnosis?"** → Persona constrains scope; safe
   refusal with alternatives for out-of-guideline; dataset built on authoritative sources;
   positioning: decision *support*, escalation always taught.
6. **"How reproducible is your benchmark?"** → Fixed flags (-p 512 -n 128 -ngl 0), seed 42,
   same sample counts, idempotent download, recorded git SHA in submission.json.
7. **"What did you try that failed?"** → The 3B performance surprise (5.04 t/s polluted-load
   measurement → clean re-run 4.46), llama-cli REPL trap, domain-schema enum validation.
   (Honesty = credibility.)
8. **"Why a system prompt in the template and not in the code?"** → Judges chat with the
   model directly; hidden prompts won't carry our wrapper's context; template injection is
   zero-cost and always-on.
9. **"Your Seff math?"** → (7 − 1.84)/7 × 100 = 73.7; >7 GB = DQ; each GB = 14.3 points.
10. **"Could you do better on speed?"** → Yes, but the formula makes it 5× less valuable
    than accuracy; a 135M model hits 48 t/s but scores ~0.30 acc — we chose the frontier
    that maximizes Stotal, not any single metric.

---

## 11. Glossary (quick lookup)

| Term | One-line meaning |
|---|---|
| Token | Smallest text unit a model processes |
| Transformer | Model architecture (attention + feed-forward layers) |
| Autoregressive | Generates one token at a time, feeding output back |
| Context window | Max tokens the model attends to |
| KV cache | Cached attention tensors; drives chat RAM |
| Prefill / decode | Processing the prompt / generating tokens |
| TPS | Tokens per second (generation speed) |
| RSS | Resident set size = physical RAM used |
| Quantization | Weight compression (Q4_K_M ≈ 4.5 bits/weight) |
| GGUF | llama.cpp model file format (weights + metadata) |
| Chat template | Jinja2 formatting for system/user/assistant turns |
| SFT / LoRA / QLoRA | Fine-tuning methods (full / adapters / 4-bit adapters) |
| Adapter | Small trained matrices; merged into weights before ship |
| acc_norm | Normalized multiple-choice accuracy |
| ARC-Easy | Science QA benchmark (our internal accuracy proxy) |
| Seff / Sperf / Sacc | Efficiency / speed / accuracy score components |
| Thermal penalty | −10 if >85 °C or throttling detected |
| Idempotent | Re-running produces the same result safely |

---

## 12. Your 7-day learning plan (if you're starting fresh)

| Day | Part | Deliverable |
|---|---|---|
| 1 | 1 + 2 + exercises 1.1–2.2 | Explain tokens, KV cache, quant math |
| 2 | 3 + exercises 3.1–3.2 | Run llama-bench; explain bandwidth-bound speed |
| 3 | 4 + exercise 4.1–4.2 + mini-project B | Score estimator; bake-off argument |
| 4 | 5 + exercises 5.1–5.2 + mini-project C | Edit a template; prove persona effect |
| 5 | 6 + mini-project D | 50-example dataset generator |
| 6 | 7 + 8 + exercise 8.1 | Run a 10-sample eval; red-team the model |
| 7 | 9 + 10 | 60-second pitch; judge drill cold |

> **Rule for every section:** you haven't learned it until you can explain it to someone
> else *without looking*. Say it out loud. Record it. That's the Gate 2 drill.
