"""Private local evidence files: bounded uploads, format checks and owner/staff access."""

from pathlib import Path
import re
import warnings

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError

from . import db

MAX_BYTES = 10 * 1024 * 1024
MAX_ATTACHMENTS = 3
TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
         "video/mp4": ".mp4", "video/webm": ".webm"}


def evidence_path(evidence_id: str) -> Path:
    # IDs come from the database, but validate them before using them in a path too.
    if not re.fullmatch(r"[a-f0-9-]{32,36}", evidence_id):
        raise HTTPException(404, "Attachment not found.")
    return db.DATA_PATH / "evidence" / evidence_id


def metadata(row) -> dict:
    return {key: row[key] for key in ("id", "filename", "mime_type", "size_bytes", "created_at")}


def report_attachments(conn, report_id: str) -> list[dict]:
    return [metadata(row) for row in conn.execute(
        "SELECT * FROM report_evidence WHERE report_id=? ORDER BY created_at,id", (report_id,))]


def validate_media(path: Path, mime_type: str) -> None:
    if mime_type.startswith("image/"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(path, formats=["JPEG", "PNG", "WEBP"]) as image:
                    expected = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}[mime_type]
                    if image.format != expected or image.width * image.height > 25_000_000:
                        raise ValueError("Invalid image format or excessive dimensions")
                    image.verify()
        except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombWarning, Image.DecompressionBombError):
            raise HTTPException(422, "This photo is invalid, too large in dimensions, or has the wrong file type.")
    else:
        with path.open("rb") as source:
            head = source.read(4096)
        valid = (mime_type == "video/mp4" and len(head) >= 12 and head[4:8] == b"ftyp") or (
            mime_type == "video/webm" and head.startswith(b"\x1aE\xdf\xa3") and b"webm" in head)
        if not valid:
            raise HTTPException(422, "This video does not match its declared file type.")


async def receive_evidence(request: Request, user: dict, *, evidence_id: str, created_at: str) -> dict:
    mime_type = request.headers.get("content-type", "").split(";")[0].lower()
    if mime_type not in TYPES:
        raise HTTPException(415, "Choose a JPEG, PNG, WebP photo, or MP4/WebM video.")
    with db.connect() as conn:
        pending = conn.execute("SELECT COUNT(*) FROM report_evidence WHERE owner_id=? AND report_id IS NULL", (user["id"],)).fetchone()[0]
        if pending >= 12:
            raise HTTPException(409, "Remove an unused attachment before uploading more.")
    path = evidence_path(evidence_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    committed = False
    try:
        size = 0
        with path.open("xb") as target:
            async for chunk in request.stream():
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "Each attachment must be 10 MB or smaller.")
                target.write(chunk)
        if not size:
            raise HTTPException(422, "The attachment is empty.")
        validate_media(path, mime_type)
        from urllib.parse import unquote
        name = unquote(request.headers.get("x-filename", "attachment"))
        name = name.replace("\\", "/").split("/")[-1]
        name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()[:150] or "attachment"
        filename = Path(name).stem + TYPES[mime_type]
        with db.connect() as conn:
            conn.execute("INSERT INTO report_evidence VALUES(?,?,NULL,?,?,?,?)",
                         (evidence_id, user["id"], filename, mime_type, size, created_at))
            row = conn.execute("SELECT * FROM report_evidence WHERE id=?", (evidence_id,)).fetchone()
        committed = True
        return metadata(row)
    finally:
        if not committed:
            path.unlink(missing_ok=True)


def download_evidence(evidence_id: str, user: dict):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM report_evidence WHERE id=?", (evidence_id,)).fetchone()
        staff = user.get("role") in {"admin", "moderator"}
        if not row or (row["owner_id"] != user["id"] and not (staff and row["report_id"])):
            raise HTTPException(404, "Attachment not found.")
    path = evidence_path(row["id"])
    if not path.is_file():
        raise HTTPException(404, "Attachment file is unavailable.")
    return FileResponse(path, media_type=row["mime_type"], filename=row["filename"],
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


def remove_evidence(evidence_id: str, user: dict):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM report_evidence WHERE id=? AND owner_id=?", (evidence_id, user["id"])).fetchone()
        if not row:
            raise HTTPException(404, "Attachment not found.")
        if row["report_id"]:
            raise HTTPException(409, "Evidence attached to a submitted report cannot be removed from the draft.")
        conn.execute("DELETE FROM report_evidence WHERE id=?", (evidence_id,))
    evidence_path(evidence_id).unlink(missing_ok=True)
