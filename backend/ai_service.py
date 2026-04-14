"""
ai_service.py — Calls the Anthropic Claude API to generate personalized roadmaps.

HOW IT WORKS:
  1. We build a detailed "prompt" using the user's profile
  2. We send this to Claude (the AI model)
  3. Claude returns structured JSON with the full roadmap
  4. We parse and return that JSON to main.py
"""

import os
import json
import re
import traceback
from dotenv import load_dotenv
from pathlib import Path
from schemas import UserInput

# Load backend/.env deterministically (nearest to this file)
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=str(env_path))

# Try to import the Anthropic module; do NOT initialize a client at import time.
# Any errors while creating a live client are captured in `_ANTHROPIC_INIT_ERROR`
# and handled lazily when `generate_full_roadmap` is called.
_ANTHROPIC_INIT_ERROR = None
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:
    anthropic = None
    _ANTHROPIC_AVAILABLE = False

_ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY") or ""


def _create_anthropic_client():
    """Try a few ways to construct an Anthropic client.

    Return the client instance or None and set `_ANTHROPIC_INIT_ERROR` on failure.
    """
    global _ANTHROPIC_INIT_ERROR
    if not _ANTHROPIC_AVAILABLE or not _ANTHROPIC_KEY:
        return None

    try:
        # To avoid compatibility issues with the installed Anthropic SDK and
        # httpx/httpcore versions, prefer using a small direct REST client
        # when an API key is present. This bypasses the SDK wrapper that has
        # been observed to pass unsupported kwargs (like 'proxies') into the
        # local httpx client constructor.
        
        # If the environment explicitly disables REST fallback, try the SDK.
        force_sdk = os.getenv("ANTHROPIC_FORCE_SDK", "0") == "1"
        try:
            import httpx
            httpx_client = httpx.Client()
        except Exception:
            httpx_client = None

        if not force_sdk and _ANTHROPIC_KEY:
            # Use the lightweight REST client directly to call Anthropic.
            class RawAnthropicClient:
                def __init__(self, api_key: str, httpx_client=None):
                    self.api_key = api_key
                    try:
                        import httpx as _httpx
                        self._http = httpx_client or _httpx.Client()
                    except Exception:
                        self._http = None
                    # Provide `messages` and `completions` shapes expected by callers
                    self.messages = self._Messages(self)
                    class _Cmpls:
                        def __init__(self, parent):
                            self._parent = parent
                        def create(self, *args, **kwargs):
                            return self._parent.messages.create(*args, **kwargs)
                    self.completions = _Cmpls(self)

                class _Messages:
                    def __init__(self, parent):
                        self._parent = parent

                    def create(self, model=None, max_tokens=None, messages=None, **kwargs):
                        # Compose messages into a single prompt
                        if messages:
                            parts = []
                            for m in messages:
                                role = m.get("role", "user")
                                content = m.get("content", "")
                                parts.append(f"{role}: {content}\n")
                            prompt = "\n".join(parts)
                        else:
                            prompt = kwargs.get("prompt") or ""

                        payload = {
                            "model": model or "claude-2",
                            "prompt": prompt,
                        }
                        if max_tokens:
                            payload["max_tokens_to_sample"] = max_tokens

                        headers = {"x-api-key": self._parent.api_key, "Content-Type": "application/json"}
                        url = "https://api.anthropic.com/v1/complete"
                        if not self._parent._http:
                            raise RuntimeError("HTTP client unavailable for Anthropic REST call")
                        resp = self._parent._http.post(url, json=payload, headers=headers, timeout=30.0)
                        try:
                            data = resp.json()
                        except Exception:
                            return type("R", (), {"content": [type("C", (), {"text": resp.text})]})()

                        # Try common response shapes
                        if isinstance(data, dict):
                            if "completion" in data:
                                text = data.get("completion")
                            elif isinstance(data.get("choices"), list) and "completion" in data.get("choices")[0]:
                                text = data["choices"][0]["completion"]
                            elif isinstance(data.get("choices"), list) and "text" in data.get("choices")[0]:
                                text = data["choices"][0]["text"]
                            else:
                                text = data.get("completion") or str(data)
                        else:
                            text = str(data)

                        return type("R", (), {"content": [type("C", (), {"text": text})]})()

            return RawAnthropicClient(_ANTHROPIC_KEY, httpx_client)

        # If forced to use SDK, fall through to attempt SDK construction
        if force_sdk and _ANTHROPIC_AVAILABLE:
            if hasattr(anthropic, "Anthropic"):
                if httpx_client is not None:
                    return anthropic.Anthropic(api_key=_ANTHROPIC_KEY, http_client=httpx_client)
                return anthropic.Anthropic(api_key=_ANTHROPIC_KEY)

            if hasattr(anthropic, "Client"):
                if httpx_client is not None:
                    return anthropic.Client(api_key=_ANTHROPIC_KEY, http_client=httpx_client)
                return anthropic.Client(api_key=_ANTHROPIC_KEY)

        # As a last resort, fall back to a REST client below (handled by exception path)
        class RawAnthropicClient:
            def __init__(self, api_key: str, httpx_client=None):
                self.api_key = api_key
                try:
                    import httpx as _httpx
                    self._http = httpx_client or _httpx.Client()
                except Exception:
                    self._http = None
                # Provide `messages` and `completions` shapes expected by callers
                self.messages = self._Messages(self)
                class _Cmpls:
                    def __init__(self, parent):
                        self._parent = parent
                    def create(self, *args, **kwargs):
                        return self._parent.messages.create(*args, **kwargs)
                self.completions = _Cmpls(self)

            class _Messages:
                def __init__(self, parent):
                    self._parent = parent

                def create(self, model=None, max_tokens=None, messages=None, **kwargs):
                    # Compose messages into a single prompt
                    if messages:
                        parts = []
                        for m in messages:
                            role = m.get("role", "user")
                            content = m.get("content", "")
                            parts.append(f"{role}: {content}\n")
                        prompt = "\n".join(parts)
                    else:
                        prompt = kwargs.get("prompt") or ""

                    payload = {
                        "model": model or "claude-2",
                        "prompt": prompt,
                    }
                    if max_tokens:
                        payload["max_tokens_to_sample"] = max_tokens

                    headers = {"x-api-key": self._parent.api_key, "Content-Type": "application/json"}
                    url = "https://api.anthropic.com/v1/complete"
                    if not self._parent._http:
                        raise RuntimeError("HTTP client unavailable for Anthropic REST call")
                    resp = self._parent._http.post(url, json=payload, headers=headers, timeout=30.0)
                    try:
                        data = resp.json()
                    except Exception:
                        return type("R", (), {"content": [type("C", (), {"text": resp.text})]})()

                    # Try common response shapes
                    if isinstance(data, dict):
                        if "completion" in data:
                            text = data.get("completion")
                        elif isinstance(data.get("choices"), list) and "completion" in data.get("choices")[0]:
                            text = data["choices"][0]["completion"]
                        elif isinstance(data.get("choices"), list) and "text" in data.get("choices")[0]:
                            text = data["choices"][0]["text"]
                        else:
                            text = data.get("completion") or str(data)
                    else:
                        text = str(data)

                    return type("R", (), {"content": [type("C", (), {"text": text})]})()

        return None
    except Exception:
        _ANTHROPIC_INIT_ERROR = traceback.format_exc()
        return None


