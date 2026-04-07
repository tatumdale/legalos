"""
legal_os/analyzer.py
Acme Dale Legal Services Legal OS — Contract RAG Analysis Engine

Uses OpenAI API (or compatible) to run clause-by-clause RAG analysis on contracts.
Captures real token usage and cost from API response.
"""
import json
import re
import uuid
import sqlite3
from datetime import datetime
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

# ─── Config ────────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gpt-4o-mini"          # cheap + fast, excellent legal reasoning
DEFAULT_COST_PER_1K_INPUT = 0.00015   # GPT-4o-mini input cost per token
DEFAULT_COST_PER_1K_OUTPUT = 0.0006   # GPT-4o-mini output cost per token
# Override in firm_config.json under "llm" key:
#   { "llm": { "provider": "openai", "model": "gpt-4o", "api_key": "sk-..." } }

RAG_SYSTEM_PROMPT = """You are AD-Review, a rigorous legal contract reviewer at Acme Dale Legal Services Solicitors, a UK law firm regulated by the SRA. You analyse contracts clause-by-clause and output a structured RAG (Red/Amber/Green) risk assessment.

Your RAG definitions:
- GREEN: Clause is balanced, commercially reasonable, no material risk to Acme Dale Legal Services. No action required.
- AMBER: Clause presents risk or imbalance that should be flagged and may require negotiation. Inform the client. Address before execution if time permits.
- RED: Clause presents material risk, is materially one-sided, or may be unenforceable. Do NOT execute in current form. Return with specific red-line requests.

Respond ONLY with valid JSON in this exact schema:
{
  "overall_rag": "RED" | "AMBER" | "GREEN",
  "overall_summary": "2-3 sentence risk summary for the contract as a whole",
  "clauses": [
    {
      "clause_ref": "e.g. 3.1, 4.5.2",
      "clause_name": "short name",
      "rag": "RED" | "AMBER" | "GREEN",
      "summary": "one sentence description",
      "action": "what Acme Dale Legal Services should do",
      "client_facing_note": "plain English explanation for the client"
    }
  ],
  "red_line_requests": [
    { "clause": "e.g. 5.1.2", "current": "current wording summary", "requested": "proposed change" }
  ],
  "flag_for_partner_review": true | false,
  "partner_review_reason": "reason if flagged"
}
"""


# ─── LLM Client ────────────────────────────────────────────────────────────────
def call_llm(prompt, model, api_key, base_url=None):
    """Make a chat completion API call. Returns (response_text, usage_dict)."""
    if not api_key:
        raise ValueError("No LLM API key configured. Set 'llm.api_key' in firm_config.json.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Use OpenAI-compatible endpoint
    endpoint = (base_url or "https://api.openai.com/v1") + "/chat/completions"

    req = urllib_request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )

    try:
        with urllib_request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode())
            usage = body.get("usage", {})
            content = body["choices"][0]["message"]["content"]
            return content, usage
    except HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"API error {e.code}: {error_body}") from e
    except URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e


def estimate_cost(usage, model):
    """Calculate USD cost from token usage dict."""
    i = usage.get("prompt_tokens", 0)
    o = usage.get("completion_tokens", 0)
    t = usage.get("total_tokens", i + o)

    # GPT-4o-mini pricing (fallback; adjust per model)
    cpi = 0.00015   # per input token
    cpo = 0.0006    # per output token

    if "gpt-4o" in model and "mini" not in model:
        cpi, cpo = 0.0025, 0.01
    elif "gpt-4o-mini" in model:
        cpi, cpo = 0.00015, 0.0006
    elif "gpt-4-turbo" in model:
        cpi, cpo = 0.01, 0.03
    elif "claude" in model.lower():
        # Anthropic approximate pricing
        cpi, cpo = 0.0003, 0.001

    return round(t * cpi / 1000 + (o * cpo / 1000), 6), int(i), int(o), int(t)


