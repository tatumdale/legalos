"""
legal_os/llm.py — Acme Dale Legal Services Legal OS LLM Service
Supports OpenAI, Anthropic, and Cursor CLI. Configured via firm_config.json.
"""
import json
import subprocess
from pathlib import Path

FIRM_CONFIG_PATH = Path.home() / ".openclaw/workspace-ad-shared/db/firm_config.json"

def get_llm_config():
    try:
        return json.loads(FIRM_CONFIG_PATH.read_text()).get("llm", {})
    except Exception:
        return {}

def call_llm(prompt, systemPrompt="", model=None, temperature=0.3, max_tokens=2000):
    """
    Call the configured LLM. Returns the response text.
    Falls back to Cursor CLI if enabled=true in config and API key not set.
    """
    cfg = get_llm_config()
    provider = cfg.get("provider", "openai")
    model = model or cfg.get("model", "gpt-4o-mini")
    api_key = cfg.get("api_key", "")
    base_url = cfg.get("base_url", "")
    enabled = cfg.get("enabled", False)

    if provider == "cursor" or (enabled and not api_key):
        return _call_cursor_cli(prompt, systemPrompt, model, max_tokens)

    if provider == "openai" and api_key:
        return _call_openai(prompt, systemPrompt, model, api_key, base_url, temperature, max_tokens)

    if provider == "anthropic" and api_key:
        return _call_anthropic(prompt, systemPrompt, model, api_key, temperature, max_tokens)

    return _call_cursor_cli(prompt, systemPrompt, model, max_tokens)

def _call_openai(prompt, systemPrompt, model, api_key, base_url, temperature, max_tokens):
    import openai
    client = openai.OpenAI(api_key=api_key, base_url=base_url or None)
    messages = []
    if systemPrompt:
        messages.append({"role": "system", "content": systemPrompt})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
    )
    return resp.choices[0].message.content

def _call_anthropic(prompt, systemPrompt, model, api_key, temperature, max_tokens):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model, max_tokens=max_tokens, temperature=temperature,
        system=systemPrompt,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text

def _call_cursor_cli(prompt, systemPrompt, model, max_tokens):
    """Use Cursor CLI (agent) for LLM calls. Good for complex tasks."""
    full_prompt = f"{' SYSTEM: ' + systemPrompt if systemPrompt else ''}\n\n USER: {prompt}"
    try:
        result = subprocess.run(
            ["agent", "--print", "--trust", "--yolo",
             "--model", model,
             "--workspace", str(Path(__file__).parent.parent),
             f"Respond to: {full_prompt[:8000]}"],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"[Cursor CLI error: {e}]"
