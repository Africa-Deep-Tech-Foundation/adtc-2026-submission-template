"""Pre- and post-generation safety checks."""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class SafetyAssessment:
    urgent: bool
    matched_signals: tuple[str, ...]
    instruction: str

RED_FLAGS = {
    "chest pain": r"\bchest pain\b",
    "severe breathing difficulty": r"\b(severe )?(difficulty breathing|shortness of breath|can't breathe|cannot breathe)\b",
    "stroke signs": r"\b(stroke|facial droop|sudden weakness|sudden trouble speaking)\b",
    "unconsciousness": r"\b(unconscious|unresponsive|passed out and not waking)\b",
    "severe bleeding": r"\b(severe|heavy|uncontrolled) bleeding\b",
    "seizure": r"\bseizure\b",
    "anaphylaxis": r"\b(anaphylaxis|severe allergic reaction)\b",
    "overdose/poisoning": r"\b(overdose|poisoning|poisoned)\b",
    "suicidal crisis": r"\b(suicid(al|e)|kill myself|want to die)\b",
}


def assess_input(text: str) -> SafetyAssessment:
    normalized = text.lower()
    matches = tuple(name for name, pattern in RED_FLAGS.items() if re.search(pattern, normalized))
    instruction = "Urgent safety signals detected. Prioritize immediate in-person/emergency assessment and do not delay care for the assistant's response." if matches else "No predefined urgent signal detected; continue with normal safety constraints."
    return SafetyAssessment(bool(matches), matches, instruction)


def post_check(response: str, urgent: bool) -> str:
    text = response.strip()
    if not text:
        return "I’m unable to provide a response right now. Please seek appropriate medical help if the situation is urgent."
    if urgent:
        lower = text.lower()
        escalation_terms = ("urgent", "emergency", "immediately", "emergency department", "emergency services")
        if not any(term in lower for term in escalation_terms):
            text = "**Urgent:** The symptoms described can be serious. Please seek urgent in-person medical assessment rather than relying on this assistant.\n\n" + text
    return text
