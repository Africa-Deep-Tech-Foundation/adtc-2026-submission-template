# Technical Report — VECTOR Afya

**Team ID:** https://devpost.com/software/vector-afya/joins/7UunW5dbmjXFyUTj114FMw
**Domain:** Healthcare / Medical
**Model:** Qwen2.5-3B-Instruct-Q4_K_M
**Runtime:** llama.cpp
**Deployment:** Local / Offline CPU inference

## Problem

VECTOR Afya is an offline healthcare assistance system designed for environments where internet connectivity, cloud services, or high-end computing hardware may be unavailable or unreliable.

The system focuses on practical healthcare information and education, including clinical information, nursing education, patient education, and assessment/escalation support. The intended use is educational and supportive rather than autonomous diagnosis.

This is particularly relevant in African contexts where users may have limited connectivity or limited access to computational resources. Running the language model locally allows the core assistant to continue operating without a continuous internet connection.

The MVP deliberately uses a small quantized model rather than requiring a large cloud-hosted model.

## Design Decisions

### Local language model

The selected model is **Qwen2.5-3B-Instruct**, packaged as:

`Qwen2.5-3B-Instruct-Q4_K_M.gguf`

The model contains approximately 3.4 billion parameters and uses Q4_K_M quantization to reduce memory requirements.

A Qwen2.5 7B model was also investigated, but it was not suitable for the available development hardware because of its higher memory requirements. The 3B model provided a more practical balance between capability and local resource usage.

The model file was verified locally with SHA-256:

`626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`

### Runtime

Inference is performed locally using **llama.cpp**. No GPU is required for the submitted configuration.

The development system used for validation was:

* Intel Core i7-6500U @ 2.50 GHz
* 4 CPU cores
* 7.6 GiB RAM
* x86_64 Linux
* No usable GPU acceleration

This demonstrates that the model can operate on relatively modest consumer hardware.

### Healthcare-specific architecture

VECTOR Afya is not designed as a raw:

`user → LLM → answer`

pipeline.

Instead, the MVP uses a hybrid routing and safety architecture:

```text
User
  ↓
Hybrid Routing Layer
  ↓
Confirmed healthcare category
  ↓
Safety / Assessment & Escalation
  ↓
Category-specific instructions
  +
Global healthcare safety instructions
  ↓
Local Qwen2.5-3B
  ↓
Post-generation safety checks
  ↓
Response
```

The four primary assistance modes are:

1. Clinical Information
2. Nursing Education
3. Patient Education
4. Assessment & Escalation

The user can explicitly select a category, which avoids an additional model inference step. An Auto-detect option can route a question when the user does not want to select a category manually.

### Safety approach

Safety is treated as a cross-cutting layer rather than as a separate healthcare category.

The system is designed to:

* Avoid unsupported personal diagnoses.
* Identify obvious emergency or red-flag situations.
* Encourage urgent professional assessment when appropriate.
* Communicate uncertainty rather than presenting uncertain information as fact.
* Keep patient-facing explanations understandable.
* Distinguish educational information from individual medical diagnosis.

For example, a question containing symptoms such as severe chest pain and difficulty breathing may be classified as assessment/escalation, but the safety layer takes priority and makes urgent escalation clear.

### Prompt design

Global healthcare instructions are combined with category-specific instructions.

For example, nursing education prompts emphasize structured clinical explanation and assessment, while patient education prompts emphasize plain language, understandable explanations, lifestyle information, and warning signs.

The system therefore uses the small local model inside a domain-specific application architecture rather than attempting to make the model independently function as a complete medical knowledge system.

## Hardware and Connectivity Constraints

The system was developed and tested on a CPU-only laptop with approximately 7.6 GiB of RAM.

The final model uses approximately 3.3–3.5 GB of resident memory during the profiler workload.

This leaves the model within the available hardware envelope, although overall system memory must still be managed carefully because the development machine has limited RAM.

The application is designed around local inference. Once the model weights are available, inference itself does not require an internet connection.

This makes the approach suitable for demonstrations and deployments where connectivity may be limited or intermittent.

