# Copilot Instructions for Rare Book Database

## Project Overview

This is a Python-based web scraper project that automatically extracts rare book data from **Le Bouquin Français** website and maintains a curated database. The primary deliverable is a database that will power an Android app for ISBN-based book pricing and availability lookup.

**Core Purpose**: Extract "livres recherchés" (searched/rare books) from `lebouquinfrancais.fr`, parse ISBN/title/author information, and maintain a clean text database for downstream consumption.

## Running the Scraper

### Full Database Update
```bash
python scrape_lbf.py
```
This fetches all current rare books from Le Bouquin Français, dedups them, and outputs to `rare_books.txt`.

### Dependencies
```bash
pip install -r requirements.txt
```

## Architecture & Key Concepts

### Data Flow
1. **Web Scraping** (`scrape_lbf.py`): HTTP request to Le Bouquin Français, HTML parsing with BeautifulSoup
2. **Text Extraction**: Per-row HTML table parsing; concatenates all `<td>` cells into searchable text
3. **ISBN Detection**: Regex pattern matching for ISBN-10 (`\d{9}[\dX]`) or ISBN-13 (`97[89]\d{10}`)
4. **Title/Author Parsing**: Attempts three extraction strategies in order: pipe delimiter (`|`), dash delimiter (` - `), or fallback
5. **Deduplication**: Converts to set to remove duplicate tuples
6. **Output**: UTF-8 formatted text file with comment header and pipe-delimited columns

### File Formats

**`rare_books.txt`** (output):
```
# Liste des livres recherchés (Bouquin Français)
# Format : Titre | Auteur | ISBN

Titre du Livre | Auteur Nom | 9781234567890
```

### Critical Functions

- **`extract_isbn(text)`**: Finds ISBN within text using regex. Returns first match or None.
- **`clean_text(t)`**: Removes known HTML artifacts/UI strings before parsing (e.g., "critique(s)", "lecteurs", "Aucune offre aujourd'hui")
- **`scrape_lbf()`**: Main orchestration—fetches page, parses rows, extracts ISBN for each, deduplicates, writes output

## Conventions & Patterns

### Text Cleaning
The `parasites` list in `clean_text()` contains hardcoded UI strings that appear in table cells but don't belong in book metadata. **If scraping breaks or produces garbage data**, the website HTML likely changed—update the `parasites` list first.

### ISBN Handling
- Accepts both ISBN-10 and ISBN-13 formats in a single regex pattern
- Acts as the primary deduplication key (uses set() on full tuples)
- If an item has no valid ISBN, it's skipped entirely

### Delimiter Precedence
Title/author splitting tries `|` first, then ` - `, then gives up and uses title-only. This reflects the current website's inconsistent formatting.

### Headers & User-Agent
The `HEADERS` dict with a full Chrome user-agent is intentional—required to avoid bot detection on the target website.

## Automated Execution

A GitHub Actions workflow (`.github/worflows/update.yml`) runs daily at 03:00 UTC, executes the scraper, and auto-commits changes. **Note the typo in folder name** (`worflows` not `workflows`)—this is intentional for this repo.

If changes occur, git will commit with message: `"Mise à jour automatique de rare_books.txt"`

## Future Integration Notes

When connecting to the Android app:
- Consume `rare_books.txt` as a CSV-like lookup table (parse by `|` delimiter)
- Use ISBN as primary key for market price lookup
- Consider migrating to a structured format (JSON, SQLite) if search performance becomes critical
