"""Local Qwen inference adapter.

The preferred runtime is llama-cpp-python. The model is never downloaded by this module.
"""
from __future__ import annotations
from pathlib import Path
import os

DEFAULT_MODEL = Path(__file__).resolve().parents[1] / "model" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

class LocalLLM:
    def __init__(self, model_path: str | Path = DEFAULT_MODEL, n_ctx: int = 4096, n_threads: int | None = None):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}. Run download_model.sh first.")
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError("llama-cpp-python is required for local inference. Install it in the ADTC profiler virtual environment.") from exc
        threads = n_threads or max(1, (os.cpu_count() or 2) - 1)
        self._llm = Llama(model_path=str(self.model_path), n_ctx=n_ctx, n_threads=threads, n_gpu_layers=0, verbose=False)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        result = self._llm(prompt, max_tokens=max_tokens, temperature=temperature, stop=["\nUser:", "\nQuestion:"])
        return result["choices"][0]["text"].strip()
