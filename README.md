# Zotero Obsidian Summarizer

> Zotero × Gemini AI × Obsidian — Academic paper summarization pipeline

Automatically fetches journal articles from your local Zotero library, extracts full PDF text, generates structured AI summaries, and saves Markdown notes with wikilinks to your Obsidian vault.

---

## Download

**[⬇ Download PaperSummarizer.exe](../../releases/latest)**

> Windows only. No Python installation required.

---

## Quick Start (3 steps)

**1. Download** `PaperSummarizer.exe` from the [Releases page](../../releases/latest)

**2. Get a free Gemini API key**
→ Go to [aistudio.google.com](https://aistudio.google.com/app/apikey) and click **Get API key**

**3. Run the exe**
→ A setup wizard will guide you through entering your API key and folder paths.
→ Settings are saved locally and never uploaded anywhere.

That's it. The app opens automatically after setup.

---

## How It Works

```
Local Zotero SQLite DB
    ↓  fetch journal articles by collection (no sync required)
Local PDF folder
    ↓  match and extract full text (pypdf)
Google Gemini API
    ↓  generate structured summary
Obsidian Vault
    ↓  save as .md with YAML frontmatter + wikilinks
```

Each output note follows this naming convention:
```
{Author}_{Year}_{JournalAcronym}.md
e.g.  Kim et al_2023_SSM.md
```

---

## Features

| Feature | Description |
|---|---|
| Setup wizard | First-run guided setup — no config files to edit manually |
| Collection picker | Real-time search, multi-select, checkbox UI |
| Local DB access | Reads Zotero SQLite directly — no sync delay, no Zotero API key |
| PDF matching | Rule-based matching by author + year + title keywords |
| AI summary | Research objective, methodology, key results, keywords |
| Auto Wikilinks | Authors, journals, tags, and keywords linked as `[[...]]` |
| Duplicate handling | Skip / Overwrite / Update if newer |
| Recent filter | Process only papers added within N days |
| Progress bar | Live progress tracking with count display |

---

## Output Note Structure

```markdown
---
title: "..."
authors:
  - Last, First
date: 2023
journal: "..."
has_pdf: true
zotero_link: zotero://select/items/0_XXXXXXXX
---

# Title

## Bibliographic Info
## AI Summary (Full PDF Content)
## Original Abstract
```

---

## Running from Source

If you prefer to run the Python script directly:

```bash
# 1. Install dependencies
pip install google-generativeai pypdf

# 2. Run
python paper_summarizer.py
```

The setup wizard will run on first launch and create a `.env` file automatically.

---

## Privacy & Security

- Your API key and folder paths are stored **only in a local `.env` file** next to the exe
- No data is uploaded except paper text sent to the Gemini API for summarization
- The `.env` file is excluded from this repository via `.gitignore`

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-generativeai` | Gemini API |
| `pypdf` | PDF text extraction |
| `tkinter` | GUI (Python standard library) |
| `sqlite3` | Local Zotero DB access (Python standard library) |

---

## Version History

| Version | Changes |
|---|---|
| v1.1 | First-run setup wizard, PyInstaller exe support, portable config |
| v1.0 | Initial build — Zotero DB fetch, Gemini summary, Obsidian export |