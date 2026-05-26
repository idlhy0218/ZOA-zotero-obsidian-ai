"""
ZOA (Zotero-Obsidian-AI Summary) — v1.0-beta

Copyright (c) 2026 Heeyoung Lee. All rights reserved.
Licensed under the MIT License. See LICENSE file in the project root for details.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, os, re, time, unicodedata, sys
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────────
# App directory & Resource Path — PyInstaller compatible
# ─────────────────────────────────────────────
def get_app_dir() -> Path:
    """Return the folder that contains the configuration."""
    # 1. On macOS, always use user's home directory (~/.zoa) to avoid read-only bundle/translocation errors
    if sys.platform == 'darwin':
        path = Path.home() / '.zoa'
        path.mkdir(parents=True, exist_ok=True)
        return path

    # 2. On Windows/Linux, prioritize executable/script directory (portable mode)
    if getattr(sys, 'frozen', False):
        local_path = Path(sys.executable).resolve().parent
    else:
        local_path = Path(__file__).resolve().parent

    # Test if the local folder is writable (for first-run .env creation)
    try:
        test_file = local_path / '.zoa_write_test'
        test_file.touch()
        test_file.unlink()
        return local_path
    except (IOError, OSError):
        # Fallback to home directory if local path is not writable (e.g., Program Files, read-only drive)
        home_path = Path.home() / '.zoa'
        home_path.mkdir(parents=True, exist_ok=True)
        return home_path

def get_resource_path(relative_path: str) -> Path:
    """Return the absolute path to a resource, compatible with PyInstaller's --onefile mode."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

def apply_window_icon(window):
    """Apply the high-resolution app icon to a window (Tk or Toplevel)."""
    try:
        icon_path = get_resource_path("app_icon.ico")
        if icon_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                window.iconphoto(True, photo)
                window._icon_image = photo
            except Exception:
                window.iconbitmap(default=str(icon_path))
    except Exception:
        pass


# ─────────────────────────────────────────────
# Config / .env
# ─────────────────────────────────────────────
def load_config():
    config = {
        'GEMINI_KEY': '',
        'CLAUDE_KEY': '',
        'OPENAI_KEY': '',
        'DEEPSEEK_KEY': '',
        'API_PROVIDER': 'gemini',
        'PDF_PATH': '',
        'OBS_PATH': '',
        'ZOTERO_DB': '',
        'MODEL_NAME': 'gemini-2.5-flash',
        'FILENAME_FMT': 'default',
        'PDF_MAX_PAGES': '30',
        'SKIP_EMPTY_ABS': 'False',
        'FULL_PDF': 'True',
        'USE_WIKILINKS': 'True',
        'USE_RECENT': 'False',
        'RECENT_DAYS': '7',
        'DUP_MODE': 'overwrite',
        'LIMIT': '500',
        'KEYWORD_COUNT': '5',
        'CUSTOM_PROMPT': 'False'
    }
    env_path = get_app_dir() / '.env'
    if env_path.exists():
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip(); v = v.strip().strip('"').strip("'")
                    if k in config: config[k] = v
    return config

def save_config(cfg: dict):
    """Write the given config dict to .env next to the exe/script."""
    try:
        env_path = get_app_dir() / '.env'
        lines = [
            "# ZOA (Zotero-Obsidian-AI Summary) — Configuration (auto-generated)",
            "# Do NOT share this file or commit it to version control.\n",
            f"GEMINI_KEY={cfg.get('GEMINI_KEY', '')}",
            f"CLAUDE_KEY={cfg.get('CLAUDE_KEY', '')}",
            f"OPENAI_KEY={cfg.get('OPENAI_KEY', '')}",
            f"DEEPSEEK_KEY={cfg.get('DEEPSEEK_KEY', '')}",
            f"API_PROVIDER={cfg.get('API_PROVIDER', 'gemini')}",
            f"PDF_PATH={cfg.get('PDF_PATH', '')}",
            f"OBS_PATH={cfg.get('OBS_PATH', '')}",
            f"ZOTERO_DB={cfg.get('ZOTERO_DB', '')}",
            f"MODEL_NAME={cfg.get('MODEL_NAME', 'gemini-2.5-flash')}",
            f"FILENAME_FMT={cfg.get('FILENAME_FMT', 'default')}",
            f"PDF_MAX_PAGES={cfg.get('PDF_MAX_PAGES', '30')}",
            f"SKIP_EMPTY_ABS={cfg.get('SKIP_EMPTY_ABS', 'False')}",
            f"FULL_PDF={cfg.get('FULL_PDF', 'True')}",
            f"USE_WIKILINKS={cfg.get('USE_WIKILINKS', 'True')}",
            f"USE_RECENT={cfg.get('USE_RECENT', 'False')}",
            f"RECENT_DAYS={cfg.get('RECENT_DAYS', '7')}",
            f"DUP_MODE={cfg.get('DUP_MODE', 'overwrite')}",
            f"LIMIT={cfg.get('LIMIT', '500')}",
            f"KEYWORD_COUNT={cfg.get('KEYWORD_COUNT', '5')}",
            f"CUSTOM_PROMPT={cfg.get('CUSTOM_PROMPT', 'False')}",
        ]
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def config_is_complete(cfg: dict) -> bool:
    """Return True only if at least one API key is present."""
    return bool(
        cfg.get('GEMINI_KEY', '').strip() or
        cfg.get('CLAUDE_KEY', '').strip() or
        cfg.get('OPENAI_KEY', '').strip() or
        cfg.get('DEEPSEEK_KEY', '').strip()
    )

CONFIG       = load_config()
GEMINI_KEY   = CONFIG.get('GEMINI_KEY', '')
CLAUDE_KEY   = CONFIG.get('CLAUDE_KEY', '')
OPENAI_KEY   = CONFIG.get('OPENAI_KEY', '')
DEEPSEEK_KEY = CONFIG.get('DEEPSEEK_KEY', '')
API_PROVIDER = CONFIG.get('API_PROVIDER', 'gemini')
PDF_PATH     = CONFIG.get('PDF_PATH', '')
OBS_PATH     = CONFIG.get('OBS_PATH', '')
ZOTERO_DB    = CONFIG.get('ZOTERO_DB', '')
MODEL_NAME   = CONFIG.get('MODEL_NAME', 'gemini-2.5-flash')

PROVIDER_MODELS = {
    "Google Gemini": [
        "gemini-3.5-flash",
        "gemini-3.1-pro",
        "gemini-3.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash"
    ],
    "Anthropic Claude": [
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001"
    ],
    "OpenAI": [
        "gpt-5.5",
        "gpt-5",
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini"
    ],
    "DeepSeek": [
        "deepseek-chat",
        "deepseek-reasoner"
    ]
}

PROVIDER_KEYS = {
    "Google Gemini": "GEMINI_KEY",
    "Anthropic Claude": "CLAUDE_KEY",
    "OpenAI": "OPENAI_KEY",
    "DeepSeek": "DEEPSEEK_KEY"
}

# ─────────────────────────────────────────────
# Package check
# ─────────────────────────────────────────────
def check_and_import():
    missing = []
    # Core requirement for PDF extraction
    for pkg, imp in [("pypdf", "pypdf")]:
        try: __import__(imp)
        except ImportError: missing.append(pkg)
    return missing

# ─────────────────────────────────────────────
# REST API Client Helpers (Pure Python)
# ─────────────────────────────────────────────
def call_claude_api(api_key, model, prompt):
    import urllib.request
    import json
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": 4000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        if "content" in res_data and len(res_data["content"]) > 0:
            return res_data["content"][0]["text"]
        raise ValueError(f"Unexpected response payload: {res_data}")

def call_openai_compatible_api(url, api_key, model, prompt):
    import urllib.request
    import json
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        if "choices" in res_data and len(res_data["choices"]) > 0:
            return res_data["choices"][0]["message"]["content"]
        raise ValueError(f"Unexpected response payload: {res_data}")

# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────
def clean_filename(text):
    if not text: return "No_Title"
    text = unicodedata.normalize('NFC', text)
    return re.sub(r'[\\/*?:"<>|]', "", text).strip()

def normalize_str(text):
    if not text: return ""
    return unicodedata.normalize('NFC', text)

def sanitize_yaml(text):
    if not text: return ""
    text = unicodedata.normalize('NFC', text)
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    text = text.replace('"', '\\"')
    return text.strip()

def sanitize_abstract(text):
    if not text: return "(No abstract available)"
    text = unicodedata.normalize('NFC', text)
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            result.append(f"> {stripped}")
        else:
            result.append(">")
    return '\n'.join(result)

def clean_date(raw_date: str) -> str:
    if not raw_date: return "No Date"
    raw_date = raw_date.strip()
    
    # 1. Check YYYY-MM-DD
    m3 = re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', raw_date)
    if m3:
        year, month, day = m3.groups()
        if day == '00' or day == '0':
            return f"{year}-{month}"
        return f"{year}-{month}-{day}"
        
    # 2. Check YYYY-MM
    m2 = re.search(r'(\d{4})[-/](\d{2})', raw_date)
    if m2:
        year, month = m2.groups()
        return f"{year}-{month}"
        
    # 3. Check YYYY
    m1 = re.search(r'\d{4}', raw_date)
    if m1:
        return m1.group(0)
        
    return raw_date

# ── SQLite helpers ──────────────────────────
def get_zotero_db():
    import sqlite3
    db_path = ZOTERO_DB or str(Path.home() / 'Zotero' / 'zotero.sqlite')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"zotero.sqlite not found: {db_path}")
    uri = f"file:{db_path}?immutable=1"
    return sqlite3.connect(uri, uri=True)

def sqlite_get_collections(db):
    cur = db.execute(
        "SELECT collectionID, key, collectionName, parentCollectionID FROM collections"
    )
    return [{'id': r[0], 'key': r[1], 'name': r[2], 'parent': r[3]} for r in cur.fetchall()]

def sqlite_get_collection_ids(db, root_name):
    cols = sqlite_get_collections(db)
    root = next((c for c in cols if c['name'] == root_name), None)
    if not root: return []
    ids = [root['id']]
    def find(pid):
        for c in cols:
            if c['parent'] == pid:
                ids.append(c['id']); find(c['id'])
    find(root['id'])
    return ids

def sqlite_get_items(db, col_ids=None, limit=500):
    base_types = "('journalArticle','conferencePaper','preprint','report','thesis')"
    if col_ids:
        placeholders = ",".join("?" * len(col_ids))
        query = f"""
            SELECT DISTINCT i.itemID, i.key, i.dateAdded
            FROM items i
            JOIN collectionItems ci ON i.itemID = ci.itemID
            JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
            WHERE ci.collectionID IN ({placeholders})
              AND it.typeName IN {base_types}
              AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
            ORDER BY i.dateAdded DESC
            LIMIT ?
        """
        rows = db.execute(query, col_ids + [limit]).fetchall()
    else:
        query = f"""
            SELECT DISTINCT i.itemID, i.key, i.dateAdded
            FROM items i
            JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
            WHERE it.typeName IN {base_types}
              AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
            ORDER BY i.dateAdded DESC
            LIMIT ?
        """
        rows = db.execute(query, [limit]).fetchall()
    return [{'itemID': r[0], 'key': r[1], 'dateAdded': r[2]} for r in rows]

def sqlite_get_item_data(db, item_id):
    cur = db.execute("""
        SELECT f.fieldName, iv.value
        FROM itemData id_
        JOIN itemDataValues iv ON id_.valueID = iv.valueID
        JOIN fields f ON id_.fieldID = f.fieldID
        WHERE id_.itemID = ?
    """, [item_id])
    return {r[0]: r[1] for r in cur.fetchall()}

def sqlite_get_creators(db, item_id):
    cur = db.execute("""
        SELECT c.lastName, c.firstName, ct.creatorType
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
    """, [item_id])
    return [{'lastName': r[0] or '', 'firstName': r[1] or '', 'type': r[2]} for r in cur.fetchall()]

def sqlite_get_tags(db, item_id):
    cur = db.execute("""
        SELECT t.name FROM itemTags it
        JOIN tags t ON it.tagID = t.tagID
        WHERE it.itemID = ?
    """, [item_id])
    return [r[0] for r in cur.fetchall()]

def sqlite_get_collection_names(db):
    cur = db.execute("SELECT collectionName FROM collections ORDER BY collectionName")
    return [r[0] for r in cur.fetchall()]

def index_pdf_files(root_path):
    out = []
    for root, _, files in os.walk(root_path):
        for f in files:
            if f.lower().endswith('.pdf'):
                out.append({'name': f, 'path': os.path.join(root, f),
                            'clean_name': normalize_str(f).lower()})
    return out

def find_best_pdf_match(fields, creators_raw, pdf_index):
    try:
        if not creators_raw: return None
        author_last = creators_raw[0].get('lastName', '') or creators_raw[0].get('firstName', '')
        year_m = re.search(r'\d{4}', fields.get('date', ''))
        year = year_m.group(0) if year_m else None
        title = fields.get('title', '')
        if not author_last or not year: return None
        ta = normalize_str(author_last).lower(); ty = str(year)
        stop = {'the','and','for','with','that','this','from','what','study','using','journal'}
        kws = [w.lower() for w in re.findall(r'\w+', title)
               if len(w) > 3 and w.lower() not in stop]
        best, hi = None, -1
        for pdf in pdf_index:
            fn = pdf['clean_name']
            if ta not in fn or ty not in fn: continue
            sc = sum(1 for k in kws if k in fn)
            if sc > hi: hi, best = sc, pdf['path']
        return best
    except: return None

