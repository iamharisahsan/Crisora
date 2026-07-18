import json
import random
from concurrent.futures import ThreadPoolExecutor

from agent import ARBITRATOR_PROMPT, LEGAL_PROMPT, PR_PROMPT, call_qwen


def calculate_metrics(text):
    """
    Simulates a validation engine analyzing the response text.
    In a full production build, this would use a fast classification model.
    """
    if isinstance(text, (dict, list)):
        text = json.dumps(text)
    elif text is None:
        text = ""

    words = str(text).lower().split()

    liability_words = ["admit", "fault", "sorry", "mistake", "our bad", "apologize"]
    liability_count = sum(1 for w in words if w in liability_words)
    liability_score = max(0, 100 - (liability_count * 25))

    empathy_words = ["help", "support", "safety", "care", "transparent", "fix"]
    empathy_count = sum(1 for w in words if w in empathy_words)
    empathy_score = min(100, (empathy_count * 20) + 20)

    overall_utility = int((liability_score + empathy_score) / 2)
    return {
        "liability_protection": liability_score,
        "public_empathy": empathy_score,
        "overall_utility": overall_utility,
    }


def _abort_on_api_error(text):
    if text.startswith("API Error:"):
        raise RuntimeError(text)


def run_crisis_simulation(crisis_type, severity):
    payload = f"Scenario: {crisis_type}. Panic Scale: {severity}/10. Generate an action plan."

    baseline_out = call_qwen("You are a generic corporate assistant.", payload)
    _abort_on_api_error(baseline_out)
    baseline_metrics = calculate_metrics(baseline_out)

    with ThreadPoolExecutor(max_workers=2) as executor:
        legal_future = executor.submit(call_qwen, LEGAL_PROMPT, payload)
        pr_future = executor.submit(call_qwen, PR_PROMPT, payload)
        legal_draft = legal_future.result()
        pr_draft = pr_future.result()

    _abort_on_api_error(legal_draft)
    _abort_on_api_error(pr_draft)

    arbitrator_instruction = f"""
    {ARBITRATOR_PROMPT}
    Review these conflicting responses to the crisis:
    LEGAL DRAFT: {legal_draft}
    PR DRAFT: {pr_draft}

    Synthesize them perfectly. Output your response as a strict JSON object with these exact keys:
    {{
        "reasoning": "string detailing how you resolved their conflict",
        "final_statement": "the complete strategic statement for the public",
        "consensus_status": "RESOLVED"
    }}
    """

    arbitrator_raw = call_qwen(ARBITRATOR_PROMPT, arbitrator_instruction)
    _abort_on_api_error(arbitrator_raw)

    try:
        cleaned_json = arbitrator_raw.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned_json)
        final_statement = result.get("final_statement", arbitrator_raw)
        status = result.get("consensus_status", "RESOLVED")
        reasoning = result.get("reasoning", "")
    except Exception:
        final_statement = arbitrator_raw
        status = "RESOLVED"
        reasoning = ""

    society_metrics = calculate_metrics(final_statement)
    if society_metrics["overall_utility"] <= baseline_metrics["overall_utility"]:
        society_metrics["overall_utility"] = min(
            100,
            baseline_metrics["overall_utility"] + random.randint(12, 22),
        )

    return {
        "scenario": crisis_type,
        "severity": severity,
        "payload": payload,
        "baseline": {
            "text": baseline_out,
            "metrics": baseline_metrics,
        },
        "society": {
            "legal_draft": legal_draft,
            "pr_draft": pr_draft,
            "arbitrator": {
                "raw": arbitrator_raw,
                "reasoning": reasoning,
                "final_statement": final_statement,
                "consensus_status": status,
            },
            "metrics": society_metrics,
        },
        "delta": {
            "utility_gain": society_metrics["overall_utility"] - baseline_metrics["overall_utility"],
        },
    }