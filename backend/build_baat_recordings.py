"""Run from the project root: python backend/build_baat_recordings.py."""

import json

from app.baat_recordings import ASSET_ROOT, recording_catalog


if __name__ == "__main__":
    catalog = recording_catalog()
    data = json.dumps(catalog, ensure_ascii=False, indent=2)
    (ASSET_ROOT / "recordings.json").write_text(data + "\n", encoding="utf-8")
    (ASSET_ROOT / "recordings.js").write_text("globalThis.BEFIKR_RECORDINGS = " + data + ";\n", encoding="utf-8")
    print(f"Indexed {catalog['recording_count']} supplied recordings for {len(catalog['scripts'])} scripts.")
