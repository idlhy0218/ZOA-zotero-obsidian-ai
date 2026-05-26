# ZOA (Zotero-Obsidian-AI Summary) v1.0-beta

![Downloads](https://img.shields.io/github/downloads/idlhy0218/ZOA-zotero-obsidian-ai/total?style=flat-square)

An automated academic paper summarization pipeline that integrates Zotero, Obsidian, and multiple AI providers. ZOA reads your local Zotero library, extracts PDF content, generates structured AI summaries, and saves them as Markdown notes directly into your Obsidian vault.

> 한국어 설명서: [README_KOR.md](README_KOR.md)

---

https://github.com/user-attachments/assets/ba92afdc-8fcd-4e8a-a1cc-d8e83f8473ff

---

## Requirements

| Tool | Purpose |
|------|---------|
| Zotero | Academic library management (queries `zotero.sqlite` locally) |
| Obsidian | Storing and managing summary Markdown notes |
| AI API Key | Generating summaries — at least one key required |
| PDF Folder | Zotero's PDF storage folder (scanned recursively) |

---

## Installation & Setup

### 1. Download

<div align="center">

[![Download ZOA](https://img.shields.io/badge/⬇%20Download%20ZOA-v1.0--beta-4A90D9?style=for-the-badge&logo=github&logoColor=white)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases)

**`ZOA.exe`** for Windows &nbsp;|&nbsp; **`ZOA-macOS.zip`** for macOS

</div>

### 2. Create a Dedicated Folder

Place the executable in its own dedicated folder (e.g., `ZOA/`). The `.env` config file is created automatically on first launch and **must remain in the same folder as the executable**.

> **Windows SmartScreen** — Click "More info" → "Run anyway" to bypass the unsigned app warning.

> **macOS Gatekeeper** — If blocked on first launch, go to **System Settings → Privacy & Security → Security** and click **"Open Anyway"** next to ZOA. Authenticate with your password or Touch ID.

### 3. Get an API Key

Obtain a key from at least one provider:

| Provider | Link |
|----------|------|
| Google Gemini | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| Anthropic Claude | [Anthropic Console](https://console.anthropic.com/) |
| OpenAI | [OpenAI Platform](https://platform.openai.com/) |
| DeepSeek | [DeepSeek Platform](https://platform.deepseek.com/) |

### 4. Run the Setup Wizard

Double-click the executable. On first launch, a Setup Wizard will guide you through entering your API key(s) and folder paths. All settings are saved locally to your `.env` file and can be reconfigured anytime via the **⚙ Settings** button.

> **Security**: API keys are stored exclusively in your local `.env` file and are never transmitted to any third party.

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-AI Support** | Google Gemini, Anthropic Claude, OpenAI, DeepSeek — switch providers and models from the Settings panel |
| **Collection Picker** | Search and select multiple Zotero collections in real time |
| **Full-Text PDF Summarization** | Automatically matches PDFs by author/year/title; extracts up to N pages (configurable) |
| **Abstract Fallback** | Falls back to abstract-only mode when no PDF is found |
| **Structured Output** | Every summary is organized into 4 sections: Research Objective, Methodology, Key Results, Keywords |
| **Custom AI Prompt** | Edit the prompt template directly in the Settings panel; placeholders: `{title}`, `{content_source}`, `{keyword_count}`, `{text}` |
| **Obsidian Wikilinks** | Authors, journals, and tags auto-converted to `[[wikilinks]]` |
| **Flexible Filename Formats** | Choose from 4 naming styles (Classic, Title, Year-Author-Title, Author-Year-Title) |
| **Duplicate Handling** | Overwrite, Skip, or Merge existing summary notes |
| **Recent Papers Filter** | Process only papers added/modified within the last N days |
| **⚙ Settings Panel** | Gear icon in the top-right — configure all preferences without touching any files |

---

## Output Markdown Structure

```markdown
---
title: "Paper Title"
authors:
  - Last, First
date: 2026
journal: "Journal Name"
zotero_link: zotero://select/items/0_XXXXXXXX
---

# Paper Title

## Bibliographic Info
- **Authors**: Last, First
- **Journal**: Journal Name
- **Date**: 2026
- **Zotero Link**: [Open in Zotero](zotero://select/items/0_XXXXXXXX)
- **PDF Status**: PDF Found
- **Zotero Tags**: tag1, tag2

## AI Summary (Full PDF Content)

### 1. Research Objective
### 2. Methodology
### 3. Key Results
### 4. Keywords
#Keyword1 #Keyword2 #Keyword3

---
## Original Abstract
> (Original abstract from Zotero)
```

---

## FAQ

**Q. Is Zotmoov required?**  
No. Point the PDF Folder to Zotero's default `storage` folder. ZOA scans recursively and matches PDFs automatically.

**Q. Where is my Zotero database?**  
Leave the field blank in the Setup Wizard. ZOA auto-detects `zotero.sqlite` if Zotero is installed in its default location.

**Q. Will I be charged for API usage?**  
Depends on each provider's pricing. Some offer free tiers — check each provider's platform for details.

---

## Bug Reports

**[→ Open an Issue on GitHub](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/issues)**  
Please include a screenshot and the contents of the **Execution Log** panel.

---

## License

[MIT License](LICENSE) — Copyright (c) 2026 Heeyoung Lee.
