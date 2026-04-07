"""
legal_os/research.py — Legal Research Service for AD Legal OS
Handles BAILII searches and internal precedent lookups.
"""
import urllib.request
import urllib.parse
import re
from pathlib import Path

DB_PATH = Path.home() / ".openclaw/workspace-ad-shared/db/ad_matters.db"

def search_bailii(query, max_results=5):
    """
    Search BAILII for UK case law. Returns list of {title, citation, url, snippet}.
    BAILII is free, no API key needed.
    """
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://www.bailii.org/cgi-bin/lucy_search.cgi?mode=simple&path=&query={encoded}&title=uk"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AD-Legal-OS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        results = []
        hits = re.findall(r'href="(/cgi-bin/lucy_search.cgi[^"]+)"[^>]*>([^<]+)</a>', html)
        for href, title in hits[:max_results]:
            title = title.strip()
            if title and len(title) > 5:
                citation_match = re.search(r'(\d{4}\]\s*\w+\s*\w+\s*\d+)', title)
                results.append({
                    "title": title,
                    "citation": citation_match.group(1) if citation_match else "",
                    "url": f"https://www.bailii.org{href}" if href.startswith("/") else href,
                    "source": "BAILII"
                })
        return results[:max_results]
    except Exception as e:
        return [{"error": str(e), "source": "BAILII"}]

def search_internal_precedents(query, practice_area=None, limit=5):
    """Search completed matters as precedent."""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    q = "SELECT * FROM matters WHERE status='completed'"
    args = []
    if practice_area:
        q += " AND practice_area=?"
        args.append(practice_area)
    if query:
        q += " AND (summary LIKE ? OR output LIKE ?)"
        args.extend([f"%{query}%", f"%{query}%"])
    q += " ORDER BY updated_at DESC LIMIT ?"
    args.append(limit)
    rows = conn.execute(q, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def parse_citation(citation_str):
    """Parse a legal citation like '[2024] EWCA Civ 12' into components."""
    m = re.match(r'\[(\d{4})\]\s*(\w+)\s*(\w+)\s*(\d+)', citation_str)
    if m:
        return {"year": m.group(1), "court": m.group(2), "type": m.group(3), "number": m.group(4)}
    return {}
