# ZOA (Zotero-Obsidian-AI Summary) v1.0-beta

![Downloads](https://img.shields.io/github/downloads/idlhy0218/ZOA-zotero-obsidian-ai/total?style=flat-square)

An automated academic paper summarization pipeline that integrates Zotero, Obsidian, and multiple AI providers (Gemini, Claude, OpenAI, DeepSeek). ZOA reads your local Zotero library, extracts PDF content, generates structured AI summaries, and saves them as Markdown notes directly into your Obsidian vault.

> 한국어 설명서: [README_KOR.md](README_KOR.md)

---

https://github.com/user-attachments/assets/ba92afdc-8fcd-4e8a-a1cc-d8e83f8473ff

---

## Requirements

| Tool | Purpose | Notes |
|------|---------|-------|
| Zotero | Academic library management | Integrates metadata locally using `zotero.sqlite` |
| Obsidian | Storing and managing summary notes | Free to download and use |
| AI API Key | Generating paper summaries | At least one key required (Gemini, Claude, OpenAI, or DeepSeek) |
| PDF Folder | Extraction of paper full-text | The directory where Zotero stores your PDF files (default `storage` folder or custom folder) |

> 💡 **Activating Full-Text Analysis:** You do not need to use plugins like Zotmoov to organize your PDFs. Whether your PDFs are auto-organized into a custom directory or scattered in Zotero's default storage folder, ZOA will scan the directory **recursively**. Simply set your PDF folder path in the ZOA options to the topmost directory containing your Zotero PDFs, and they will be matched perfectly.

---

## Installation & Setup

### 📥 Download the Latest Release
* **[Download ZOA (GitHub Releases)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases)**
* Download the build for your OS: `ZOA.exe` (Windows) or `ZOA-macOS.zip` (macOS).

https://github.com/user-attachments/assets/f95b8227-991f-4deb-bb5c-d9f9d37b7802

### 1. Create a Dedicated ZOA Folder
You must create a dedicated folder named **ZOA** and place the downloaded executable (`ZOA.exe` for Windows, `ZOA-macOS.zip` for macOS) inside it.
* **[Crucial Requirement]** The executable and the `.env` configuration file (created automatically on first launch) **must always reside in the same folder together.** If you move only the executable to another location (like your Desktop) or separate it from the `.env` file, ZOA will fail to detect your settings and won't run.
* **[Windows SmartScreen Warning]** When launching `ZOA.exe` for the first time, Windows Defender may display a **"Windows protected your PC"** warning. This is a common warning for unsigned custom executables. You can safely ignore this by clicking **"More info"** and then clicking the **"Run anyway"** button to start the app.

### 2. Obtain an API Key
Get an API key from at least one of the following providers:
* [Google AI Studio](https://aistudio.google.com/app/apikey) — Gemini
* [Anthropic Console](https://console.anthropic.com/) — Claude
* [OpenAI Platform](https://platform.openai.com/) — GPT
* [DeepSeek Platform](https://platform.deepseek.com/) — DeepSeek

### 3. Run the Setup Wizard & Security Information
Double-click the executable. On first launch, a Setup Wizard will guide you through entering your API key(s) and folder paths. All settings are saved locally to your `.env` file.

> **⚠️ API Key Privacy & Security Guarantee**
> The API keys stored in your `.env` file are kept strictly local to your machine. They are **never shared with or transmitted to anyone else.** You can use ZOA with complete peace of mind.

---

## Features

* **Setup Wizard**: A GUI-based first-run wizard lets beginners configure API keys and folder paths without manually editing any files.
* **Multi-AI Support & Dynamic Model Switching**: Supports Google Gemini, Anthropic Claude, OpenAI, and DeepSeek. The model dropdown updates automatically when you switch providers.
* **Multi-Collection Selection**: Browse and search your Zotero collection tree in real time; select multiple folders to summarize at once.
* **Local DB Integration**: Queries your local `zotero.sqlite` directly — no sync delays, instant results.
* **Intelligent PDF Matching & Full-Text Summarization**: Automatically matches PDFs using author name, year, and title keywords. When matched, up to 30 pages of PDF text are extracted for precise summarization; falls back to abstract-only mode if no PDF is found.
* **Structured Academic Summary Format**: Every AI summary is organized into four clear sections — Research Objective, Methodology, Key Results, and Keywords. The number of keywords (1–10, default 5) can be configured directly in the app.
* **Customizable AI Prompt**: Easily modify the AI summarization prompt template using the integrated collapsible text editor. Supports dynamic placeholder tags like `{title}`, `{content_source}`, `{keyword_count}`, and `{text}`. Custom templates are persistently saved locally in `prompt_template.txt`.
* **Auto Wikilinks & Tag Linking**: Authors, journals, and tags in the summary are automatically converted to Obsidian `[[wikilinks]]` for knowledge graph integration.
* **Filtering & Duplicate Handling**: Filter by papers added within the last N days; handle existing notes with Skip, Overwrite, or Update-if-newer modes.

---

## Output Markdown Structure

Each summary saved to Obsidian follows this template:

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
- **URL**: https://...

## AI Summary (Full PDF Content)

### 1. Research Objective
(Central research question and the population or context under study.)

### 2. Methodology
(Data source(s) and sample, key variables, statistical models or analytic strategy.)

### 3. Key Results
(Main findings, including direction and magnitude of effects where available.)

### 4. Keywords
#Keyword1 #Keyword2 #Keyword3 #Keyword4 #Keyword5

---
## Original Abstract
> (The original abstract from Zotero is preserved here.)
```

---

## FAQ

**Q. Is the Zotmoov plugin required?**  
No. Even if you don't use Zotmoov, ZOA will work perfectly as long as you point the PDF Folder path in the options to your default Zotero storage folder (usually containing folders of individual items). ZOA recursively scans the directories to match PDFs with paper entries. If no matching PDF is found, ZOA automatically falls back to abstract-based summarization.

**Q. Will I be charged for API usage?**  
Charges depend on each provider's pricing policy (Google, Anthropic, OpenAI, DeepSeek). Some offer free tiers. Check each provider's official platform for details.

**Q. I don't know where my Zotero database is. What do I do?**  
Leave the field blank in the Setup Wizard. If Zotero is installed in its default location, ZOA will detect `zotero.sqlite` automatically.

---

## Privacy & Security

* **Local Storage Only**: Your API keys and configuration are never sent to any external server. They are stored exclusively in the `.env` file located next to the executable.
* **Direct Communication**: Paper data and extracted PDF text are sent only to the official AI API endpoint you select (Google, Anthropic, OpenAI, or DeepSeek). No third-party servers are involved.

---

## Version History

* **v1.0-beta (Initial Beta Release)**
  * Full rewrite of the GOZ pipeline with multi-provider API architecture
  * Support for Google Gemini, Anthropic Claude, OpenAI, and DeepSeek
  * Dynamic model combobox that updates when switching providers
  * Lightweight REST client using Python's standard `urllib` library — no heavy SDK dependencies
  * Structured academic AI prompt: 4-section output (Research Objective / Methodology / Key Results / Keywords)
  * Keyword count setting added to UI (1–10, default 5)

---

## Bug Reports & Feature Requests

If you encounter a bug or have a feature suggestion, please open an issue:
* **[Report an Issue (GitHub Issues)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/issues)**
* Include a screenshot of the error and the contents of the **Execution Log** panel at the bottom of the app for faster resolution.

---

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2026 Heeyoung Lee. All rights reserved.
