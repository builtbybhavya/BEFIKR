"""BEFIKR modular monolith API. External integrations remain explicit adapters."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, Request as ApiRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import db
from .providers import (GoogleRoutesProvider, MapboxDirectionsProvider, PublicWalkingProvider, OSMnxWalkingProvider, UnconfiguredEvidenceStorage,
                        UnconfiguredNotificationProvider, configured_mapping_provider)
from .risk import calculate_route, calculate_segment, compare_routes
from .route_demo import demo_catalog, demo_lookup
from .geo import distance_km
from .places_csv import nearby_csv_places
from .baat_recordings import attach_recordings, recording_catalog
from . import evidence

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.getenv("BEFIKR_WEB_DIR", os.path.abspath(os.path.join(APP_DIR, "..", "web")))
TOKEN_SECRET = os.getenv("BEFIKR_TOKEN_SECRET", "development-only-change-this-secret")
TOKEN_HOURS = int(os.getenv("BEFIKR_TOKEN_HOURS", "12"))
REPORT_CATEGORIES = {"harassment", "suspicious activity", "poor lighting", "isolated area",
                     "unsafe public transport", "recurring local concern", "other"}
REPORT_STATUSES = {"submitted", "pending_review", "under_review", "corroborated", "validated", "rejected"}
PLACE_CATEGORIES = {"police", "hospital", "park", "public_space", "restaurant", "cafe", "support"}
GOOGLE_MAPS_SERVER_KEY = os.getenv("GOOGLE_MAPS_SERVER_KEY", "").strip()
GOOGLE_MAPS_BROWSER_KEY = os.getenv("GOOGLE_MAPS_BROWSER_KEY", "").strip()
GOOGLE_MAPS_EMBED_KEY = os.getenv("GOOGLE_MAPS_EMBED_KEY", "").strip()
DELHI_ROAD_SAFETY_REPORT_URL = "https://transport.delhi.gov.in/sites/default/files/2023-08/road_safety_data_to_action_report.pdf"
MAPPING_PROVIDER = configured_mapping_provider()
NOTIFICATION_PROVIDER = UnconfiguredNotificationProvider()
EVIDENCE_STORAGE = UnconfiguredEvidenceStorage()

app = FastAPI(title="BEFIKR API", version="0.1.0", description="Privacy-conscious safety ecosystem API")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("BEFIKR_CORS_ORIGINS", "http://localhost:8000").split(","),
                   allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["*"])


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime | None = None) -> str:
    return (value or now()).isoformat()


def uid() -> str:
    return str(uuid.uuid4())


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt, expected = encoded.split("$")
        actual = hash_password(password, bytes.fromhex(salt)).split("$")[-1]
        return scheme == "pbkdf2_sha256" and hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def issue_token(user_id: str, role: str) -> str:
    expiry_at = now() + timedelta(hours=TOKEN_HOURS)
    expiry = int(expiry_at.timestamp())
    session_id = uid()
    with db.connect() as conn:
        conn.execute("INSERT INTO auth_sessions VALUES(?,?,?,?,NULL)", (session_id, user_id, stamp(), stamp(expiry_at)))
    body = base64.urlsafe_b64encode(json.dumps({"sub": user_id, "role": role, "exp": expiry, "jti": session_id}, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(TOKEN_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    return body + "." + base64.urlsafe_b64encode(signature).decode().rstrip("=")


def decode_token(token: str) -> dict[str, Any]:
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(TOKEN_SECRET.encode(), body.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if payload["exp"] < int(now().timestamp()):
            raise ValueError("expired")
        with db.connect() as conn:
            session = conn.execute("SELECT revoked_at FROM auth_sessions WHERE id=? AND owner_id=?", (payload["jti"], payload["sub"])).fetchone()
        if not session or session["revoked_at"] is not None:
            raise ValueError("revoked")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(401, "Session expired or invalid. Please sign in again.")


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Sign in to continue.")
    payload = decode_token(authorization[7:])
    with db.connect() as conn:
        user = conn.execute("SELECT id,name,email,role FROM users WHERE id=?", (payload["sub"],)).fetchone()
    if not user:
        raise HTTPException(401, "Account no longer exists.")
    return dict(user)


def optional_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        payload = decode_token(authorization[7:])
        with db.connect() as conn:
            user = conn.execute("SELECT id,name,email,role FROM users WHERE id=?", (payload["sub"],)).fetchone()
        return dict(user) if user else None
    except Exception:
        return None


def admin_user(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user["role"] not in {"admin", "moderator"}:
        raise HTTPException(403, "Administrator access required.")
    return user


def audit(conn, actor: str, action: str, target_type: str, target_id: str, detail: str = "") -> None:
    conn.execute("INSERT INTO audit_logs VALUES(?,?,?,?,?,?,?)", (uid(), actor, action, target_type, target_id, detail[:500], stamp()))


def rowdict(row) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


class RegisterInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Enter your name")
        return value


class LoginInput(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)


class PreferencesInput(BaseModel):
    analytics_opt_in: bool
    push_opt_in: bool


class ContactInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    phone: str = Field(min_length=4, max_length=32)
    relationship: str = Field(default="", max_length=40)

    @field_validator("name", "phone")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class ReportInput(BaseModel):
    category: str
    description: str = Field(min_length=10, max_length=2000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    occurred_at: str | None = Field(default=None, max_length=50)
    location_label: str | None = Field(default=None, max_length=300)
    location_place_id: str | None = Field(default=None, max_length=255)
    evidence_ids: list[str] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def valid_report_location_and_evidence(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Choose both latitude and longitude, or leave the location empty")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("Duplicate attachment IDs are not allowed")
        return self

    @field_validator("category")
    @classmethod
    def valid_category(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in REPORT_CATEGORIES:
            raise ValueError("Select a supported report category")
        return value

    @field_validator("description")
    @classmethod
    def meaningful_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Please provide at least 10 non-space characters")
        return value


class AppealInput(BaseModel):
    message: str = Field(min_length=10, max_length=1000)


class ModerationInput(BaseModel):
    status: str
    reason: str = Field(default="", max_length=1000)

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in REPORT_STATUSES:
            raise ValueError("Unsupported moderation status")
        return value


class SegmentInput(BaseModel):
    length_km: float = Field(gt=0, le=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    model_config = ConfigDict(extra="allow")


class RouteRiskInput(BaseModel):
    segments: list[SegmentInput] = Field(min_length=1, max_length=100)


class RouteInput(BaseModel):
    origin: str = Field(min_length=1, max_length=160)
    destination: str = Field(min_length=1, max_length=160)
    origin_latitude: float | None = Field(default=None, ge=-90, le=90)
    origin_longitude: float | None = Field(default=None, ge=-180, le=180)
    destination_latitude: float | None = Field(default=None, ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, ge=-180, le=180)
    use_google_maps: bool = False
    context: Literal["raahi", "safe_spot"] = "raahi"
    demo_time_band: Literal["current", "Day", "Evening", "Night", "morning", "day", "evening", "night"] = "current"
    mode: Literal["auto", "synthetic", "real"] = "auto"

    @field_validator("origin", "destination")
    @classmethod
    def strip_location_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 1:
            raise ValueError("Enter a place name")
        return value


class OfflineDecideInput(BaseModel):
    origin: str = Field(min_length=1, max_length=160)
    destination: str = Field(min_length=1, max_length=160)
    origin_latitude: float | None = Field(default=None, ge=-90, le=90)
    origin_longitude: float | None = Field(default=None, ge=-180, le=180)
    destination_latitude: float | None = Field(default=None, ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, ge=-180, le=180)
    time_band: Literal["morning", "day", "evening", "night", "current"] = "day"
    mode: Literal["auto", "synthetic", "real"] = "auto"
    k_alternatives: int = Field(default=5, ge=1, le=10)


class CheckinFromRouteInput(BaseModel):
    route_id: str
    duration_minutes: int = Field(ge=1, le=720)
    risk_score: float = Field(ge=0.0, le=100.0)
    destination: str = Field(default="Destination", max_length=160)


class SafetyDemoInput(BaseModel):
    origin: str = Field(min_length=2, max_length=160)
    destination: str = Field(min_length=2, max_length=160)
    time_band: Literal["current", "Day", "Evening", "Night"] = "current"


class SosInput(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class TrackingInput(BaseModel):
    recipient_ids: list[str] = Field(default_factory=list, max_length=10)
    destination: str | None = Field(default=None, max_length=160)
    duration_minutes: int = Field(default=120, ge=5, le=1440)


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CheckinInput(BaseModel):
    duration_minutes: int = Field(default=120, ge=5, le=1440)
    grace_minutes: int = Field(default=10, ge=1, le=60)
    destination: str | None = Field(default=None, max_length=160)
    risk_route: float = Field(default=50, ge=0, le=100)
    risk_population: float = Field(default=50, ge=0, le=100)
    risk_time: float = Field(default=50, ge=0, le=100)
    risk_isolation: float = Field(default=50, ge=0, le=100)
    risk_deviation: float = Field(default=0, ge=0, le=100)
    risk_eta: float = Field(default=50, ge=0, le=100)
    risk_mode: float = Field(default=50, ge=0, le=100)


class PlaceInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str
    address: str = Field(min_length=3, max_length=240)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    phone: str = Field(default="", max_length=32)
    source: str = Field(min_length=3, max_length=200)
    source_url: str = Field(default="", max_length=1000)
    verified_at: str = Field(min_length=10, max_length=50)
    active: bool = True

    @field_validator("category")
    @classmethod
    def valid_category(cls, value: str) -> str:
        if value not in PLACE_CATEGORIES:
            raise ValueError("Unsupported Safe Spot category")
        return value

    @field_validator("name", "address", "source")
    @classmethod
    def strip_place_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("source_url")
    @classmethod
    def valid_place_source_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("Source URL must be a public http(s) URL")
        return value


class PlaceCandidateInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str
    address: str = Field(min_length=3, max_length=240)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    phone: str = Field(default="", max_length=32)
    source_url: str = Field(min_length=8, max_length=1000)
    source_date: str | None = Field(default=None, max_length=80)
    dataset_id: str | None = Field(default=None, max_length=160)

    @field_validator("category")
    @classmethod
    def valid_candidate_category(cls, value: str) -> str:
        aliases = {"police station": "police", "police stations": "police", "hospital": "hospital",
                   "hospitals": "hospital", "clinic": "hospital", "clinics": "hospital", "park": "park",
                   "parks": "park", "public space": "public_space", "public spaces": "public_space",
                   "community centre": "public_space", "community center": "public_space",
                   "restaurant": "restaurant", "restaurants": "restaurant", "cafe": "cafe", "cafes": "cafe"}
        normalized = value.strip().lower().replace("-", " ").replace("_", " ")
        category = aliases.get(normalized)
        if not category:
            raise ValueError("Category must be police, hospital, park, public_space, restaurant, or cafe")
        return category

    @field_validator("name", "address", "source_url")
    @classmethod
    def strip_candidate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("source_url")
    @classmethod
    def require_public_source_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("Source URL must be a public http(s) URL")
        return value

    @field_validator("latitude")
    @classmethod
    def candidate_latitude_in_delhi_region(cls, value: float) -> float:
        if not 28.0 <= value <= 29.2:
            raise ValueError("Candidate latitude must be within the Delhi region")
        return value

    @field_validator("longitude")
    @classmethod
    def candidate_longitude_in_delhi_region(cls, value: float) -> float:
        if not 76.0 <= value <= 78.0:
            raise ValueError("Candidate longitude must be within the Delhi region")
        return value


class PlaceCandidateBatch(BaseModel):
    candidates: list[PlaceCandidateInput] = Field(min_length=1, max_length=250)


class PlaceCandidateReview(BaseModel):
    decision: str
    notes: str = Field(default="", max_length=1000)

    @field_validator("decision")
    @classmethod
    def valid_candidate_decision(cls, value: str) -> str:
        if value not in {"approve", "reject"}:
            raise ValueError("Decision must be approve or reject")
        return value


@app.on_event("startup")
def startup() -> None:
    db.initialize()
    email = os.getenv("BEFIKR_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("BEFIKR_ADMIN_PASSWORD", "")
    if email and len(password) >= 14:
        with db.connect() as conn:
            existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if not existing:
                conn.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (uid(), "BEFIKR Admin", email, hash_password(password), "admin", stamp()))


@app.get("/api/health")
def health():
    with db.connect() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "ok", "service": "befikr-api", "database": "sqlite-development"}


@app.get("/api/capabilities")
def capabilities():
    return {"mapping": {"state": "demo_only", "provider": MAPPING_PROVIDER.name,
                         "requested_provider": os.getenv("BEFIKR_MAP_PROVIDER") or None, "live": False},
            "notifications": {"state": "not_configured", "credentials_present": {"push": bool(os.getenv("FCM_CREDENTIALS")), "sms": bool(os.getenv("SMS_API_KEY"))}},
            "evidence_storage": {"state": "private_local", "max_files": 3, "max_bytes": evidence.MAX_BYTES,
                                 "malware_scanning": False}, "background_jobs": {"state": "not_configured"},
            "tracking": {"state": "account_session_only", "external_sharing": False},
            "voice": {"state": "browser_speech_synthesis", "offline_availability": "device_dependent"}}


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterInput):
    user_id = uid()
    try:
        with db.connect() as conn:
            conn.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (user_id, data.name.strip(), data.email, hash_password(data.password), "user", stamp()))
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(409, "An account with that email already exists.")
        raise
    return {"access_token": issue_token(user_id, "user"), "token_type": "bearer", "user": {"id": user_id, "name": data.name.strip(), "email": data.email, "role": "user"}}


@app.post("/api/auth/login")
def login(data: LoginInput):
    email = data.email.strip().lower()
    with db.connect() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Email or password is incorrect.")
    return {"access_token": issue_token(user["id"], user["role"]), "token_type": "bearer", "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}}


@app.post("/api/auth/logout")
def logout(user=Depends(current_user), authorization: str | None = Header(default=None)):
    payload = decode_token(authorization[7:])
    with db.connect() as conn:
        conn.execute("UPDATE auth_sessions SET revoked_at=? WHERE id=? AND owner_id=?", (stamp(), payload["jti"], user["id"]))
    return {"message": "This session has been revoked."}


@app.get("/api/profile")
def get_profile(user=Depends(current_user)):
    return user


@app.patch("/api/profile")
def update_profile(data: ProfileUpdate, user=Depends(current_user)):
    if data.name is not None:
        with db.connect() as conn:
            conn.execute("UPDATE users SET name=? WHERE id=?", (data.name.strip(), user["id"]))
        user["name"] = data.name.strip()
    return user


@app.delete("/api/profile", status_code=204)
def delete_profile(user=Depends(current_user)):
    with db.connect() as conn:
        files = [row[0] for row in conn.execute("SELECT id FROM report_evidence WHERE owner_id=?", (user["id"],))]
        conn.execute("DELETE FROM users WHERE id=?", (user["id"],))
    for attachment_id in files:
        evidence.evidence_path(attachment_id).unlink(missing_ok=True)
    return None


@app.get("/api/profile/export")
def export_profile(user=Depends(current_user)):
    with db.connect() as conn:
        contacts = [dict(row) for row in conn.execute("SELECT id,name,phone,relationship,created_at FROM contacts WHERE owner_id=?", (user["id"],))]
        reports = [dict(row) for row in conn.execute("SELECT id,category,description,latitude,longitude,occurred_at,status,created_at,updated_at FROM reports WHERE owner_id=?", (user["id"],))]
        sos_events = [dict(row) for row in conn.execute("SELECT id,status,delivery_state,latitude,longitude,created_at,cancelled_at FROM sos_events WHERE owner_id=?", (user["id"],))]
        tracking = [dict(row) for row in conn.execute("SELECT id,status,destination,created_at,expires_at FROM tracking_sessions WHERE owner_id=?", (user["id"],))]
        consents = [dict(row) for row in conn.execute("SELECT purpose,granted,scope,created_at FROM consent_events WHERE owner_id=?", (user["id"],))]
    return {"profile": user, "contacts": contacts, "reports": reports, "emergency_events": sos_events,
            "journeys": tracking, "consent_history": consents, "exported_at": stamp()}


@app.get("/api/profile/preferences")
def get_preferences(user=Depends(current_user)):
    with db.connect() as conn:
        conn.execute("INSERT OR IGNORE INTO user_preferences(owner_id,updated_at) VALUES(?,?)", (user["id"], stamp()))
        row = conn.execute("SELECT analytics_opt_in,push_opt_in,updated_at FROM user_preferences WHERE owner_id=?", (user["id"],)).fetchone()
    return {"analytics_opt_in": bool(row["analytics_opt_in"]), "push_opt_in": bool(row["push_opt_in"]), "updated_at": row["updated_at"]}


@app.patch("/api/profile/preferences")
def update_preferences(data: PreferencesInput, user=Depends(current_user)):
    with db.connect() as conn:
        conn.execute("INSERT INTO user_preferences(owner_id,analytics_opt_in,push_opt_in,updated_at) VALUES(?,?,?,?) ON CONFLICT(owner_id) DO UPDATE SET analytics_opt_in=excluded.analytics_opt_in,push_opt_in=excluded.push_opt_in,updated_at=excluded.updated_at",
                     (user["id"], int(data.analytics_opt_in), int(data.push_opt_in), stamp()))
    return {"analytics_opt_in": data.analytics_opt_in, "push_opt_in": data.push_opt_in}


@app.get("/api/contacts")
def list_contacts(user=Depends(current_user)):
    with db.connect() as conn:
        return [dict(row) for row in conn.execute("SELECT id,name,phone,relationship,created_at FROM contacts WHERE owner_id=? ORDER BY created_at", (user["id"],))]


@app.post("/api/contacts", status_code=201)
def add_contact(data: ContactInput, user=Depends(current_user)):
    contact_id = uid()
    with db.connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM contacts WHERE owner_id=?", (user["id"],)).fetchone()[0]
        if count >= 10:
            raise HTTPException(400, "You can add up to 10 trusted contacts.")
        conn.execute("INSERT INTO contacts VALUES(?,?,?,?,?,?)", (contact_id, user["id"], data.name.strip(), data.phone.strip(), data.relationship.strip(), stamp()))
        return rowdict(conn.execute("SELECT id,name,phone,relationship,created_at FROM contacts WHERE id=?", (contact_id,)).fetchone())


@app.delete("/api/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        cur = conn.execute("DELETE FROM contacts WHERE id=? AND owner_id=?", (contact_id, user["id"]))
        if cur.rowcount == 0:
            raise HTTPException(404, "Contact not found.")
    return None


@app.post("/api/evidence", status_code=201)
async def upload_evidence(request: ApiRequest, user=Depends(current_user)):
    return await evidence.receive_evidence(request, user, evidence_id=uid(), created_at=stamp())


@app.get("/api/evidence/{evidence_id}")
def read_evidence(evidence_id: str, user=Depends(current_user)):
    return evidence.download_evidence(evidence_id, user)


@app.delete("/api/evidence/{evidence_id}", status_code=204)
def delete_evidence(evidence_id: str, user=Depends(current_user)):
    evidence.remove_evidence(evidence_id, user)
    return Response(status_code=204)


@app.post("/api/reports", status_code=201)
def create_report(data: ReportInput, user=Depends(current_user)):
    report_id, moment = uid(), stamp()
    with db.connect() as conn:
        for attachment_id in data.evidence_ids:
            attachment = conn.execute("SELECT owner_id,report_id FROM report_evidence WHERE id=?", (attachment_id,)).fetchone()
            if not attachment or attachment["owner_id"] != user["id"] or attachment["report_id"] is not None:
                raise HTTPException(422, "One attachment is unavailable or already belongs to a report.")
            if not evidence.evidence_path(attachment_id).is_file():
                raise HTTPException(422, "One attachment file is unavailable. Please upload it again.")
        if data.latitude is not None and data.longitude is not None:
            duplicate = conn.execute("""SELECT id FROM reports WHERE owner_id=? AND category=? AND status!='rejected'
                AND created_at>=? AND latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ? LIMIT 1""",
                (user["id"], data.category, stamp(now() - timedelta(hours=24)), data.latitude - .005, data.latitude + .005,
                 data.longitude - .005, data.longitude + .005)).fetchone()
            if duplicate:
                raise HTTPException(409, "You already have a similar report awaiting review in this approximate area.")
        conn.execute("INSERT INTO reports(id,owner_id,category,description,latitude,longitude,occurred_at,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                     (report_id, user["id"], data.category, data.description.strip(), data.latitude, data.longitude, data.occurred_at, "pending_review", moment, moment))
        conn.execute("INSERT INTO report_history VALUES(?,?,?,?,?,?,?)", (uid(), report_id, user["id"], None, "pending_review", "Report submitted", moment))
        conn.execute("UPDATE reports SET location_label=?,location_place_id=? WHERE id=?",
                     (data.location_label, data.location_place_id, report_id))
        for attachment_id in data.evidence_ids:
            changed = conn.execute("UPDATE report_evidence SET report_id=? WHERE id=? AND owner_id=? AND report_id IS NULL",
                                   (report_id, attachment_id, user["id"]))
            if changed.rowcount != 1:
                raise HTTPException(409, "An attachment changed while the report was being submitted. Please retry.")
        conn.execute("INSERT INTO consent_events VALUES(?,?,?,?,?,?)", (uid(), user["id"], "raaz_report_submission", 1, "Private account-linked report; not public; review and retention apply", moment))
    return {"id": report_id, "status": "pending_review", "message": "Report received by this development service and is awaiting review. It is not public."}


def public_report(row) -> dict[str, Any]:
    return {key: row[key] for key in ("id", "category", "description", "occurred_at", "status", "created_at", "updated_at")}


@app.get("/api/reports")
def list_reports(user=Depends(current_user)):
    with db.connect() as conn:
        rows = conn.execute("SELECT id,category,description,occurred_at,status,created_at,updated_at,location_label FROM reports WHERE owner_id=? ORDER BY created_at DESC", (user["id"],)).fetchall()
        return [{**public_report(row), "location_label": row["location_label"],
                 "evidence": evidence.report_attachments(conn, row["id"])} for row in rows]


@app.get("/api/reports/status/{report_id}")
def report_status(report_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        row = conn.execute("SELECT id,status,created_at,updated_at FROM reports WHERE id=? AND owner_id=?", (report_id, user["id"])).fetchone()
    if not row:
        raise HTTPException(404, "Report not found.")
    return dict(row)


@app.post("/api/reports/{report_id}/appeal", status_code=201)
def appeal_report(report_id: str, data: AppealInput, user=Depends(current_user)):
    with db.connect() as conn:
        report = conn.execute("SELECT status FROM reports WHERE id=? AND owner_id=?", (report_id, user["id"])).fetchone()
        if not report:
            raise HTTPException(404, "Report not found.")
        if report["status"] != "rejected":
            raise HTTPException(400, "Only rejected reports can be appealed.")
        appeal_id = uid()
        conn.execute("INSERT INTO appeals VALUES(?,?,?,?,?,?)", (appeal_id, report_id, user["id"], data.message.strip(), "pending", stamp()))
        return {"id": appeal_id, "status": "pending"}


@app.get("/api/routes/safety-demo")
def safety_demo_catalog(user=Depends(optional_user)):
    """List supplied synthetic examples without requesting any map service."""
    return demo_catalog()


@app.post("/api/routes/safety-demo")
def safety_demo_lookup(data: SafetyDemoInput, user=Depends(optional_user)):
    """Look up an area pair for demonstration, without assigning risk to a real route."""
    return demo_lookup(data.origin, data.destination, data.time_band)


@app.post("/api/routes/alternatives")
def route_alternatives(data: RouteInput, user=Depends(optional_user)):
    """Return actual walking geometry from Google Maps or the configured fallback provider."""
    provider = MAPPING_PROVIDER
    from .offline_provider import OfflineMappingProvider
    if isinstance(provider, GoogleRoutesProvider) and not data.use_google_maps:
        provider = OfflineMappingProvider()
    if data.context == "safe_spot" and not isinstance(provider, (GoogleRoutesProvider, MapboxDirectionsProvider)):
        if getattr(provider, "name", "") in ("offline_ai_decider", "offline"):
            pass
        elif os.getenv("BEFIKR_MAPPING_PROVIDER", "").strip().lower() in ("offline", "offline_ai_decider"):
            provider = OfflineMappingProvider()
        elif getattr(provider, "name", "") == "demo":
            provider = PublicWalkingProvider()
    origin_coordinates = ((data.origin_latitude, data.origin_longitude)
                          if data.origin_latitude is not None and data.origin_longitude is not None else None)
    destination_coordinates = ((data.destination_latitude, data.destination_longitude)
                              if data.destination_latitude is not None and data.destination_longitude is not None else None)

    if isinstance(provider, OfflineMappingProvider):
        result = provider.alternatives(
            data.origin.strip(),
            data.destination.strip(),
            origin_coordinates,
            destination_coordinates,
            time_band=data.demo_time_band.lower(),
            context=data.context
        )
        try:
            demo_band = data.demo_time_band.capitalize() if data.demo_time_band.lower() != "current" else "current"
            result["safety_demo"] = demo_lookup(data.origin, data.destination, demo_band)
        except Exception:
            result["safety_demo"] = None
        return result

    result = provider.alternatives(data.origin.strip(), data.destination.strip(),
                                   origin_coordinates, destination_coordinates)
    if isinstance(provider, GoogleRoutesProvider) and not result.get("routes"):
        fallback_provider = PublicWalkingProvider() if data.context == "safe_spot" else OSMnxWalkingProvider()
        fallback = fallback_provider.alternatives(data.origin.strip(), data.destination.strip(),
                                                       origin_coordinates, destination_coordinates)
        if fallback.get("routes"):
            fallback["provider_state"] = "google_routes_fallback"
            fallback["warning"] = "Showing an OpenStreetMap walking route estimate."
            result = fallback
    result["routes"] = compare_routes(result["routes"])
    # This area-pair example does not rate, recolour, or rank the provider's street geometry.
    result["safety_demo"] = demo_lookup(data.origin, data.destination, data.demo_time_band)
    return result


@app.post("/api/routes/offline-decide")
def route_offline_decide(data: OfflineDecideInput, user=Depends(optional_user)):
    """Evaluate candidate paths, 7 risk parameters, ML approximation, and return offline recommendations."""
    from .offline_provider import OfflineMappingProvider
    provider = OfflineMappingProvider(mode=data.mode)
    orig_coords = ((data.origin_latitude, data.origin_longitude)
                   if data.origin_latitude is not None and data.origin_longitude is not None else None)
    dest_coords = ((data.destination_latitude, data.destination_longitude)
                   if data.destination_latitude is not None and data.destination_longitude is not None else None)
    return provider.alternatives(
        data.origin.strip(),
        data.destination.strip(),
        orig_coords,
        dest_coords,
        time_band=data.time_band
    )


@app.post("/api/routes/risk")
def route_risk(data: RouteRiskInput, user=Depends(optional_user)):
    results = []
    for segment in data.segments:
        payload = segment.model_dump(exclude={"length_km", "latitude", "longitude"})
        corroboration = None
        aggregated = False
        if segment.latitude is not None and segment.longitude is not None and payload.get("incident") is None:
            with db.connect() as conn:
                reports = conn.execute("SELECT owner_id,created_at FROM reports WHERE status='validated' AND ROUND(latitude,2)=ROUND(?,2) AND ROUND(longitude,2)=ROUND(?,2)",
                                       (segment.latitude, segment.longitude)).fetchall()
            distinct_reporters = len({row["owner_id"] for row in reports})
            if distinct_reporters >= 3:
                ages = []
                for row in reports:
                    created = datetime.fromisoformat(row["created_at"])
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    ages.append(max(0.0, (now() - created).total_seconds() / 86400))
                payload["incident"] = min(100, distinct_reporters * 20)
                payload["freshness"] = round(sum(100 * math.exp(-age / 90) for age in ages) / len(ages), 1)
                corroboration = 1.0
                aggregated = True
        result = calculate_segment(payload, corroboration=corroboration, minimum_coverage=0.40)
        results.append({"score": result.score, "confidence": result.confidence, "coverage": result.coverage,
                        "classification": result.classification, "explanation": result.explanation,
                        "length_km": segment.length_km, "aggregated_validated_reports": aggregated})
    return {"segments": results, "route": calculate_route(results), "model": "configurable prototype; not scientifically validated",
            "privacy_note": "Only validated reports from a coarse geographic cell with at least three distinct reporters can contribute. Raw report text and exact locations are not returned."}


@app.get("/api/routes/data-status")
def route_data_status(user=Depends(optional_user)):
    synthetic = demo_catalog()
    return {"state": "not configured", "minimum_aggregation_threshold": 3,
            "last_updated": None,
            "message": "Walking-route geometry can use the configured Google Maps, OSMnx or Mapbox provider. Verified route safety data is not connected. Synthetic area-pair examples are available separately for demonstration only; they do not classify individual roads or rank map alternatives. Delhi Transport Department's public report is historical road-crash analysis for 2019–2021; it is not a personal-safety dataset.",
            "synthetic_demo": {key: synthetic[key] for key in ("source", "available", "notice", "counts")},
            "source_url": DELHI_ROAD_SAFETY_REPORT_URL,
            "mapping_provider": getattr(MAPPING_PROVIDER, "name", "unknown"),
            "nirakshak_state": "official_feed_not_connected",
            "safetipin_state": "authorized_iudx_resource_or_export_required",
            "data_gov_state": "dataset_resource_id_and_api_key_required",
            "dda_state": "infrastructure_context_only",
            "google_places_state": "configured" if GOOGLE_MAPS_SERVER_KEY else "google_maps_key_required"}


@app.get("/api/maps/config")
def maps_config():
    # Only keys intended for frontend use belong here. Restrict them to approved HTTP referrers.
    embed_key = GOOGLE_MAPS_EMBED_KEY or GOOGLE_MAPS_BROWSER_KEY
    return {
        "google_maps_browser_key": GOOGLE_MAPS_BROWSER_KEY or None,
        "google_maps_enabled": bool(GOOGLE_MAPS_BROWSER_KEY),
        "google_maps_embed_key": embed_key or None,
        "google_maps_embed_enabled": bool(embed_key),
        "google_places_enabled": bool(GOOGLE_MAPS_SERVER_KEY),
    }


@app.post("/api/sos", status_code=201)
def create_sos(data: SosInput, user=Depends(current_user)):
    event_id = uid()
    with db.connect() as conn:
        conn.execute("INSERT INTO sos_events VALUES(?,?,?,?,?,?,?,?)", (event_id, user["id"], "created", "not_configured", data.latitude, data.longitude, stamp(), None))
    with db.connect() as conn:
        conn.execute("INSERT INTO consent_events VALUES(?,?,?,?,?,?)", (uid(), user["id"], "emergency_event", 1, "User explicitly created an emergency event record; no dispatch", stamp()))
    return {"id": event_id, "status": "created", "delivery_state": "not_configured",
            "message": "Emergency event saved. No contact, emergency service, SMS, or push notification was sent."}


@app.patch("/api/sos/{event_id}/location")
def update_sos_location(event_id: str, data: SosInput, user=Depends(current_user)):
    if data.latitude is None or data.longitude is None:
        raise HTTPException(400, "Both current location coordinates are required.")
    with db.connect() as conn:
        cur = conn.execute(
            "UPDATE sos_events SET latitude=?,longitude=? WHERE id=? AND owner_id=? AND status='created'",
            (data.latitude, data.longitude, event_id, user["id"]),
        )
        if not cur.rowcount:
            raise HTTPException(404, "Active SOS event not found.")
        event = conn.execute(
            "SELECT id,status,delivery_state,latitude,longitude FROM sos_events WHERE id=? AND owner_id=?",
            (event_id, user["id"]),
        ).fetchone()
    return dict(event)


@app.get("/api/sos")
def list_sos_events(user=Depends(current_user)):
    with db.connect() as conn:
        return [dict(row) for row in conn.execute("SELECT id,status,delivery_state,created_at,cancelled_at FROM sos_events WHERE owner_id=? ORDER BY created_at DESC LIMIT 100", (user["id"],))]


@app.get("/api/sos/{event_id}")
def get_sos(event_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        event = conn.execute("SELECT id,status,delivery_state,created_at,cancelled_at FROM sos_events WHERE id=? AND owner_id=?", (event_id, user["id"])).fetchone()
    if not event:
        raise HTTPException(404, "Event not found.")
    return dict(event)


@app.post("/api/sos/{event_id}/cancel")
def cancel_sos(event_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        cur = conn.execute("UPDATE sos_events SET status='cancelled',cancelled_at=? WHERE id=? AND owner_id=? AND status='created'", (stamp(), event_id, user["id"]))
        if not cur.rowcount:
            raise HTTPException(404, "Active event not found.")
        event = conn.execute("SELECT id,status,delivery_state,cancelled_at FROM sos_events WHERE id=?", (event_id,)).fetchone()
    return dict(event)


@app.post("/api/tracking/start", status_code=201)
def start_tracking(data: TrackingInput, user=Depends(current_user)):
    session_id = uid()
    with db.connect() as conn:
        owned = {r[0] for r in conn.execute("SELECT id FROM contacts WHERE owner_id=?", (user["id"],))}
        if any(contact_id not in owned for contact_id in data.recipient_ids):
            raise HTTPException(400, "Choose trusted contacts from your account.")
        expires = now() + timedelta(minutes=data.duration_minutes)
        conn.execute("INSERT INTO tracking_sessions VALUES(?,?,?,?,?,?,?,?,?,?)",
                     (session_id, user["id"], json.dumps(data.recipient_ids), "active", data.destination, None, None, None, stamp(), stamp(expires)))
        conn.execute("INSERT INTO consent_events VALUES(?,?,?,?,?,?)", (uid(), user["id"], "track_me_session", 1, "Explicitly started; account-only; contact sharing disabled", stamp()))
    return {"id": session_id, "status": "active", "expires_at": stamp(expires), "external_sharing": False,
            "message": "Journey session is active in your account. Live contact sharing is not configured."}


@app.post("/api/tracking/{session_id}/location")
def update_tracking(session_id: str, data: LocationUpdate, user=Depends(current_user)):
    with db.connect() as conn:
        cur = conn.execute("UPDATE tracking_sessions SET last_latitude=?,last_longitude=?,location_at=? WHERE id=? AND owner_id=? AND status='active' AND expires_at>?",
                           (data.latitude, data.longitude, stamp(), session_id, user["id"], stamp()))
        if not cur.rowcount:
            raise HTTPException(404, "Active journey session not found or expired.")
    return {"id": session_id, "location_recorded": True, "external_sharing": False}


@app.get("/api/tracking/{session_id}")
def get_tracking(session_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        row = conn.execute("SELECT id,status,destination,last_latitude,last_longitude,location_at,created_at,expires_at FROM tracking_sessions WHERE id=? AND owner_id=?", (session_id, user["id"])).fetchone()
    if not row:
        raise HTTPException(404, "Journey session not found.")
    result = dict(row)
    if result["status"] == "active" and result["expires_at"] <= stamp():
        with db.connect() as conn:
            conn.execute("UPDATE tracking_sessions SET status='expired',last_latitude=NULL,last_longitude=NULL,location_at=NULL WHERE id=? AND owner_id=?", (session_id, user["id"]))
        result.update({"status": "expired", "last_latitude": None, "last_longitude": None, "location_at": None})
    return {**result, "external_sharing": False}


@app.post("/api/tracking/{session_id}/stop")
@app.post("/api/tracking/{session_id}/revoke")
def stop_tracking(session_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        cur = conn.execute("UPDATE tracking_sessions SET status='stopped',last_latitude=NULL,last_longitude=NULL,location_at=NULL WHERE id=? AND owner_id=? AND status='active'", (session_id, user["id"]))
        if not cur.rowcount:
            raise HTTPException(404, "Active journey session not found.")
    return {"id": session_id, "status": "stopped", "location_deleted": True}


def tapme_risk_score(data: CheckinInput) -> float:
    score = (0.25 * data.risk_route + 0.15 * data.risk_population + 0.10 * data.risk_time
             + 0.15 * data.risk_isolation + 0.10 * data.risk_deviation
             + 0.10 * data.risk_eta + 0.15 * data.risk_mode)
    return round(max(0.0, min(100.0, score)), 1)


def tapme_checkin_count(duration_minutes: int, risk_score: float) -> int:
    base = math.ceil(duration_minutes / 120)
    return min(12, max(1, math.ceil(base * (1 + risk_score / 100))))


def tapme_checkpoint(started: datetime, duration_minutes: int, total_checkins: int,
                     completed: int, risk_score: float) -> datetime:
    """Weight later checkpoint intervals more tightly as the illustrative risk rises."""
    q = max(0.6, 1 - risk_score / 250)
    weights = [q ** index for index in range(total_checkins)]
    fraction = sum(weights[:min(total_checkins, completed + 1)]) / sum(weights)
    return started + timedelta(minutes=duration_minutes * fraction)


@app.post("/api/checkins/start", status_code=201)
def start_checkins(data: CheckinInput, user=Depends(current_user)):
    started = now()
    risk_score = tapme_risk_score(data)
    total_checkins = tapme_checkin_count(data.duration_minutes, risk_score)
    due = tapme_checkpoint(started, data.duration_minutes, total_checkins, 0, risk_score)
    first_interval = max(1, math.ceil((due - started).total_seconds() / 60))
    journey_id = uid()
    with db.connect() as conn:
        conn.execute("""INSERT INTO journeys(id,owner_id,interval_minutes,grace_minutes,status,destination,next_due_at,created_at,
                      duration_minutes,total_checkins,risk_score,started_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (journey_id, user["id"], first_interval, data.grace_minutes, "active", data.destination,
                      stamp(due), stamp(started), data.duration_minutes, total_checkins, risk_score, stamp(started)))
        conn.execute("INSERT INTO consent_events VALUES(?,?,?,?,?,?)", (uid(), user["id"], "tap_me_journey", 1, "Explicitly started; duration and illustrative risk-based schedule; reminders while app open; no external escalation", stamp()))
    return {"id": journey_id, "status": "active", "next_due_at": stamp(due), "duration_minutes": data.duration_minutes,
            "total_checkins": total_checkins, "checkins_completed": 0, "checkins_remaining": total_checkins,
            "risk_score": risk_score, "risk_model": "illustrative weighted equation; missing inputs use neutral defaults",
            "reminder_mode": "while_app_is_open", "remote_escalation": False}