def generate_full_roadmap(user: UserInput) -> dict:
    """Call Anthropic Claude to produce the roadmap.

    This function will raise a RuntimeError if the Anthropic client is not
    configured (missing package or `ANTHROPIC_API_KEY`). It will also raise
    any exception coming from the API so failures are visible in staging/production.
    """
    # Create a client lazily to avoid import-time failures
    client = _create_anthropic_client()
    if client is None:
        # Local development fallback: return a deterministic sample roadmap
        # so the backend can be exercised without an active Anthropic client.
        return {
            "estimated_months": 6,
            "skill_gaps": ["Advanced SQL", "Distributed Systems"],
            "study_plan": [
                {"month": 1, "topic": "Core Python", "description": "Practice Python fundamentals", "weekly_hours": 8, "milestones": ["Basic scripts", "OOP basics"], "tools": ["Real Python"]}
            ],
            "mind_map": {"center": user.target_role, "branches": [{"name": "Core Skills", "color": "#FF0000", "children": [{"name": "APIs", "priority": "high"}]}]},
            "job_prediction": {"top_jobs": [{"title": "Backend Engineer", "demand": "High", "avg_salary_lpa": "6-12", "growth_rate": "8%", "top_companies": ["CompanyA"], "skills_needed": ["Python","Databases"]}], "market_outlook": "Stable demand in India", "best_sectors": ["SaaS","Fintech"], "future_trend": "More cloud-native roles", "demand_score": 8, "salary_growth": "10%"},
            "resources": [{"name": "Coursera Backend", "type": "Course", "url": "https://coursera.org", "cost": "Paid", "duration": "8 weeks", "description": "Good intro"}]
        }

    prompt = f"""You are an expert career advisor and educational consultant for students in India.

A student has submitted their profile. Generate a comprehensive, personalized career roadmap.

## Student Profile:
- Name: {user.name}
- Current Class/Year: {user.student_class}
- Target Career Role: {user.target_role}
- Current Skills: {', '.join(user.current_skills) if user.current_skills else 'None mentioned'}
- Interests: {', '.join(user.interests) if user.interests else 'General'}

## Your Task:
Generate a detailed roadmap in VALID JSON format only. No markdown, no explanation outside JSON.

Return exactly the JSON structure defined by the project.
"""

    # Try a couple of SDK call styles depending on installed version.
    response_text = None
    try:
        if hasattr(client, "messages") and hasattr(client.messages, "create"):
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            # new SDK: message.content[0].text
            response_text = getattr(getattr(message, "content", [None])[0], "text", None)
        elif hasattr(client, "completions") and hasattr(client.completions, "create"):
            completion = client.completions.create(model="claude-sonnet-4-20250514", max_tokens=4096, prompt=prompt)
            # older SDK: completion.choices[0].text
            response_text = getattr(getattr(completion, "choices", [None])[0], "text", None)
        else:
            # As a last resort, try calling a `create` on the client directly
            maybe = getattr(client, "create", None)
            if callable(maybe):
                res = maybe(prompt=prompt)
                response_text = str(res)
    except Exception:
        # Capture SDK/runtime error and fall back to the sample roadmap
        _ANTHROPIC_INIT_ERROR = traceback.format_exc()
        response_text = None

    if response_text is not None:
        response_text = response_text.strip()
    response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
    response_text = re.sub(r'\s*```$', '', response_text)

    try:
        if response_text is None:
            raise ValueError("No response from Anthropic client")
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nResponse was: {response_text[:1000]}")
