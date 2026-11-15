"""Supplied Baat Banao recordings: mapping, transcript isolation and numeric ordering."""

import json
from collections import Counter
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import urlsplit

from app import main
from app.baat_recordings import ASSET_ROOT, TRANSCRIPTS_PATH, attach_recordings, recording_catalog, supplied_transcripts


class BaatRecordingTests(unittest.TestCase):
    def test_all_twenty_scripts_use_all_141_local_recordings(self):
        catalog = recording_catalog()
        self.assertEqual(len(catalog["scripts"]), 20)
        self.assertEqual(catalog["recording_count"], 141)
        self.assertEqual(len(set(catalog["assets"])), 141)
        for url in catalog["assets"]:
            path = ASSET_ROOT / urlsplit(url).path.removeprefix("/assets/baat-banao/")
            self.assertTrue(path.is_file(), url)
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"ID3") or (data[0] == 255 and data[1] & 224 == 224), str(path))

    def test_generated_offline_manifest_matches_the_actual_files(self):
        self.assertEqual(json.loads((ASSET_ROOT / "recordings.json").read_text(encoding="utf-8")), recording_catalog())

    def test_scripts_are_mapped_to_their_own_character_language_and_scenario(self):
        catalog = recording_catalog()
        for script_id, entry in catalog["scripts"].items():
            expected_character = "mom" if script_id.startswith("mother-") else script_id.split("-")[0]
            self.assertIn(expected_character, entry["folder"])
            self.assertEqual(entry["folder"].endswith("-hi"), script_id.endswith("-hindi"))
            self.assertEqual(entry["folder"].startswith("worried-"), "-worried-" in script_id)
            self.assertTrue(all(f"/{entry['folder']}/" in url for url in entry["audio_clips"]))
        sister = catalog["scripts"]["sister-worried-english"]["audio_clips"]
        self.assertTrue(urlsplit(sister[8]).path.endswith("/9.mp3"))
        self.assertTrue(urlsplit(sister[9]).path.endswith("/10.mp3"))

    def test_all_supplied_transcripts_match_caller_audio_and_user_turns_have_no_audio(self):
        result = main.voice_scripts()
        self.assertEqual(result["recording_count"], 141)
        for script in result["scripts"]:
            caller_turns = [turn for turn in script["dialogue"] if turn["speaker"] not in {"user", "daughter"}]
            user_turns = [turn for turn in script["dialogue"] if turn["speaker"] in {"user", "daughter"}]
            self.assertEqual([turn["audio"] for turn in caller_turns], script["audio_clips"])
            self.assertTrue(all("audio" not in turn for turn in user_turns))
            self.assertFalse(script["transcript_pending"])
            self.assertEqual(script["missing_audio_turns"], [])
            self.assertEqual(script["lines"], [turn["text"] for turn in caller_turns])
            if script["id"] == "mother-checking-in-hindi":
                self.assertTrue(script["lines"][0].startswith("हेलो बेटा!"))
            self.assertEqual(script["loop_turns"], [])

    def test_missing_sequence_number_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            folder = root / "father-checking-in-hi"
            folder.mkdir()
            (folder / "2.mp3").write_bytes(b"ID3test")
            with self.assertRaises(ValueError):
                recording_catalog(root)

    def test_attaching_audio_does_not_modify_original_scripts(self):
        original = {"id": "father-checking-in-english", "lines": ["Old placeholder"]}
        result = attach_recordings(original, recording_catalog())
        self.assertEqual(original["lines"], ["Old placeholder"])
        self.assertEqual(result["lines"][0], supplied_transcripts()[original["id"]]["dialogue"][0]["text"])

    def test_the_nineteen_source_transcripts_are_preserved_except_requested_removal(self):
        source = TRANSCRIPTS_PATH.with_name("baat_transcripts_supplied.txt").read_text(encoding="utf-8-sig")
        lines = [match[2] for line in source.splitlines()
                 if (match := re.match(r"^([^:]{1,30})\s*:\s*(.+)$", line.strip()))]
        scripts = supplied_transcripts()
        removed = scripts["sister-worried-hindi"]["removed_caller_lines"][0]
        expected = Counter(lines)
        expected[removed] -= 1
        actual = Counter(turn["text"] for key, entry in scripts.items()
                         if key != "mother-checking-in-hindi" for turn in entry["dialogue"])
        self.assertEqual(actual, +expected)
        self.assertNotIn(removed, [turn["text"] for turn in scripts["sister-worried-hindi"]["dialogue"]])
        self.assertEqual(len(recording_catalog()["scripts"]["sister-worried-hindi"]["audio_clips"]), 9)

    def test_hinglish_exists_for_every_caller_and_user_turn_of_all_ten_hindi_scripts(self):
        scripts = supplied_transcripts()
        hindi = [entry for key, entry in scripts.items() if key.endswith("-hindi")]
        self.assertEqual(len(hindi), 10)
        for entry in hindi:
            for turn in entry["dialogue"]:
                self.assertTrue(turn["hinglish"].strip())
                self.assertNotRegex(turn["hinglish"], r"[\u0900-\u097f]")

    def test_identically_labelled_sister_replies_stay_silent_in_both_languages(self):
        for script_id in ("sister-checking-in-hindi", "sister-checking-in-english",
                          "sister-worried-hindi", "sister-worried-english"):
            script = main.voice_script(script_id)
            self.assertTrue(any(t["speaker"] == "user" for t in script["dialogue"]))
            for turn in script["dialogue"]:
                self.assertEqual("audio" in turn, turn["speaker"] == "caller")
