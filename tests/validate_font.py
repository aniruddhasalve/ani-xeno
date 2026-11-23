#!/usr/bin/env python3
"""Validate Ani Xeno binaries and write an evidence report.

This intentionally treats an empty fonts/ directory as a pre-release state,
not as a successful font test.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIRS = [ROOT / "fonts" / "otf", ROOT / "fonts" / "ttf", ROOT / "fonts" / "webfonts"]
REPORT_DIR = ROOT / "evidence" / "reports"
REQUIRED_NAME = "Ani Xeno"
REQUIRED_AUTHOR = "Aniruddha Salve"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def names(font: TTFont) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    if "name" not in font:
        return result
    for record in font["name"].names:
        key = str(record.nameID)
        try:
            value = record.toUnicode()
        except Exception:
            value = "<undecodable>"
        if value not in result.setdefault(key, []):
            result[key].append(value)
    return result


def validate(path: Path) -> dict:
    item = {"file": str(path.relative_to(ROOT)), "sha256": sha256(path), "checks": {}}
    try:
        font = TTFont(path, recalcBBoxes=False, recalcTimestamp=False)
        n = names(font)
        family_values = n.get("1", [])
        full_values = n.get("4", [])
        designer_values = n.get("9", [])
        item["checks"] = {
            "opens": True,
            "has_name_table": "name" in font,
            "family_is_ani_xeno": REQUIRED_NAME in family_values,
            "full_name_present": bool(full_values),
            "designer_is_aniruddha_salve": REQUIRED_AUTHOR in designer_values,
            "has_unicode_map": "cmap" in font and bool(font["cmap"].tables),
            "glyph_count": len(font.getGlyphOrder()),
        }
        item["names"] = {"family": family_values, "full": full_values, "designer": designer_values}
        item["status"] = "pass" if all(v is True for k, v in item["checks"].items() if isinstance(v, bool)) else "fail"
    except Exception as exc:
        item["status"] = "fail"
        item["checks"] = {"opens": False}
        item["error"] = repr(exc)
    return item


def main() -> int:
    files = sorted(p for d in FONT_DIRS if d.exists() for p in d.iterdir() if p.suffix.lower() in {".otf", ".ttf", ".woff", ".woff2"})
    now = datetime.now(timezone.utc).isoformat()
    report = {"project": REQUIRED_NAME, "generated_at": now, "status": "pre-release", "files": []}
    if files:
        report["files"] = [validate(p) for p in files]
        report["status"] = "pass" if all(x["status"] == "pass" for x in report["files"]) else "fail"
    else:
        report["message"] = "No generated font binaries found. Add source-derived fonts before release testing."
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out = REPORT_DIR / f"{stamp}__font-validation.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Evidence report: {out}")
    return 0 if report["status"] in {"pre-release", "pass"} else 1


if __name__ == "__main__":
    sys.exit(main())
