"""
Naive baseline: what you'd get from a single generic prompt with none of
drafter.py's grounding/safety/tone rules. This exists purely to give the
evaluation something honest to compare against — per the brief's
requirement for "baseline: time and quality under manual process or
simple ChatGPT use."
"""
import json
from lead_drafter.config import config

NAIVE_PROMPT = (
    "Write a personalized outreach email and SMS for this lead. "
    "Return JSON with keys email_draft and sms_draft."
)


def _build_naive_content(lead_data: dict) -> str:
    # Give baseline the same sender identity access as the real system --
    # a real person doing "simple ChatGPT use" would type their company
    # name into the prompt too. Keeps the comparison isolating what the
    # system's specific grounding/safety/tone RULES contribute, not just
    # "does it happen to know your company name."
    content = f"{NAIVE_PROMPT}\n\nLead: {json.dumps(lead_data)}"
    if config.company_name or config.sender_name:
        identity = {"company_name": config.company_name, "sender_name": config.sender_name}
        content += f"\n\nSender: {json.dumps(identity)}"
    return content


def draft_naive(lead_data: dict) -> dict:
    content = _build_naive_content(lead_data)
    if config.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        resp = client.messages.create(
            model=config.llm_model,
            max_tokens=500,
            messages=[{"role": "user", "content": content}],
        )
        text = resp.content[0].text.strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    elif config.llm_provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=config.gemini_api_key)
        resp = client.models.generate_content(
            model=config.llm_model,
            contents=content,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = resp.text.strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    else:
        from openai import OpenAI
        client = OpenAI(api_key=config.openai_api_key)
        resp = client.chat.completions.create(
            model=config.llm_model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
