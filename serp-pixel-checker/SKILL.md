---
name: serp-pixel-checker
description: Check meta title and description pixel widths against Google SERP limits (580px title, 990px description). Use when validating SEO metadata, checking SERP pixel lengths, or auditing meta tags — whether single strings, small batches, or full spreadsheets.
---

# SERP Pixel Width Checker

Google truncates SERP snippets by **pixel width**, not character count. This skill validates meta titles and descriptions using the same font rendering Google uses (Arial, via Pillow's FreeType engine). Tested to within 0-4px of browser-based SERP pixel checkers.

## Pixel Limits

| Field | Font | Size | Max Pixels |
|-------|------|------|------------|
| Title | Arial | 20px | 580px |
| Description | Arial | 14px | 990px |

## Usage

Always use the Python script `serp_pixel_calculator.py` located in this skill's directory (next to this file).

### Single string

```
python "<skill-dir>/serp_pixel_calculator.py" --title "Your Meta Title" --desc "Your meta description text here"
```

Add `--json` for machine-readable output.

### Spreadsheet batch

```
python "<skill-dir>/serp_pixel_calculator.py" batch --file "<path>" --sheet "<sheet>" [--title-col <letter>] [--desc-col <letter>] [--start-row <n>]
```

Add `--json` for machine-readable output.

## Workflow

1. **Identify what to check.** If `$ARGUMENTS` contains a file path or string, use it. Otherwise ask.
2. **Run the script** against the input (single string or batch).
3. **Present results** as a clear table showing pixels, limit, and OK/OVER status.
4. **If items are over the limit**, offer to suggest shortened versions.

## Platform Support

The script auto-detects Arial on **Windows**, **macOS**, and **Linux**:

- **Windows** — uses `%WINDIR%\Fonts\arial.ttf`
- **macOS** — checks `/Library/Fonts/`, `/System/Library/Fonts/Supplemental/`, and `~/Library/Fonts/`
- **Linux** — checks for MS core fonts or falls back to Liberation Sans / DejaVu Sans

If Arial isn't found, set the `SERP_FONT_PATH` environment variable to your font file:
```
SERP_FONT_PATH=/path/to/arial.ttf python serp_pixel_calculator.py --title "Test"
```

On Linux, install Arial with:
```
sudo apt install ttf-mscorefonts-installer
# or the metrically-compatible alternative:
sudo apt install fonts-liberation
```

## Dependencies

The script requires `pillow` (and `openpyxl` for batch Excel mode):

```
pip install pillow openpyxl
```

