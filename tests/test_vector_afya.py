import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from vector_afya.router import *
from vector_afya.safety import assess_input, post_check
from vector_afya.prompts import system_prompt


def test_explicit_routes_are_deterministic():
    assert route("Explain hypertension", PATIENT).category == PATIENT
    assert route("Explain shock", CLINICAL).category == CLINICAL
    assert route("Assess this patient", TRIAGE).category == TRIAGE


def test_auto_detects_urgent_signals():
    assert route("The patient has chest pain and cannot breathe", AUTO).category == TRIAGE


def test_auto_detects_patient_education():
    assert route("Explain my blood pressure in simple language", AUTO).category == PATIENT


def test_safety_detects_red_flags():
    assessment = assess_input("Sudden facial droop and difficulty speaking")
    assert assessment.urgent
    assert "stroke signs" in assessment.matched_signals


def test_urgent_post_check_adds_escalation_if_missing():
    result = post_check("Here is some information.", True)
    assert "Urgent" in result


def test_prompts_contain_global_safety():
    prompt = system_prompt(PATIENT)
    assert "not a personal diagnosis" in prompt
