"""legal_os/dms.py — Legal OS DMS

# Drive root: LegalClawOS | https://drive.google.com/drive/folders/1aOipSxzKu1iuoP5w8vaQX273koOhqgKp
# Folder path: LegalClawOS / [Client Name] / [Matter Ref] — [Matter Type]
legal_os/dms.py — Acme Dale Legal Services Legal OS DMS
Google Drive-backed document management via gog CLI.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Optional

import sqlite3

BASE_DIR = Path.home() / ".openclaw" / "workspace-ad-shared"
DB_PATH = BASE_DIR / "db" / "ad_matters.db"
DRIVE_ROOT = "1aOipSxzKu1iuoP5w8vaQX273koOhqgKp"  # LegalClawOS root
TEMPLATE_DIR = BASE_DIR / "templates"
GOG = "/opt/homebrew/bin/gog"

DOC_TYPES = (
    "intake",
    "draft",
    "reviewed",
    "final",
    "correspondence",
    "precedent",
    "other",
)

ROOT_FOLDER_NAME = ""  # DRIVE_ROOT is LegalClawOS itself — clients go directly inside


def _matter_dict(matter: Any) -> dict:
    if isinstance(matter, Mapping):
        return dict(matter)
    return dict(matter)


def _gog_json(args: list[str], timeout: int = 120) -> dict | list:
    cmd = [GOG, *args, "-j", "--results-only", "--no-input"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"gog failed ({r.returncode}): {err or 'no output'}")
    out = (r.stdout or "").strip()
    if not out:
        return {}
    return json.loads(out)


def _escape_drive_query_value(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def _find_child_folder(parent_id: str, name: str) -> Optional[str]:
    q = (
        "mimeType='application/vnd.google-apps.folder' and "
        f"name='{_escape_drive_query_value(name)}' and "
        f"'{parent_id}' in parents"
    )
    res = _gog_json(["drive", "search", "--raw-query", q, "--max", "5"])
    if isinstance(res, list) and res:
        return res[0].get("id")
    return None


def _mkdir(name: str, parent_id: str) -> dict:
    return _gog_json(["drive", "mkdir", name, "--parent", parent_id])


def _ensure_child_folder(parent_id: str, name: str) -> dict:
    existing = _find_child_folder(parent_id, name)
    if existing:
        return {"id": existing, "webViewLink": folder_url(existing)}
    return _mkdir(name, parent_id)


def folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


def file_view_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"


def ensure_matter_folder(matter: Any, db: sqlite3.Connection) -> dict[str, Any]:
    """
    Folder path: LegalClawOS / [Client Name] / [Matter Ref] - [Matter Type]  (DRIVE_ROOT = LegalClawOS folder)
    """
    m = _matter_dict(matter)
    matter_id = m["id"]
    client_name = (m.get("client_name") or "Unknown Client").strip() or "Unknown Client"
    cid = m.get("client_id")
    if cid:
        crow = db.execute(
            "SELECT company_name, name FROM clients WHERE id=?",
            (cid,),
        ).fetchone()
        if crow:
            if crow["company_name"] and str(crow["company_name"]).strip():
                client_name = str(crow["company_name"]).strip()
            elif crow["name"] and str(crow["name"]).strip():
                client_name = str(crow["name"]).strip()
    matter_ref = (m.get("ref") or matter_id).strip()
    matter_type = (m.get("matter_type") or "General").strip() or "General"
    matter_folder_label = f"{matter_ref} - {matter_type}"

    # Create or get root node (either a named subfolder of DRIVE_ROOT, or DRIVE_ROOT itself)
    if ROOT_FOLDER_NAME:
        root_node = _ensure_child_folder(DRIVE_ROOT, ROOT_FOLDER_NAME)
        parent_id = root_node["id"]
    else:
        parent_id = DRIVE_ROOT  # ROOT_FOLDER_NAME is empty — clients go directly inside DRIVE_ROOT

    client_node = _ensure_child_folder(parent_id, client_name)
    client_folder_id = client_node["id"]

    matter_node = _ensure_child_folder(client_folder_id, matter_folder_label)
    matter_folder_id = matter_node["id"]
    folder_url_str = matter_node.get("webViewLink") or folder_url(matter_folder_id)

    now = datetime.now().isoformat()
    existing = db.execute(
        "SELECT id FROM documents WHERE matter_id=? AND doc_type='folder' LIMIT 1",
        (matter_id,),
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE documents SET name=?, drive_folder_id=?, drive_web_link=?, "
            "updated_at=? WHERE id=?",
            (matter_folder_label, matter_folder_id, folder_url_str, now, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO documents (id, matter_id, doc_type, name, description, "
            "drive_file_id, drive_folder_id, drive_web_link, mime_type, size, version, "
            "tags, uploaded_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                str(uuid.uuid4()),
                matter_id,
                "folder",
                matter_folder_label,
                None,
                None,
                matter_folder_id,
                folder_url_str,
                "application/vnd.google-apps.folder",
                None,
                1,
                None,
                "system",
                now,
                now,
            ),
        )
    db.commit()
    return {"folder_id": matter_folder_id, "folder_url": folder_url_str}


def get_document_download_url(doc: Any) -> Optional[str]:
    d = _matter_dict(doc)
    if d.get("drive_web_link"):
        return d["drive_web_link"]
    if d.get("drive_file_id"):
        return file_view_url(d["drive_file_id"])
    if d.get("drive_folder_id"):
        return folder_url(d["drive_folder_id"])
    return None


def list_matter_documents(matter_id: str, db: sqlite3.Connection) -> list[dict]:
    rows = db.execute(
        "SELECT * FROM documents WHERE matter_id=? AND doc_type != 'folder' "
        "ORDER BY created_at DESC",
        (matter_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def upload_document(
    matter_id: str,
    file_obj: Any,
    doc_type: str,
    description: str = "",
    tags: str = "",
    uploaded_by: str = "system",
    db: Optional[sqlite3.Connection] = None,
) -> dict:
    if doc_type not in DOC_TYPES:
        raise ValueError(f"Invalid doc_type: {doc_type}")
    own = db is None
    if own:
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
    assert db is not None
    try:
        matter = db.execute("SELECT * FROM matters WHERE id=?", (matter_id,)).fetchone()
        if not matter:
            raise ValueError(f"Matter {matter_id} not found")
        folder_info = ensure_matter_folder(matter, db)
        folder_id = folder_info["folder_id"]

        orig_name = getattr(file_obj, "filename", None) or "document"
        suffix = Path(orig_name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_obj.save(tmp_path)
        try:
            st = os.stat(tmp_path)
            size = st.st_size
            meta = _gog_json(
                [
                    "drive",
                    "upload",
                    tmp_path,
                    "--parent",
                    folder_id,
                    "--name",
                    orig_name,
                ]
            )
        finally:
            os.unlink(tmp_path)

        if not isinstance(meta, dict):
            raise RuntimeError("Unexpected gog upload response")
        file_id = meta.get("id")
        web_link = meta.get("webViewLink") or (
            file_view_url(file_id) if file_id else None
        )
        mime_type = meta.get("mimeType") or "application/octet-stream"

        now = datetime.now().isoformat()
        doc_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO documents (id, matter_id, doc_type, name, description, "
            "drive_file_id, drive_folder_id, drive_web_link, mime_type, size, version, "
            "tags, uploaded_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                doc_id,
                matter_id,
                doc_type,
                orig_name,
                description or None,
                file_id,
                folder_id,
                web_link,
                mime_type,
                size,
                1,
                tags or None,
                uploaded_by,
                now,
                now,
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else {}
    finally:
        if own:
            db.close()


def _template_filename_map() -> dict[str, str]:
    return {
        "client_care_letter": "client_care_letter.txt",
        "nda_standard": "nda_standard.txt",
        "contract_review_rag": "contract_review_rag.txt",
        "matter_summary": "matter_summary.txt",
        "client_care_letter.txt": "client_care_letter.txt",
        "nda_standard.txt": "nda_standard.txt",
        "contract_review_rag.txt": "contract_review_rag.txt",
        "matter_summary.txt": "matter_summary.txt",
    }


def _resolve_template_path(template_name: str) -> Path:
    m = _template_filename_map()
    base = m.get(template_name, template_name)
    if not base.endswith(".txt"):
        base = f"{base}.txt"
    path = TEMPLATE_DIR / base
    if not path.is_file():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return path


def create_doc_from_template(
    matter_id: str,
    template_name: str,
    doc_type: str,
    title: str,
    description: str = "",
    uploaded_by: str = "system",
    db: Optional[sqlite3.Connection] = None,
    firm_config: Optional[dict] = None,
) -> dict:
    if doc_type not in DOC_TYPES:
        raise ValueError(f"Invalid doc_type: {doc_type}")
    path = _resolve_template_path(template_name)
    content = path.read_text(encoding="utf-8")

    own = db is None
    if own:
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
    assert db is not None
    try:
        matter = db.execute("SELECT * FROM matters WHERE id=?", (matter_id,)).fetchone()
        if not matter:
            raise ValueError(f"Matter {matter_id} not found")
        md = dict(matter)
        cfg = firm_config or {}
        firm_name = cfg.get("firm_name", "Acme Dale Legal Services Solicitors")
        sra_number = cfg.get("sra_number", "PENDING")
        date_str = datetime.now().strftime("%d %B %Y")

        subst = {
            "{{client_name}}": md.get("client_name") or "",
            "{{client_email}}": md.get("client_email") or "",
            "{{matter_ref}}": md.get("ref") or matter_id,
            "{{practice_area}}": md.get("practice_area") or "",
            "{{matter_type}}": md.get("matter_type") or "",
            "{{date}}": date_str,
            "{{firm_name}}": firm_name,
            "{{sra_number}}": str(sra_number),
            "{{fee_estimate}}": md.get("fee_estimate") or "TBC",
            "{{party_a}}": md.get("client_name") or "Party A",
            "{{party_b}}": "Counterparty",
            "{{contract_name}}": "the agreement",
            "{{overall_rag}}": "[Run contract review to populate]",
        }
        for k, v in subst.items():
            content = content.replace(k, str(v))

        folder_info = ensure_matter_folder(matter, db)
        folder_id = folder_info["folder_id"]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            meta = _gog_json(
                [
                    "drive",
                    "upload",
                    tmp_path,
                    "--parent",
                    folder_id,
                    "--name",
                    title,
                    "--convert-to",
                    "doc",
                ]
            )
        finally:
            os.unlink(tmp_path)

        if not isinstance(meta, dict):
            raise RuntimeError("Unexpected gog upload response")
        file_id = meta.get("id")
        web_link = meta.get("webViewLink") or (
            f"https://docs.google.com/document/d/{file_id}/edit" if file_id else None
        )

        now = datetime.now().isoformat()
        doc_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO documents (id, matter_id, doc_type, name, description, "
            "drive_file_id, drive_folder_id, drive_web_link, mime_type, size, version, "
            "tags, uploaded_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                doc_id,
                matter_id,
                doc_type,
                title,
                description or None,
                file_id,
                folder_id,
                web_link,
                "application/vnd.google-apps.document",
                None,
                1,
                f"template:{path.name}",
                uploaded_by,
                now,
                now,
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else {}
    finally:
        if own:
            db.close()


def share_document_with_client(doc: Any, client_email: str) -> None:
    d = _matter_dict(doc)
    fid = d.get("drive_file_id")
    if not fid:
        raise ValueError("Document has no Drive file id")
    email = (client_email or "").strip()
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Invalid client email")
    _gog_json(
        [
            "drive",
            "share",
            fid,
            "--to=user",
            f"--email={email}",
            "--role=reader",
        ]
    )
