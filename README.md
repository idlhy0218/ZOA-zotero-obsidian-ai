# zotero-obsidian-summarizer

> Zotero × Gemini AI × Obsidian — Academic paper summarization pipeline

A desktop app that connects Zotero, Google Gemini AI, and Obsidian into a single academic workflow. Automatically fetches journal articles, extracts full PDF text, generates structured AI summaries, and saves Markdown notes with wikilinks for building a personal knowledge network.


---

## File Structure

```
📁 project root
├── paper_summarizer.py     # Main application (GUI + pipeline)
├── Paper Summarizer.bat    # Windows launcher (double-click to run)
├── .env                    # API keys and paths (not tracked by Git)
├── .gitignore              # Excludes .env and cache files
└── README.md               # This file
```

---

## How It Works

```
Zotero API
    ↓  fetch journal articles by collection
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

## Setup

**1. Install dependencies**
```bash
pip install pyzotero google-generativeai pypdf
```

**2. Configure `.env`**

Copy `.env.template` to `.env` and fill in your credentials:
```
USER_ID=your_zotero_user_id
ZOTERO_KEY=your_zotero_api_key
GEMINI_KEY=your_gemini_api_key
PDF_PATH=C:\path\to\zotero_pdf_folder
OBS_PATH=C:\path\to\obsidian\output_folder
```

**3. Run**

Double-click `Paper Summarizer.bat`, or run directly:
```bash
python paper_summarizer.py
```

---

## Features

| Feature | Description |
|---|---|
| Collection picker | Real-time search, multi-select, checkbox UI |
| PDF matching | Rule-based matching by author + year + title keywords |
| AI summary | Research objective, methodology, key results, keywords |
| Auto Wikilinks | Authors, journals, tags, and keywords linked as `[[...]]` |
| Duplicate handling | Skip / Overwrite / Update if newer |
| Recent filter | Process only papers added within N days |
| Progress bar | Live progress tracking with count display |
| `.env` config | All credentials and paths stored outside source code |

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

## Development History

| Version | Changes |
|---|---|
| v1.0 | Initial build — Zotero fetch, Gemini summary, Obsidian export |
| v2.0 | Added multi-collection (B2), recent filter (B3), duplicate handling (A1), progress bar (A4), auto wikilinks (C1), `.env` support (D1) |
| v3.0 | Full UI redesign (Segoe UI, modern flat layout), CollectionPicker with real-time search and checkbox selection, hover effects, path variables moved to `.env` |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pyzotero` | Zotero API client |
| `google-generativeai` | Gemini API |
| `pypdf` | PDF text extraction |
| `tkinter` | GUI (Python standard library) |

---

## Security Notes

- `.env` is excluded from Git via `.gitignore`
- `paper_summarizer.py` contains no credentials or personal paths
- Do not rename `.env.template` directly — copy it to `.env`
