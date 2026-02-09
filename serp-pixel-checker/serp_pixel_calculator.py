"""
SERP Pixel Length Calculator
Measures meta title and description pixel widths using HarfBuzz text shaping
with the same fonts browsers use for Google SERPs.

Requires uharfbuzz. Accurate to within 0-1px across all scripts: Latin,
Cyrillic, Greek, Arabic, Thai, Chinese/CJK, and more.

Title:       arial,sans-serif 20px, max 580px
Description: arial,sans-serif 14px, max 990px

Usage (single string):
    python serp_pixel_calculator.py --title "Your Page Title Here"
    python serp_pixel_calculator.py --desc "Your meta description here"
    python serp_pixel_calculator.py --title "Title" --desc "Description"
    python serp_pixel_calculator.py --json --title "Title" --desc "Desc"

Usage (batch Excel):
    python serp_pixel_calculator.py batch --file "data.xlsx" --sheet "Sheet1" --title-col E --desc-col H
    python serp_pixel_calculator.py batch --file "data.xlsx" --sheet "DE MD" --desc-col L --start-row 2
"""

import sys
import os
import platform
import argparse
import json

import uharfbuzz as hb

TITLE_FONT_SIZE = 20
DESC_FONT_SIZE = 14
TITLE_MAX_PX = 580
DESC_MAX_PX = 990


# ---------------------------------------------------------------------------
# Font discovery
# ---------------------------------------------------------------------------

