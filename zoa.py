"""
ZOA (Zotero-Obsidian-AI Summary) — v1.0
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
    """Return the folder that contains the exe (or script when developing)."""
    if getattr(sys, 'frozen', False):   # running as PyInstaller bundle
        return Path(sys.executable).parent
    return Path(__file__).parent

def get_resource_path(relative_path: str) -> Path:
    """Return the absolute path to a resource, compatible with PyInstaller's --onefile mode."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

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
        'MODEL_NAME': 'gemini-2.5-flash'
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
    ]
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

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
# Design tokens — clean academic
# ─────────────────────────────────────────────
BG           = "#F4F3F1"       # warm off-white page
BG_CARD      = "#FFFFFF"
BG_INPUT     = "#FAFAF9"
BG_HOVER     = "#F0EFED"
BG_SEL       = "#1C1C1C"       # selected row fill
FG           = "#1C1C1C"
FG_MID       = "#555550"
FG_DIM       = "#888882"
FG_LIGHT     = "#BABAB4"
BORDER       = "#E2E1DE"
BORDER_MID   = "#C8C7C3"
ACCENT       = "#1C1C1C"
ACCENT_H     = "#383838"
LOG_BG       = "#F8F8F7"
LOG_FG       = "#555550"
LOG_OK       = "#1C1C1C"
LOG_SKIP     = "#BABAB4"
LOG_WARN     = "#888882"
TAG_BG       = "#EFEFED"
TAG_FG       = "#444440"

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

def make_btn_primary(parent, text, command):
    btn = tk.Button(parent, text=text, command=command,
                    bg=ACCENT, fg=BG_CARD, relief="flat",
                    font=FONT_BTN_P, padx=18, pady=8,
                    cursor="hand2", bd=0,
                    activebackground=ACCENT_H, activeforeground=BG_CARD)
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_H))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))
    return btn

def make_btn_ghost(parent, text, command):
    btn = tk.Button(parent, text=text, command=command,
                    bg=BG_CARD, fg=FG_MID, relief="flat",
                    font=FONT_BTN_G, padx=14, pady=8,
                    cursor="hand2", bd=1,
                    activebackground=BG_HOVER, activeforeground=FG,
                    highlightthickness=0)
    btn.bind("<Enter>", lambda e: btn.config(bg=BG_HOVER, fg=FG))
    btn.bind("<Leave>", lambda e: btn.config(bg=BG_CARD, fg=FG_MID))
    return btn

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

