---
name: serp-pixel-checker
description: Check meta title and description pixel widths against Google SERP limits (580px title, 990px description). Use when validating SEO metadata, checking SERP pixel lengths, or auditing meta tags — whether single strings, small batches, or full spreadsheets.
---

# SERP Pixel Width Checker

Google truncates SERP snippets by **pixel width**, not character count. This skill validates meta titles and descriptions using HarfBuzz text shaping with automatic font fallback — the same rendering pipeline browsers use. Accurate to within 0-1px across all scripts.

## SERP Limits

Google renders titles at **20px** (max **580px**) and descriptions at **14px** (max **990px**). The CSS rule is `font-family: arial, sans-serif` — browsers fall back to system fonts for scripts Arial doesn't cover.

| Script | Font Used | Accuracy |
|--------|-----------|----------|
| Latin, Cyrillic, Greek, Arabic | Arial | 0–1px |
| Korean | Malgun Gothic | 0–5px |
| Thai | Tahoma | 0–5px |
| Chinese / Japanese / CJK | Microsoft YaHei | 0–4px |

Fonts are auto-detected from system directories. The script selects the correct font based on Unicode script detection.

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

The script auto-detects fonts on **Windows**, **macOS**, and **Linux**:

- **Arial** — Primary font for Latin, Cyrillic, Greek, Arabic
- **Malgun Gothic** — Auto-detected for Korean (Hangul)
- **Tahoma** — Auto-detected for Thai script
- **Microsoft YaHei** / Noto Sans CJK — Auto-detected for Chinese/Japanese/CJK

Override the primary font with `SERP_FONT_PATH` environment variable.

## Dependencies

```
pip install uharfbuzz openpyxl
```
