"""Terminal MVP for VECTOR Afya."""
from __future__ import annotations
import argparse
from .router import AUTO, MODES, route
from .safety import assess_input, post_check
from .prompts import build_prompt
from .llm import LocalLLM


def choose_mode() -> str:
    options = [("1", "clinical_information"), ("2", "medical_qa"), ("3", "triage_support"), ("4", "patient_education"), ("5", AUTO)]
    print("\nHow would you like VECTOR Afya to help?\n")
    for number, key in options:
        print(f"  {number}. {MODES.get(key, 'Auto-detect')}")
    choice = input("\nSelect [1-5]: ").strip()
    return dict(options).get(choice, AUTO)


def main() -> None:
    parser = argparse.ArgumentParser(description="VECTOR Afya offline healthcare assistant")
    parser.add_argument("--mode", default=AUTO, choices=[*MODES.keys(), AUTO])
    parser.add_argument("--question")
    parser.add_argument("--model")
    parser.add_argument("--max-tokens", type=int, default=256)
    args = parser.parse_args()

    print("\nVECTOR AFYA — Offline Healthcare Assistant")
    print("Educational support only; not a diagnosis or replacement for professional care.\n")
    mode = args.mode if args.mode != AUTO or args.question else choose_mode()
    question = args.question or input("Enter your question:\n> ").strip()
    if not question:
        raise SystemExit("Question cannot be empty.")

    selected_route = route(question, mode)
    safety = assess_input(question)
    print(f"\nRouting: {selected_route.label} ({selected_route.confidence})")
    print(f"Safety: {'URGENT SIGNALS DETECTED' if safety.urgent else 'No predefined urgent signal detected'}")
    if safety.urgent:
        print(f"Signals: {', '.join(safety.matched_signals)}")

    llm = LocalLLM(args.model) if args.model else LocalLLM()
    answer = llm.generate(build_prompt(selected_route.category, question), max_tokens=args.max_tokens)
    print("\n" + post_check(answer, safety.urgent) + "\n")

if __name__ == "__main__":
    main()