def to_wikilinks(items):
    return ", ".join(f"[[{i.strip()}]]" for i in items if i.strip())

def extract_keywords_from_summary(summary_text):
    return re.findall(r'#([\w\-]+)', summary_text)

def apply_wikilinks_to_summary(summary_text, keywords):
    for kw in keywords:
        pattern = re.compile(
            r'(?<!\[\[)(?<!\w)' + re.escape(kw) + r'(?!\w)(?!\]\])', re.IGNORECASE)
        summary_text = pattern.sub(f'[[{kw}]]', summary_text, count=2)
    return summary_text

# ─────────────────────────────────────────────
# Design tokens — ZOA Academic Signature
# ─────────────────────────────────────────────
BG           = "#F4F3F1"       # warm off-white page
BG_CARD      = "#FFFFFF"
BG_INPUT     = "#FAFAF9"
BG_HOVER     = "#F0EFED"
BG_SEL       = "#615478"       # Deep Violet Gray (selected row fill)
FG           = "#1C1C1C"
FG_MID       = "#555550"
FG_DIM       = "#888882"
FG_LIGHT     = "#BABAB4"
BORDER       = "#E2E1DE"
BORDER_MID   = "#C8C7C3"
ACCENT       = "#615478"       # Deep Violet Gray (primary accent)
ACCENT_H     = "#504464"       # Darker Deep Violet Gray (hover)
ACCENT_POINT = "#a40808"       # Academic Crimson Red (run button)
ACCENT_POINT_H = "#840606"     # Darker Academic Crimson Red (hover)
LOG_BG       = "#F8F8F7"
LOG_FG       = "#555550"
LOG_OK       = "#615478"       # Deep Violet for success logs
LOG_SKIP     = "#BABAB4"
LOG_WARN     = "#888882"
TAG_BG       = "#ECE9F2"       # Light violet gray for tag backgrounds
TAG_FG       = "#504464"       # Deep Violet for tag text

# Fonts — larger, readable
FONT_H1      = ("Segoe UI",     16, "bold")
FONT_APPNAME = ("Segoe UI",     15, "bold")
FONT_SUBNAME = ("Segoe UI",      10)
FONT_VER     = ("Consolas",      10)
FONT_SEC     = ("Segoe UI",      10, "bold")   # section labels
FONT_LABEL   = ("Segoe UI",     12)
FONT_LABEL_B = ("Segoe UI",     12, "bold")
FONT_SMALL   = ("Segoe UI",     11)
FONT_ENTRY   = ("Consolas",     12)
FONT_BTN_P   = ("Segoe UI",     12, "bold")
FONT_BTN_G   = ("Segoe UI",     12)
FONT_LOG     = ("Consolas",     11)
FONT_STATUS  = ("Segoe UI",     11)
FONT_TAG     = ("Segoe UI",     11)
FONT_MONO    = ("Consolas",     11)

# ─────────────────────────────────────────────
# Prompt Templates and Helpers
# ─────────────────────────────────────────────
DEFAULT_PROMPT_TEMPLATE = """You are an expert academic research analyst specializing in summarizing \
peer-reviewed academic literature. Your summaries are precise, jargon-aware, \
and strictly grounded in the provided text.

## Task
Summarize the provided {content_source} of the research paper titled: "{title}".

## Critical Constraints
- Base your summary on the provided text. Synthesize the context logically to provide a useful summary even if some specific details are not explicitly spelled out.
- If specific details (like precise sample sizes or statistical models) are not mentioned, summarize the conceptual goals, qualitative approaches, or overall trends instead. Avoid generic "not reported" statements unless the text provides absolutely zero context.
- Use clear academic English. Be concise: each section should be 1–3 sentences maximum.

## Output Format (Markdown)

### 1. Research Objective
State the central research question and the population or context under study.

### 2. Methodology
Specify: (a) data source(s) and sample, (b) key variables, \
(c) statistical models or analytic strategy.

### 3. Key Results
Report the main findings, including direction and magnitude of effects where available. \
Prioritize statistically significant results.

### 4. Keywords
Provide exactly {keyword_count} keywords using # prefix. Apply these rules in order:
- Include at least 2 methodology keywords (e.g., #DiD, #Fixed-Effects, #Multilevel-Model).
- Use umbrella/concept terms for substantive topics (e.g., #Substance-Use, not #Opioids).
- Capitalize the first letter of each word; hyphenate multi-word terms."""

def load_prompt_template() -> str:
    path = get_app_dir() / 'prompt_template.txt'
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            pass
    return DEFAULT_PROMPT_TEMPLATE

def save_prompt_template(content: str):
    try:
        path = get_app_dir() / 'prompt_template.txt'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save prompt template: {e}")

# ─────────────────────────────────────────────
# Widget helpers
# ─────────────────────────────────────────────
def make_entry(parent, textvariable, width=46, placeholder=""):
    e = tk.Entry(parent, textvariable=textvariable, width=width,
                 bg=BG_INPUT, fg=FG, relief="flat", font=FONT_ENTRY,
                 insertbackground=FG,
                 highlightthickness=1,
                 highlightbackground=BORDER,
                 highlightcolor=ACCENT)
    return e

class ModernButton(tk.Label):
    """Custom premium label-based button that supports uniform custom colors on all platforms including macOS."""
    def __init__(self, parent, text, command, bg, fg, font, hover_bg, active_bg=None, border_color=None, **kwargs):
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.active_bg = active_bg or hover_bg
        self.fg = fg
        self.enabled = True
        
        highlightthickness = 1 if border_color else 0
        highlightbackground = border_color or bg
        highlightcolor = border_color or bg
        
        super().__init__(parent, text=text, font=font, bg=bg, fg=fg,
                         cursor="hand2", relief="flat", bd=0,
                         highlightthickness=highlightthickness,
                         highlightbackground=highlightbackground,
                         highlightcolor=highlightcolor,
                         **kwargs)
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_click(self, event=None):
        if self.enabled and self.command:
            # Subtle flash click effect
            orig_bg = self.cget("bg")
            self.config(bg=self.active_bg)
            self.after(80, lambda: self.config(bg=orig_bg))
            self.command()
            
    def _on_enter(self, event=None):
        if self.enabled:
            self.config(bg=self.hover_bg)
            
    def _on_leave(self, event=None):
        if self.enabled:
            self.config(bg=self.bg)
            
    def set_state(self, state):
        if state == "disabled":
            self.enabled = False
            self.config(fg=FG_LIGHT, cursor="arrow")
        else:
            self.enabled = True
            self.config(fg=self.fg, cursor="hand2")
            
    def config(self, **kwargs):
        if "state" in kwargs:
            self.set_state(kwargs["state"])
            del kwargs["state"]
        if "fg" in kwargs:
            self.fg = kwargs["fg"]
        super().config(**kwargs)
        
    def configure(self, **kwargs):
        self.config(**kwargs)

def make_btn_primary(parent, text, command, bg_color=None, hover_color=None):
    bg = bg_color or ACCENT
    hov = hover_color or ACCENT_H
    return ModernButton(parent, text=text, command=command, bg=bg, fg=BG_CARD,
                        font=FONT_BTN_P, hover_bg=hov, active_bg=hov, padx=18, pady=8)

def make_btn_ghost(parent, text, command):
    return ModernButton(parent, text=text, command=command, bg=BG_CARD, fg=FG_MID,
                        font=FONT_BTN_G, hover_bg=BG_HOVER, active_bg=BG_HOVER,
                        border_color=BORDER, padx=14, pady=8)

def make_section_label(parent, text):
    """Minimal uppercase section label, no horizontal rule."""
    row = tk.Frame(parent, bg=BG)
    row.pack(fill="x", pady=(22, 7))
    tk.Label(row, text=text.upper(), font=FONT_SEC,
             fg=FG_DIM, bg=BG).pack(side="left")

def card(parent, **kw):
    return tk.Frame(parent, bg=BG_CARD,
                    bd=1, relief="solid",
                    highlightthickness=0,
                    padx=18, pady=14, **kw)

def field_label(parent, text):
    tk.Label(parent, text=text, font=FONT_SMALL,
             fg=FG_DIM, bg=BG_CARD).pack(anchor="w", pady=(0, 4))

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<ButtonPress>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 15
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#1C1C1C", foreground="#FAFAF9",
                         relief="solid", borderwidth=1, highlightthickness=0,
                         font=("Segoe UI", 10), padx=8, pady=6)
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class CircledExclamation(tk.Canvas):
    def __init__(self, parent, bg_card):
        super().__init__(parent, width=16, height=16, bg=bg_card, highlightthickness=0, cursor="hand2")
        self.create_oval(2, 2, 14, 14, outline=BORDER_MID, width=1.5)
        self.create_text(8, 8, text="!", font=("Segoe UI", 9, "bold"), fill=ACCENT_POINT)

def field_label_with_tooltip(parent, text, tooltip_text):
    row = tk.Frame(parent, bg=BG_CARD)
    row.pack(anchor="w", pady=(0, 4))
    
    lbl = tk.Label(row, text=text, font=FONT_SMALL,
                   fg=FG_DIM, bg=BG_CARD)
    lbl.pack(side="left")
    
    info_icon = CircledExclamation(row, BG_CARD)
    info_icon.pack(side="left", padx=(5, 0))
    
    ToolTip(info_icon, tooltip_text)

def thin_divider(parent, pady=(12, 12)):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=pady)

# ─────────────────────────────────────────────
# Modern Custom UI Widgets
# ─────────────────────────────────────────────
class ModernCheckbutton(tk.Frame):
    def __init__(self, parent, text, variable, command=None, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL, active_color=None):
        super().__init__(parent, bg=bg)
        self.variable = variable
        self.command = command
        self.bg = bg
        self.fg = fg
        self.active_color = active_color or ACCENT
        
        self.canvas = tk.Canvas(self, width=18, height=18, bg=bg, highlightthickness=0, cursor="hand2")
        self.canvas.pack(side="left", padx=(0, 8))
        
        self.label = tk.Label(self, text=text, font=font, fg=fg, bg=bg, cursor="hand2")
        self.label.pack(side="left")
        
        self.canvas.bind("<Button-1>", self._toggle)
        self.label.bind("<Button-1>", self._toggle)
        
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        
        self.var_trace = self.variable.trace_add("write", self._update_ui)
        self._update_ui()
        
    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()
            
    def _update_ui(self, *args):
        self.canvas.delete("all")
        val = self.variable.get()
        if val:
            self.canvas.create_rectangle(1, 1, 17, 17, fill=self.active_color, outline=self.active_color, width=1)
            self.canvas.create_line(5, 9, 8, 12, fill="white", width=2)
            self.canvas.create_line(8, 12, 13, 5, fill="white", width=2)
        else:
            self.canvas.create_rectangle(1, 1, 17, 17, fill=BG_INPUT, outline=BORDER_MID, width=1.5)
            
    def _on_enter(self, event=None):
        if not self.variable.get():
            self.canvas.delete("all")
            self.canvas.create_rectangle(1, 1, 17, 17, fill=BG_INPUT, outline=self.active_color, width=1.5)
            
    def _on_leave(self, event=None):
        if not self.variable.get():
            self.canvas.delete("all")
            self.canvas.create_rectangle(1, 1, 17, 17, fill=BG_INPUT, outline=BORDER_MID, width=1.5)

class ModernRadiobutton(tk.Frame):
    def __init__(self, parent, text, variable, value, command=None, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL):
        super().__init__(parent, bg=bg)
        self.variable = variable
        self.value = value
        self.command = command
        self.bg = bg
        self.fg = fg
        
        self.canvas = tk.Canvas(self, width=18, height=18, bg=bg, highlightthickness=0, cursor="hand2")
        self.canvas.pack(side="left", padx=(0, 8))
        
        self.label = tk.Label(self, text=text, font=font, fg=fg, bg=bg, cursor="hand2")
        self.label.pack(side="left")
        
        self.canvas.bind("<Button-1>", self._select)
        self.label.bind("<Button-1>", self._select)
        
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        
        self.var_trace = self.variable.trace_add("write", self._update_ui)
        self._update_ui()
        
    def _select(self, event=None):
        self.variable.set(self.value)
        if self.command:
            self.command()
            
    def _update_ui(self, *args):
        self.canvas.delete("all")
        val = self.variable.get()
        if val == self.value:
            self.canvas.create_oval(1, 1, 17, 17, outline=ACCENT, width=1.5)
            self.canvas.create_oval(5, 5, 13, 13, fill=ACCENT, outline=ACCENT)
        else:
            self.canvas.create_oval(1, 1, 17, 17, outline=BORDER_MID, width=1.5)
            
    def _on_enter(self, event=None):
        val = self.variable.get()
        if val != self.value:
            self.canvas.delete("all")
            self.canvas.create_oval(1, 1, 17, 17, outline=ACCENT, width=1.5)
            
    def _on_leave(self, event=None):
        val = self.variable.get()
        if val != self.value:
            self.canvas.delete("all")
            self.canvas.create_oval(1, 1, 17, 17, outline=BORDER_MID, width=1.5)

