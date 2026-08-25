"""Deterministic hybrid routing for VECTOR Afya.

User-selected modes are the preferred path. Auto-detect uses lightweight keyword
scoring and never calls the language model merely to classify a request.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

CLINICAL = "clinical_information"
MEDICAL_QA = "medical_qa"
TRIAGE = "triage_support"
PATIENT = "patient_education"
AUTO = "auto_detect"

MODES = {
    CLINICAL: "Clinical Information",
    MEDICAL_QA: "Medical Q&A",
    TRIAGE: "Triage Support",
    PATIENT: "Patient Education",
}

@dataclass(frozen=True)
class Route:
    category: str
    label: str
    confidence: str
    reason: str

TRIAGE_TERMS = {
    "chest pain", "difficulty breathing", "shortness of breath", "can't breathe",
    "cannot breathe", "severe bleeding", "unconscious", "fainted", "seizure",
    "stroke", "sudden weakness", "facial droop", "severe allergic", "anaphylaxis",
    "poisoning", "overdose", "suicidal", "severe burns", "heavy bleeding",
}
NURSING_TERMS = {"nurse", "nursing", "student nurse", "nursing student", "care plan", "nursing assessment"}
PATIENT_TERMS = {"patient", "newly diagnosed", "diagnosed", "explain simply", "simple language", "my blood pressure", "my symptoms"}
CLINICAL_TERMS = {"causes", "signs and symptoms", "pathophysiology", "clinical", "differential", "risk factors", "physiology", "mechanism"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def validate_category(category: str) -> str:
    category = category.strip().lower()
    aliases = {
        "clinical": CLINICAL, "clinical information": CLINICAL,
        "medical": MEDICAL_QA, "medical q&a": MEDICAL_QA, "medical qa": MEDICAL_QA,
        "triage": TRIAGE, "triage support": TRIAGE, "urgent symptoms": TRIAGE,
        "patient": PATIENT, "patient education": PATIENT,
        "auto": AUTO, "auto-detect": AUTO, "auto detect": AUTO,
    }
    if category in MODES or category == AUTO:
        return category
    if category in aliases:
        return aliases[category]
    raise ValueError(f"Unknown category: {category}")


def _score(text: str, terms: set[str]) -> int:
    return sum(1 for term in terms if term in text)


def route(question: str, selected: str = AUTO) -> Route:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    selected = validate_category(selected)
    if selected != AUTO:
        return Route(selected, MODES[selected], "explicit", "User-selected category")

    text = normalize(question)
    triage = _score(text, TRIAGE_TERMS)
    nursing = _score(text, NURSING_TERMS)
    patient = _score(text, PATIENT_TERMS)
    clinical = _score(text, CLINICAL_TERMS)

    if triage:
        return Route(TRIAGE, MODES[TRIAGE], "high", "Urgent-symptom language detected")
    if nursing > 0:
        return Route(CLINICAL if clinical > 0 else MEDICAL_QA, MODES[CLINICAL if clinical > 0 else MEDICAL_QA], "medium", "Clinical/nursing terminology detected")
    if patient > 0:
        return Route(PATIENT, MODES[PATIENT], "medium", "Patient-facing language detected")
    if clinical > 0:
        return Route(CLINICAL, MODES[CLINICAL], "medium", "Clinical terminology detected")
    return Route(MEDICAL_QA, MODES[MEDICAL_QA], "low", "No strong category signal; defaulted to Medical Q&A")