def thin_divider(parent, pady=(12, 12)):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=pady)

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

        self._vsb = tk.Scrollbar(list_outer, orient="vertical",
                                 bg=BG, troughcolor=BG,
                                 width=8, bd=0, relief="flat")
        self._vsb.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self._canvas = tk.Canvas(list_outer, bg=BG_CARD,
                                 highlightthickness=0,
                                 yscrollcommand=self._vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._vsb.config(command=self._canvas.yview)

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

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

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
        tk.Label(left, text="Heeyoung Lee",
                 font=FONT_SUBNAME, fg=FG_DIM, bg=BG_CARD).pack(anchor="w", pady=(2, 0))

        tk.Label(inner_h, text="v1.0",
                 font=FONT_VER, fg=FG_LIGHT, bg=BG_CARD).pack(side="right", anchor="se")

        # ── Scroll canvas
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        self._main_vsb = tk.Scrollbar(outer, orient="vertical",
                                      bg=BG, troughcolor=BG,
                                      width=8, bd=0, relief="flat")
        self._main_vsb.pack(side="right", fill="y")

        self._canvas = tk.Canvas(outer, bg=BG, highlightthickness=0,
                                 yscrollcommand=self._main_vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._main_vsb.config(command=self._canvas.yview)

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
        tk.Checkbutton(top, text="Entire Library",
                       variable=self.all_var, command=self._toggle_all,
                       bg=BG_CARD, fg=FG_MID, selectcolor=BG_CARD,
                       activebackground=BG_CARD, font=FONT_LABEL,
                       relief="flat", bd=0).pack(side="right")

        self._picker = CollectionPicker(c1, height=210)
        self._picker.pack(fill="x")

        # ─── 02  Paths ────────────────────────
        make_section_label(M, "02  File Paths")
        c2 = card(M); c2.pack(fill="x")

        field_label(c2, "PDF Folder")
        self.pdf_path_var = tk.StringVar(value=PDF_PATH)
        self._path_row(c2, self.pdf_path_var)
        thin_divider(c2, (12, 12))
        field_label(c2, "Obsidian Vault")
        self.obs_path_var = tk.StringVar(value=OBS_PATH)
        self._path_row(c2, self.obs_path_var)

        # ─── 03  Options ──────────────────────
        make_section_label(M, "03  Options")
        c3 = card(M); c3.pack(fill="x")

        # Toggle row
        tog_row = tk.Frame(c3, bg=BG_CARD); tog_row.pack(fill="x", pady=(0, 12))
        self.full_pdf_var = tk.BooleanVar(value=False)
        self._toggle_chk(tog_row, "Read full PDF", self.full_pdf_var)
        self.wikilink_var = tk.BooleanVar(value=False)
        self._toggle_chk(tog_row, "Auto Wikilinks", self.wikilink_var, pad_left=28)

        thin_divider(c3, (0, 12))

        # Recent filter row
        rec_row = tk.Frame(c3, bg=BG_CARD); rec_row.pack(fill="x", pady=(0, 12))
        self.recent_var = tk.BooleanVar(value=False)
        self._toggle_chk(rec_row, "Recent papers only", self.recent_var,
                         command=self._toggle_recent)
        tk.Label(rec_row, text="Days:", font=FONT_LABEL,
                 fg=FG_DIM, bg=BG_CARD).pack(side="left", padx=(20, 6))
        self.recent_days_var = tk.StringVar(value="7")
        self.recent_spin = tk.Spinbox(rec_row, from_=1, to=365,
                                      textvariable=self.recent_days_var,
                                      width=4, font=FONT_ENTRY,
                                      bg=BG_INPUT, fg=FG_DIM, relief="flat",
                                      highlightthickness=1,
                                      highlightbackground=BORDER, bd=0,
                                      buttonbackground=BG,
                                      state="disabled")
        self.recent_spin.pack(side="left")

        thin_divider(c3, (0, 12))

        # Duplicate + limit row
        dup_row = tk.Frame(c3, bg=BG_CARD); dup_row.pack(fill="x", pady=(0, 10))
        tk.Label(dup_row, text="Duplicate:", font=FONT_LABEL,
                 fg=FG_DIM, bg=BG_CARD).pack(side="left", padx=(0, 10))
        self.dup_var = tk.StringVar(value="skip")
        for lbl, val in [("Skip", "skip"), ("Overwrite", "overwrite"), ("Update if newer", "update")]:
            tk.Radiobutton(dup_row, text=lbl, variable=self.dup_var, value=val,
                           bg=BG_CARD, fg=FG_MID, selectcolor=BG_CARD,
                           activebackground=BG_CARD, font=FONT_LABEL,
                           relief="flat", bd=0).pack(side="left", padx=(0, 10))

        lim_row = tk.Frame(c3, bg=BG_CARD); lim_row.pack(fill="x")
        tk.Label(lim_row, text="Max papers:", font=FONT_LABEL,
                 fg=FG_DIM, bg=BG_CARD).pack(side="left")
        self.limit_var = tk.StringVar(value="500")
        tk.Spinbox(lim_row, from_=1, to=2000, textvariable=self.limit_var,
                   width=5, font=FONT_ENTRY, bg=BG_INPUT, fg=FG,
                   relief="flat", highlightthickness=1,
                   highlightbackground=BORDER, bd=0,
                   buttonbackground=BG).pack(side="left", padx=(6, 20))

        # Multi-provider API Comboboxes
        tk.Label(lim_row, text="Provider:", font=FONT_LABEL,
                 fg=FG_DIM, bg=BG_CARD).pack(side="left")
        
        self.provider_map = {
            "Google Gemini": "gemini",
            "Anthropic Claude": "claude",
            "OpenAI": "openai",
            "DeepSeek": "deepseek"
        }
        self.provider_rev_map = {v: k for k, v in self.provider_map.items()}

        default_provider_name = self.provider_rev_map.get(API_PROVIDER, "Google Gemini")
        self.provider_var = tk.StringVar(value=default_provider_name)
        
        self._apply_combo_style()
        self.provider_cb = ttk.Combobox(lim_row, textvariable=self.provider_var,
                                        values=list(PROVIDER_MODELS.keys()), state="readonly",
                                        font=FONT_ENTRY, width=15)
        self.provider_cb.pack(side="left", padx=(6, 20))
        self.provider_cb.bind("<<ComboboxSelected>>", self._on_provider_changed)

        tk.Label(lim_row, text="Model:", font=FONT_LABEL,
                 fg=FG_DIM, bg=BG_CARD).pack(side="left")
        self.model_var = tk.StringVar(value=MODEL_NAME)
        self.model_cb = ttk.Combobox(lim_row, textvariable=self.model_var,
                                     values=PROVIDER_MODELS[default_provider_name], state="readonly",
                                     font=FONT_ENTRY, width=22)
        self.model_cb.pack(side="left", padx=(6, 0))
        self.model_cb.bind("<<ComboboxSelected>>", self._on_model_changed)

        # ─── 04  Progress ─────────────────────
        make_section_label(M, "04  Progress")
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
        self.run_btn = make_btn_primary(btn_row, "▶  Run", self._start_run)
        self.run_btn.pack(side="left", padx=(0, 10))
        self.stop_btn = make_btn_ghost(btn_row, "◼  Stop", self._stop_run)
        self.stop_btn.config(state="disabled", fg=FG_LIGHT)
        self.stop_btn.pack(side="left", padx=(0, 20))
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(btn_row, textvariable=self.status_var,
                 font=FONT_STATUS, fg=FG_DIM, bg=BG).pack(side="left")

        # ─── 05  Log ──────────────────────────
        make_section_label(M, "05  Execution Log")
        log_wrap = tk.Frame(M, bg=LOG_BG,
                            bd=1, relief="solid",
                            highlightthickness=0)
        log_wrap.pack(fill="both", expand=True, pady=(0, 28))

        vsb_log = tk.Scrollbar(log_wrap, bg=LOG_BG,
                               troughcolor=LOG_BG, bd=0, width=7)
        vsb_log.pack(side="right", fill="y")

        self.log_box = tk.Text(log_wrap, height=14, font=FONT_LOG,
                               bg=LOG_BG, fg=LOG_FG,
                               insertbackground=LOG_FG,
                               wrap="word", relief="flat",
                               padx=18, pady=14,
                               yscrollcommand=vsb_log.set,
                               state="disabled")
        self.log_box.pack(side="left", fill="both", expand=True)
        vsb_log.config(command=self.log_box.yview)

        self.log_box.tag_config("ok",   foreground=LOG_OK)
        self.log_box.tag_config("info", foreground=LOG_FG)
        self.log_box.tag_config("warn", foreground=LOG_WARN)
        self.log_box.tag_config("err",  foreground="#B85450")
        self.log_box.tag_config("done", foreground=LOG_OK,
                                font=("Consolas", 11, "bold"))
        self.log_box.tag_config("skip", foreground=LOG_SKIP)

        self._log("ZOA initialized.", "ok")
        self._log("Load Zotero collections and configure paths to begin.", "info")

    # ── Helpers ──────────────────────────────
    def _on_root_scroll(self, event):
        w = event.widget
        try:
            cur = w
            while cur:
                if cur is self._picker._canvas or cur is self._picker._inner:
                    return
                cur = cur.master
        except: pass
        self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _toggle_chk(self, parent, text, var, command=None, pad_left=0):
        kw = {"command": command} if command else {}
        tk.Checkbutton(parent, text=text, variable=var,
                       bg=BG_CARD, fg=FG_MID, selectcolor=BG_CARD,
                       activebackground=BG_CARD, font=FONT_LABEL,
                       relief="flat", bd=0, **kw).pack(side="left", padx=(pad_left, 0))

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

    def _toggle_recent(self):
        if self.recent_var.get():
            self.recent_spin.config(state="normal", fg=FG)
        else:
            self.recent_spin.config(state="disabled", fg=FG_DIM)

    def _on_provider_changed(self, event=None):
        prov_name = self.provider_var.get()
        models = PROVIDER_MODELS[prov_name]
        self.model_cb.config(values=models)
        if models:
            self.model_cb.set(models[0])
            self.model_var.set(models[0])
        # Auto-save immediately
        _cfg = load_config()
        _cfg['API_PROVIDER'] = self.provider_map[prov_name]
        _cfg['MODEL_NAME'] = self.model_var.get()
        save_config(_cfg)

    def _on_model_changed(self, event=None):
        _cfg = load_config()
        _cfg['MODEL_NAME'] = self.model_var.get()
        save_config(_cfg)

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
        prov_name   = self.provider_var.get()
        prov_val    = self.provider_map[prov_name]
        model_name  = self.model_var.get()
        
        # Auto-save paths and selections to .env
        _cfg = load_config()
        _cfg['PDF_PATH'] = pdf_path
        _cfg['OBS_PATH'] = obs_path
        _cfg['API_PROVIDER'] = prov_val
        _cfg['MODEL_NAME'] = model_name
        save_config(_cfg)
        
        read_full   = self.full_pdf_var.get()
        limit       = int(self.limit_var.get())
        dup_mode    = self.dup_var.get()
        use_wiki    = self.wikilink_var.get()
        use_recent  = self.recent_var.get()
        recent_days = int(self.recent_days_var.get()) if use_recent else None
        if not obs_path:
            self._log("Set Obsidian output folder first.", "err"); return
        if read_full and not pdf_path:
            self._log("Set PDF folder or disable full PDF mode.", "err"); return

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

        threading.Thread(
            target=self._run_pipeline,
            args=(col_names, pdf_path, obs_path, read_full,
                  limit, prov_name, model_name, dup_mode, use_wiki,
                  use_recent, recent_days),
            daemon=True).start()

    def _stop_run(self):
        self.running = False
        self._set_status("Stopping…")
        self._log("Stop requested.", "warn")

    def _run_pipeline(self, col_names, pdf_path, obs_path, read_full,
                      limit, prov_name, active_model, dup_mode, use_wiki, use_recent, recent_days):
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
                abstract    = fields.get('abstractNote', '')
                date        = fields.get('date', 'No Date')
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
                pub_ac = ("".join(w[0] for w in publication.split()).upper()
                          if publication and publication != 'No Journal' else "NoJournal")
                filename    = clean_filename(f"{author_for_file}_{year}_{pub_ac}.md")
                full_path   = os.path.join(obs_path, filename)
                zotero_link = f"zotero://select/items/0_{item_key}"
                pg          = f"[{idx:>3}/{total}]"

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

                has_pdf = False; content_source = "Abstract Only"; final_text = abstract
                if read_full and pdf_index:
                    matched = find_best_pdf_match(fields, creators_raw, pdf_index)
                    if matched:
                        try:
                            from pypdf import PdfReader
                            reader = PdfReader(matched)
                            extracted = "".join(p.extract_text() or "" for p in reader.pages[:30])
                            if len(extracted) > 500:
                                final_text = extracted; content_source = "Full PDF Content"; has_pdf = True
                                self._log(f"       ✓  {os.path.basename(matched)}", "ok")
                            else:
                                self._log("       —  PDF insufficient; using abstract.", "warn")
                        except Exception as e:
                            self._log(f"       ✗  PDF error: {e}", "warn")
                    else:
                        self._log("       —  No PDF match.", "skip")

                if not final_text:
                    self._log("       ✗  No content. Skipping.", "warn")
                    self.root.after(0, lambda i=idx: self._set_progress(i, total))
                    continue

                prompt = f"""You are a professional researcher.
I will provide text from a research paper titled: "{title}".
Task: Summarize the provided text ({content_source}) in English.
Constraint: Focus ONLY on the content related to the paper "{title}".

[Text Input]:
{final_text[:50000]}

[Output Format - Markdown]:
1. **Research Objective**: 
2. **Methodology**: (data sources, statistical models)
3. **Key Results**: 
4. **Keywords**: Provide 5 keywords with # prefix.
   - Must include methodology keywords (e.g., #DiD, #OLS, #Panel-Data).
   - Use umbrella terms (e.g., #Substance-Use).
   - Capitalize first letters.
"""
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
        self.geometry("560x580")
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
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"560x580+{x}+{y}")

    # ── Layout skeleton ──────────────────────
    def _build(self):
        # Progress bar area
        self._prog_frame = tk.Frame(self, bg=BG, padx=36, pady=18)
        self._prog_frame.pack(fill="x")

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
        
        nav = tk.Frame(self, bg=BG_CARD, padx=36, pady=16)
        nav.pack(side="bottom", fill="x")

        # Content area (packed next to fill the remaining space in the middle)
        self._content = tk.Frame(self, bg=BG, padx=44, pady=24)
        self._content.pack(fill="both", expand=True)

        self._back_btn = make_btn_ghost(nav, "← Back", self._prev_step)
        self._back_btn.pack(side="left")

        self._skip_btn = tk.Button(nav, text="Skip", font=FONT_BTN_G,
                                   bg=BG_CARD, fg=FG_DIM, relief="flat",
                                   bd=0, cursor="hand2",
                                   activebackground=BG_CARD,
                                   command=self._skip_step)
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
                rb = tk.Radiobutton(prov_frame, text=name, variable=self._provider_var, value=val,
                                    bg=BG, fg=FG_MID, selectcolor=BG, activebackground=BG,
                                    font=FONT_LABEL, relief="flat", bd=0)
                rb.pack(anchor="w", pady=5)

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
        myappid = 'heeyounglee.zoa.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    root = tk.Tk()
    
    # Set default window and taskbar icon bitmap
    try:
        icon_path = get_resource_path("app_icon.ico")
        if icon_path.exists():
            # Use PIL to load high-resolution image to prevent pixelation/blurriness in the taskbar
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                root.iconphoto(True, photo)
                # Keep a reference to prevent garbage collection
                root._icon_image = photo
            except Exception:
                # Fallback to standard iconbitmap if PIL loading fails
                root.iconbitmap(default=str(icon_path))
    except:
        pass

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