@app.post("/api/checkins/from-route", status_code=201)
def start_checkins_from_route(data: CheckinFromRouteInput, user=Depends(current_user)):
    """Start a Tap Me checkin cadence directly from a computed Raahi route's duration and risk score."""
    started = now()
    risk_score = round(max(0.0, min(100.0, data.risk_score)), 1)
    total_checkins = tapme_checkin_count(data.duration_minutes, risk_score)
    due = tapme_checkpoint(started, data.duration_minutes, total_checkins, 0, risk_score)
    first_interval = max(1, math.ceil((due - started).total_seconds() / 60))
    journey_id = uid()
    with db.connect() as conn:
        conn.execute("""INSERT INTO journeys(id,owner_id,interval_minutes,grace_minutes,status,destination,next_due_at,created_at,
                      duration_minutes,total_checkins,risk_score,started_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (journey_id, user["id"], first_interval, 5, "active", data.destination,
                      stamp(due), stamp(started), data.duration_minutes, total_checkins, risk_score, stamp(started)))
        conn.execute("INSERT INTO consent_events VALUES(?,?,?,?,?,?)", (uid(), user["id"], "tap_me_journey", 1, f"Started from Raahi route {data.route_id}; risk: {risk_score}", stamp()))
    return {"id": journey_id, "status": "active", "next_due_at": stamp(due), "duration_minutes": data.duration_minutes,
            "total_checkins": total_checkins, "checkins_completed": 0, "checkins_remaining": total_checkins,
            "risk_score": risk_score, "route_id": data.route_id, "derived_from_offline_route": True,
            "reminder_mode": "while_app_is_open", "remote_escalation": False}


@app.get("/api/checkins/{journey_id}")
def get_checkins(journey_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM journeys WHERE id=? AND owner_id=?", (journey_id, user["id"])).fetchone()
        events = conn.execute("SELECT response,created_at FROM checkin_events WHERE journey_id=? ORDER BY created_at DESC", (journey_id,)).fetchall()
    if not row:
        raise HTTPException(404, "Journey not found.")
    result = dict(row)
    if result["status"] == "active" and datetime.fromisoformat(result["next_due_at"]) + timedelta(minutes=result["grace_minutes"]) < now():
        result["status"] = "needs_attention"
        result["escalation"] = "local_status_only_no_contacts_notified"
    result["events"] = [dict(e) for e in events]
    result["checkins_completed"] = len(events)
    result["checkins_remaining"] = max(0, int(result.get("total_checkins", 1)) - len(events))
    return result


@app.post("/api/checkins/{journey_id}/respond")
def respond_checkin(journey_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM journeys WHERE id=? AND owner_id=? AND status='active'", (journey_id, user["id"])).fetchone()
        if not row:
            raise HTTPException(404, "Active journey not found.")
        events_count = conn.execute("SELECT COUNT(*) FROM checkin_events WHERE journey_id=?", (journey_id,)).fetchone()[0]
        conn.execute("INSERT INTO checkin_events VALUES(?,?,?,?)", (uid(), journey_id, "safe", stamp()))
        total = int(row["total_checkins"] or 1)
        completed = events_count + 1
        if completed >= total:
            conn.execute("UPDATE journeys SET status='completed',completed_at=?,next_due_at=? WHERE id=?",
                         (stamp(), stamp(), journey_id))
            return {"id": journey_id, "status": "completed", "last_response": "safe", "checkins_completed": completed,
                    "total_checkins": total, "checkins_remaining": 0, "next_due_at": None}
        started = datetime.fromisoformat(row["started_at"] or row["created_at"])
        due = tapme_checkpoint(started, int(row["duration_minutes"] or 120), total, completed, float(row["risk_score"] or 50))
        due = max(due, now() + timedelta(seconds=15))
        interval = max(1, math.ceil((due - now()).total_seconds() / 60))
        conn.execute("UPDATE journeys SET next_due_at=?,interval_minutes=? WHERE id=?", (stamp(due), interval, journey_id))
    return {"id": journey_id, "status": "active", "last_response": "safe", "next_due_at": stamp(due),
            "checkins_completed": completed, "total_checkins": total, "checkins_remaining": total - completed}


@app.post("/api/checkins/{journey_id}/cancel")
def cancel_checkins(journey_id: str, user=Depends(current_user)):
    with db.connect() as conn:
        cur = conn.execute("UPDATE journeys SET status='cancelled',completed_at=? WHERE id=? AND owner_id=? AND status='active'", (stamp(), journey_id, user["id"]))
        if not cur.rowcount:
            raise HTTPException(404, "Active journey not found.")
    return {"id": journey_id, "status": "cancelled"}


@app.get("/api/places/categories")
def place_categories():
    categories = [("police", "Police stations"), ("hospital", "Hospitals"), ("park", "Parks"),
                  ("public_space", "Public spaces"), ("restaurant", "Restaurants"), ("cafe", "Cafes"),
                  ("directory", "BEFIKR directory"), ("support", "Support organisations")]
    return {"categories": [{"id": key, "label": label} for key, label in categories]}


GOOGLE_PLACE_TYPES = {
    "police": ("police",),
    "hospital": ("hospital", "general_hospital", "medical_clinic", "medical_center"),
    "park": ("park", "city_park", "garden"),
    "public_space": ("library", "community_center", "cultural_center", "plaza"),
    "restaurant": ("restaurant",),
    "cafe": ("cafe", "coffee_shop"),
}
PLACE_LABELS = {
    "police": "Police station", "hospital": "Hospital or clinic", "park": "Park",
    "public_space": "Public space", "restaurant": "Restaurant", "cafe": "Cafe",
    "support": "Support organisation",
}


class NearbyPlacesInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=5, ge=0.1, le=10)
    category: str | None = None
    source: Literal["csv", "google"] = "csv"


class PlaceSearchSession(BaseModel):
    session_token: str = Field(min_length=1, max_length=36, pattern=r"^[A-Za-z0-9_-]+$")


class PlaceAutocompleteInput(PlaceSearchSession):
    model_config = ConfigDict(str_strip_whitespace=True)

    input: str = Field(min_length=2, max_length=200)


class PlaceResolveInput(PlaceSearchSession):
    place_id: str = Field(min_length=1, max_length=512, pattern=r"^[A-Za-z0-9_-]+$")


def google_place_request(path: str, field_mask: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    if not GOOGLE_MAPS_SERVER_KEY:
        raise HTTPException(503, "Google place search is not configured. You can still choose a point on the map.")

    headers = {"X-Goog-Api-Key": GOOGLE_MAPS_SERVER_KEY, "X-Goog-FieldMask": field_mask}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        f"https://places.googleapis.com/v1/{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=8) as result:
            payload = json.loads(result.read(1_000_001))
    except HTTPError as error:
        if error.code == 404 and body is None:
            raise HTTPException(404, "Google Maps could not find this place. Choose another suggestion.") from None
        raise HTTPException(503, "Google place search is unavailable. Try again or choose a point on the map.") from None
    except (OSError, ValueError):
        raise HTTPException(503, "Google place search is unavailable. Try again or choose a point on the map.") from None
    if not isinstance(payload, dict) or "error" in payload:
        raise HTTPException(503, "Google Maps returned an invalid place search response.")
    return payload


@app.post("/api/places/autocomplete")
def autocomplete_places(data: PlaceAutocompleteInput, response: Response, user=Depends(optional_user)):
    response.headers["Cache-Control"] = "no-store"
    from .offline_places import OFFLINE_PLACES
    offline_matches = OFFLINE_PLACES.autocomplete(data.input, limit=10)
    if offline_matches:
        return {"suggestions": offline_matches, "source": "offline_map_data"}

    if GOOGLE_MAPS_SERVER_KEY:
        try:
            payload = google_place_request(
                "places:autocomplete",
                "suggestions.placePrediction.placeId,suggestions.placePrediction.text.text,"
                "suggestions.placePrediction.structuredFormat.mainText.text,"
                "suggestions.placePrediction.structuredFormat.secondaryText.text",
                {
                    "input": data.input,
                    "sessionToken": data.session_token,
                    "includedRegionCodes": ["in"],
                    "regionCode": "in",
                    "locationBias": {"rectangle": {
                        "low": {"latitude": 27.0, "longitude": 75.7},
                        "high": {"latitude": 29.6, "longitude": 78.7},
                    }},
                },
            )
            suggestions = []
            predictions = payload.get("suggestions", [])
            for item in predictions:
                prediction = item.get("placePrediction")
                if not prediction:
                    continue
                place_id = prediction.get("placeId")
                label = (prediction.get("text") or {}).get("text")
                if not place_id or not label:
                    continue
                structured = prediction.get("structuredFormat") or {}
                suggestions.append({
                    "place_id": place_id,
                    "label": label,
                    "name": (structured.get("mainText") or {}).get("text") or label,
                    "address": (structured.get("secondaryText") or {}).get("text") or "",
                })
            if suggestions:
                return {"suggestions": suggestions}
        except Exception:
            pass

    return {"suggestions": offline_matches, "source": "offline_map_data"}


@app.post("/api/places/resolve")
def resolve_place(data: PlaceResolveInput, response: Response, user=Depends(optional_user)):
    response.headers["Cache-Control"] = "no-store"
    from .offline_places import OFFLINE_PLACES
    resolved = OFFLINE_PLACES.resolve(data.place_id)
    if resolved:
        return resolved

    if GOOGLE_MAPS_SERVER_KEY and not data.place_id.startswith("off_"):
        query = urlencode({"sessionToken": data.session_token, "regionCode": "in"})
        try:
            payload = google_place_request(f"places/{data.place_id}?{query}", "id,formattedAddress,location,attributions")
            location = payload.get("location") or {}
            latitude, longitude = location.get("latitude"), location.get("longitude")
            if (isinstance(latitude, (int, float)) and -90 <= latitude <= 90
                    and isinstance(longitude, (int, float)) and -180 <= longitude <= 180):
                return {
                    "place_id": payload.get("id") or data.place_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "address": payload.get("formattedAddress") or "",
                    "attributions": payload.get("attributions") or [],
                }
        except Exception:
            pass

    raise HTTPException(404, "Place coordinates could not be resolved. Please choose another suggestion.")


def google_nearby_places(latitude: float, longitude: float, radius_km: float,
                         category: str | None) -> list[dict[str, Any]]:
    type_categories = {place_type: key for key, types in GOOGLE_PLACE_TYPES.items() for place_type in types}
    body = {
        "includedTypes": GOOGLE_PLACE_TYPES[category] if category else list(type_categories),
        "maxResultCount": 20,
        "rankPreference": "DISTANCE",
        "locationRestriction": {"circle": {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius": radius_km * 1000,
        }},
    }
    fields = ("id", "displayName", "formattedAddress", "location", "types", "primaryType",
              "businessStatus", "attributions")
    request = Request(
        "https://places.googleapis.com/v1/places:searchNearby",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Goog-Api-Key": GOOGLE_MAPS_SERVER_KEY,
                 "X-Goog-FieldMask": ",".join(f"places.{field}" for field in fields)},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        payload = json.load(response)
    if not isinstance(payload, dict) or "error" in payload or not isinstance(payload.get("places", []), list):
        raise ValueError("Invalid Google Places response")

    results = []
    for place in payload.get("places", []):
        place_id = place.get("id")
        if not place_id or place.get("businessStatus") in {"CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"}:
            continue
        point = place.get("location") or {}
        lat, lon = point.get("latitude"), point.get("longitude")
        name = (place.get("displayName") or {}).get("text")
        if lat is None or lon is None or not name:
            continue
        types = place.get("types") or []
        primary = place.get("primaryType")
        if category:
            if not set(GOOGLE_PLACE_TYPES[category]).intersection([primary, *types]):
                continue
            kind = category
        else:
            kind = type_categories.get(primary)
            if not kind:
                kind = next((type_categories[t] for t in types if t in type_categories), None)
            if not kind:
                continue

        distance = distance_km(latitude, longitude, lat, lon)
        if distance > radius_km:
            continue
        results.append({
            "id": f"google-{place_id}", "name": name, "category": kind,
            "category_label": PLACE_LABELS[kind], "address": place.get("formattedAddress") or "",
            "phone": "", "latitude": lat, "longitude": lon, "distance_km": round(distance, 1),
            "source": "Google Maps", "source_kind": "google_places", "google_place_id": place_id,
            "verified_at": None, "attributions": place.get("attributions") or [],
        })
    return sorted(results, key=lambda place: place["distance_km"])


def nearby_directory_places(data: NearbyPlacesInput) -> list[dict[str, Any]]:
    query = "SELECT * FROM places WHERE active=1"
    parameters = ()
    if data.category == "support":
        query += " AND category=?"
        parameters = ("support",)
    with db.connect() as conn:
        rows = conn.execute(query, parameters).fetchall()

    results = []
    for row in rows:
        distance = distance_km(data.latitude, data.longitude, row["latitude"], row["longitude"])
        if distance <= data.radius_km:
            item = dict(row)
            item["distance_km"] = round(distance, 1)
            item["category_label"] = PLACE_LABELS.get(item["category"], item["category"])
            item["source_kind"] = "managed_directory"
            results.append(item)
    return sorted(results, key=lambda place: place["distance_km"])[:100]


def search_nearby_places(data: NearbyPlacesInput) -> dict[str, Any]:
    if data.category is not None and data.category not in {*PLACE_CATEGORIES, "directory"}:
        raise HTTPException(422, "Unsupported Safe Spot category")
    if data.category in {"support", "directory"}:
        places = nearby_directory_places(data)
        return {
            "places": places, "source_state": "curated_directory_only",
            "managed_count": len(places), "google_count": 0, "attribution": None,
            "message": "Listings from the BEFIKR directory.",
            "empty_message": "The BEFIKR directory has no listings near this pin.",
        }

    if data.source == "csv":
        result = nearby_csv_places(data.latitude, data.longitude, data.radius_km, data.category)
        from .offline_places import OFFLINE_PLACES
        nearest_spot, dist = OFFLINE_PLACES.find_nearest_safe_spot(data.latitude, data.longitude, preferred_category="police")
        if nearest_spot:
            result["nearest_safe_spot"] = {
                "id": nearest_spot.id,
                "name": nearest_spot.name,
                "category": nearest_spot.category,
                "address": nearest_spot.address,
                "latitude": nearest_spot.latitude,
                "longitude": nearest_spot.longitude,
                "distance_km": dist
            }
            from .offline_provider import OfflineMappingProvider
            provider = OfflineMappingProvider()
            route_res = provider.alternatives(
                origin="Your Location",
                destination=nearest_spot.name,
                origin_coordinates=(data.latitude, data.longitude),
                destination_coordinates=(nearest_spot.latitude, nearest_spot.longitude),
                context="safe_spot"
            )
            rec_route = route_res.get("recommended_route") or (route_res.get("routes") or [None])[0]
            if rec_route:
                result["safe_route_to_nearest"] = {
                    "distance_km": rec_route.get("distance_km"),
                    "minutes": rec_route.get("minutes"),
                    "risk_score": rec_route.get("risk_score"),
                    "classification": rec_route.get("classification", "GREEN"),
                    "is_safe": rec_route.get("classification") in ("GREEN", "YELLOW") or (rec_route.get("risk_score") is not None and rec_route.get("risk_score") < 65),
                    "geometry": rec_route.get("geometry"),
                    "steps": route_res.get("safe_spot_walking", {}).get("steps", []),
                    "explanation": rec_route.get("tradeoff_explanation", "Direct safe route using evaluated offline road network.")
                }
        return result

    places = []
    source_state = "google_places"
    message = "Nearby places from Google Maps. Distances are straight line estimates."
    empty_message = "Google Maps found no matching places within this radius."
    if not GOOGLE_MAPS_SERVER_KEY:
        source_state = "google_places_not_configured"
        message = empty_message = "Google Maps listings aren’t connected to BEFIKR yet. You can search in Google Maps."
    else:
        try:
            places = google_nearby_places(data.latitude, data.longitude, data.radius_km, data.category)
        except (OSError, ValueError, TypeError, AttributeError, KeyError):
            source_state = "google_places_unavailable"
            message = empty_message = "Google Maps couldn’t load nearby places. Try again or open Google Maps."
    return {
        "places": places, "source_state": source_state, "managed_count": 0,
        "google_count": len(places), "message": message, "empty_message": empty_message,
        "attribution": "Google Maps" if places else None,
    }


@app.post("/api/places/nearby")
def nearby_places_post(data: NearbyPlacesInput, response: Response, user=Depends(optional_user)):
    response.headers["Cache-Control"] = "no-store"
    return search_nearby_places(data)


@app.get("/api/places/nearby")
def nearby_places(
    latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180),
    category: str | None = None, radius_km: float = Query(default=5, ge=0.1, le=10),
    source: Literal["csv", "google"] = "csv", user=Depends(optional_user), *, response: Response = None,
):
    if response is not None:
        response.headers["Cache-Control"] = "no-store"
    return search_nearby_places(NearbyPlacesInput(latitude=latitude, longitude=longitude,
                                                radius_km=radius_km, category=category, source=source))


VOICE_CONTENT = [
    {"caller": "Mother", "voice": "female", "scenarios": [
        {"id": "checking-in", "title": "Checking in", "english": ["Beta, just checking in. Are you okay?", "Call me when you get a moment.", "I’m right here. Take your time."], "hindi": ["हेलो बेटा! हाँ, कहाँ पहुँच गई तू? कब से तेरा इंतज़ार कर रही हूँ मैं।", "अच्छा, और कितनी देर लगेगी? खाना भी लगा दिया है मैंने। तुझे पता है न, मैं तेरे बिना खाना नहीं खाती।", "अच्छा सुन, आज तेरे पापा भी जल्दी घर आ गए हैं। तेरे बारे में ही पूछ रहे थे। कह रहे थे कि बेटी को फ़ोन लगाओ, कहाँ रह गई है।", "और सुन, कल तूने मुझे उस कपड़े के बारे में बताया था न, मैंने वह देख लिया है। बहुत सुंदर है! घर आकर मुझे दोबारा दिखाना।", "अच्छा, एक काम करना। जब तू घर के पास पहुँच जाए न, तो मुझे बता देना। मैं दरवाज़ा खोल दूँगी। और अपना फ़ोन पास ही रखना, समझी?", "चल, ठीक है बेटा। आराम से आना। मैं यहीं हूँ, तेरा इंतज़ार कर रही हूँ।"], "hinglish": ["Hello beta! Haan, kahaan pahunch gayi tu? Kab se tera intezaar kar rahi hoon main.", "Achha, aur kitni der lagegi? Khana bhi laga diya hai maine. Tujhe pata hai na, main tere bina khana nahi khaati.", "Achha sun, aaj tere papa bhi jaldi ghar aa gaye hain. Tere baare mein hi pooch rahe the. Keh rahe the ki beti ko phone lagao, kahaan reh gayi hai.", "Aur sun, kal tune mujhe us kapde ke baare mein bataya tha na, maine woh dekh liya hai. Bahut sundar hai! Ghar aakar mujhe dobara dikhana.", "Achha, ek kaam karna. Jab tu ghar ke paas pahunch jaaye na, toh mujhe bata dena. Main darwaaza khol doongi. Aur apna phone paas hi rakhna, samjhi?", "Chal, theek hai beta. Aaram se aana. Main yahin hoon, tera intezaar kar rahi hoon."]},
        {"id": "worried", "title": "Worried", "english": ["Beta, I haven’t heard from you in a while. Is everything okay?", "Please call me when you can. I’m getting worried.", "I can come get you. Just let me know what you need."], "hindi": ["बेटा, काफ़ी देर से तुम्हारा जवाब नहीं आया। सब ठीक है?", "जब हो सके मुझे कॉल करना, मुझे चिंता हो रही है।", "अगर चाहो तो मैं तुम्हें लेने आ जाऊँ। बस बता देना।"], "hinglish": ["Beta, kaafi der se tumhara jawab nahi aaya. Sab theek hai?", "Jab ho sake mujhe call karna, mujhe chinta ho rahi hai.", "Agar chaho toh main tumhe lene aa jaaun. Bas bata dena."]},
    ]},
    {"caller": "Father", "voice": "male", "scenarios": [
        {"id": "checking-in", "title": "Checking in", "english": ["Hey, just checking—are things going okay?", "I wanted to see how your evening is going.", "Call me when you’re free, no rush."], "hindi": ["बेटा, बस पूछ रहा हूँ—सब ठीक चल रहा है?", "तुम्हारी शाम कैसी जा रही है, यही जानना था।", "फुर्सत मिले तो कॉल करना, कोई जल्दी नहीं।"], "hinglish": ["Beta, bas pooch raha hoon—sab theek chal raha hai?", "Tumhari shaam kaisi ja rahi hai, yahi jaan-na tha.", "Fursat mile toh call karna, koi jaldi nahi."]},
        {"id": "worried", "title": "Worried", "english": ["I haven’t been able to reach you. Is everything all right?", "Call me as soon as you can; I’m concerned.", "Would you like me to come pick you up?"], "hindi": ["तुमसे बात नहीं हो पा रही है। सब ठीक तो है?", "जब हो सके मुझे कॉल करना, मुझे फ़िक्र हो रही है।", "क्या मैं तुम्हें लेने आ जाऊँ?"], "hinglish": ["Tumse baat nahi ho paa rahi hai. Sab theek toh hai?", "Jab ho sake mujhe call karna, mujhe fikr ho rahi hai.", "Kya main tumhe lene aa jaaun?"]},
    ]},
    {"caller": "Sister", "voice": "female", "scenarios": [
        {"id": "checking-in", "title": "Checking in", "english": ["Hey, just checking in. Did you get there okay?", "Call me when you get a chance.", "I’m here if you need anything."], "hindi": ["सुन, बस पूछ रही हूँ—तुम ठीक से पहुँच गई?", "मौका मिले तो मुझे कॉल करना।", "कुछ चाहिए तो मैं यहीं हूँ।"], "hinglish": ["Sun, bas pooch rahi hoon—tum theek se pahunch gayi?", "Mauka mile toh mujhe call karna.", "Kuch chahiye toh main yahin hoon."]},
        {"id": "worried", "title": "Worried", "english": ["I haven’t heard from you in a while. Is everything okay?", "I’m getting worried—please call me when you can.", "Want me to come meet you?"], "hindi": ["काफ़ी देर से तुम्हारा मैसेज नहीं आया। सब ठीक है?", "मुझे चिंता हो रही है—हो सके तो कॉल करना।", "क्या मैं तुमसे मिलने आ जाऊँ?"], "hinglish": ["Kaafi der se tumhara message nahi aaya. Sab theek hai?", "Mujhe chinta ho rahi hai—ho sake toh call karna.", "Kya main tumse milne aa jaaun?"]},
    ]},
    {"caller": "Brother", "voice": "male", "scenarios": [
        {"id": "checking-in", "title": "Checking in", "english": ["Hey, just checking—are you doing okay?", "Let me know when you get a minute.", "I’m around if you need me."], "hindi": ["सुन, बस पूछ रहा हूँ—सब ठीक है?", "फुर्सत मिले तो मुझे बता देना।", "ज़रूरत हो तो मैं यहीं हूँ।"], "hinglish": ["Sun, bas pooch raha hoon—sab theek hai?", "Fursat mile toh mujhe bata dena.", "Zaroorat ho toh main yahin hoon."]},
        {"id": "worried", "title": "Worried", "english": ["You haven’t replied for a while. Is everything all right?", "I’m a bit worried—call me when you can.", "Should I come pick you up?"], "hindi": ["काफ़ी देर से तुम्हारा जवाब नहीं आया। सब ठीक तो है?", "थोड़ी चिंता हो रही है—हो सके तो कॉल करना।", "क्या मैं तुम्हें लेने आ जाऊँ?"], "hinglish": ["Kaafi der se tumhara jawab nahi aaya. Sab theek toh hai?", "Thodi chinta ho rahi hai—ho sake toh call karna.", "Kya main tumhe lene aa jaaun?"]},
    ]},
    {"caller": "Boyfriend", "voice": "male", "scenarios": [
        {"id": "checking-in", "title": "Checking in", "english": ["Hey, just checking in. Are you doing okay?", "Call me when you get a chance.", "I’m here if you need me."], "hindi": ["अरे, बस पूछ रहा था—तुम ठीक हो?", "मौका मिले तो मुझे कॉल कर लेना।", "मैं यहीं हूँ, अगर तुम्हें मेरी ज़रूरत हो।"], "hinglish": ["Arey, bas pooch raha tha—tum theek ho?", "Mauka mile toh mujhe call kar lena.", "Main yahin hoon, agar tumhe meri zaroorat ho."]},
        {"id": "worried", "title": "Worried", "english": ["I haven’t heard from you for a bit. Is everything okay?", "I’m getting a little worried—please call when you can.", "If you want, I can come meet you."], "hindi": ["काफ़ी देर से तुम्हारी ख़बर नहीं मिली। सब ठीक है?", "थोड़ी चिंता हो रही है—हो सके तो मुझे कॉल करना।", "अगर चाहो तो मैं तुमसे मिलने आ जाऊँ।"], "hinglish": ["Kaafi der se tumhari khabar nahi mili. Sab theek hai?", "Thodi chinta ho rahi hai—ho sake toh mujhe call karna.", "Agar chaho toh main tumse milne aa jaaun."]},
    ]},
]
VOICE_SCRIPTS = [
    {"id": f"{person['caller'].lower()}-{scenario['id']}-{language.lower()}", "title": scenario["title"], "situation": scenario["id"], "scenario": scenario["id"], "scenario_label": scenario["title"], "caller": person["caller"], "voice": person["voice"], "language": language, "lines": scenario["hindi"] if language == "Hindi" else scenario["english"], **({"hinglish_lines": scenario["hinglish"]} if language == "Hindi" else {})}
    for person in VOICE_CONTENT for scenario in person["scenarios"] for language in ("English", "Hindi")
]

MOM_CHECKING_HINDI_DIALOGUE = [
    {"speaker": "mother", "text": "हेलो बेटा! हाँ, कहाँ पहुँच गई तू? कब से तेरा इंतज़ार कर रही हूँ मैं।", "hinglish": "Hello beta! Haan, kahaan pahunch gayi tu? Kab se tera intezaar kar rahi hoon main.", "audio": "/assets/baat-banao/mom-checking-in-hi/01.mp3"},
    {"speaker": "daughter", "text": "बस माँ, आ रही हूँ।", "hinglish": "Bas Maa, aa rahi hoon."},
    {"speaker": "mother", "text": "अच्छा, और कितनी देर लगेगी? खाना भी लगा दिया है मैंने। तुझे पता है न, मैं तेरे बिना खाना नहीं खाती।", "hinglish": "Achha, aur kitni der lagegi? Khana bhi laga diya hai maine. Tujhe pata hai na, main tere bina khana nahi khaati.", "audio": "/assets/baat-banao/mom-checking-in-hi/02.mp3"},
    {"speaker": "daughter", "text": "हाँ माँ, बस थोड़ी देर में पहुँच जाऊँगी।", "hinglish": "Haan Maa, bas thodi der mein pahunch jaaungi."},
    {"speaker": "mother", "text": "अच्छा सुन, आज तेरे पापा भी जल्दी घर आ गए हैं। तेरे बारे में ही पूछ रहे थे। कह रहे थे कि बेटी को फ़ोन लगाओ, कहाँ रह गई है।", "hinglish": "Achha sun, aaj tere papa bhi jaldi ghar aa gaye hain. Tere baare mein hi pooch rahe the. Keh rahe the ki beti ko phone lagao, kahaan reh gayi hai.", "audio": "/assets/baat-banao/mom-checking-in-hi/03.mp3"},
    {"speaker": "daughter", "text": "अच्छा, ठीक है माँ।", "hinglish": "Achha, theek hai Maa."},
    {"speaker": "mother", "text": "और सुन, कल तूने मुझे उस कपड़े के बारे में बताया था न, मैंने वह देख लिया है। बहुत सुंदर है! घर आकर मुझे दोबारा दिखाना।", "hinglish": "Aur sun, kal tune mujhe us kapde ke baare mein bataya tha na, maine woh dekh liya hai. Bahut sundar hai! Ghar aakar mujhe dobara dikhana.", "audio": "/assets/baat-banao/mom-checking-in-hi/04.mp3"},
    {"speaker": "daughter", "text": "हाँ माँ, दिखा दूँगी।", "hinglish": "Haan Maa, dikha doongi."},
    {"speaker": "mother", "text": "अच्छा, एक काम करना। जब तू घर के पास पहुँच जाए न, तो मुझे बता देना। मैं दरवाज़ा खोल दूँगी। और अपना फ़ोन पास ही रखना, समझी?", "hinglish": "Achha, ek kaam karna. Jab tu ghar ke paas pahunch jaaye na, toh mujhe bata dena. Main darwaaza khol doongi. Aur apna phone paas hi rakhna, samjhi?", "audio": "/assets/baat-banao/mom-checking-in-hi/05.mp3"},
    {"speaker": "daughter", "text": "हाँ माँ।", "hinglish": "Haan Maa."},
    {"speaker": "mother", "text": "चल, ठीक है बेटा। आराम से आना। मैं यहीं हूँ, तेरा इंतज़ार कर रही हूँ।", "hinglish": "Chal, theek hai beta. Aaram se aana. Main yahin hoon, tera intezaar kar rahi hoon.", "audio": "/assets/baat-banao/mom-checking-in-hi/06.mp3"},
]
MOM_CHECKING_ENGLISH_DIALOGUE = [
    {"speaker": "mother", "text": "Hello, sweetheart! Hey, where have you reached? I've been waiting for you for so long."},
    {"speaker": "daughter", "text": "I'm coming, Mom. I'll be there soon."},
    {"speaker": "mother", "text": "Alright, how much longer will you take? I've already served dinner. You know I never eat without you."},
    {"speaker": "daughter", "text": "Yes, Mom. Just a little while longer."},
    {"speaker": "mother", "text": 'Listen, your father came home early today as well. He was asking about you. He said, "Call our daughter and ask where she has been."'},
    {"speaker": "daughter", "text": "Oh, okay, Mom."},
    {"speaker": "mother", "text": "And listen, remember that dress you told me about yesterday? I found it! It's really beautiful. Show it to me again when you get home."},
    {"speaker": "daughter", "text": "Yes, Mom. I'll show you."},
    {"speaker": "mother", "text": "Alright, do one thing. Let me know when you're close to home. I'll open the gate for you. And keep your phone with you, understood?"},
    {"speaker": "daughter", "text": "Yes, Mom."},
    {"speaker": "mother", "text": "Alright, sweetheart. Come home safely and take your time. I'll be right here waiting for you."},
]
MOM_WORRIED_HINDI_DIALOGUE = [
    {"speaker": "mother", "text": "नमस्ते! बेटा, मेरी आवाज़ सुनाई दे रही है? हाँ, अब बता, सब ठीक है न?", "hinglish": "Namaste! Beta, meri awaaz sunai de rahi hai? Haan, ab bata, sab theek hai na?"},
    {"speaker": "daughter", "text": "हाँ माँ, सब ठीक है।", "hinglish": "Haan Maa, sab theek hai."},
    {"speaker": "mother", "text": "अच्छा। आज तेरा दिन कैसा रहा? सुबह तो बड़ी जल्दी में निकली थी तू।", "hinglish": "Achha. Aaj tera din kaisa raha? Subah toh badi jaldi mein nikli thi tu."},
    {"speaker": "daughter", "text": "हाँ माँ, थोड़ा काम था।", "hinglish": "Haan Maa, thoda kaam tha."},
    {"speaker": "mother", "text": "अच्छा, वह जो तूने बताया था न कि आज तेरा कोई ज़रूरी काम है, वह हो गया?", "hinglish": "Achha, woh jo tune bataya tha na ki aaj tera koi zaroori kaam hai, woh ho gaya?"},
    {"speaker": "daughter", "text": "हाँ, हो गया।", "hinglish": "Haan, ho gaya."},
    {"speaker": "mother", "text": "चलो, अच्छी बात है। देख बेटा, घर आकर आराम करना। मैं तेरे लिए चाय बना दूँगी। और हाँ, तेरे पसंदीदा पकौड़े भी बना रखे हैं।", "hinglish": "Chalo, achhi baat hai. Dekh beta, ghar aakar aaram karna. Main tere liye chai bana doongi. Aur haan, tere pasandeeda pakode bhi bana rakhe hain."},
    {"speaker": "daughter", "text": "अच्छा माँ!", "hinglish": "Achha Maa!"},
    {"speaker": "mother", "text": "हाँ, हाँ! और सुन, पापा भी बस थोड़ी देर में आ जाएँगे। वे कह रहे थे कि आज सब साथ बैठकर खाना खाएँगे।", "hinglish": "Haan, haan! Aur sun, papa bhi bas thodi der mein aa jaayenge. Woh keh rahe the ki aaj sab saath baithkar khana khaayenge."},
    {"speaker": "daughter", "text": "ठीक है माँ।", "hinglish": "Theek hai Maa."},
    {"speaker": "mother", "text": "अच्छा, तू मुझसे बात करती रह। मुझे भी तेरे साथ थोड़ी देर बातें करनी हैं। बहुत दिन हो गए, हमने ढंग से बात ही नहीं की।", "hinglish": "Achha, tu mujhse baat karti reh. Mujhe bhi tere saath thodi der baatein karni hain. Bahut din ho gaye, humne dhang se baat hi nahi ki."},
]
MOM_WORRIED_HINDI_LOOP = [
    {"speaker": "mother", "text": "हम्म, अच्छा।", "hinglish": "Hmm, achha.", "loop": True},
]
MOM_WORRIED_ENGLISH_DIALOGUE = [
    {"speaker": "mother", "text": "Hello! Sweetheart, can you hear me? Yes, now tell me, everything is alright, isn't it?"},
    {"speaker": "daughter", "text": "Yes, Mom. Everything is fine."},
    {"speaker": "mother", "text": "Alright. How was your day today? You left in such a hurry this morning."},
    {"speaker": "daughter", "text": "Yes, Mom. I had some work to take care of."},
    {"speaker": "mother", "text": "Oh, right! You told me you had something important to do today. Did everything go well?"},
    {"speaker": "daughter", "text": "Yes, it did."},
    {"speaker": "mother", "text": "That's good to hear. Listen, sweetheart, make sure you get some rest when you come home. I'll make some tea for you. And yes, I've also made your favourite pakoras."},
    {"speaker": "daughter", "text": "Oh, lovely, Mom!"},
    {"speaker": "mother", "text": "Of course! And listen, your father will be home in a little while too. He said we should all sit together and have dinner today."},
    {"speaker": "daughter", "text": "Alright, Mom."},
    {"speaker": "mother", "text": "Now, keep talking to me. I want to chat with you for a little while too. It's been so long since we've had a proper conversation."},
]
MOM_WORRIED_ENGLISH_LOOP = [
    {"speaker": "mother", "text": "Hmm, okay.", "loop": True},
]
for voice_script in VOICE_SCRIPTS:
    if voice_script["id"] == "mother-checking-in-hindi":
        voice_script["dialogue"] = MOM_CHECKING_HINDI_DIALOGUE
        voice_script["lines"] = [turn["text"] for turn in MOM_CHECKING_HINDI_DIALOGUE if turn["speaker"] == "mother"]
        voice_script["hinglish_lines"] = [turn["hinglish"] for turn in MOM_CHECKING_HINDI_DIALOGUE if turn["speaker"] == "mother"]
    elif voice_script["id"] == "mother-checking-in-english":
        voice_script["dialogue"] = MOM_CHECKING_ENGLISH_DIALOGUE
        voice_script["lines"] = [turn["text"] for turn in MOM_CHECKING_ENGLISH_DIALOGUE if turn["speaker"] == "mother"]
    elif voice_script["id"] == "mother-worried-hindi":
        voice_script["title"] = "Worried Mom"
        voice_script["scenario_label"] = "Worried Mom"
        voice_script["dialogue"] = MOM_WORRIED_HINDI_DIALOGUE
        voice_script["lines"] = [turn["text"] for turn in MOM_WORRIED_HINDI_DIALOGUE if turn["speaker"] == "mother"]
        voice_script["hinglish_lines"] = [turn["hinglish"] for turn in MOM_WORRIED_HINDI_DIALOGUE if turn["speaker"] == "mother"]
        voice_script["loop_turns"] = MOM_WORRIED_HINDI_LOOP
    elif voice_script["id"] == "mother-worried-english":
        voice_script["title"] = "Worried Mom"
        voice_script["scenario_label"] = "Worried Mom"
        voice_script["dialogue"] = MOM_WORRIED_ENGLISH_DIALOGUE
        voice_script["lines"] = [turn["text"] for turn in MOM_WORRIED_ENGLISH_DIALOGUE if turn["speaker"] == "mother"]
        voice_script["loop_turns"] = MOM_WORRIED_ENGLISH_LOOP



@app.get("/api/voice/scripts")
def voice_scripts():
    catalog = recording_catalog()
    return {"scripts": [attach_recordings(script, catalog) for script in VOICE_SCRIPTS],
            "mode": "supplied MP3 recordings only", "real_call": False,
            "recording_count": catalog["recording_count"], "revision": catalog["revision"]}


@app.get("/api/voice/scripts/{script_id}")
def voice_script(script_id: str):
    script = next((item for item in VOICE_SCRIPTS if item["id"] == script_id), None)
    if not script:
        raise HTTPException(404, "Script not found.")
    return attach_recordings(script, recording_catalog())


@app.get("/api/admin/dashboard")
def admin_dashboard(user=Depends(admin_user)):
    with db.connect() as conn:
        counts = {row["status"]: row["n"] for row in conn.execute("SELECT status,COUNT(*) AS n FROM reports GROUP BY status")}
        total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
        appeals = conn.execute("SELECT COUNT(*) FROM appeals WHERE status='pending'").fetchone()[0]
        sos_count = conn.execute("SELECT COUNT(*) FROM sos_events WHERE created_at>=?", (stamp(now() - timedelta(days=30)),)).fetchone()[0]
    return {"total_users": total_users, "reports": counts, "pending_review": counts.get("pending_review", 0) + counts.get("submitted", 0),
            "pending_appeals": appeals, "sos_events_30d": sos_count, "safe_spots": "administrator_managed",
            "integrations": capabilities(), "note": "SOS totals are account events, not confirmed dispatched alerts."}


@app.get("/api/admin/reports")
def admin_reports(status: str | None = None, user=Depends(admin_user)):
    with db.connect() as conn:
        audit(conn, user["id"], "sensitive_reports_queue_viewed", "reports_queue", status or "all", "Narratives and approximate locations accessed by authorised staff")
        rows = conn.execute("SELECT r.*,u.email AS reporter_email FROM reports r JOIN users u ON u.id=r.owner_id" + (" WHERE r.status=?" if status in REPORT_STATUSES else "") + " ORDER BY r.created_at DESC LIMIT 200", ((status,) if status in REPORT_STATUSES else ())).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["history"] = []
        with db.connect() as conn:
            item["evidence"] = evidence.report_attachments(conn, row["id"])
            item["history"] = [dict(h) for h in conn.execute("SELECT old_status,new_status,reason,created_at FROM report_history WHERE report_id=? ORDER BY created_at", (row["id"],))]
            peers = []
            if row["latitude"] is not None and row["longitude"] is not None:
                peers = conn.execute("SELECT id,owner_id,created_at FROM reports WHERE id<>? AND category=? AND status<>'rejected' AND ROUND(latitude,2)=ROUND(?,2) AND ROUND(longitude,2)=ROUND(?,2)",
                                     (row["id"], row["category"], row["latitude"], row["longitude"])).fetchall()
        submitted = datetime.fromisoformat(row["created_at"])
        if submitted.tzinfo is None:
            submitted = submitted.replace(tzinfo=timezone.utc)
        nearby_reporters = set()
        for peer in peers:
            peer_created = datetime.fromisoformat(peer["created_at"])
            if peer_created.tzinfo is None:
                peer_created = peer_created.replace(tzinfo=timezone.utc)
            if abs((submitted - peer_created).total_seconds()) <= 86400:
                nearby_reporters.add(peer["owner_id"])
        item["nearby_similar_reporters"] = len(nearby_reporters)
        result.append(item)
    return result


@app.patch("/api/admin/reports/{report_id}/status")
def moderate_report(report_id: str, data: ModerationInput, user=Depends(admin_user)):
    with db.connect() as conn:
        report = conn.execute("SELECT status FROM reports WHERE id=?", (report_id,)).fetchone()
        if not report:
            raise HTTPException(404, "Report not found.")
        transitions = {
            "submitted": {"pending_review", "under_review"},
            "pending_review": {"under_review"},
            "under_review": {"corroborated", "validated", "rejected"},
            "corroborated": {"under_review", "validated", "rejected"},
            "validated": {"under_review", "rejected"},
            "rejected": {"under_review"},
        }
        if data.status != report["status"] and data.status not in transitions.get(report["status"], set()):
            raise HTTPException(409, f"Cannot change a report from {report['status']} to {data.status} in one step.")
        if report["status"] == "validated" and data.status != "validated" and not data.reason.strip():
            raise HTTPException(400, "A reason is required to change a validated report.")
        moment = stamp()
        conn.execute("UPDATE reports SET status=?,internal_reason=?,updated_at=? WHERE id=?", (data.status, data.reason.strip(), moment, report_id))
        conn.execute("INSERT INTO report_history VALUES(?,?,?,?,?,?,?)", (uid(), report_id, user["id"], report["status"], data.status, data.reason.strip(), moment))
        audit(conn, user["id"], "report_status_changed", "report", report_id, data.status)
        return {"id": report_id, "previous_status": report["status"], "status": data.status}


@app.get("/api/admin/appeals")
def admin_appeals(user=Depends(admin_user)):
    with db.connect() as conn:
        return [dict(row) for row in conn.execute("SELECT id,report_id,message,status,created_at FROM appeals WHERE status='pending' ORDER BY created_at")]


@app.patch("/api/admin/appeals/{appeal_id}")
def review_appeal(appeal_id: str, decision: str = Query(pattern="^(upheld|reopen)$"), user=Depends(admin_user)):
    with db.connect() as conn:
        appeal = conn.execute("SELECT report_id FROM appeals WHERE id=? AND status='pending'", (appeal_id,)).fetchone()
        if not appeal:
            raise HTTPException(404, "Pending appeal not found.")
        conn.execute("UPDATE appeals SET status=? WHERE id=?", (decision, appeal_id))
        if decision == "reopen":
            report = conn.execute("SELECT status FROM reports WHERE id=?", (appeal["report_id"],)).fetchone()
            conn.execute("UPDATE reports SET status='under_review',updated_at=? WHERE id=?", (stamp(), appeal["report_id"]))
            conn.execute("INSERT INTO report_history VALUES(?,?,?,?,?,?,?)", (uid(), appeal["report_id"], user["id"], report["status"], "under_review", "Reopened after appeal", stamp()))
        audit(conn, user["id"], "appeal_reviewed", "appeal", appeal_id, decision)
    return {"id": appeal_id, "status": decision, "report_status": "under_review" if decision == "reopen" else "rejected"}


@app.get("/api/admin/places")
def admin_places(user=Depends(admin_user)):
    with db.connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM places ORDER BY updated_at DESC")]


@app.get("/api/admin/place-candidates")
def admin_place_candidates(status: str = Query(default="pending", pattern="^(pending|approved|rejected|all)$"),
                           user=Depends(admin_user)):
    query = "SELECT * FROM place_candidates"
    params: tuple[Any, ...] = ()
    if status != "all":
        query += " WHERE status=?"
        params = (status,)
    query += " ORDER BY created_at DESC LIMIT 500"
    with db.connect() as conn:
        return [dict(row) for row in conn.execute(query, params)]


@app.post("/api/admin/place-candidates/import", status_code=201)
def import_place_candidates(data: PlaceCandidateBatch, user=Depends(admin_user)):
    imported, duplicates = 0, 0
    moment = stamp()
    batch_id = uid()
    with db.connect() as conn:
        for candidate in data.candidates:
            stable = "|".join((candidate.name.strip().casefold(), candidate.category,
                               f"{candidate.latitude:.5f}", f"{candidate.longitude:.5f}", candidate.source_url.strip()))
            candidate_key = hashlib.sha256(stable.encode("utf-8")).hexdigest()
            result = conn.execute("""INSERT INTO place_candidates
                (id,candidate_key,name,category,address,latitude,longitude,phone,source_url,source_date,dataset_id,status,review_notes,created_at,reviewed_at,reviewed_by)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,'pending','',?,NULL,NULL)
                ON CONFLICT(candidate_key) DO NOTHING""",
                (uid(), candidate_key, candidate.name.strip(), candidate.category, candidate.address.strip(),
                 candidate.latitude, candidate.longitude, candidate.phone.strip(), candidate.source_url.strip(),
                 candidate.source_date, candidate.dataset_id, moment))
            imported += result.rowcount
            duplicates += 1 - result.rowcount
        audit(conn, user["id"], "tinyfish_places_imported", "place_candidate_batch", batch_id,
              json.dumps({"imported": imported, "duplicates": duplicates}, separators=(",", ":")))
    return {"batch_id": batch_id, "imported": imported, "duplicates": duplicates,
            "status": "pending_review", "message": "Imported rows are private candidates and are not shown in Safe Spots until an administrator reviews and approves them."}


@app.patch("/api/admin/place-candidates/{candidate_id}")
def review_place_candidate(candidate_id: str, data: PlaceCandidateReview, user=Depends(admin_user)):
    moment = stamp()
    with db.connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        candidate = conn.execute("SELECT * FROM place_candidates WHERE id=? AND status='pending'", (candidate_id,)).fetchone()
        if not candidate:
            raise HTTPException(404, "Pending place candidate not found.")
        place_id = None
        if data.decision == "approve":
            duplicate = conn.execute("""SELECT id FROM places WHERE category=? AND lower(name)=lower(?)
                AND ABS(latitude-?)<0.0001 AND ABS(longitude-?)<0.0001 LIMIT 1""",
                (candidate["category"], candidate["name"], candidate["latitude"], candidate["longitude"])).fetchone()
            if duplicate:
                place_id = duplicate["id"]
            else:
                place_id = uid()
                source_host = urlparse(candidate["source_url"]).netloc
                conn.execute("""INSERT INTO places
                    (id,name,category,address,latitude,longitude,phone,source,source_url,verified_at,active,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (place_id, candidate["name"], candidate["category"], candidate["address"],
                     candidate["latitude"], candidate["longitude"], candidate["phone"],
                     f"TinyFish source · {source_host}"[:200], candidate["source_url"], moment, 1, moment, moment))
        conn.execute("UPDATE place_candidates SET status=?,review_notes=?,reviewed_at=?,reviewed_by=? WHERE id=?",
                     ("approved" if data.decision == "approve" else "rejected", data.notes.strip(), moment,
                      user["id"], candidate_id))
        audit(conn, user["id"], f"place_candidate_{data.decision}", "place_candidate", candidate_id,
              json.dumps({"place_id": place_id, "source_url": candidate["source_url"], "notes": data.notes.strip()}, ensure_ascii=False))
    if data.decision == "reject":
        message = "Candidate rejected."
    elif duplicate:
        message = "Candidate reviewed. A matching directory listing already exists."
    else:
        message = "Listing added to the Safe Spot directory."
    return {"id": candidate_id, "status": "approved" if data.decision == "approve" else "rejected",
            "place_id": place_id, "source_url": candidate["source_url"], "message": message}