class ModernScrollbar(tk.Canvas):
    """A beautiful, premium, custom-colored scrollbar that works on all platforms."""
    def __init__(self, parent, command=None, orient="vertical", thumb_color="#BABAB4", hover_color="#615478", trough_color=BG, width=10, on_scroll_start=None, **kwargs):
        self.command = command
        self.orient = orient
        self.thumb_color = thumb_color
        self.hover_color = hover_color
        self.trough_color = trough_color
        self.width = width
        self.on_scroll_start = on_scroll_start
        
        super().__init__(parent, width=width if orient == "vertical" else None, 
                         height=width if orient == "horizontal" else None,
                         bg=trough_color, highlightthickness=0, bd=0, **kwargs)
        
        self.fraction_start = 0.0
        self.fraction_end = 1.0
        self._first_y = 0
        self._first_x = 0
        self._start_fraction = 0.0
        self._hover_active = False
        
        self.bind("<Button-1>", self._on_trough_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda e: self._draw())
        
    def set(self, start, end):
        self.fraction_start = max(0.0, min(1.0, float(start)))
        self.fraction_end = max(0.0, min(1.0, float(end)))
        self._draw()
        
    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        if self.orient == "vertical":
            if h <= 1: return
            y1 = int(self.fraction_start * h)
            y2 = int(self.fraction_end * h)
            if (y2 - y1) < 15:
                y2 = y1 + 15
                if y2 > h:
                    y2 = h
                    y1 = h - 15
            
            color = self.hover_color if self._hover_active else self.thumb_color
            pad = 1
            r = (w - 2 * pad) // 2
            if r < 1: r = 1
            
            if (y2 - y1) >= (2 * r + 2 * pad):
                self.create_oval(pad, y1 + pad, w - pad - 1, y1 + pad + 2 * r, fill=color, outline="")
                self.create_rectangle(pad, y1 + pad + r, w - pad - 1, y2 - pad - r, fill=color, outline="")
                self.create_oval(pad, y2 - pad - 2 * r, w - pad - 1, y2 - pad, fill=color, outline="")
            else:
                self.create_rectangle(pad, y1 + pad, w - pad - 1, y2 - pad, fill=color, outline="")
        else:
            if w <= 1: return
            x1 = int(self.fraction_start * w)
            x2 = int(self.fraction_end * w)
            if (x2 - x1) < 15:
                x2 = x1 + 15
                if x2 > w:
                    x2 = w
                    x1 = w - 15
            
            color = self.hover_color if self._hover_active else self.thumb_color
            pad = 1
            r = (h - 2 * pad) // 2
            if r < 1: r = 1
            
            if (x2 - x1) >= (2 * r + 2 * pad):
                self.create_oval(x1 + pad, pad, x1 + pad + 2 * r, h - pad - 1, fill=color, outline="")
                self.create_rectangle(x1 + pad + r, pad, x2 - pad - r, h - pad - 1, fill=color, outline="")
                self.create_oval(x2 - pad - 2 * r, pad, x2 - pad, h - pad - 1, fill=color, outline="")
            else:
                self.create_rectangle(x1 + pad, pad, x2 - pad, h - pad - 1, fill=color, outline="")

    def _on_enter(self, event=None):
        self._hover_active = True
        self._draw()
        
    def _on_leave(self, event=None):
        self._hover_active = False
        self._draw()
        
    def _on_trough_click(self, event):
        if self.on_scroll_start:
            self.on_scroll_start()
            
        h = self.winfo_height()
        w = self.winfo_width()
        
        if self.orient == "vertical":
            click_y = event.y
            y1 = int(self.fraction_start * h)
            y2 = int(self.fraction_end * h)
            
            if (y2 - y1) < 15:
                y2 = y1 + 15
                if y2 > h:
                    y2 = h
                    y1 = h - 15
            
            if click_y < y1:
                if self.command:
                    self.command("scroll", -1, "pages")
                self._first_y = click_y
                self._start_fraction = self.fraction_start
            elif click_y > y2:
                if self.command:
                    self.command("scroll", 1, "pages")
                self._first_y = click_y
                self._start_fraction = self.fraction_start
            else:
                self._first_y = click_y
                self._start_fraction = self.fraction_start
        else:
            click_x = event.x
            x1 = int(self.fraction_start * w)
            x2 = int(self.fraction_end * w)
            
            if (x2 - x1) < 15:
                x2 = x1 + 15
                if x2 > w:
                    x2 = w
                    x1 = w - 15
            
            if click_x < x1:
                if self.command:
                    self.command("scroll", -1, "pages")
                self._first_x = click_x
                self._start_fraction = self.fraction_start
            elif click_x > x2:
                if self.command:
                    self.command("scroll", 1, "pages")
                self._first_x = click_x
                self._start_fraction = self.fraction_start
            else:
                self._first_x = click_x
                self._start_fraction = self.fraction_start
                
    def _on_drag(self, event):
        if self.on_scroll_start:
            self.on_scroll_start()
            
        if self.orient == "vertical":
            h = self.winfo_height()
            if h <= 1: return
            dy = event.y - self._first_y
            fraction_diff = dy / h
            new_start = max(0.0, min(1.0 - (self.fraction_end - self.fraction_start), self._start_fraction + fraction_diff))
            if self.command:
                self.command("moveto", new_start)
        else:
            w = self.winfo_width()
            if w <= 1: return
            dx = event.x - self._first_x
            fraction_diff = dx / w
            new_start = max(0.0, min(1.0 - (self.fraction_end - self.fraction_start), self._start_fraction + fraction_diff))
            if self.command:
                self.command("moveto", new_start)

