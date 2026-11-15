"""Index only supplied caller recordings. Never generate or substitute speech."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

ASSET_ROOT = Path(__file__).resolve().parents[2] / "web" / "assets" / "baat-banao"
TRANSCRIPTS_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "baat_transcripts.json"


def supplied_transcripts() -> dict:
    scripts = json.loads(TRANSCRIPTS_PATH.read_text(encoding="utf-8"))
    for script_id, script in scripts.items():
        for turn in script["dialogue"]:
            if turn.get("speaker") not in {"caller", "user"} or not turn.get("text") or "audio" in turn:
                raise ValueError(f"Invalid transcript speaker/text in {script_id}")
            if script_id.endswith("-hindi") and not turn.get("hinglish"):
                raise ValueError(f"Missing Hinglish transcript in {script_id}")
    return scripts


def recording_catalog(root: Path = ASSET_ROOT) -> dict:
    scripts = {}
    transcripts = supplied_transcripts()
    for character in ("mother", "father", "sister", "brother", "boyfriend"):
        folder_character = "mom" if character == "mother" else character
        for scenario in ("checking-in", "worried"):
            for language, suffix in (("Hindi", "hi"), ("English", "eng")):
                folder = f"{folder_character}-checking-in-{suffix}" if scenario == "checking-in" else f"worried-{folder_character}-{suffix}"
                clips = []
                for path in (root / folder).glob("*.mp3"):
                    match = re.fullmatch(r"(\d+)\.mp3", path.name, re.IGNORECASE)
                    if match and path.stat().st_size:
                        clips.append((int(match[1]), path))
                clips.sort(key=lambda entry: entry[0])
                numbers = [number for number, _ in clips]
                if numbers != list(range(1, len(clips) + 1)):
                    raise ValueError(f"Missing or duplicate recording numbers in {folder}")
                urls = []
                for _, path in clips:
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
                    urls.append(f"/assets/baat-banao/{folder}/{path.name}?v={digest}")
                loop = root / folder / "loop.mp3"
                loop_url = None
                if loop.is_file() and loop.stat().st_size:
                    digest = hashlib.sha256(loop.read_bytes()).hexdigest()[:12]
                    loop_url = f"/assets/baat-banao/{folder}/loop.mp3?v={digest}"
                script_id = f"{character}-{scenario}-{language.lower()}"
                dialogue = deepcopy(transcripts.get(script_id, {}).get("dialogue", []))
                caller_count = sum(turn["speaker"] == "caller" for turn in dialogue)
                scripts[script_id] = {"folder": folder, "audio_clips": urls, "loop_audio": loop_url,
                                      "transcript_pending": not bool(dialogue), "dialogue": dialogue,
                                      "caller_turn_count": caller_count,
                                      "missing_audio_turns": list(range(len(urls) + 1, caller_count + 1))}
    assets = [url for script in scripts.values() for url in [*script["audio_clips"], script["loop_audio"]] if url]
    content = {"scripts": scripts, "assets": assets, "recording_count": len(assets)}
    content["revision"] = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:12]
    return content


def attach_recordings(script: dict, catalog: dict) -> dict:
    result = deepcopy(script)
    entry = catalog["scripts"].get(script["id"], {})
    clips = entry.get("audio_clips", [])
    result.update(audio_clips=clips, audio_count=len(clips), transcript_pending=entry.get("transcript_pending", True))
    if not result["transcript_pending"]:
        result["dialogue"] = deepcopy(entry["dialogue"])
        result["loop_turns"] = []
        result["lines"] = [turn["text"] for turn in result["dialogue"] if turn["speaker"] == "caller"]
        result["hinglish_lines"] = [turn["hinglish"] for turn in result["dialogue"]
                                    if turn["speaker"] == "caller" and "hinglish" in turn]
        result["missing_audio_turns"] = entry.get("missing_audio_turns", [])
        index = 0
        for turn in result.get("dialogue", []):
            turn.pop("audio", None)
            if turn.get("speaker") not in {"daughter", "user"}:
                if index < len(clips):
                    turn["audio"] = clips[index]
                index += 1
    else:
        # Transcripts will be added by the user. Do not pair these files with old canned lines.
        result.update(lines=[], hinglish_lines=[], dialogue=[], loop_turns=[])
        for index, audio in enumerate(clips):
            result["dialogue"].append({"speaker": "caller", "text": "", "audio": audio, "transcript_pending": True})
            if index < len(clips) - 1:
                result["dialogue"].append({"speaker": "user", "text": "", "transcript_pending": True})
    if entry.get("loop_audio"):
        result["loop_turns"] = [{"speaker": "caller", "text": "", "audio": entry["loop_audio"],
                                 "loop": True, "transcript_pending": result["transcript_pending"]}]
    return result
