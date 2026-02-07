"""
SERP Pixel Length Calculator
Measures meta title and description pixel widths using Arial font,
matching Google's SERP rendering.

Title:       Arial 20px, max 580px
Description: Arial 14px, max 990px

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
from PIL import ImageFont

TITLE_FONT_SIZE = 20
DESC_FONT_SIZE = 14
TITLE_MAX_PX = 580
DESC_MAX_PX = 990
DESC_CORRECTION = 0.98  # Pillow over-reports desc widths by ~2% vs browser canvas


def _find_arial() -> str:
    """Locate Arial font across Windows, macOS, and Linux."""
    candidates = []
    system = platform.system()

    if system == "Windows":
        windir = os.environ.get("WINDIR", "C:\\Windows")
        candidates = [
            os.path.join(windir, "Fonts", "arial.ttf"),
            "C:/Windows/Fonts/arial.ttf",
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Arial.ttf",
            os.path.expanduser("~/Library/Fonts/Arial.ttf"),
        ]
    else:  # Linux
        candidates = [
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    # Last resort: let Pillow try to find it
    try:
        ImageFont.truetype("arial.ttf", 14)
        return "arial.ttf"
    except OSError:
        pass

    print("Error: Could not find Arial font.", file=sys.stderr)
    if system == "Linux":
        print("Install it with: sudo apt install ttf-mscorefonts-installer", file=sys.stderr)
        print("Or Liberation Sans: sudo apt install fonts-liberation", file=sys.stderr)
    print("You can also set the SERP_FONT_PATH environment variable.", file=sys.stderr)
    sys.exit(1)


ARIAL_PATH = os.environ.get("SERP_FONT_PATH") or _find_arial()

# Cache fonts so we don't reload per cell
_font_cache = {}


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(ARIAL_PATH, size)
    return _font_cache[size]


def get_pixel_width(text: str, font_size: int) -> int:
    return round(_get_font(font_size).getlength(text))


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
    px = round(get_pixel_width(text, DESC_FONT_SIZE) * DESC_CORRECTION)
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


def col_letter_to_index(letter: str) -> int:
    """Convert Excel column letter (A, B, ..., Z, AA, AB, ...) to 0-based index."""
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

    # Output
    output = {
        "file": args.file,
        "sheet": args.sheet,
    }

    if title_col is not None:
        output["title"] = {
            "total": title_total,
            "ok": title_ok_count,
            "over": len(title_over),
            "max_px": TITLE_MAX_PX,
            "over_rows": [
                {
                    "row": r["row"],
                    "pixels": r["pixels"],
                    "over_by": abs(r["remaining_px"]),
                    "chars": r["chars"],
                    "text": r["text"],
                }
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
                {
                    "row": r["row"],
                    "pixels": r["pixels"],
                    "over_by": abs(r["remaining_px"]),
                    "chars": r["chars"],
                    "text": r["text"],
                }
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

    # Single string mode (default)
    parser.add_argument("--title", type=str, help="Meta title to measure")
    parser.add_argument("--desc", type=str, help="Meta description to measure")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Batch mode
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
