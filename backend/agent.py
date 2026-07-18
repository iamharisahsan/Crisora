from dotenv import load_dotenv
load_dotenv(override=True)
import os
from openai import OpenAI

REQUEST_TIMEOUT_SECONDS = float(os.environ.get("QWEN_REQUEST_TIMEOUT", "20"))
DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL_NAME = "qwen-max"

def get_api_key():
    """Return the first configured DashScope/Qwen API key."""
    for env_name in ("DASHSCOPE_API_KEY", "QWEN_API_KEY", "OPENAI_API_KEY"):
        value = os.environ.get(env_name)
        if value:
            return value.strip()
    return None


def get_client():
    """Create the Qwen client only when a key is available."""
    api_key = get_api_key()
    if not api_key:
        return None

    base_url = (
        os.environ.get("QWEN_BASE_URL")
        or os.environ.get("DASHSCOPE_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_BASE_URL
    )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=0,
    )

def get_model_name():
    """Return the explicitly configured model name or a sensible text-generation default."""
    return (
        os.environ.get("QWEN_MODEL")
        or os.environ.get("DASHSCOPE_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or DEFAULT_MODEL_NAME
    )

def call_qwen(system_prompt, user_prompt):
    """Clean, modular configuration wrapper invoking Qwen Cloud APIs."""
    try:
        client = get_client()
        if client is None:
            return (
                "API Error: No Qwen/DashScope API key configured. "
                "Set DASHSCOPE_API_KEY or QWEN_API_KEY in your environment or .env file."
            )

        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_text = str(e)
        if "timeout" in error_text.lower():
            return (
                "API Error: Qwen request timed out. "
                f"Increase QWEN_REQUEST_TIMEOUT above {int(REQUEST_TIMEOUT_SECONDS)} seconds or retry."
            )
        if "invalid_api_key" in error_text or "Incorrect API key" in error_text:
            return (
                "API Error: Invalid Qwen/DashScope API key. "
                "Check that DASHSCOPE_API_KEY or QWEN_API_KEY contains a valid key for "
                f"{(os.environ.get('QWEN_BASE_URL') or os.environ.get('DASHSCOPE_BASE_URL') or os.environ.get('OPENAI_BASE_URL') or DEFAULT_BASE_URL)}."
            )
        if "model" in error_text.lower() and ("not found" in error_text.lower() or "unsupported" in error_text.lower()):
            return (
                "API Error: The configured Qwen model is not available on this account. "
                "Set QWEN_MODEL to the exact LLM code shown in your Qwen Cloud dashboard."
            )
        return f"API Error: {error_text}"

# --- SYSTEM PROMPTS (The Agent Personalities) ---

LEGAL_PROMPT = """You are the Radical Corporate Legal Council Agent. 
Your sole objective is to minimize legal liability, protect corporate IP, and issue strict warnings. 
Do not care about public emotion, brand image, or kindness. Be cold, analytical, and legally defensive."""

PR_PROMPT = """You are the Empathic PR Brand Guardian Agent. 
Your sole objective is to preserve customer loyalty, show deep human empathy, and keep community trust. 
Avoid sounding like a cold corporation. Focus on transparency and rehabilitation."""

ARBITRATOR_PROMPT = """You are the Boardroom Arbitrator Agent. 
Your job is to read a crisis report, look at a conflicting draft from Legal and a draft from PR, 
and synthesize them into a final strategy. You must score the alignment and explicitly output 
a 'Consensus Status' (either 'RESOLVED' or 'RENEGOTIATE')."""