def _find_font(names, label="font"):
    """Search system font directories for a font file by candidate names."""
    system = platform.system()
    if system == "Windows":
        dirs = [os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")]
    elif system == "Darwin":
        dirs = [
            "/Library/Fonts",
            "/System/Library/Fonts/Supplemental",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    else:
        dirs = [
            "/usr/share/fonts/truetype/msttcorefonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/TTF",
            "/usr/share/fonts",
        ]

    for d in dirs:
        for name in names:
            path = os.path.join(d, name)
            if os.path.isfile(path):
                return path
    return None


def _find_arial():
    path = os.environ.get("SERP_FONT_PATH")
    if path and os.path.isfile(path):
        return path

    path = _find_font(["arial.ttf", "Arial.ttf"])
    if path:
        return path

    # Fallbacks for Linux
    path = _find_font([
        "LiberationSans-Regular.ttf",
        "liberation-sans/LiberationSans-Regular.ttf",
        "DejaVuSans.ttf",
    ])
    if path:
        return path

    print("Error: Could not find Arial font.", file=sys.stderr)
    print("Set SERP_FONT_PATH environment variable to your font file.", file=sys.stderr)
    if platform.system() == "Linux":
        print("Install with: sudo apt install ttf-mscorefonts-installer", file=sys.stderr)
    sys.exit(1)


def _find_thai_font():
    return _find_font([
        "tahoma.ttf", "Tahoma.ttf",
        "leelawui.ttf", "LeelawUI.ttf",
        "Leelawad.ttf",
    ], "Thai")


def _find_cjk_font():
    return _find_font([
        "msyh.ttc", "msyh.ttf",
        "NotoSansCJKsc-Regular.otf", "NotoSansSC-Regular.otf",
        "wqy-microhei.ttc",
    ], "CJK")


def _find_korean_font():
    return _find_font([
        "malgun.ttf", "MalgunGothic.ttf",
        "NotoSansKR-Regular.otf", "NotoSansKR-Regular.ttf",
    ], "Korean")


ARIAL_PATH = _find_arial()
THAI_FONT_PATH = _find_thai_font()
CJK_FONT_PATH = _find_cjk_font()
KOREAN_FONT_PATH = _find_korean_font()


# ---------------------------------------------------------------------------
# Script detection
# ---------------------------------------------------------------------------

def _detect_script(text):
    """Detect the dominant non-Latin script in text to select the right font."""
    for ch in text:
        cp = ord(ch)
        # Thai
        if 0x0E00 <= cp <= 0x0E7F:
            return "thai"
        # Korean Hangul Syllables and Jamo
        if (0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF or
                0x3130 <= cp <= 0x318F or 0xA960 <= cp <= 0xA97F or
                0xD7B0 <= cp <= 0xD7FF):
            return "korean"
        # CJK Unified Ideographs, Extension A, Radicals, Hiragana, Katakana,
        # CJK Symbols, Fullwidth Forms
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
                0x2E80 <= cp <= 0x2EFF or 0x3000 <= cp <= 0x303F or
                0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF or
                0xFF00 <= cp <= 0xFFEF or 0x20000 <= cp <= 0x2A6DF):
            return "cjk"
    return "default"


def _font_path_for_text(text):
    """Return the appropriate font path for the given text."""
    script = _detect_script(text)
    if script == "thai" and THAI_FONT_PATH:
        return THAI_FONT_PATH
    if script == "korean" and KOREAN_FONT_PATH:
        return KOREAN_FONT_PATH
    if script == "cjk" and CJK_FONT_PATH:
        return CJK_FONT_PATH
    return ARIAL_PATH


# ---------------------------------------------------------------------------
# HarfBuzz measurement engine
# ---------------------------------------------------------------------------

_hb_face_cache = {}


def _get_hb_face(font_path):
    if font_path not in _hb_face_cache:
        with open(font_path, "rb") as f:
            blob = hb.Blob(f.read())
        _hb_face_cache[font_path] = hb.Face(blob, 0)
    return _hb_face_cache[font_path]


def _measure_harfbuzz(text, font_size, font_path):
    face = _get_hb_face(font_path)
    font = hb.Font(face)
    upem = face.upem

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    total_advance = sum(pos.x_advance for pos in buf.glyph_positions)
    return round(total_advance * font_size / upem)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_pixel_width(text: str, font_size: int) -> int:
    """Measure pixel width of text at the given font size.
    Uses HarfBuzz with automatic font fallback for all scripts.
    """
    font_path = _font_path_for_text(text)
    return _measure_harfbuzz(text, font_size, font_path)


def check_title(text: str) -> dict:
    px = get_pixel_width(text, TITLE_FONT_SIZE)
    return {
        "text": text,
        "type": "title",
        "chars": len(text),
        "pixels": px,
        "max_pixels": TITLE_MAX_PX,
        "remaining_px": TITLE_MAX_PX - px,
        "ok": px <= TITLE_MAX_PX,
    }


def check_description(text: str) -> dict:
    px = get_pixel_width(text, DESC_FONT_SIZE)
    return {
        "text": text,
        "type": "description",
        "chars": len(text),
        "pixels": px,
        "max_pixels": DESC_MAX_PX,
        "remaining_px": DESC_MAX_PX - px,
        "ok": px <= DESC_MAX_PX,
    }


def format_result(result: dict) -> str:
    status = "OK" if result["ok"] else "OVER"
    label = result["type"].upper()
    return (
        f"[{status}] {label}: {result['pixels']}px / {result['max_pixels']}px "
        f"({result['remaining_px']:+d}px) | {result['chars']} chars\n"
        f"       {result['text']}"
    )


# ---------------------------------------------------------------------------
# Batch mode
# ---------------------------------------------------------------------------

def col_letter_to_index(letter: str) -> int:
    result = 0
    for char in letter.upper():
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1


def run_batch(args):
    import openpyxl

    wb = openpyxl.load_workbook(args.file, read_only=True, data_only=True)
    ws = wb[args.sheet]

    start_row = args.start_row or 2
    title_col = col_letter_to_index(args.title_col) if args.title_col else None
    desc_col = col_letter_to_index(args.desc_col) if args.desc_col else None

    if title_col is None and desc_col is None:
        print("Error: specify at least one of --title-col or --desc-col")
        sys.exit(1)

    title_over = []
    desc_over = []
    title_ok_count = 0
    desc_ok_count = 0
    title_total = 0
    desc_total = 0

    for row in ws.iter_rows(min_row=start_row):
        row_num = row[0].row

        if title_col is not None:
            cell_val = row[title_col].value
            if cell_val and str(cell_val).strip():
                text = str(cell_val).strip()
                result = check_title(text)
                result["row"] = row_num
                title_total += 1
                if result["ok"]:
                    title_ok_count += 1
                else:
                    title_over.append(result)

        if desc_col is not None:
            cell_val = row[desc_col].value
            if cell_val and str(cell_val).strip():
                text = str(cell_val).strip()
                result = check_description(text)
                result["row"] = row_num
                desc_total += 1
                if result["ok"]:
                    desc_ok_count += 1
                else:
                    desc_over.append(result)

    wb.close()

    output = {"file": args.file, "sheet": args.sheet}

    if title_col is not None:
        output["title"] = {
            "total": title_total,
            "ok": title_ok_count,
            "over": len(title_over),
            "max_px": TITLE_MAX_PX,
            "over_rows": [
                {"row": r["row"], "pixels": r["pixels"], "over_by": abs(r["remaining_px"]),
                 "chars": r["chars"], "text": r["text"]}
                for r in title_over
            ],
        }

    if desc_col is not None:
        output["description"] = {
            "total": desc_total,
            "ok": desc_ok_count,
            "over": len(desc_over),
            "max_px": DESC_MAX_PX,
            "over_rows": [
                {"row": r["row"], "pixels": r["pixels"], "over_by": abs(r["remaining_px"]),
                 "chars": r["chars"], "text": r["text"]}
                for r in desc_over
            ],
        }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"File:  {args.file}")
        print(f"Sheet: {args.sheet}")
        print()

        if "title" in output:
            t = output["title"]
            print(f"TITLES: {t['ok']}/{t['total']} OK | {t['over']} over {TITLE_MAX_PX}px limit")
            if t["over_rows"]:
                print(f"  {'Row':<6} {'Pixels':<10} {'Over by':<10} {'Text'}")
                print(f"  {'---':<6} {'------':<10} {'-------':<10} {'----'}")
                for r in t["over_rows"]:
                    text_preview = r["text"][:70] + "..." if len(r["text"]) > 70 else r["text"]
                    print(f"  {r['row']:<6} {r['pixels']:<10} +{r['over_by']}px{'':<5} {text_preview}")
            print()

        if "description" in output:
            d = output["description"]
            print(f"DESCRIPTIONS: {d['ok']}/{d['total']} OK | {d['over']} over {DESC_MAX_PX}px limit")
            if d["over_rows"]:
                print(f"  {'Row':<6} {'Pixels':<10} {'Over by':<10} {'Text'}")
                print(f"  {'---':<6} {'------':<10} {'-------':<10} {'----'}")
                for r in d["over_rows"]:
                    text_preview = r["text"][:70] + "..." if len(r["text"]) > 70 else r["text"]
                    print(f"  {r['row']:<6} {r['pixels']:<10} +{r['over_by']}px{'':<5} {text_preview}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SERP pixel length calculator")
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("--title", type=str, help="Meta title to measure")
    parser.add_argument("--desc", type=str, help="Meta description to measure")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    batch_parser = subparsers.add_parser("batch", help="Check an Excel file")
    batch_parser.add_argument("--file", required=True, help="Path to Excel file")
    batch_parser.add_argument("--sheet", required=True, help="Sheet name")
    batch_parser.add_argument("--title-col", type=str, help="Column letter for titles (e.g. E)")
    batch_parser.add_argument("--desc-col", type=str, help="Column letter for descriptions (e.g. H)")
    batch_parser.add_argument("--start-row", type=int, default=2, help="First data row (default: 2)")
    batch_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "batch":
        run_batch(args)
    elif args.title or args.desc:
        results = []
        if args.title:
            results.append(check_title(args.title))
        if args.desc:
            results.append(check_description(args.desc))

        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for r in results:
                print(format_result(r))
                print()
    else:
        parser.print_help()
        sys.exit(1)