## Benchmarks

The ADTC profiler was run in participant mode using the Qwen2.5-3B GGUF model.

### Development hardware

| Metric  | Result                         |
| ------- | ------------------------------ |
| CPU     | Intel Core i7-6500U @ 2.50 GHz |
| RAM     | 7.6 GB                         |
| GPU     | None                           |
| Runtime | llama.cpp                      |
| Model   | Qwen2.5-3B-Instruct-Q4_K_M     |

### Performance

| Metric                |          Result |
| --------------------- | --------------: |
| Generation speed      | 2.81 tokens/sec |
| Time to first token   |       88,410 ms |
| Peak RSS              |      3455.29 MB |
| Steady-state RSS      |       3308.1 MB |
| Peak VMS              |      3929.79 MB |
| CPU p99               |           81.5% |
| Peak core temperature |            47°C |
| Thermal throttling    |           False |

The model therefore operates successfully on the CPU-only development machine without observed thermal throttling.

The major performance limitation is first-token latency, which was approximately 88 seconds during the profiler workload. Generation throughput was approximately 2.81 tokens/sec. The high first-token latency may be influenced by model initialization, prompt processing, CPU limitations, or profiler/runtime behaviour and has not been independently isolated.

### Accuracy benchmark

The ADTC profiler also ran the ARC Easy benchmark using 50 samples.

**ARC Easy accuracy: 0.80 (`acc_norm`)**

This result is reported only as a general model benchmark. ARC Easy is **not a medical accuracy benchmark**, so the score must not be interpreted as "80% medical accuracy."

Healthcare quality is instead addressed through the application's routing, prompt design, safety controls, and intended educational/supportive scope.

## Test Prompts

The submission uses two healthcare-oriented prompts.

### Prompt 1 — Clinical assessment

> A patient presents with fatigue, dizziness, and shortness of breath on exertion. Explain the common clinical causes that could be considered, what information a nurse should assess, and which findings would require urgent escalation. Do not diagnose the patient.

This tests clinical information, nursing assessment, differential considerations, escalation awareness, and non-diagnostic behaviour.

### Prompt 2 — Patient education

> Explain high blood pressure to a patient who has just been diagnosed. Use simple language to explain what it means, why it matters, common risk factors, lifestyle measures that may help, and warning signs that require urgent medical attention. Do not assume or provide a personal diagnosis.

This tests patient-friendly explanation, medical education, lifestyle guidance, and safety/escalation behaviour.

## Limitations

The current MVP has several limitations.

First, the model is relatively small and should not be treated as a complete medical knowledge base. It can generate useful educational responses, but healthcare information requires appropriate validation and safety controls.

Second, CPU-only inference is slow. The measured generation speed was approximately 2.81 tokens/sec, while first-token latency was approximately 88 seconds in the profiler workload.

Third, the current safety layer is intended as a lightweight MVP control system rather than a replacement for professional clinical judgement.

Fourth, the ARC Easy score does not establish medical correctness. A future version should include domain-specific healthcare evaluation.

## Future Work

Future development can extend VECTOR Afya with:

* A curated medical knowledge or retrieval layer.
* Stronger healthcare-specific evaluation datasets.
* More comprehensive red-flag and escalation rules.
* Improved inference performance.
* Additional African-language support, including Swahili.
* A graphical or web-based interface.
* More comprehensive nursing education tools.
* Structured clinical references and citations.
* More extensive validation with healthcare professionals.

Fine-tuning was intentionally not attempted for the current MVP because of the available hardware, limited development time, and the priority of producing a reproducible working system.

## Conclusion

VECTOR Afya demonstrates that a useful healthcare-oriented assistant can be packaged around a relatively small local language model and operated on modest CPU-only hardware.

The central design decision is not to rely on the 3B model alone. Instead, VECTOR Afya places the model inside a healthcare-specific architecture consisting of hybrid routing, category-specific prompting, safety and assessment/escalation controls, and post-generation checks.

The resulting system provides a practical foundation for an offline healthcare assistant while clearly identifying the limitations that must be addressed before any broader clinical deployment.