# ─────────────────────────────────────────────
# Collection Picker Widget
# ─────────────────────────────────────────────
class CollectionPicker(tk.Frame):
    ROW_H = 34

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        self._all_names  = []
        self._filtered   = []
        self._checked    = set()
        self._row_frames = []
        self._build()

    def _build(self):
        # ── Search bar
        search_wrap = tk.Frame(self, bg=BG_INPUT,
                               highlightthickness=1, highlightbackground=BORDER)
        search_wrap.pack(fill="x", pady=(0, 8))

        tk.Label(search_wrap, text="⌕", font=("Segoe UI", 13),
                 bg=BG_INPUT, fg=FG_DIM).pack(side="left", padx=(10, 4))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        search_entry = tk.Entry(search_wrap, textvariable=self._search_var,
                                bg=BG_INPUT, fg=FG, relief="flat",
                                font=FONT_ENTRY, insertbackground=FG,
                                highlightthickness=0)
        search_entry.pack(side="left", fill="x", expand=True, ipady=7)

        self._clear_btn = tk.Label(search_wrap, text="✕", font=("Segoe UI", 10),
                                   bg=BG_INPUT, fg=FG_DIM, cursor="hand2", padx=10)
        self._clear_btn.pack(side="right")
        self._clear_btn.bind("<Button-1>", lambda e: self._search_var.set(""))

        # ── List area
        list_outer = tk.Frame(self, bg=BG_CARD,
                              highlightthickness=1, highlightbackground=BORDER)
        list_outer.pack(fill="both", expand=True)

        self._vsb = ModernScrollbar(list_outer, command=None, orient="vertical",
                                    thumb_color=BORDER_MID, hover_color=ACCENT,
                                    trough_color=BG_CARD, width=8, on_scroll_start=self.stop_smooth_scroll)
        self._vsb.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self._canvas = tk.Canvas(list_outer, bg=BG_CARD,
                                 highlightthickness=0,
                                 yscrollcommand=self._vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._vsb.command = self._canvas.yview

        self._inner = tk.Frame(self._canvas, bg=BG_CARD)
        self._win   = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._win, width=e.width))

        for widget in (self._canvas, self._inner):
            widget.bind("<MouseWheel>", self._on_mousewheel)

        # ── Selected tags bar
        tags_outer = tk.Frame(self, bg=BG, pady=7)
        tags_outer.pack(fill="x")
        tk.Label(tags_outer, text="Selected:", font=FONT_SMALL,
                 fg=FG_DIM, bg=BG).pack(side="left", padx=(2, 8))
        self._tags_frame = tk.Frame(tags_outer, bg=BG)
        self._tags_frame.pack(side="left", fill="x", expand=True)
        tk.Label(self._tags_frame, text="None",
                 font=FONT_SMALL, fg=FG_LIGHT, bg=BG).pack(side="left")

        self._count_lbl = tk.Label(tags_outer, text="",
                                   font=FONT_MONO, fg=FG_DIM, bg=BG)
        self._count_lbl.pack(side="right", padx=(0, 2))

    def _on_inner_configure(self, e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        for w in self._inner.winfo_children():
            if not hasattr(w, '_mw_bound'):
                w.bind("<MouseWheel>", self._on_mousewheel)
                for c in w.winfo_children():
                    c.bind("<MouseWheel>", self._on_mousewheel)
                w._mw_bound = True

    def stop_smooth_scroll(self):
        self._scrolling_active = False

    def _on_mousewheel(self, event):
        if not hasattr(self, "_target_scroll"):
            self._target_scroll = self._canvas.yview()[0]
            self._scrolling_active = False

        delta = event.delta
        bbox = self._canvas.bbox("all")
        if not bbox:
            return
        scroll_height = bbox[3] - bbox[1]
        view_height = self._canvas.winfo_height()
        if scroll_height <= view_height:
            return
            
        pixel_step = 80 if sys.platform != 'darwin' else 20
        multiplier = (delta / 120.0) if sys.platform != 'darwin' else (delta / 3.0)
        
        current_y = self._canvas.yview()[0]
        if not self._scrolling_active:
            self._target_scroll = current_y
            
        change_fraction = -(pixel_step * multiplier) / scroll_height
        self._target_scroll = max(0.0, min(1.0, self._target_scroll + change_fraction))
        
        if not self._scrolling_active:
            self._scrolling_active = True
            self._animate_scroll()

    def _animate_scroll(self):
        if not self._scrolling_active:
            return
        current_y = self._canvas.yview()[0]
        diff = self._target_scroll - current_y
        if abs(diff) < 0.001:
            self._canvas.yview_moveto(self._target_scroll)
            self._scrolling_active = False
            return
        step = current_y + diff * 0.2
        self._canvas.yview_moveto(step)
        self.after(12, self._animate_scroll)


    def _on_search(self, *_):
        if not self._all_names: return
        q = self._search_var.get().strip().lower()
        self._filtered = [n for n in self._all_names if q in n.lower()] if q else list(self._all_names)
        self._render_rows()
        self._canvas.yview_moveto(0)

    def load(self, names):
        self._all_names = list(names)
        self._filtered  = list(names)
        self._checked   = set()
        self._search_var.set("")
        self._render_rows()
        self._refresh_tags()

    def _render_rows(self):
        for w in self._inner.winfo_children():
            w.destroy()
        self._row_frames = []

        for name in self._filtered:
            checked = name in self._checked
            row = tk.Frame(self._inner,
                           bg=BG_SEL if checked else BG_CARD,
                           cursor="hand2")
            row.pack(fill="x")

            def _enter(e, r=row, n=name):
                if n not in self._checked:
                    r.config(bg=BG_HOVER)
                    for c in r.winfo_children(): c.config(bg=BG_HOVER)
            def _leave(e, r=row, n=name):
                col = BG_SEL if n in self._checked else BG_CARD
                r.config(bg=col)
                for c in r.winfo_children(): c.config(bg=col)

            row.bind("<Enter>", _enter)
            row.bind("<Leave>", _leave)
            row.bind("<Button-1>", lambda e, n=name: self._toggle(n))
            row.bind("<MouseWheel>", self._on_mousewheel)

            # Left accent bar (3px)
            accent = tk.Frame(row, width=3,
                              bg=ACCENT if checked else BORDER)
            accent.pack(side="left", fill="y")
            accent.bind("<Button-1>", lambda e, n=name: self._toggle(n))

            lbl_fg = BG_CARD if checked else FG
            lbl_bg = BG_SEL  if checked else BG_CARD
            lbl = tk.Label(row, text=f"  {name}", font=FONT_LABEL,
                           fg=lbl_fg, bg=lbl_bg,
                           anchor="w", pady=8)
            lbl.pack(side="left", fill="both", expand=True)
            lbl.bind("<Button-1>", lambda e, n=name: self._toggle(n))
            lbl.bind("<MouseWheel>", self._on_mousewheel)

            tk.Frame(self._inner, bg=BORDER, height=1).pack(fill="x")
            self._row_frames.append((name, row, lbl))

        if not self._filtered:
            tk.Label(self._inner,
                     text="No collections found." if self._search_var.get()
                          else "Click 'Load' to fetch collections.",
                     font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD, pady=18).pack()

        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _toggle(self, name):
        if name in self._checked: self._checked.discard(name)
        else: self._checked.add(name)
        self._render_rows()
        self._refresh_tags()

    def _refresh_tags(self):
        for w in self._tags_frame.winfo_children():
            w.destroy()

        if not self._checked:
            tk.Label(self._tags_frame, text="None",
                     font=FONT_SMALL, fg=FG_LIGHT, bg=BG).pack(side="left")
            self._count_lbl.config(text="")
            return

        for name in sorted(self._checked):
            tag_f = tk.Frame(self._tags_frame, bg=TAG_BG,
                             bd=1, relief="solid",
                             highlightthickness=0)
            tag_f.pack(side="left", padx=(0, 5), pady=1)
            short = name if len(name) <= 22 else name[:20] + "…"
            tk.Label(tag_f, text=short, font=FONT_TAG,
                     fg=TAG_FG, bg=TAG_BG, padx=7, pady=3).pack(side="left")
            x_btn = tk.Label(tag_f, text="×", font=FONT_TAG,
                             fg=FG_DIM, bg=TAG_BG, cursor="hand2", padx=5)
            x_btn.pack(side="left")
            x_btn.bind("<Button-1>", lambda e, n=name: self._toggle(n))

        n = len(self._checked)
        self._count_lbl.config(text=f"{n} selected")

    def get_selected(self):
        return list(self._checked)

    def set_disabled(self, disabled):
        self._canvas.config(state="disabled" if disabled else "normal")
        self._search_var.set("")


# ─────────────────────────────────────────────
# Preferences / Settings Dialog
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# Preferences / Settings Dialog Helpers
# ─────────────────────────────────────────────
def chk_with_tooltip(parent, text, variable, tooltip_text, command=None):
    row = tk.Frame(parent, bg=BG_CARD)
    row.pack(fill="x", pady=4)
    
    chk = ModernCheckbutton(row, text=text, variable=variable, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL, command=command)
    chk.pack(side="left")
    
    info = CircledExclamation(row, BG_CARD)
    info.pack(side="left", padx=(5, 0))
    ToolTip(info, tooltip_text)
    return chk

def entry_row_with_tooltip(parent, label_text, variable, suffix, tooltip_text):
    row = tk.Frame(parent, bg=BG_CARD)
    row.pack(fill="x", pady=6)
    
    left = tk.Frame(row, bg=BG_CARD)
    left.pack(side="left", fill="y", anchor="w")
    
    lbl = tk.Label(left, text=label_text, font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD)
    lbl.pack(side="left")
    
    info = CircledExclamation(left, BG_CARD)
    info.pack(side="left", padx=(5, 0))
    ToolTip(info, tooltip_text)
    
    right = tk.Frame(row, bg=BG_CARD)
    right.pack(side="right", fill="y", anchor="e")
    
    entry = tk.Entry(right, textvariable=variable, width=8, font=FONT_ENTRY,
                     bg=BG_INPUT, fg=FG, relief="flat", insertbackground=FG,
                     highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
    entry.pack(side="left", ipady=2)
    
    if suffix:
        tk.Label(right, text=f" {suffix}", font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD).pack(side="left", padx=(4, 0))
        
    return entry


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Preferences — ZOA")
        self.geometry("640x700")
        self.resizable(True, True)
        self.minsize(580, 500)
        self.configure(bg=BG)
        self.grab_set()
        apply_window_icon(self)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Mappings
        self.provider_map = {
            "Google Gemini": "gemini",
            "Anthropic Claude": "claude",
            "OpenAI": "openai",
            "DeepSeek": "deepseek"
        }
        self.provider_reverse_map = {v: k for k, v in self.provider_map.items()}
        
        # Load current configuration values
        self._provider_var = tk.StringVar(value=self._get_provider_display_name(CONFIG.get('API_PROVIDER', 'gemini')))
        self._model_var = tk.StringVar(value=CONFIG.get('MODEL_NAME', 'gemini-2.5-flash'))
        self._custom_prompt_var = tk.BooleanVar(value=CONFIG.get('CUSTOM_PROMPT', 'False') == 'True')
        
        self._limit_var = tk.StringVar(value=CONFIG.get('LIMIT', '500'))
        self._keyword_count_var = tk.StringVar(value=CONFIG.get('KEYWORD_COUNT', '5'))
        self._dup_var = tk.StringVar(value=CONFIG.get('DUP_MODE', 'overwrite'))
        self._wikilink_var = tk.BooleanVar(value=CONFIG.get('USE_WIKILINKS', 'True') == 'True')
        
        self._full_pdf_var = tk.BooleanVar(value=CONFIG.get('FULL_PDF', 'True') == 'True')
        self._pdf_pages_var = tk.StringVar(value=CONFIG.get('PDF_MAX_PAGES', '30'))
        self._skip_empty_var = tk.BooleanVar(value=CONFIG.get('SKIP_EMPTY_ABS', 'False') == 'True')
        
        self._use_recent_var = tk.BooleanVar(value=CONFIG.get('USE_RECENT', 'False') == 'True')
        self._recent_days_var = tk.StringVar(value=CONFIG.get('RECENT_DAYS', '7'))
        
        self._filename_var = tk.StringVar(value=CONFIG.get('FILENAME_FMT', 'default'))
        
        self._build_ui()
        
        # Center on screen
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 640) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 700) // 2
        self.geometry(f"640x700+{x}+{y}")
        
    def _get_provider_display_name(self, internal_name):
        mapping = {
            "gemini": "Google Gemini",
            "claude": "Anthropic Claude",
            "openai": "OpenAI",
            "deepseek": "DeepSeek"
        }
        return mapping.get(internal_name, "Google Gemini")
        
    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self, bg=BG_CARD, bd=0, highlightthickness=1, highlightbackground=BORDER)
        hdr.pack(fill="x")
        inner_hdr = tk.Frame(hdr, bg=BG_CARD, pady=14, padx=24)
        inner_hdr.pack(fill="x")
        tk.Label(inner_hdr, text="ZOA Preferences", font=FONT_H1, fg=FG, bg=BG_CARD).pack(anchor="w")
        tk.Label(inner_hdr, text="Configure folders, naming patterns, models, and limits.", font=FONT_SUBNAME, fg=FG_DIM, bg=BG_CARD).pack(anchor="w", pady=(2, 0))
        
        # ── Scrollable Content Area
        outer_f = tk.Frame(self, bg=BG)
        outer_f.pack(fill="both", expand=True, padx=20, pady=(15, 10))
        
        canvas = tk.Canvas(outer_f, bg=BG, highlightthickness=0)
        vsb = ModernScrollbar(outer_f, command=canvas.yview, orient="vertical", thumb_color=BORDER_MID, hover_color=ACCENT, trough_color=BG, width=8)
        canvas.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        self._inner = inner_f = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner_f, anchor="nw")
        
        def _configure_inner(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
            
        inner_f.bind("<Configure>", _configure_inner)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        
        self._canvas = canvas
        
        # ── 01. AI Engine Card
        make_section_label(inner_f, "01  AI Model & Provider")
        c1 = card(inner_f)
        c1.pack(fill="x", pady=(0, 10))
        
        prov_row = tk.Frame(c1, bg=BG_CARD)
        prov_row.pack(fill="x", pady=4)
        
        col1 = tk.Frame(prov_row, bg=BG_CARD)
        col1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        lbl1_row = tk.Frame(col1, bg=BG_CARD)
        lbl1_row.pack(anchor="w", pady=(0, 4))
        tk.Label(lbl1_row, text="API Provider", font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD).pack(side="left")
        info1 = CircledExclamation(lbl1_row, BG_CARD)
        info1.pack(side="left", padx=(5, 0))
        ToolTip(info1, "Select the AI service provider to generate paper summaries.")
        
        self.provider_cb = ttk.Combobox(col1, textvariable=self._provider_var,
                                        values=list(self.provider_map.keys()),
                                        state="readonly", font=FONT_LABEL)
        self.provider_cb.pack(fill="x")
        self.provider_cb.bind("<<ComboboxSelected>>", self._on_provider_changed)
        
        col2 = tk.Frame(prov_row, bg=BG_CARD)
        col2.pack(side="left", fill="both", expand=True)
        
        lbl2_row = tk.Frame(col2, bg=BG_CARD)
        lbl2_row.pack(anchor="w", pady=(0, 4))
        tk.Label(lbl2_row, text="Model Name", font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD).pack(side="left")
        info2 = CircledExclamation(lbl2_row, BG_CARD)
        info2.pack(side="left", padx=(5, 0))
        ToolTip(info2, "Select the specific LLM model version. Different models vary in performance, speed, and token cost.")
        
        current_provider_name = self._get_provider_display_name(CONFIG.get('API_PROVIDER', 'gemini'))
        self.model_cb = ttk.Combobox(col2, textvariable=self._model_var,
                                     values=PROVIDER_MODELS.get(current_provider_name, []),
                                     state="readonly", font=FONT_LABEL)
        self.model_cb.pack(fill="x")
        self.model_cb.bind("<<ComboboxSelected>>", self._on_model_changed)
        
        thin_divider(c1, pady=(12, 12))
        
        self._prompt_chk = chk_with_tooltip(
            c1, "Customize AI Prompt Template", self._custom_prompt_var,
            "Enable to edit the system prompt template used for generating summaries.",
            command=self._toggle_prompt_editor
        )
        
        self.prompt_editor_frame = tk.Frame(c1, bg=BG_CARD)
        
        desc_txt = "Available placeholders:  {title}   {content_source}   {keyword_count}   {text}"
        tk.Label(self.prompt_editor_frame, text=desc_txt, font=FONT_VER,
                 fg=FG_DIM, bg=BG_CARD).pack(anchor="w", pady=(8, 4))
                 
        text_wrap = tk.Frame(self.prompt_editor_frame, bg=BG_INPUT,
                            bd=1, relief="solid", highlightthickness=0)
        text_wrap.pack(fill="x", pady=4)
        
        text_vsb = ModernScrollbar(text_wrap, command=None, orient="vertical",
                                   thumb_color=BORDER_MID, hover_color=ACCENT,
                                   trough_color=BG_INPUT, width=8)
        text_vsb.pack(side="right", fill="y")
        
        self.prompt_text_box = tk.Text(text_wrap, height=10, font=FONT_ENTRY,
                                       bg=BG_INPUT, fg=FG, insertbackground=FG,
                                       wrap="word", relief="flat", padx=10, pady=8,
                                       yscrollcommand=text_vsb.set)
        self.prompt_text_box.pack(side="left", fill="x", expand=True)
        text_vsb.command = self.prompt_text_box.yview
        
        self.prompt_text_box.insert("1.0", load_prompt_template())
        
        action_row = tk.Frame(self.prompt_editor_frame, bg=BG_CARD)
        action_row.pack(fill="x", pady=(6, 0))
        
        make_btn_ghost(action_row, "Reset to Default", self._reset_custom_prompt).pack(side="left")
        
        # ── 02. Summarization Preferences Card
        make_section_label(inner_f, "02  Summarization Preferences")
        c2 = card(inner_f)
        c2.pack(fill="x", pady=(0, 10))
        
        self._limit_entry = entry_row_with_tooltip(
            c2, "Maximum Papers to Process", self._limit_var, "papers",
            "The maximum number of papers ZOA will process in a single execution. Prevents unexpected API costs."
        )
        
        self._kw_entry = entry_row_with_tooltip(
            c2, "Keywords to Extract", self._keyword_count_var, "keywords",
            "The number of scholarly keywords the AI should extract and append to each paper summary."
        )
        
        thin_divider(c2, pady=(10, 10))
        
        dup_lbl_row = tk.Frame(c2, bg=BG_CARD)
        dup_lbl_row.pack(anchor="w", pady=(4, 6))
        tk.Label(dup_lbl_row, text="Duplicate File Mode", font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD).pack(side="left")
        dup_info = CircledExclamation(dup_lbl_row, BG_CARD)
        dup_info.pack(side="left", padx=(5, 0))
        ToolTip(dup_info, "How ZOA handles Zotero items that already have a summary Markdown file in Obsidian.")
        
        dup_modes = [
            ("overwrite", "Overwrite (replace existing summaries)"),
            ("skip", "Skip (leave existing summaries untouched)"),
            ("merge", "Merge (append new sections to existing summaries)")
        ]
        for val, desc in dup_modes:
            rb_row = tk.Frame(c2, bg=BG_CARD)
            rb_row.pack(fill="x", pady=2)
            rb = ModernRadiobutton(rb_row, text=desc, variable=self._dup_var, value=val, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL)
            rb.pack(anchor="w")
            
        thin_divider(c2, pady=(10, 10))
        
        self._wiki_chk = chk_with_tooltip(
            c2, "Use [[Wikilinks]] for Collections", self._wikilink_var,
            "Format Zotero collections inside summaries as Obsidian internal wikilinks [[Collection Name]]."
        )
        
        # ── 03. Text Extraction Options Card
        make_section_label(inner_f, "03  Text Extraction Options")
        c3 = card(inner_f)
        c3.pack(fill="x", pady=(0, 10))
        
        self._full_pdf_chk = chk_with_tooltip(
            c3, "Read Full PDF Content", self._full_pdf_var,
            "Extract text from attached PDF files to feed to the AI. If disabled, ZOA falls back to the Zotero abstract.",
            command=self._on_full_pdf_toggled
        )
        
        self._pg_entry = entry_row_with_tooltip(
            c3, "Maximum PDF Pages to Analyze", self._pdf_pages_var, "pages",
            "Limits text extraction to the first N pages of PDFs to save API tokens and time."
        )
        
        self._skip_chk = chk_with_tooltip(
            c3, "Skip papers with empty abstracts in Zotero DB", self._skip_empty_var,
            "Skip summarization for papers that do not have any abstract text in Zotero."
        )
        
        # ── 04. Recent Papers Filter Card
        make_section_label(inner_f, "04  Recent Papers Filter")
        c4 = card(inner_f)
        c4.pack(fill="x", pady=(0, 10))
        
        self._use_recent_chk = chk_with_tooltip(
            c4, "Only Process Recent Papers", self._use_recent_var,
            "Limit summarization to papers that were added or modified in Zotero within a specific number of days.",
            command=self._on_use_recent_toggled
        )
        
        self._recent_days_entry = entry_row_with_tooltip(
            c4, "Recent Days Limit", self._recent_days_var, "days",
            "Specify the threshold in days. Only papers newer than this will be processed."
        )
        
        # ── 05. Obsidian Filename Format Card
        make_section_label(inner_f, "05  Obsidian Filename Format")
        c5 = card(inner_f)
        c5.pack(fill="x", pady=(0, 10))
        
        fn_lbl_row = tk.Frame(c5, bg=BG_CARD)
        fn_lbl_row.pack(anchor="w", pady=(0, 6))
        tk.Label(fn_lbl_row, text="Filename Format Style", font=FONT_SMALL, fg=FG_DIM, bg=BG_CARD).pack(side="left")
        fn_info = CircledExclamation(fn_lbl_row, BG_CARD)
        fn_info.pack(side="left", padx=(5, 0))
        ToolTip(fn_info, "Select the naming style for generated Markdown files in your vault.")
        
        formats = [
            ("default", "Classic ZOA: [Author]_[Year]_[Journal]\n(e.g., Lee_2026_ZOA.md)"),
            ("title", "Clean Title: [Paper Title]\n(e.g., An Automated Paper Summary Pipeline.md)"),
            ("year_author_title", "Structured Year: [[Year]] [Author] - [Title]\n(e.g., [2026] Lee - An Automated Paper Summary Pipeline.md)"),
            ("author_year_title", "Readable Year: [Author] ([Year]) - [Title]\n(e.g., Lee (2026) - An Automated Paper Summary Pipeline.md)")
        ]
        
        for val, desc in formats:
            row = tk.Frame(c5, bg=BG_CARD)
            row.pack(fill="x", pady=6)
            rb = ModernRadiobutton(row, text=desc, variable=self._filename_var, value=val, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL)
            rb.pack(anchor="w")
            
        # ── 06. System Utilities Card
        sec6_row = tk.Frame(inner_f, bg=BG)
        sec6_row.pack(fill="x", pady=(22, 7))
        tk.Label(sec6_row, text="06  SYSTEM UTILITIES", font=FONT_SEC,
                 fg=FG_DIM, bg=BG).pack(side="left")
        util_info = CircledExclamation(sec6_row, BG)
        util_info.pack(side="left", padx=(7, 0))
        ToolTip(util_info,
                "Open Config Directory  →  .env file (all keys & folder paths)\n"
                "Open AI Prompt File    →  prompt_template.txt (system prompt)\n\n"
                "Keys editable in .env:\n"
                "  GEMINI_KEY / CLAUDE_KEY / OPENAI_KEY / DEEPSEEK_KEY\n"
                "  API_PROVIDER   (gemini | claude | openai | deepseek)\n"
                "  PDF_PATH       (Zotero PDF storage folder)\n"
                "  OBS_PATH       (Obsidian vault output folder)\n"
                "  ZOTERO_DB      (path to Zotero SQLite database)\n"
                "  MODEL_NAME     (e.g. gemini-2.5-flash, gpt-4o)")

        c6 = card(inner_f)
        c6.pack(fill="x", pady=(0, 15))
        
        field_label(c6, "Easily locate configurations and prompt templates:")
        
        btn_row = tk.Frame(c6, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(8, 4))
        
        make_btn_ghost(btn_row, "Open .env Directory", self._open_env_dir).pack(side="left", padx=(0, 8), fill="x", expand=True)
        make_btn_ghost(btn_row, "Open AI Prompt File", self._open_prompt_template).pack(side="left", padx=(0, 8), fill="x", expand=True)
        
        thin_divider(c6, pady=(12, 12))
        
        field_label(c6, "Rerun initial setup wizard to re-authenticate keys or directories:")
        make_btn_primary(c6, "Rerun Setup Wizard", self._rerun_wizard, bg_color=ACCENT_POINT, hover_color=ACCENT_POINT_H).pack(fill="x", pady=(4, 0))
        
        # ── Footer / Navigation Bar
        ftr_border = tk.Frame(self, bg=BORDER, height=1)
        ftr_border.pack(fill="x")
        
        ftr = tk.Frame(self, bg=BG_CARD, padx=24, pady=12)
        ftr.pack(fill="x", side="bottom")
        
        make_btn_primary(ftr, "Save Settings", self._save_settings).pack(side="right", padx=(8, 0))
        make_btn_ghost(ftr, "Cancel", self._on_close).pack(side="right")
        
        # Initialize dynamic view states
        self._toggle_prompt_editor()
        self._on_full_pdf_toggled()
        self._on_use_recent_toggled()
        
        # Bind mousewheel scrolling dynamically to all widgets
        self._bind_mousewheel(self, self._dialog_scroll)
        
    def _on_provider_changed(self, event=None):
        prov_name = self._provider_var.get()
        models = PROVIDER_MODELS.get(prov_name, [])
        self.model_cb.config(values=models)
        if models:
            self.model_cb.set(models[0])
            self._model_var.set(models[0])
            
    def _on_model_changed(self, event=None):
        pass
        
    def _toggle_prompt_editor(self):
        if self._custom_prompt_var.get():
            self.prompt_editor_frame.pack(fill="x", pady=(8, 0))
        else:
            self.prompt_editor_frame.pack_forget()
        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        
    def _on_full_pdf_toggled(self):
        state = "normal" if self._full_pdf_var.get() else "disabled"
        self._pg_entry.config(state=state, bg=BG_INPUT if state == "normal" else BORDER)
        
    def _on_use_recent_toggled(self):
        state = "normal" if self._use_recent_var.get() else "disabled"
        self._recent_days_entry.config(state=state, bg=BG_INPUT if state == "normal" else BORDER)
        
    def _reset_custom_prompt(self):
        self.prompt_text_box.delete("1.0", "end")
        self.prompt_text_box.insert("1.0", DEFAULT_PROMPT_TEMPLATE)
        save_prompt_template(DEFAULT_PROMPT_TEMPLATE)
        
    def _open_env_dir(self):
        try:
            import platform, subprocess
            path = get_app_dir()
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open directory: {e}", parent=self)
            
    def _open_prompt_template(self):
        try:
            import platform, subprocess
            path = get_app_dir() / 'prompt_template.txt'
            if not path.exists():
                save_prompt_template(DEFAULT_PROMPT_TEMPLATE)
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}", parent=self)
            
    def _rerun_wizard(self):
        if messagebox.askyesno("Setup Wizard", "Do you want to rerun the initial setup wizard?", parent=self):
            self.destroy()
            wizard = SetupWizard(self.app.root)
            self.app.root.wait_window(wizard)
            
            global CONFIG, GEMINI_KEY, CLAUDE_KEY, OPENAI_KEY, DEEPSEEK_KEY, API_PROVIDER, PDF_PATH, OBS_PATH, ZOTERO_DB, MODEL_NAME
            CONFIG = load_config()
            GEMINI_KEY   = CONFIG.get('GEMINI_KEY', '')
            CLAUDE_KEY   = CONFIG.get('CLAUDE_KEY', '')
            OPENAI_KEY   = CONFIG.get('OPENAI_KEY', '')
            DEEPSEEK_KEY = CONFIG.get('DEEPSEEK_KEY', '')
            API_PROVIDER = CONFIG.get('API_PROVIDER', 'gemini')
            PDF_PATH     = CONFIG.get('PDF_PATH', '')
            OBS_PATH     = CONFIG.get('OBS_PATH', '')
            ZOTERO_DB    = CONFIG.get('ZOTERO_DB', '')
            MODEL_NAME   = CONFIG.get('MODEL_NAME', 'gemini-2.5-flash')
            
            self.app._check_env()
            
    def _save_settings(self):
        try:
            limit = int(self._limit_var.get().strip())
            if limit <= 0: raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Max Papers Limit must be a positive integer.", parent=self)
            return
            
        try:
            kw_count = int(self._keyword_count_var.get().strip())
            if kw_count <= 0: raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Keywords to Extract must be a positive integer.", parent=self)
            return
            
        try:
            pages = int(self._pdf_pages_var.get().strip())
            if pages <= 0: raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Maximum PDF Pages must be a positive integer.", parent=self)
            return
            
        try:
            recent_days = int(self._recent_days_var.get().strip())
            if recent_days <= 0: raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Recent Days Limit must be a positive integer.", parent=self)
            return

        if self._custom_prompt_var.get():
            prompt_content = self.prompt_text_box.get("1.0", "end-1c").strip()
            if prompt_content:
                save_prompt_template(prompt_content)
            else:
                messagebox.showerror("Validation Error", "Custom AI Prompt Template cannot be empty.", parent=self)
                return

        global CONFIG
        CONFIG['API_PROVIDER'] = self.provider_map[self._provider_var.get()]
        CONFIG['MODEL_NAME'] = self._model_var.get()
        CONFIG['CUSTOM_PROMPT'] = "True" if self._custom_prompt_var.get() else "False"
        
        CONFIG['LIMIT'] = str(limit)
        CONFIG['KEYWORD_COUNT'] = str(kw_count)
        CONFIG['DUP_MODE'] = self._dup_var.get()
        CONFIG['USE_WIKILINKS'] = "True" if self._wikilink_var.get() else "False"
        
        CONFIG['FULL_PDF'] = "True" if self._full_pdf_var.get() else "False"
        CONFIG['PDF_MAX_PAGES'] = str(pages)
        CONFIG['SKIP_EMPTY_ABS'] = "True" if self._skip_empty_var.get() else "False"
        
        CONFIG['USE_RECENT'] = "True" if self._use_recent_var.get() else "False"
        CONFIG['RECENT_DAYS'] = str(recent_days)
        
        CONFIG['FILENAME_FMT'] = self._filename_var.get()
        
        save_config(CONFIG)
        
        global GEMINI_KEY, CLAUDE_KEY, OPENAI_KEY, DEEPSEEK_KEY, API_PROVIDER, MODEL_NAME
        GEMINI_KEY   = CONFIG.get('GEMINI_KEY', '')
        CLAUDE_KEY   = CONFIG.get('CLAUDE_KEY', '')
        OPENAI_KEY   = CONFIG.get('OPENAI_KEY', '')
        DEEPSEEK_KEY = CONFIG.get('DEEPSEEK_KEY', '')
        API_PROVIDER = CONFIG.get('API_PROVIDER', 'gemini')
        MODEL_NAME   = CONFIG.get('MODEL_NAME', 'gemini-2.5-flash')
        
        self.app._check_env()
        
        self.destroy()
        messagebox.showinfo("Saved", "Preferences have been saved successfully.", parent=self.app.root)
        
    def _on_close(self):
        self.grab_release()
        self.destroy()
        
    def center_window(self):
        self.update_idletasks()
        w, h = 640, 700
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
    def _dialog_scroll(self, event):
        delta = event.delta
        scroll_units = -1 * (delta // 120) if sys.platform != 'darwin' else -1 * delta
        self._canvas.yview_scroll(scroll_units, "units")

    def _bind_mousewheel(self, widget, callback):
        widget.bind("<MouseWheel>", callback)
        for child in widget.winfo_children():
            self._bind_mousewheel(child, callback)



# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────
class ZOAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZOA (Zotero-Obsidian-AI Summary)")
        self.root.geometry("820x920")
        self.root.resizable(True, True)
        self.root.configure(bg=BG)
        self.root.minsize(720, 760)
        self.running = False
        self._build_ui()
        self._check_deps()
        self._check_env()

    def _build_ui(self):
        # ── Header
        header = tk.Frame(self.root, bg=BG_CARD,
                          bd=0, highlightthickness=1,
                          highlightbackground=BORDER)
        header.pack(fill="x")

        inner_h = tk.Frame(header, bg=BG_CARD, pady=18, padx=32)
        inner_h.pack(fill="x")

        left = tk.Frame(inner_h, bg=BG_CARD)
        left.pack(side="left")
        tk.Label(left, text="ZOA (Zotero-Obsidian-AI Summary)",
                 font=FONT_APPNAME, fg=FG, bg=BG_CARD).pack(anchor="w")
        tk.Label(left, text="v1.0-beta  |  Copyright (c) 2026 Heeyoung Lee",
                 font=FONT_SUBNAME, fg=FG_DIM, bg=BG_CARD).pack(anchor="w", pady=(2, 0))

        right_h = tk.Frame(inner_h, bg=BG_CARD)
        right_h.pack(side="right", fill="y", anchor="se")
        
        tk.Label(right_h, text="MIT License",
                 font=FONT_VER, fg=FG_LIGHT, bg=BG_CARD).pack(side="left", anchor="center", padx=(0, 15))
                 
        self.settings_btn = ModernButton(right_h, text="⚙ Settings", command=self._open_settings,
                                         bg=BG_CARD, fg=FG_MID, font=FONT_SUBNAME,
                                         hover_bg=BG_HOVER, border_color=BORDER, padx=8, pady=4)
        self.settings_btn.pack(side="left", anchor="center")

        # ── Scroll canvas
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        self._main_vsb = ModernScrollbar(outer, command=None, orient="vertical",
                                         thumb_color=BORDER_MID, hover_color=ACCENT,
                                         trough_color=BG, width=10, on_scroll_start=self.stop_smooth_scroll)
        self._main_vsb.pack(side="right", fill="y")

        self._canvas = tk.Canvas(outer, bg=BG, highlightthickness=0,
                                 yscrollcommand=self._main_vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._main_vsb.command = self._canvas.yview

        self.main = tk.Frame(self._canvas, bg=BG, padx=30, pady=22)
        self._wid = self._canvas.create_window((0, 0), window=self.main, anchor="nw")

        def _resize(e):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
            self._canvas.itemconfig(self._wid, width=self._canvas.winfo_width())
        self.main.bind("<Configure>", _resize)
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._wid, width=e.width))
        self.root.bind_all("<MouseWheel>", self._on_root_scroll)

        M = self.main

        # ─── 01  Collections ──────────────────
        make_section_label(M, "01  Zotero Collections")
        c1 = card(M); c1.pack(fill="x")

        top = tk.Frame(c1, bg=BG_CARD); top.pack(fill="x", pady=(0, 12))
        self._load_btn = make_btn_primary(top, "Load Collections", self._load_collections)
        self._load_btn.pack(side="left", padx=(0, 14))

        self.all_var = tk.BooleanVar()
        self.all_chk = ModernCheckbutton(top, text="Entire Library",
                                         variable=self.all_var, command=self._toggle_all,
                                         bg=BG_CARD, fg=FG_MID, font=FONT_LABEL)
        self.all_chk.pack(side="right")

        self._picker = CollectionPicker(c1, height=210)
        self._picker.pack(fill="x")

        # ─── 02  Paths ────────────────────────
        make_section_label(M, "02  File Paths")
        c2 = card(M); c2.pack(fill="x")

        field_label_with_tooltip(c2, "PDF Folder", 
                                 "Select the folder containing your Zotero PDFs.\n(Scans recursively. Zotero 'storage' or Zotmoov folders work perfectly.)")
        self.pdf_path_var = tk.StringVar(value=PDF_PATH)
        self._path_row(c2, self.pdf_path_var)
        thin_divider(c2, (12, 12))
        field_label_with_tooltip(c2, "Obsidian Vault",
                                 "Select your Obsidian Vault (or subfolder)\nwhere the summary Markdown (.md) notes will be saved.")
        self.obs_path_var = tk.StringVar(value=OBS_PATH)
        self._path_row(c2, self.obs_path_var)

        # ─── 03  Progress ─────────────────────
        make_section_label(M, "03  Progress")
        c4 = card(M); c4.pack(fill="x")

        prog_top = tk.Frame(c4, bg=BG_CARD); prog_top.pack(fill="x", pady=(0, 8))
        self.prog_label = tk.Label(prog_top, text="Ready",
                                   font=FONT_STATUS, fg=FG_DIM, bg=BG_CARD)
        self.prog_label.pack(side="left")
        self.prog_count = tk.Label(prog_top, text="",
                                   font=FONT_MONO, fg=FG_MID, bg=BG_CARD)
        self.prog_count.pack(side="right")

        sty = ttk.Style()
        sty.theme_use("default")
        sty.configure("Slim.Horizontal.TProgressbar",
                       troughcolor=BORDER, background=ACCENT,
                       bordercolor=BORDER, lightcolor=ACCENT,
                       darkcolor=ACCENT, thickness=3)
        self.progress = ttk.Progressbar(c4, style="Slim.Horizontal.TProgressbar",
                                        orient="horizontal", mode="determinate")
        self.progress.pack(fill="x")

        # ─── Run / Stop ───────────────────────
        tk.Frame(M, bg=BORDER, height=1).pack(fill="x", pady=(20, 14))
        btn_row = tk.Frame(M, bg=BG); btn_row.pack(fill="x")
        self.run_btn = make_btn_primary(btn_row, "▶  Run", self._start_run, bg_color=ACCENT_POINT, hover_color=ACCENT_POINT_H)
        self.run_btn.pack(side="left", padx=(0, 10))
        self.stop_btn = make_btn_ghost(btn_row, "◼  Stop", self._stop_run)
        self.stop_btn.config(state="disabled", fg=FG_LIGHT)
        self.stop_btn.pack(side="left", padx=(0, 20))
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(btn_row, textvariable=self.status_var,
                 font=FONT_STATUS, fg=FG_DIM, bg=BG).pack(side="left")

        # ─── 04  Log ──────────────────────────
        make_section_label(M, "04  Execution Log")
        log_wrap = tk.Frame(M, bg=LOG_BG,
                            bd=1, relief="solid",
                            highlightthickness=0)
        log_wrap.pack(fill="both", expand=True, pady=(0, 28))

        vsb_log = ModernScrollbar(log_wrap, command=None, orient="vertical",
                                  thumb_color=BORDER_MID, hover_color=ACCENT,
                                  trough_color=LOG_BG, width=8)
        vsb_log.pack(side="right", fill="y")

        self.log_box = tk.Text(log_wrap, height=14, font=FONT_LOG,
                               bg=LOG_BG, fg=LOG_FG,
                               insertbackground=LOG_FG,
                               wrap="word", relief="flat",
                               padx=18, pady=14,
                               yscrollcommand=vsb_log.set,
                               state="disabled")
        self.log_box.pack(side="left", fill="both", expand=True)
        vsb_log.command = self.log_box.yview

        self.log_box.tag_config("ok",   foreground=LOG_OK)
        self.log_box.tag_config("info", foreground=LOG_FG)
        self.log_box.tag_config("warn", foreground=LOG_WARN)
        self.log_box.tag_config("err",  foreground="#B85450")
        self.log_box.tag_config("done", foreground=LOG_OK,
                                font=("Consolas", 11, "bold"))
        self.log_box.tag_config("skip", foreground=LOG_SKIP)

        self._log("ZOA initialized.", "ok")
        self._log("Load Zotero collections and configure paths to begin.", "info")

    def stop_smooth_scroll(self):
        self._scrolling_active = False

    def _open_settings(self):
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog)

    def _on_root_scroll(self, event):
        w = event.widget
        try:
            toplevel = w.winfo_toplevel()
            if toplevel != self.root:
                return
            cur = w
            while cur:
                if (cur is self._picker._canvas or 
                    cur is self._picker._inner or 
                    cur is self.log_box):
                    return
                cur = cur.master
        except: pass
        
        if not hasattr(self, "_target_scroll"):
            self._target_scroll = self._canvas.yview()[0]
            self._scrolling_active = False

        delta = event.delta
        bbox = self._canvas.bbox("all")
        if not bbox:
            return
        scroll_height = bbox[3] - bbox[1]
        view_height = self._canvas.winfo_height()
        if scroll_height <= view_height:
            return
            
        pixel_step = 80 if sys.platform != 'darwin' else 20
        multiplier = (delta / 120.0) if sys.platform != 'darwin' else (delta / 3.0)
        
        current_y = self._canvas.yview()[0]
        if not self._scrolling_active:
            self._target_scroll = current_y
            
        change_fraction = -(pixel_step * multiplier) / scroll_height
        self._target_scroll = max(0.0, min(1.0, self._target_scroll + change_fraction))
        
        if not self._scrolling_active:
            self._scrolling_active = True
            self._animate_scroll()

    def _animate_scroll(self):
        if not self._scrolling_active:
            return
        current_y = self._canvas.yview()[0]
        diff = self._target_scroll - current_y
        if abs(diff) < 0.001:
            self._canvas.yview_moveto(self._target_scroll)
            self._scrolling_active = False
            return
        step = current_y + diff * 0.2
        self._canvas.yview_moveto(step)
        self.root.after(12, self._animate_scroll)


    def _toggle_chk(self, parent, text, var, command=None, pad_left=0):
        chk = ModernCheckbutton(parent, text=text, variable=var,
                                command=command, bg=BG_CARD, fg=FG_MID, font=FONT_LABEL)
        chk.pack(side="left", padx=(pad_left, 0))

    def _path_row(self, parent, var):
        row = tk.Frame(parent, bg=BG_CARD); row.pack(fill="x")
        make_entry(row, var, width=54).pack(side="left", padx=(0, 10), ipady=6)
        make_btn_ghost(row, "Browse…", lambda: self._browse(var)).pack(side="left")

    def _apply_combo_style(self):
        s = ttk.Style()
        s.configure("TCombobox",
                    fieldbackground=BG_INPUT, background=BG_INPUT,
                    foreground=FG, selectbackground=BG_INPUT,
                    selectforeground=FG, bordercolor=BORDER,
                    arrowcolor=FG, relief="flat", padding=5)
        s.map("TCombobox",
              fieldbackground=[("readonly", BG_INPUT)],
              selectbackground=[("readonly", BG_INPUT)],
              selectforeground=[("readonly", FG)])

    def _browse(self, var):
        p = filedialog.askdirectory(initialdir=var.get() or os.path.expanduser("~"))
        if p: var.set(p)

    def _toggle_all(self):
        self._picker.set_disabled(self.all_var.get())



    def _load_collections(self):
        self._log("Loading collections from local Zotero DB…", "info")
        self._load_btn.config(state="disabled")
        def _fetch():
            try:
                db = get_zotero_db()
                names = sqlite_get_collection_names(db)
                db.close()
                self.root.after(0, lambda: self._set_collections(names))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {e}", "err"))
            finally:
                self.root.after(0, lambda: self._load_btn.config(state="normal"))
        threading.Thread(target=_fetch, daemon=True).start()

    def _set_collections(self, names):
        self._picker.load(names)
        self._log(f"✓  {len(names)} collections loaded.", "ok")

    def _check_env(self):
        env_path = get_app_dir() / '.env'
        if env_path.exists():
            self._log("✓  Config loaded from .env", "ok")
        else:
            self._log("  .env not found — run Setup to configure.", "warn")

    def _check_deps(self):
        missing = check_and_import()
        if missing:
            self._log("Missing packages: " + ", ".join(missing), "err")
            self._log("Run:  pip install " + " ".join(missing), "err")

    def _log(self, msg, tag="info"):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _set_status(self, msg):
        self.status_var.set(msg)

    def _set_progress(self, current, total):
        pct = int(current / total * 100) if total > 0 else 0
        self.progress['value'] = pct
        self.prog_count.config(text=f"{current} / {total}")
        self.prog_label.config(text=f"{pct}%  complete")

    def _start_run(self):
        if check_and_import():
            self._log("Install missing packages first.", "err"); return
        use_all   = self.all_var.get()
        col_names = [] if use_all else self._picker.get_selected()
        if not use_all and not col_names:
            self._log("Select at least one collection, or check Entire Library.", "err")
            return
        pdf_path    = self.pdf_path_var.get().strip()
        obs_path    = self.obs_path_var.get().strip()
        
        # Auto-save paths to CONFIG
        global CONFIG
        CONFIG['PDF_PATH'] = pdf_path
        CONFIG['OBS_PATH'] = obs_path
        save_config(CONFIG)
        
        # Load settings from CONFIG
        read_full     = CONFIG.get('FULL_PDF', 'True') == 'True'
        try:
            limit = int(CONFIG.get('LIMIT', '500'))
        except:
            limit = 500
        try:
            keyword_count = int(CONFIG.get('KEYWORD_COUNT', '5'))
        except:
            keyword_count = 5
            
        dup_mode      = CONFIG.get('DUP_MODE', 'overwrite')
        use_wiki      = CONFIG.get('USE_WIKILINKS', 'True') == 'True'
        use_recent    = CONFIG.get('USE_RECENT', 'False') == 'True'
        try:
            recent_days = int(CONFIG.get('RECENT_DAYS', '7')) if use_recent else None
        except:
            recent_days = 7 if use_recent else None
            
        if not obs_path:
            self._log("Set Obsidian output folder first.", "err"); return
        if read_full and not pdf_path:
            self._log("Set PDF folder or disable full PDF mode in Settings.", "err"); return

        self.running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal", fg=FG)
        self._set_status("Running…")
        self.progress['value'] = 0
        self.prog_label.config(text="Starting…")
        self.prog_count.config(text="")
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        # Get active provider display name and model name from CONFIG
        prov_code = CONFIG.get('API_PROVIDER', 'gemini')
        prov_map_rev = {
            "gemini": "Google Gemini",
            "claude": "Anthropic Claude",
            "openai": "OpenAI",
            "deepseek": "DeepSeek"
        }
        prov_name = prov_map_rev.get(prov_code, "Google Gemini")
        model_name = CONFIG.get('MODEL_NAME', 'gemini-2.5-flash')

        threading.Thread(
            target=self._run_pipeline,
            args=(col_names, pdf_path, obs_path, read_full,
                  limit, prov_name, model_name, dup_mode, use_wiki,
                  use_recent, recent_days, keyword_count),
            daemon=True).start()

    def _stop_run(self):
        self.running = False
        self._set_status("Stopping…")
        self._log("Stop requested.", "warn")

    def _run_pipeline(self, col_names, pdf_path, obs_path, read_full,
                      limit, prov_name, active_model, dup_mode, use_wiki, use_recent, recent_days, keyword_count=5):
        try:
            _cfg = load_config()
            active_provider = _cfg.get('API_PROVIDER', 'gemini')
            key_field = PROVIDER_KEYS.get(prov_name, 'GEMINI_KEY')
            active_key = _cfg.get(key_field, '')

            if not active_key:
                self._log(f"Error: API Key for {prov_name} is missing in your .env configuration.", "err")
                self._finish()
                return

            self._log(f"Connecting to {prov_name} API…", "info")
            if active_provider == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=active_key)
                model = genai.GenerativeModel(active_model)
                self._log(f"✓  {prov_name} (using {active_model}) connected.", "ok")
            else:
                self._log(f"✓  {prov_name} (using {active_model}) initialized.", "ok")

            self._log("Opening local Zotero database…", "info")
            db = get_zotero_db()
            self._log("✓  Zotero DB connected.", "ok")

            pdf_index = []
            if read_full and pdf_path and os.path.exists(pdf_path):
                self._log("Indexing PDFs…", "info")
                pdf_index = index_pdf_files(pdf_path)
                self._log(f"✓  {len(pdf_index)} PDFs indexed.", "ok")
            elif read_full:
                self._log("PDF folder not found — abstract mode.", "warn")
                read_full = False

            self._log("Fetching items from Zotero DB…", "info")
            if not col_names:
                self._log("  Mode: Entire Library", "info")
                row_items = sqlite_get_items(db, col_ids=None, limit=limit)
            else:
                self._log(f"  Mode: Collections — {col_names}", "info")
                all_col_ids = []
                for col_name in col_names:
                    ids = sqlite_get_collection_ids(db, col_name)
                    self._log(f"  '{col_name}' → {len(ids)} collection(s)", "info")
                    all_col_ids.extend(ids)
                row_items = sqlite_get_items(db, col_ids=all_col_ids, limit=limit)

            if use_recent and recent_days:
                cutoff = datetime.utcnow() - timedelta(days=recent_days)
                before = len(row_items)
                row_items = [it for it in row_items
                             if self._parse_date(it['dateAdded']) >= cutoff]
                self._log(f"  Recent filter ({recent_days}d): {before} → {len(row_items)}", "ok")

            total = len(row_items)
            self._log(f"✓  {total} items to process.\n" + "─" * 50, "ok")
            self.root.after(0, lambda: self._set_progress(0, total))
            if not os.path.exists(obs_path): os.makedirs(obs_path)
            success = skip_count = 0

            for idx, row in enumerate(row_items, 1):
                if not self.running: break
                item_id   = row['itemID']
                item_key  = row['key']
                date_added = row['dateAdded'] or ''

                fields       = sqlite_get_item_data(db, item_id)
                creators_raw = sqlite_get_creators(db, item_id)
                zot_tags     = sqlite_get_tags(db, item_id)

                title       = fields.get('title', 'No Title')
                raw_abstract = fields.get('abstractNote')
                abstract    = str(raw_abstract).strip() if raw_abstract is not None else ''
                date        = clean_date(fields.get('date', 'No Date'))
                url         = fields.get('url', '')
                publication = fields.get('publicationTitle', 'No Journal')

                all_authors, author_for_file = [], "Unknown"
                if creators_raw:
                    for c in creators_raw:
                        name = f"{c['lastName']}, {c['firstName']}".strip(", ") if c['lastName'] else c['firstName']
                        if name: all_authors.append(name)
                    first = creators_raw[0]['lastName'] or creators_raw[0]['firstName'] or 'Unknown'
                    if len(creators_raw) == 1:
                        author_for_file = first
                    elif len(creators_raw) == 2:
                        second = creators_raw[1]['lastName'] or creators_raw[1]['firstName'] or 'Unknown'
                        author_for_file = f"{first} and {second}"
                    else:
                        author_for_file = f"{first} et al"

                year_m = re.search(r'\d{4}', date)
                year   = year_m.group(0) if year_m else 'NoYear'
                
                # Dynamic filename formatting based on preferences
                fmt = CONFIG.get('FILENAME_FMT', 'default')
                if fmt == 'title':
                    filename = clean_filename(f"{title}.md")
                elif fmt == 'year_author_title':
                    filename = clean_filename(f"[{year}] {author_for_file} - {title}.md")
                elif fmt == 'author_year_title':
                    filename = clean_filename(f"{author_for_file} ({year}) - {title}.md")
                else:
                    # 'default'
                    pub_ac = ("".join(w[0] for w in publication.split()).upper()
                              if publication and publication != 'No Journal' else "NoJournal")
                    filename = clean_filename(f"{author_for_file}_{year}_{pub_ac}.md")
                full_path   = os.path.join(obs_path, filename)
                zotero_link = f"zotero://select/items/0_{item_key}"
                pg          = f"[{idx:>3}/{total}]"

                # Check for empty abstract skip setting
                if CONFIG.get('SKIP_EMPTY_ABS', 'False') == 'True' and not abstract.strip():
                    self._log(f"{pg}  skip (empty abstract)  {title}", "skip")
                    skip_count += 1
                    self.root.after(0, lambda i=idx: self._set_progress(i, total))
                    continue

                if os.path.exists(full_path):
                    if dup_mode == "skip":
                        self._log(f"{pg}  skip  {filename}", "skip")
                        skip_count += 1
                        self.root.after(0, lambda i=idx: self._set_progress(i, total))
                        continue
                    elif dup_mode == "update":
                        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                        if self._parse_date(date_added) <= mtime:
                            self._log(f"{pg}  up-to-date  {filename}", "skip")
                            skip_count += 1
                            self.root.after(0, lambda i=idx: self._set_progress(i, total))
                            continue
                        else:
                            self._log(f"{pg}  updating  {filename}", "warn")

                self._log(f"{pg}  →  {filename}", "info")
                self._set_status(f"{pg} Processing…")

                has_pdf = False; content_source = "abstract"; final_text = abstract
                if read_full and pdf_index:
                    matched = find_best_pdf_match(fields, creators_raw, pdf_index)
                    if matched:
                        try:
                            from pypdf import PdfReader
                            reader = PdfReader(matched)
                            max_pages_cfg = CONFIG.get('PDF_MAX_PAGES', '30')
                            try:
                                max_pages = int(max_pages_cfg)
                                if max_pages <= 0: max_pages = 30
                            except:
                                max_pages = 30
                            extracted = "".join(p.extract_text() or "" for p in reader.pages[:max_pages])
                            if len(extracted) > 500:
                                final_text = extracted; content_source = "full PDF content"; has_pdf = True
                                self._log(f"       ✓  {os.path.basename(matched)}", "ok")
                            else:
                                self._log("       —  PDF insufficient; using abstract.", "warn")
                        except Exception as e:
                            self._log(f"       ✗  PDF error: {e}", "warn")
                    else:
                        self._log("       —  No PDF match.", "skip")

                if not final_text or not final_text.strip():
                    self._log("       ✗  No abstract or PDF text content. Skipping.", "warn")
                    self.root.after(0, lambda i=idx: self._set_progress(i, total))
                    continue

                try:
                    raw_template = self.prompt_text_box.get("1.0", "end-1c").strip()
                except:
                    raw_template = load_prompt_template()

                try:
                    prompt = raw_template.format(
                        content_source=content_source,
                        title=title,
                        keyword_count=keyword_count,
                        text=final_text[:50000]
                    )
                except Exception as format_err:
                    self._log(f"       ⚠  Prompt format error: {format_err}. Using fallback.", "warn")
                    prompt = DEFAULT_PROMPT_TEMPLATE.format(
                        content_source=content_source,
                        title=title,
                        keyword_count=keyword_count,
                        text=final_text[:50000]
                    )
                try:
                    if active_provider == 'gemini':
                        summary_text = model.generate_content(prompt).text
                    elif active_provider == 'claude':
                        summary_text = call_claude_api(active_key, active_model, prompt)
                    elif active_provider == 'openai':
                        url = "https://api.openai.com/v1/chat/completions"
                        summary_text = call_openai_compatible_api(url, active_key, active_model, prompt)
                    elif active_provider == 'deepseek':
                        url = "https://api.deepseek.com/v1/chat/completions"
                        summary_text = call_openai_compatible_api(url, active_key, active_model, prompt)
                except Exception as e:
                    self._log(f"       ⚠  Error: {e}. Retrying in 5s…", "warn")
                    time.sleep(5)
                    try:
                        if active_provider == 'gemini':
                            summary_text = model.generate_content(prompt).text
                        elif active_provider == 'claude':
                            summary_text = call_claude_api(active_key, active_model, prompt)
                        elif active_provider == 'openai':
                            url = "https://api.openai.com/v1/chat/completions"
                            summary_text = call_openai_compatible_api(url, active_key, active_model, prompt)
                        elif active_provider == 'deepseek':
                            url = "https://api.deepseek.com/v1/chat/completions"
                            summary_text = call_openai_compatible_api(url, active_key, active_model, prompt)
                    except Exception as e2:
                        summary_text = f"Summary Failed: {e2}"

                if use_wiki:
                    kws          = extract_keywords_from_summary(summary_text)
                    summary_text = apply_wikilinks_to_summary(summary_text, kws)
                    authors_wl   = to_wikilinks(all_authors)
                    journal_wl   = f"[[{publication.title()}]]" if publication else "No Journal"
                    tags_wl      = to_wikilinks(zot_tags) if zot_tags else "None"
                else:
                    authors_wl = ", ".join(all_authors)
                    journal_wl = publication.title() if publication else "No Journal"
                    tags_wl    = ", ".join(zot_tags) if zot_tags else "None"

                authors_yaml = "\n".join(f"  - {a}" for a in all_authors)
                md_content = f"""---
title: "{sanitize_yaml(title)}"
authors:
{authors_yaml}
date: {date}
date_added: {date_added}
journal: "{sanitize_yaml(publication.title() if publication else 'No Journal')}"
url: {url}
zotero_link: {zotero_link}
---

# {sanitize_yaml(title)}

## Bibliographic Info
- **Authors**: {authors_wl}
- **Journal**: {journal_wl}
- **Date**: {date}
- **Zotero Link**: [Open in Zotero]({zotero_link})
- **PDF Status**: {"PDF Found" if has_pdf else "PDF Not Found"}
- **Zotero Tags**: {tags_wl}
- **URL**: {url}

## AI Summary ({content_source})
{summary_text}

---
## Original Abstract
{sanitize_abstract(abstract)}
"""
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                self._log("       ✓  Saved.", "ok")
                success += 1
                self.root.after(0, lambda i=idx: self._set_progress(i, total))
                time.sleep(1)

            self._log("\n" + "─" * 50, "ok")
            self._log(f"Done.  {success} saved  |  {skip_count} skipped.", "done")
            self._set_status(f"Done — {success} processed, {skip_count} skipped.")
            self.root.after(0, lambda: self._set_progress(total, total))

        except Exception as e:
            import traceback
            self._log(f"Fatal: {e}", "err")
            self._log(traceback.format_exc(), "err")
            self._set_status("Error.")
        finally:
            try: db.close()
            except: pass
            self._finish()

    def _parse_date(self, s):
        try:    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        except: return datetime.min

    def _finish(self):
        self.running = False
        self.root.after(0, lambda: self.run_btn.config(state="normal"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled", fg=FG_LIGHT))


# ─────────────────────────────────────────────
# First-run Setup Wizard
# ─────────────────────────────────────────────
class SetupWizard(tk.Toplevel):
    """Modal setup wizard shown on first launch (no .env or missing API keys)."""

    STEPS = [
        {
            "title": "API Keys",
            "icon": "🔑",
            "desc": ("Enter the API keys for the services you want to use.\n"
                     "You need at least one key configured to run the application."),
            "type": "keys",
        },
        {
            "title": "Default Provider",
            "icon": "🤖",
            "desc": "Select which AI provider you want to use by default.",
            "type": "provider",
        },
        {
            "title": "Obsidian Vault Folder",
            "icon": "📓",
            "desc": ("Choose the Obsidian folder where summary notes will be saved.\n"
                     "You can also set or change this later inside the app."),
            "field": "OBS_PATH",
            "label": "Obsidian Output Folder",
            "placeholder": "C:\\Users\\You\\Obsidian\\Papers",
            "browse": True,
            "required": False,
        },
        {
            "title": "Zotero Database",
            "icon": "📚",
            "desc": ("ZOA reads your local Zotero database directly — "
                     "no sync needed.\nLeave blank to use the default Zotero location."),
            "field": "ZOTERO_DB",
            "label": "Zotero DB Path  (zotero.sqlite)",
            "placeholder": "Auto-detect  (leave blank for default)",
            "browse": False,
            "required": False,
        },
        {
            "title": "PDF Folder",
            "icon": "📄",
            "desc": ("Optional: point to the folder where Zotero stores PDFs\n"
                     "to enable full-text summarization instead of abstract-only."),
            "field": "PDF_PATH",
            "label": "Zotero PDF Storage Folder",
            "placeholder": "Optional — leave blank to use abstract only",
            "browse": True,
            "required": False,
        },
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Setup — ZOA (Zotero-Obsidian-AI Summary)")
        self.geometry("560x640")
        apply_window_icon(self)

        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()                 # modal
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._step   = 0
        self._values = {
            "GEMINI_KEY": tk.StringVar(),
            "CLAUDE_KEY": tk.StringVar(),
            "OPENAI_KEY": tk.StringVar(),
            "DEEPSEEK_KEY": tk.StringVar(),
            "OBS_PATH": tk.StringVar(),
            "ZOTERO_DB": tk.StringVar(),
            "PDF_PATH": tk.StringVar(),
        }
        self._provider_var = tk.StringVar(value="gemini")
        self._ok     = False            # did the user finish setup?

        # pre-fill with existing config
        cfg = load_config()
        for field in self._values:
            self._values[field].set(cfg.get(field, ""))
        if cfg.get("API_PROVIDER"):
            self._provider_var.set(cfg["API_PROVIDER"])

        # auto-detect Zotero DB
        default_db = Path.home() / 'Zotero' / 'zotero.sqlite'
        if default_db.exists() and not self._values["ZOTERO_DB"].get():
            self._values["ZOTERO_DB"].set(str(default_db))

        self._build()
        self._render_step()
        self.update_idletasks()
        # Center on screen
        x = (self.winfo_screenwidth()  - 560) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"560x640+{x}+{y}")

    # ── Layout skeleton ──────────────────────
    def _build(self):
        # Progress bar area
        self._prog_frame = tk.Frame(self, bg=BG, padx=36)
        self._prog_frame.pack(fill="x", pady=(16, 8))

        # Step dots
        self._dot_frame = tk.Frame(self._prog_frame, bg=BG)
        self._dot_frame.pack()
        self._dots = []
        for i in range(len(self.STEPS)):
            d = tk.Label(self._dot_frame, text="●", font=("Segoe UI", 9),
                         bg=BG, fg=FG_LIGHT)
            d.pack(side="left", padx=4)
            self._dots.append(d)

        # Bottom bar (packed first at the bottom to remain visible)
        bottom_border = tk.Frame(self, bg=BORDER, height=1)
        bottom_border.pack(side="bottom", fill="x")
        
        nav = tk.Frame(self, bg=BG_CARD, padx=36)
        nav.pack(side="bottom", fill="x", pady=16)

        # Content area (packed next to fill the remaining space in the middle)
        self._content = tk.Frame(self, bg=BG, padx=44)
        self._content.pack(fill="both", expand=True, pady=(12, 16))

        self._back_btn = make_btn_ghost(nav, "← Back", self._prev_step)
        self._back_btn.pack(side="left")

        self._skip_btn = ModernButton(nav, text="Skip", command=self._skip_step,
                                      bg=BG_CARD, fg=FG_DIM, font=FONT_BTN_G,
                                      hover_bg=BG_HOVER, padx=14, pady=8)
        self._skip_btn.pack(side="left", padx=12)

        self._next_btn = make_btn_primary(nav, "Next →", self._next_step)
        self._next_btn.pack(side="right")

    # ── Step rendering ───────────────────────
    def _render_step(self):
        # Update dots
        for i, d in enumerate(self._dots):
            d.config(fg=ACCENT if i == self._step else FG_LIGHT)

        # Clear content
        for w in self._content.winfo_children():
            w.destroy()

        s = self.STEPS[self._step]
        is_last = self._step == len(self.STEPS) - 1

        if s.get("type") == "keys":
            # Icon + title
            tk.Label(self._content, text=s["icon"], font=("Segoe UI", 32), bg=BG).pack(anchor="w")
            tk.Label(self._content, text=s["title"], font=FONT_H1, fg=FG, bg=BG).pack(anchor="w", pady=(4, 0))
            tk.Label(self._content, text=f"Step {self._step + 1} of {len(self.STEPS)}",
                     font=FONT_SMALL, fg=FG_DIM, bg=BG).pack(anchor="w", pady=(2, 10))
            tk.Label(self._content, text=s["desc"], font=FONT_LABEL, fg=FG_MID, bg=BG,
                     justify="left", wraplength=460).pack(anchor="w", pady=(0, 10))

            keys_frame = tk.Frame(self._content, bg=BG)
            keys_frame.pack(fill="x")

            key_fields = [
                ("GEMINI_KEY", "Gemini Key:"),
                ("CLAUDE_KEY", "Claude Key:"),
                ("OPENAI_KEY", "OpenAI Key:"),
                ("DEEPSEEK_KEY", "DeepSeek Key:"),
            ]

            self._key_entries = {}
            for field, label in key_fields:
                row = tk.Frame(keys_frame, bg=BG)
                row.pack(fill="x", pady=6)
                
                lbl = tk.Label(row, text=label, font=FONT_LABEL_B, fg=FG_DIM, bg=BG, width=13, anchor="w")
                lbl.pack(side="left")
                
                var = self._values[field]
                entry = tk.Entry(row, textvariable=var, font=FONT_ENTRY, bg=BG_INPUT, fg=FG,
                                 relief="flat", show="*", insertbackground=FG,
                                 highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
                entry.pack(side="left", fill="x", expand=True, ipady=5)
                self._key_entries[field] = entry

            # Option to toggle show/hide keys
            self._showing_keys = False
            self.toggle_lbl = tk.Label(keys_frame, text="Show keys", font=FONT_SMALL, fg=FG_DIM, bg=BG, cursor="hand2")
            self.toggle_lbl.pack(anchor="w", pady=(8, 0))
            self.toggle_lbl.bind("<Button-1>", self._toggle_all_keys)

            self._next_btn.config(text="Next →")
            self._back_btn.config(state="disabled")
            self._skip_btn.config(state="disabled")

        elif s.get("type") == "provider":
            # Icon + title
            tk.Label(self._content, text=s["icon"], font=("Segoe UI", 32), bg=BG).pack(anchor="w")
            tk.Label(self._content, text=s["title"], font=FONT_H1, fg=FG, bg=BG).pack(anchor="w", pady=(4, 0))
            tk.Label(self._content, text=f"Step {self._step + 1} of {len(self.STEPS)}",
                     font=FONT_SMALL, fg=FG_DIM, bg=BG).pack(anchor="w", pady=(2, 10))
            tk.Label(self._content, text=s["desc"], font=FONT_LABEL, fg=FG_MID, bg=BG,
                     justify="left", wraplength=460).pack(anchor="w", pady=(0, 18))

            prov_frame = tk.Frame(self._content, bg=BG)
            prov_frame.pack(fill="x", pady=10)

            providers = [
                ("gemini", "Google Gemini"),
                ("claude", "Anthropic Claude"),
                ("openai", "OpenAI"),
                ("deepseek", "DeepSeek")
            ]

            for val, name in providers:
                rb = ModernRadiobutton(prov_frame, text=name, variable=self._provider_var, value=val,
                                       bg=BG, fg=FG_MID, font=FONT_LABEL)
                rb.pack(anchor="w", pady=6)

            self._next_btn.config(text="Next →")
            self._back_btn.config(state="normal")
            self._skip_btn.config(state="disabled")

        else:
            # Icon + title
            tk.Label(self._content, text=s["icon"],
                     font=("Segoe UI", 32), bg=BG).pack(anchor="w")
            tk.Label(self._content, text=s["title"],
                     font=FONT_H1, fg=FG, bg=BG).pack(anchor="w", pady=(4, 0))

            # Step counter
            tk.Label(self._content,
                     text=f"Step {self._step + 1} of {len(self.STEPS)}",
                     font=FONT_SMALL, fg=FG_DIM, bg=BG).pack(anchor="w", pady=(2, 10))

            # Description
            tk.Label(self._content, text=s["desc"],
                     font=FONT_LABEL, fg=FG_MID, bg=BG,
                     justify="left", wraplength=460).pack(anchor="w", pady=(0, 18))

            # Input field
            field_row = tk.Frame(self._content, bg=BG)
            field_row.pack(fill="x")

            tk.Label(field_row, text=s["label"],
                     font=FONT_SEC, fg=FG_DIM, bg=BG).pack(anchor="w", pady=(0, 6))

            entry_row = tk.Frame(field_row, bg=BG)
            entry_row.pack(fill="x")

            var = self._values[s["field"]]
            entry = tk.Entry(entry_row, textvariable=var,
                             font=FONT_ENTRY, bg=BG_INPUT, fg=FG,
                             relief="flat", insertbackground=FG,
                             highlightthickness=1,
                             highlightbackground=BORDER,
                             highlightcolor=ACCENT)
            entry.pack(side="left", fill="x", expand=True, ipady=7)
            entry.focus_set()

            if s["browse"]:
                make_btn_ghost(entry_row, "Browse…",
                               lambda f=s["field"]: self._browse(f)
                               ).pack(side="left", padx=(8, 0))

            # Next button label
            self._next_btn.config(text="Finish & Save ✓" if is_last else "Next →")
            self._back_btn.config(state="normal" if self._step > 0 else "disabled")

            # Skip not shown for required steps
            self._skip_btn.config(state="disabled" if s.get("required") else "normal")

    def _toggle_all_keys(self, event):
        self._showing_keys = not self._showing_keys
        show = "" if self._showing_keys else "*"
        for entry in self._key_entries.values():
            entry.config(show=show)
        self.toggle_lbl.config(text="Hide keys" if self._showing_keys else "Show keys")

    def _browse(self, field):
        cur = self._values[field].get()
        path = filedialog.askdirectory(initialdir=cur or os.path.expanduser("~"))
        if path:
            self._values[field].set(path)

    # ── Navigation ───────────────────────────
    def _next_step(self):
        s = self.STEPS[self._step]
        if s.get("type") == "keys":
            # Must have at least one key to continue!
            gem = self._values["GEMINI_KEY"].get().strip()
            cld = self._values["CLAUDE_KEY"].get().strip()
            opn = self._values["OPENAI_KEY"].get().strip()
            dps = self._values["DEEPSEEK_KEY"].get().strip()
            if not (gem or cld or opn or dps):
                messagebox.showwarning("Required",
                    "At least one API Key must be provided to continue.",
                    parent=self)
                return
        elif s.get("required") and not self._values[s["field"]].get().strip():
            messagebox.showwarning("Required",
                f"{s['title']} is required to continue.",
                parent=self)
            return
            
        if self._step < len(self.STEPS) - 1:
            self._step += 1
            self._render_step()
        else:
            self._finish()

    def _skip_step(self):
        if self.STEPS[self._step].get("required"):
            return
        if self._step < len(self.STEPS) - 1:
            self._step += 1
            self._render_step()
        else:
            self._finish()

    def _prev_step(self):
        if self._step > 0:
            self._step -= 1
            self._render_step()

    def _finish(self):
        cfg = {field: self._values[field].get().strip() for field in self._values}
        cfg["API_PROVIDER"] = self._provider_var.get()
        
        # Default model name based on chosen default provider
        default_models = {
            "gemini": "gemini-2.5-flash",
            "claude": "claude-sonnet-4-6",
            "openai": "gpt-4o-mini",
            "deepseek": "deepseek-chat"
        }
        cfg["MODEL_NAME"] = default_models.get(cfg["API_PROVIDER"], "gemini-2.5-flash")
        
        save_config(cfg)
        self._ok = True
        self.grab_release()
        self.destroy()

    def _on_close(self):
        if not self._ok:
            if messagebox.askyesno("Exit Setup",
                "Setup is not complete.\nExit the application?",
                parent=self):
                self.master.destroy()
                sys.exit(0)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Force taskbar icon to display correctly on Windows (overrides default Python shell grouping)
    try:
        import ctypes
        myappid = 'heeyounglee.zoa.1.0.beta'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    root = tk.Tk()
    apply_window_icon(root)


    root.withdraw()          # hide main window during setup

    cfg = load_config()
    if not config_is_complete(cfg):
        wizard = SetupWizard(root)
        root.wait_window(wizard)
        # Reload config after wizard saves .env
        cfg          = load_config()
        GEMINI_KEY   = cfg.get('GEMINI_KEY', '')
        CLAUDE_KEY   = cfg.get('CLAUDE_KEY', '')
        OPENAI_KEY   = cfg.get('OPENAI_KEY', '')
        DEEPSEEK_KEY = cfg.get('DEEPSEEK_KEY', '')
        API_PROVIDER = cfg.get('API_PROVIDER', 'gemini')
        PDF_PATH     = cfg.get('PDF_PATH', '')
        OBS_PATH     = cfg.get('OBS_PATH', '')
        ZOTERO_DB    = cfg.get('ZOTERO_DB', '')
        MODEL_NAME   = cfg.get('MODEL_NAME', 'gemini-2.5-flash')

    root.deiconify()         # show main window
    ZOAApp(root)
    root.mainloop()