# ─── PDF Text Extraction ───────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF using Python's built-in capabilities.
    Handles common PDF encoding. For complex PDFs, falls back to raw text extraction.
    """

    try:
        with open(pdf_path, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    except Exception as e:
        raise RuntimeError(f"Cannot read PDF: {e}")

    # Extract text objects from PDF (BT...ET blocks)
    # This handles plain text PDFs reasonably well
    blocks = re.findall(rb"BT\s*(.*?)\s*ET", raw, re.DOTALL)
    text_parts = []

    for block in blocks:
        # Find strings in parentheses (PDF string encoding)
        strings = re.findall(rb"\(([^)]*)\)", block)
        for s in strings:
            try:
                decoded = s.decode("latin-1", errors="replace")
                # Filter out binary noise
                cleaned = "".join(c if c.isprintable() else " " for c in decoded)
                cleaned = re.sub(r"\s+", " ", cleaned).strip()
                if cleaned and len(cleaned) > 2:
                    text_parts.append(cleaned)
            except Exception:
                pass

    text = "\n".join(text_parts)

    if not text.strip():
        # Fallback: try to find all readable ASCII strings
        words = re.findall(b"[\x20-\x7e]{4,}", raw)
        text = b" ".join(words).decode("ascii", errors="replace")

    return text.strip()


# ─── RAG Analysis Runner ────────────────────────────────────────────────────────
def run_rag_analysis(contract_text, model, api_key, base_url=None):
    """
    Main entry point. Sends contract text to LLM and returns parsed RAG result.
    """
    prompt = (
        "Analyse the following contract and produce a clause-by-clause RAG assessment.\n\n"
        "CONTRACT TEXT:\n"
        "=" * 60 + "\n"
        f"{contract_text}\n"
        "=" * 60 + "\n\n"
        "Respond ONLY with valid JSON matching the schema described in your instructions."
    )

    raw_response, usage = call_llm(prompt, model, api_key, base_url)
    cost, in_tokens, out_tokens, total_tokens = estimate_cost(usage, model)

    # Parse JSON from response
    try:
        # Strip markdown code blocks if present
        cleaned = re.sub(r"```json\s*", "", raw_response.strip())
        cleaned = re.sub(r"```\s*$", "", cleaned)
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM returned invalid JSON: {e}\n\nRaw: {raw_response[:500]}") from e

    result["_meta"] = {
        "model": model,
        "input_tokens": in_tokens,
        "output_tokens": out_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost
    }

    return result


# ─── DB Update ─────────────────────────────────────────────────────────────────
def update_matter_with_analysis(db_path, matter_id, rag_result, reviewer="AD-Review (AI)"):
    """Write RAG analysis output + audit log entry to the Legal OS DB."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.now().isoformat()
    meta = rag_result.pop("_meta")

    # Update matter output field with full RAG JSON
    cur.execute(
        "UPDATE matters SET output=?, updated_at=? WHERE id=?",
        (json.dumps(rag_result), now, matter_id)
    )

    # Count RAG ratings
    red = sum(1 for c in rag_result.get("clauses", []) if c.get("rag") == "RED")
    amber = sum(1 for c in rag_result.get("clauses", []) if c.get("rag") == "AMBER")
    green = sum(1 for c in rag_result.get("clauses", []) if c.get("rag") == "GREEN")

    audit_id = str(uuid.uuid4())
    detail = (
        f"RAG analysis complete. "
        f"Overall: {rag_result.get('overall_rag')} | "
        f"RED:{red} AMBER:{amber} GREEN:{green} | "
        f"Tokens: {meta['total_tokens']} | "
        f"Cost: £{meta['cost_usd']:.4f}"
    )

    cur.execute("""
        INSERT INTO audit_log
        (id, matter_id, agent_id, action_type, detail,
         tokens_used, cost_usd, model_used, confidence_score, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        audit_id, matter_id, "AD-Review",
        "rag_analysis_completed",
        detail,
        meta["total_tokens"],
        meta["cost_usd"],
        meta["model"],
        None,
        now
    ))

    conn.commit()
    conn.close()

    return meta, {"red": red, "amber": amber, "green": green}
