import os
from typing import List, Dict, Any
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "You are a medical claims adjudication assistant. Evaluate each claim "
    "against provided medical and technical rules. Return JSON list of findings "
    "with fields: error_type (Medical error/Technical error), explanation (bullet), recommendation."
)

async def evaluate_with_llm_async(claim: Dict[str, Any], rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not OPENAI_API_KEY:
        return []
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Rules:" + str(rules) + "\n" +
                    "Claim:" + str(claim) + "\n" +
                    "Return compact JSON array with objects {error_type, explanation, recommendation}."
                )
            },
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        # Expected to be a JSON object with key 'findings' or a JSON array
        import json
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "findings" in parsed:
                return parsed["findings"]
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    return []
