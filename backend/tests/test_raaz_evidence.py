"""HTTP evidence workflow using a temporary database and private directory."""

import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from app import db, evidence, main


class RaazEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.old_data, self.old_db = db.DATA_PATH, db.DB_PATH
        db.DATA_PATH = Path(self.directory.name)
        db.DB_PATH = db.DATA_PATH / "test.db"
        db.initialize()
        self.client = TestClient(main.app)
        self.owner = self.account("owner")
        self.other = self.account("other")
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2), "red").save(buffer, format="PNG")
        self.photo = buffer.getvalue()

    def tearDown(self):
        self.client.close()
        db.DATA_PATH, db.DB_PATH = self.old_data, self.old_db
        self.directory.cleanup()

    def account(self, name):
        result = main.register(main.RegisterInput(name=name, email=f"{name}@example.test", password="test-password-123"))
        return {"user": result["user"], "headers": {"Authorization": f"Bearer {result['access_token']}"}}

    def upload(self, account=None, content=None, mime="image/png", filename="evidence.png"):
        return self.client.post("/api/evidence", content=self.photo if content is None else content,
                                headers={**(account or self.owner)["headers"], "Content-Type": mime, "X-Filename": filename})

    def report(self, attachment_id, account=None, **extra):
        return self.client.post("/api/reports", json={"category": "poor lighting",
            "description": "Street lights are not working on this road.", "evidence_ids": [attachment_id], **extra},
            headers=(account or self.owner)["headers"])

    def test_private_upload_report_link_owner_and_reviewer_access(self):
        uploaded = self.upload(filename="..%2Fprivate.png")
        self.assertEqual(uploaded.status_code, 201, uploaded.text)
        item = uploaded.json()
        path = evidence.evidence_path(item["id"])
        self.assertEqual(path.parent, db.DATA_PATH / "evidence")
        self.assertEqual(path.read_bytes(), self.photo)
        self.assertEqual(self.client.get(f"/api/evidence/{item['id']}").status_code, 401)
        self.assertEqual(self.client.get(f"/api/evidence/{item['id']}", headers=self.other["headers"]).status_code, 404)
        with db.connect() as conn:
            conn.execute("UPDATE users SET role='moderator' WHERE id=?", (self.other["user"]["id"],))
        self.assertEqual(self.client.get(f"/api/evidence/{item['id']}", headers=self.other["headers"]).status_code, 404)
        report = self.report(item["id"], latitude=0, longitude=0, location_label="Selected incident location", location_place_id="place-test")
        self.assertEqual(report.status_code, 201, report.text)
        listed = self.client.get("/api/reports", headers=self.owner["headers"]).json()[0]
        self.assertEqual(listed["evidence"][0]["id"], item["id"])
        self.assertEqual(listed["location_label"], "Selected incident location")
        self.assertNotIn("latitude", listed)
        download = self.client.get(f"/api/evidence/{item['id']}", headers=self.other["headers"])
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.content, self.photo)
        self.assertEqual(download.headers["cache-control"], "no-store")
        self.assertEqual(download.headers["x-content-type-options"], "nosniff")
        self.assertIn("attachment", download.headers["content-disposition"])
        queue = self.client.get("/api/admin/reports", headers=self.other["headers"]).json()
        self.assertEqual(queue[0]["evidence"][0]["id"], item["id"])

    def test_invalid_empty_and_disguised_files_leave_no_private_file(self):
        for content, mime, status in [(b"<script>bad</script>", "image/png", 422),
                                      (self.photo, "image/jpeg", 422), (b"", "image/png", 422),
                                      (b"hello", "text/html", 415), (b"fake video", "video/mp4", 422)]:
            with self.subTest(mime=mime, status=status):
                result = self.upload(content=content, mime=mime)
                self.assertEqual(result.status_code, status, result.text)
        self.assertEqual(list((db.DATA_PATH / "evidence").glob("*")), [])
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM report_evidence").fetchone()[0], 0)

    def test_stream_size_limit_and_upload_authentication(self):
        with patch.object(evidence, "MAX_BYTES", 20):
            result = self.upload()
        self.assertEqual(result.status_code, 413)
        self.assertEqual(list((db.DATA_PATH / "evidence").glob("*")), [])
        self.assertEqual(self.client.post("/api/evidence", content=self.photo, headers={"Content-Type": "image/png"}).status_code, 401)

    def test_unowned_or_reused_attachment_cannot_be_attached(self):
        item = self.upload().json()
        self.assertEqual(self.report(item["id"], self.other).status_code, 422)
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0], 0)
        self.assertEqual(self.report(item["id"]).status_code, 201)
        self.assertEqual(self.report(item["id"]).status_code, 422)

    def test_remove_draft_but_preserve_submitted_evidence(self):
        item = self.upload().json()
        self.assertEqual(self.client.delete(f"/api/evidence/{item['id']}", headers=self.other["headers"]).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/evidence/{item['id']}", headers=self.owner["headers"]).status_code, 204)
        self.assertFalse(evidence.evidence_path(item["id"]).exists())
        item = self.upload().json()
        self.report(item["id"])
        self.assertEqual(self.client.delete(f"/api/evidence/{item['id']}", headers=self.owner["headers"]).status_code, 409)

    def test_report_attachment_count_duplicate_ids_and_partial_location_are_rejected(self):
        body = {"category": "poor lighting", "description": "The street lights are broken."}
        for change in ({"evidence_ids": ["same", "same"]}, {"evidence_ids": ["a", "b", "c", "d"]}, {"latitude": 28.6}):
            result = self.client.post("/api/reports", json={**body, **change}, headers=self.owner["headers"])
            self.assertEqual(result.status_code, 422, result.text)

    def test_account_deletion_removes_private_evidence_files(self):
        item = self.upload().json()
        self.report(item["id"])
        self.assertEqual(self.client.delete("/api/profile", headers=self.owner["headers"]).status_code, 204)
        self.assertFalse(evidence.evidence_path(item["id"]).exists())

    def test_database_upgrade_is_repeatable_and_preserves_reports(self):
        result = main.create_report(main.ReportInput(category="poor lighting", description="A street light is broken."), self.owner["user"])
        db.initialize()
        db.initialize()
        self.assertEqual(main.list_reports(self.owner["user"])[0]["id"], result["id"])
