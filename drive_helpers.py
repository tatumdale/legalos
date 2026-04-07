import subprocess
import json
from pathlib import Path

DRIVE_ROOT = "1aOipSxzKu1iuoP5w8vaQX273koOhqgKp"
GOG_ACCOUNT = "tatum@tatumdale.com"

def _gog(args, timeout=20):
    cmd = ["gog", "drive"] + args + ["--account", GOG_ACCOUNT, "-j"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None

def _get_folder_id_from_result(result):
    """Extract folder id/webLink from gog mkdir/search result."""
    if not result:
        return None, None
    # mkdir wraps in {"folder": {...}}, search returns {"files": [...]}
    if "folder" in result:
        d = result["folder"]
        return d.get("id"), d.get("webViewLink")
    if "files" in result and result["files"]:
        f = result["files"][0]
        return f.get("id"), f.get("webViewLink")
    return None, None

def _find_client_folder(client_name):
    """Find a client folder inside LegalClawOS. Returns folder_id or None."""
    result = _gog([
        "search",
        f"name:'{client_name}' and mimeType='application/vnd.google-apps.folder' and '{DRIVE_ROOT}' in parents"
    ])
    if result and result.get("files"):
        return result["files"][0]["id"]
    return None

def _create_folder(name, parent_id):
    """Create a folder. Returns (folder_id, web_link)."""
    result = _gog(["mkdir", name, "--parent", parent_id])
    return _get_folder_id_from_result(result)

def find_matter_folder_id(matter):
    """Search Drive for the matter folder inside LegalClawOS/[Client]/[Matter].
    Returns (folder_id, web_link) or (None, None).
    """
    ref = matter.get("ref", "")
    mtype = matter.get("matter_type", "")
    client = matter.get("client_name", "")
    folder_name = f"{ref} - {mtype}" if mtype else ref

    # Find client folder inside LegalClawOS
    client_folder_id = _find_client_folder(client)
    if not client_folder_id:
        return None, None

    # Search for matter folder inside the client folder
    result = _gog([
        "search",
        f"name:'{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{client_folder_id}' in parents"
    ])
    if result and result.get("files"):
        f = result["files"][0]
        return f["id"], f.get("webViewLink", "")
    return None, None

def get_or_create_matter_folder(matter):
    """Get the Drive folder for a matter, creating it if missing.
    Returns (folder_id, web_link).
    """
    fid, link = find_matter_folder_id(matter)
    if fid:
        return fid, link

    # Create it
    ref = matter.get("ref", "")
    mtype = matter.get("matter_type", "")
    client = matter.get("client_name", "")
    folder_name = f"{ref} - {mtype}" if mtype else ref

    # Find or create client folder
    client_folder_id = _find_client_folder(client)
    if not client_folder_id:
        # Create client folder in LegalClawOS root
        client_folder_id, _ = _create_folder(client, DRIVE_ROOT)
    if not client_folder_id:
        return None, None

    # Create matter folder inside client folder
    return _create_folder(folder_name, client_folder_id)

def list_drive_folder(folder_id):
    """List all files in a Drive folder. Returns list of file dicts."""
    if not folder_id:
        return []
    result = _gog(["ls", "--parent", folder_id])
    if not result:
        return []
    return result.get("files", [])

def get_matter_documents(matter):
    """Get all Drive documents for a matter.
    Returns (docs_list, folder_url).
    """
    folder_id, folder_url = get_or_create_matter_folder(matter)
    if not folder_id:
        return [], ""

    files = list_drive_folder(folder_id)
    docs = []
    for f in files:
        name = f.get("name", "")
        mime = f.get("mimeType", "")
        if mime == "application/vnd.google-apps.folder":
            continue

        # File type label
        if "pdf" in mime or name.lower().endswith(".pdf"):
            ftype = "PDF"
        elif "document" in mime or name.lower().endswith((".doc", ".docx")):
            ftype = "DOCX"
        elif "spreadsheet" in mime or name.lower().endswith((".xls", ".xlsx", ".csv")):
            ftype = "XLSX"
        elif "presentation" in mime or name.lower().endswith((".ppt", ".pptx")):
            ftype = "PPTX"
        elif "image" in mime:
            ftype = "Image"
        elif "plain" in mime or "text" in mime:
            ftype = "Text"
        elif "shortcut" in mime:
            ftype = "Shortcut"
        else:
            ext = Path(name).suffix.upper().lstrip(".") or "File"
            ftype = ext if len(ext) <= 5 else "File"

        # Source label
        nl = name.lower()
        if "engagement" in nl or "letter" in nl:
            source = "Correspondence"
        elif "contract" in nl or "agreement" in nl:
            source = "Contract"
        elif "draft" in nl:
            source = "Draft"
        elif "invoice" in nl:
            source = "Invoice"
        elif "email" in nl or "e-mail" in nl:
            source = "Email"
        elif "note" in nl or "memo" in nl:
            source = "Note"
        elif "questionnaire" in nl or "intake" in nl:
            source = "Intake"
        else:
            source = "Upload"

        # Size
        size_bytes = int(f.get("size", 0) or 0)
        if size_bytes < 1024:
            size_str = f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes // 1024}KB"
        else:
            size_str = f"{size_bytes / (1024*1024):.1f}MB"

        docs.append({
            "id": f.get("id", ""),
            "name": name,
            "type": ftype,
            "source": source,
            "size": size_str,
            "size_bytes": size_bytes,
            "created_time": f.get("createdTime", ""),
            "modified_time": f.get("modifiedTime", ""),
            "mime_type": mime,
            "web_view_link": f.get("webViewLink", ""),
            "drive_folder_id": folder_id,
        })

    return docs, folder_url
