# ZOA (Zotero-Obsidian-AI Summary) v1.0-beta

> 한국어 설명서: [README_KOR.md](README_KOR.md)

An automated academic paper summarization pipeline that integrates Zotero, Obsidian, and multiple AI providers. ZOA reads your local Zotero library, extracts PDF content, generates structured AI summaries, and saves them as Markdown notes directly into your Obsidian vault.

> ## [Download Latest Release (ZOA.exe / ZOA-macOS.zip)](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases/latest)

---
https://github.com/user-attachments/assets/e27cc9a9-26a7-4494-83bb-c08af3ae6aa0
---

## Requirements

| Tool       | Purpose                                                       |
| ---------- | ------------------------------------------------------------- |
| Zotero     | Academic library management (queries `zotero.sqlite` locally) |
| Obsidian   | Storing and managing summary Markdown notes                   |
| AI API Key | Generating summaries — at least one key required              |
| PDF Folder | Zotero's PDF storage folder (scanned recursively)             |

---

## Installation & Setup

Go to [GitHub Releases](https://github.com/idlhy0218/ZOA-zotero-obsidian-ai/releases), choose your preferred format, or get started using one of the methods below.

### 1. Auto-Setup via AI Coding Agent (Claude Code, Antigravity, etc. - Recommended 🚀)
1. **Command the Agent**: In your AI agent's chat, paste this repository link and ask it to install the project:
   > "Please install and setup https://github.com/idlhy0218/ZOA-zotero-obsidian-ai on my system and run it."
2. **Automatic Setup**: The agent will automatically clone the repository, build a virtual environment, and install all required python libraries.
3. **Answer Prompts**: Answer any questions the agent asks about your API keys or Obsidian paths. The agent will build your `.env` and launch ZOA for you.

---

### 2. Windows Executable (`ZOA.exe` - Portable)
1. **Download & Place**: Download `ZOA.exe`, create a dedicated folder (e.g., `ZOA/`), and place the file inside.
2. **Run ZOA**: Double-click `ZOA.exe` to launch. (If Windows SmartScreen warns you, click "More info" → "Run anyway").
3. **Setup Wizard**: Follow the auto-launched setup wizard to input your API keys and folder paths.

---

### 3. macOS App Bundle (`ZOA-macOS.zip` - Portable)
1. **Extract**: Download `ZOA-macOS.zip`, extract it, and place `ZOA.app` into a dedicated folder.
2. **Bypass Gatekeeper**: On first launch, if macOS blocks the app, go to **System Settings → Privacy & Security → Security** and click **"Open Anyway"** under ZOA, then authenticate.
3. **Setup Wizard**: Complete the setup wizard. Your configuration is safely kept in `~/.zoa/.env`.

---

### 4. Run from Source (`Source code.zip` - Python 3.11+)
1. **Extract**: Download `Source code.zip` and extract it into a folder.
2. **Install Dependencies**: Open your terminal in the extracted folder and run:
   ```bash
   pip install google-generativeai pypdf pillow
   ```
3. **Run ZOA**: On Windows, double-click **`ZOA.bat`**. On macOS/Linux, run:
   ```bash
   python zoa.py
   ```

> **Security Note**: All API keys are saved exclusively in your local `.env` file (or `~/.zoa/.env` on macOS) and are never transmitted to any third party.

---

## Features

| Feature                         | Description                                                                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Multi-AI Support**            | Google Gemini, Anthropic Claude, OpenAI, DeepSeek — switch providers and models from the Settings panel                           |
| **Collection Picker**           | Search and select multiple Zotero collections in real time                                                                        |
| **Full-Text PDF Summarization** | Automatically matches PDFs by author/year/title; extracts up to N pages (configurable)                                            |
| **Abstract Fallback**           | Falls back to abstract-only mode when no PDF is found                                                                             |
| **Structured Output**           | Every summary is organized into 4 sections: Research Objective, Methodology, Key Results, Keywords                                |
| **Custom AI Prompt**            | Edit the prompt template directly in the Settings panel; placeholders: `{title}`, `{content_source}`, `{keyword_count}`, `{text}` |
| **Obsidian Wikilinks**          | Authors, journals, and tags auto-converted to `[[wikilinks]]`                                                                     |
| **Flexible Filename Formats**   | Choose from 4 naming styles (Classic, Title, Year-Author-Title, Author-Year-Title)                                                |
| **Duplicate Handling**          | Overwrite, Skip, or Merge existing summary notes                                                                                  |
| **Recent Papers Filter**        | Process only papers added/modified within the last N days                                                                         |
| **⚙ Settings Panel**            | Gear icon in the top-right — configure all preferences without touching any files                                                 |

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