@app.post("/api/admin/places", status_code=201)
def create_place(data: PlaceInput, user=Depends(admin_user)):
    place_id, moment = uid(), stamp()
    with db.connect() as conn:
        conn.execute("""INSERT INTO places
            (id,name,category,address,latitude,longitude,phone,source,source_url,verified_at,active,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (place_id, data.name.strip(), data.category, data.address.strip(), data.latitude,
             data.longitude, data.phone.strip(), data.source.strip(), data.source_url, data.verified_at,
             int(data.active), moment, moment))
        audit(conn, user["id"], "place_created", "place", place_id)
    return {"id": place_id, **data.model_dump()}


@app.patch("/api/admin/places/{place_id}")
def update_place(place_id: str, data: PlaceInput, user=Depends(admin_user)):
    with db.connect() as conn:
        cur = conn.execute("UPDATE places SET name=?,category=?,address=?,latitude=?,longitude=?,phone=?,source=?,source_url=?,verified_at=?,active=?,updated_at=? WHERE id=?",
                           (data.name.strip(), data.category, data.address.strip(), data.latitude, data.longitude,
                            data.phone.strip(), data.source.strip(), data.source_url, data.verified_at, int(data.active), stamp(), place_id))
        if not cur.rowcount:
            raise HTTPException(404, "Safe Spot not found.")
        audit(conn, user["id"], "place_updated", "place", place_id)
    return {"id": place_id, **data.model_dump()}


@app.get("/api/admin/audit-logs")
def admin_audit_logs(limit: int = Query(default=100, ge=1, le=500), user=Depends(admin_user)):
    with db.connect() as conn:
        return [dict(row) for row in conn.execute("SELECT id,actor_id,action,target_type,target_id,detail,created_at FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))]


if os.path.isdir(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
