import base64
import io
import json
import os
import shutil
import subprocess
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageTk

try:  # crisp text on high-DPI Windows displays
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

APP_NAME = "Golf Sim Launcher"
CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "GolfSimLauncher"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOGO_STORE = CONFIG_DIR / "logos"  # copies of logos you add to custom tiles
BG_STORE = CONFIG_DIR / "backgrounds"  # copy of the background image you choose

DEFAULT_GAME_NAMES = ["GSPro", "Awesome Golf", "Square Golf", "PurePlay"]
DEFAULT_CONFIG = {
    "games": [{"name": n, "path": ""} for n in DEFAULT_GAME_NAMES],
    "fullscreen": True,
    "minimize_on_launch": False,
    "background": "",      # path to a custom background image ("" = default)
    "bg_dim": 0.68,        # how much the background is darkened, 0.0 - 0.9
}

# Accent color per known game; any other game cycles through ACCENT_CYCLE
ACCENTS = {"gspro": "#2ecc71", "awesome golf": "#f5a623", "square golf": "#4aa3ff", "pureplay": "#c76bff"}
ACCENT_CYCLE = ["#2ecc71", "#f5a623", "#4aa3ff", "#c76bff", "#ff6b81", "#2dd4bf", "#facc15"]


def accent_for(name, idx):
    return ACCENTS.get(name.lower()) or ACCENT_CYCLE[idx % len(ACCENT_CYCLE)]


# Palette
BG = "#0d141b"
CARD = "#17222d"
CARD_HOVER = "#1f2f3e"
CARD_BORDER = "#25384a"
TEXT = "#f2f6fa"
MUTED = "#8ea2b4"
TILE = "#123222"          # deep fairway green
TILE_HOVER = "#1b4a32"
TILE_BORDER = "#2c6a45"
PUTT_GREEN = "#38a15d"    # putting-green surface
PUTT_RIM = "#226b3d"
GREEN = "#3ddc84"
AMBER = "#f5a623"
GREY = "#5f7183"
FONT = "Segoe UI"


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    try:
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            cfg.update({k: v for k, v in data.items() if k != "games"})
            if isinstance(data.get("games"), list):
                cfg["games"] = [
                    {"name": str(g.get("name", "")).strip(), "path": str(g.get("path", "")).strip(),
                     "logo": str(g.get("logo", "")).strip()}
                    for g in data["games"] if isinstance(g, dict) and str(g.get("name", "")).strip()
                ]
            else:  # older config: one key per game name
                cfg["games"] = [{"name": n, "path": str(data.get(n, "")).strip()} for n in DEFAULT_GAME_NAMES]
    except Exception:
        pass
    return cfg


def save_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def store_file(src, folder):
    """Copy a chosen image into the launcher's own folder so it survives the original moving."""
    if not src:
        return ""
    p = Path(src)
    try:
        if p.resolve().parent == folder.resolve():
            return str(p)
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"{uuid.uuid4().hex[:10]}{p.suffix.lower()}"
        shutil.copy2(p, dest)
        return str(dest)
    except Exception:
        return src


def prune_store(folder, keep_paths):
    """Delete stored copies in `folder` that aren't in use anymore."""
    try:
        keep = {Path(k).resolve() for k in keep_paths if k}
        for f in folder.glob("*"):
            if f.resolve() not in keep:
                f.unlink()
    except Exception:
        pass


def store_logo(src):
    return store_file(src, LOGO_STORE)


def prune_logo_store(games):
    prune_store(LOGO_STORE, [g.get("logo") for g in games])


config = load_config()

root = tk.Tk()
root.title(APP_NAME)
root.configure(bg=BG)
root.minsize(900, 650)

canvas = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

# --------------------------------------------------------------------- logos
# Logos are embedded below as base64 PNGs, so no external files are needed.
LOGO_DATA = {
    "GSPro": (
        "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"
        "n/PHiR/YqZFJrrxFc7hfB/h9BK//2Q2t5sXS5+z8lIsbp/xrDJZJNZI+o24clYhq9dLb23urG14yE05pbNmypVSv1+2wkyuVUgPV"
        "ajX37NmzwpYtWz6lYPBnbqAJglmV9/fBtxXfrj4zVnq+OrwqcPRaHf/79hbf6hr0pRTsmqxgv+C+x9Frddx7GI0NZ8qN6//1F/7Z"
        "cN9zjc/djEKhRKfiq8O2HccpIpp6GFnXdcdd14XjOJPNehh2XOwmIjbQ2L4RkZJSyt62bVsxwlcyy6qMwXB+yvVNKGRS3Wkjuwr8"
        "7o7nW/Slv29lJ9cf0BHT96bcyETCUrFw9ss6/nAs0TXPWlRN5kuctnx3ehMiko/4NvJKxSfJa2luztIcD8dxgGbvCtd1b23dunWC"
        "T1j8mSk39qr9CgubEBIOgtuzHt6BP0KhL7my4wuqEuPV+2YUw7p6X/DBK/58z8bzGu1zpqOIKCiliiC+kkwmr9AK/ooeERnWWl+v"
        "VCqPHce5PDc3F4IQ44mHoMUCCc9GK62G+5LBLCZuz3pGje9n3/ojWkwo8NXVEQXHcb7r1pfZdd1Xl4bIm9sP44iuEVLX0sz9GEwk"
        "EoOO45Qsyyr09PQEJcwoFGJCudqdW0R+hrpXctxB5SdEveXwvft55M/z0WdAH4xEs8FQ2E6uFNKlst06SVmWtdLrNkqhEPwz5bru"
        "eKVSGTCkayZpY2V22Mdjed1acMmvUw9hY9o2kF/3Y0KOgo6iDLHW2ua05T/pdLoUlx4MXRBlGBCRu5VKZZjWiAd+nnGffti9jaH8"
        "rJh4/+H3nWV/QBGF6UdmCYVZn7ZBTNh6YEeOLiOZTI6CyaJhiYWMUurC06dPCz5+6C5aNoBV8k7lax2Fbs118LObo13Fpi5zbVe7"
        "57tQKHSf87Jd13118dgfCeEl0nrEV7FAfCOTbFQcvHHK33SssIr5hGmnD16xfBVT9x6FG3WZZaJqYCRogu6j2bTqVQA3aY3wxEKl"
        "UrF7e3vHaI3WvP+yRjmEleaB5xT6MyqQo3ifPQjPCZ7YE2xr66Ds9Mf7Hh92CgViMul0etJxnCMicj2qdtibDaXUhbm5ueL27dsn"
        "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"
        "QmCC"
    ),
    "Awesome Golf": (
        "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"
    ),
    "Square Golf": (
        "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"
        "TkSuQmCC"
    ),
    "PurePlay": (
        "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"
        "PCB5hCxvMHUA+xUkgohkEARcqawqIuzKZrMfajRWvnDbbbftJCK1RQT8pkCsQeulpaVCrbZ8eaFQfHOr5SrXbeuYEImNfJZBWP1i"
        "N4paXV19QrNZ+6RlWV9NpdIvIiKq1Wqq0+noZB1G+i3Eeh/Ia9c+EQnXdXWtVlNCyHK5XH4js7y+Xl/94x//+MfOFiI5fY2TUoqr"
        "1WrIrIuFQmn2zDMfubC8vHxmLCMss3uHNUcgIpLMjGq1EhYKpecD6oparbbtaCTw8Of0Z9rtdtiHVkIAVDaby0gpzh+lMREi3JPN"
        "ZtOxZ456lF1s27as1+t1Zvo8AAg9QoWg13lR6biNnJwm+GcT/iYAntICPiwBZGIX0bCTMNgQwIEJeiGEbLc7XK3WVC5XeMHERHlx"
        "efmepxgBv7GEa//+/WnLwqWl0rbfqFYrITOkEBvvlurXlbOwsGARkd6/f3+6Vlt5t+PIb2Yy6ZeFYYjI6hy5rkfB5ZaQnDAMuVqt"
        "hkJQIZ/Pv+fUU0+5+uDBX55ORGphYcE63mUEEVkJEXSc1FNSKesby8sHLiai0CiKozE/1Wo1LJWKT1Oqs/eOO+7IHEWZ08xMpdLE"
        "j9rtzo3ZbLafcA8KggDM9GIAmJ2d5SGPgWLmtFI83W63+7Xe62w2C63DhbiigxSjYALcyOhhit3CCwzrfMLt5xF+SwEX+MC3soC0"
        "I7fw0HoL09ZoZzdCmpMgIYSs1Wqh4zinO076a6urdz3LCPiNGX4i4lIp+0/l8vjzq9WVILL6DZeQ9vhZOTU1FR44cOcTJiZKVxWL"
        "hXdorXK12mHiN8qHaBiGXKvVwlQq9axUKvvNAwfuunBqasrsgTVj1Gg0lBA0ls1mLltdvfdVxlswMvNj1Wq1YGxs21Q+n/7bOA5Q"
        "rFXsFhcXJRF1pBRfllKi19wxZhadTgdE4om12sFHxmFDQ6FJCwsLFjNTvV65MJvNnNZut3U/yiURoJSClPThQwJ6FCbY32CrFxF4"
        "ihDOMEQcH3gNA+c2gT9QwD2Fw3UYNrwYpTYWwHUTIq1WS9m2VXKc3KfjgH01rM291ZGUCqnVVl9TLJZ+q1arhHHw8mZ8F4uI1MGD"
        "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"
    ),
}

_logo_src = {}
for _name, _b64 in LOGO_DATA.items():
    try:
        _logo_src[_name.lower()] = Image.open(io.BytesIO(base64.b64decode(_b64))).convert("RGBA")
    except Exception:
        pass  # falls back to plain text if a logo fails to decode
_logo_photos = []  # keep references so Tk doesn't garbage-collect them


_custom_cache = {}


def load_custom_logo(path):
    if path not in _custom_cache:
        try:
            im = Image.open(path).convert("RGBA")
            box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
            _custom_cache[path] = im.crop(box) if box else im  # trim empty margins
        except Exception:
            _custom_cache[path] = None
    return _custom_cache[path]


def logo_image(name, max_w, max_h, custom=""):
    """A logo you added takes priority; otherwise the built-in one; otherwise None (text is shown)."""
    src = load_custom_logo(custom) if custom else None
    if src is None:
        src = _logo_src.get(name.lower())
    if src is None:
        return None
    scale = min(max_w / src.width, max_h / src.height)
    size = (max(1, int(src.width * scale)), max(1, int(src.height * scale)))
    photo = ImageTk.PhotoImage(src.resize(size, Image.LANCZOS))
    _logo_photos.append(photo)
    return photo


# ---------------------------------------------------------------- background
_bg_photo = None
_bg_cache = {}


def get_bg_source():
    """Your chosen background, else background.png next to the script, else None (gradient)."""
    custom = config.get("background", "")
    for path in ([Path(custom)] if custom else []) + [Path(__file__).resolve().parent / "background.png"]:
        key = str(path)
        if key not in _bg_cache:
            try:
                im = Image.open(path).convert("RGB")
                im.thumbnail((2560, 1440), Image.LANCZOS)  # keeps resizing fast on huge photos
                _bg_cache[key] = im
            except Exception:
                _bg_cache[key] = None
        if _bg_cache[key] is not None:
            return _bg_cache[key]
    return None


def make_background(w, h):
    """Image scaled to cover the window and darkened by the chosen amount, else a gradient."""
    source = get_bg_source()
    if source is not None:
        try:
            dim = min(0.9, max(0.0, float(config.get("bg_dim", 0.68))))
        except (TypeError, ValueError):
            dim = 0.68
        img = ImageOps.fit(source, (w, h), Image.LANCZOS)
        img = Image.blend(img, Image.new("RGB", (w, h), (8, 12, 18)), dim)
    else:
        img = Image.new("RGB", (w, h))
        d = ImageDraw.Draw(img)
        top, bot = (22, 36, 50), (9, 13, 19)
        for y in range(h):
            t = y / max(h - 1, 1)
            d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return ImageTk.PhotoImage(img)


# ------------------------------------------------------------------- helpers
def set_fullscreen(value):
    root.attributes("-fullscreen", bool(value))


def rrect(x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def status_of(game):
    exe = game.get("path", "").strip()
    if not exe:
        return "Not set up", GREY
    if not Path(exe).is_file():
        return "File not found", AMBER
    return "Ready to launch", GREEN


def launch(game):
    name, exe = game["name"], game.get("path", "").strip()
    if not exe:
        messagebox.showwarning("Program not configured",
                               f"Select the {name} .exe file in Settings first.")
        open_settings()
        return
    if not Path(exe).is_file():
        messagebox.showerror("Program not found",
                             f"The saved file for {name} could not be found:\n\n{exe}")
        open_settings()
        return
    try:
        subprocess.Popen([exe], cwd=str(Path(exe).parent))
        if config.get("minimize_on_launch", False):
            root.iconify()
    except Exception as e:
        messagebox.showerror("Launch error", f"Could not start {name}:\n\n{e}")


def close_launcher():
    root.destroy()


def remove_game(idx):
    game = config["games"][idx]
    if messagebox.askyesno("Remove tile", f"Remove the {game['name']} tile?\n\n"
                           "(This only removes the shortcut, not the program.)"):
        del config["games"][idx]
        save_config()
        draw()


def move_game(idx, new_idx):
    games = config["games"]
    if 0 <= new_idx < len(games) and new_idx != idx:
        games.insert(new_idx, games.pop(idx))
        save_config()
    draw()


# drag-to-reorder state (filled in by draw / the handlers below)
_slots = []   # (x1, y1, x2, y2) of each tile position, in order
_drag = {}


def nearest_slot(x, y):
    if not _slots:
        return 0
    return min(range(len(_slots)),
               key=lambda i: ((_slots[i][0] + _slots[i][2]) / 2 - x) ** 2 + ((_slots[i][1] + _slots[i][3]) / 2 - y) ** 2)


def drag_start(e, idx):
    _drag.clear()
    _drag.update(idx=idx, x0=e.x, y0=e.y, lx=e.x, ly=e.y, active=False)


def drag_move(e):
    if not _drag:
        return
    tag = f"card{_drag['idx']}"
    if not _drag["active"]:
        if max(abs(e.x - _drag["x0"]), abs(e.y - _drag["y0"])) < 8:
            return
        _drag["active"] = True
        canvas.tag_raise(tag + "_shadow")
        canvas.tag_raise(tag)
    canvas.move(tag, e.x - _drag["lx"], e.y - _drag["ly"])
    canvas.move(tag + "_shadow", e.x - _drag["lx"], e.y - _drag["ly"])
    _drag["lx"], _drag["ly"] = e.x, e.y
    canvas.config(cursor="fleur")
    # dashed outline shows where the tile will land
    canvas.delete("dropzone")
    target = nearest_slot(e.x, e.y)
    if target != _drag["idx"]:
        x1, y1, x2, y2 = _slots[target]
        rrect(x1, y1, x2, y2, 20, fill="", outline="#77b5fe", width=2, dash=(6, 4), tags="dropzone")
        canvas.tag_raise(tag + "_shadow")
        canvas.tag_raise(tag)


def drag_end(e, game):
    st = dict(_drag)
    _drag.clear()
    if not st:
        return
    if not st["active"]:          # a plain click launches the game
        launch(game)
        return
    canvas.config(cursor="")
    move_game(st["idx"], nearest_slot(e.x, e.y))   # redraws, snapping back if unchanged


def show_tile_menu(event, idx):
    menu = tk.Menu(root, tearoff=0, bg=CARD, fg=TEXT, activebackground="#2d7dd2",
                   activeforeground="white", relief="flat", font=(FONT, 10))
    menu.add_command(label="Edit in Settings…", command=open_settings)
    last = len(config["games"]) - 1
    menu.add_command(label="◀  Move left", command=lambda: move_game(idx, idx - 1),
                     state="normal" if idx > 0 else "disabled")
    menu.add_command(label="Move right  ▶", command=lambda: move_game(idx, idx + 1),
                     state="normal" if idx < last else "disabled")
    menu.add_separator()
    menu.add_command(label="Remove tile", command=lambda: remove_game(idx))
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


# ------------------------------------------------------------------ settings
def open_settings(add_new=False):
    win = tk.Toplevel(root)
    win.title("Golf Sim Launcher - Settings")
    win.configure(bg=BG)
    win.transient(root)
    win.grab_set()

    tk.Label(win, text="SETTINGS", font=(FONT, 20, "bold"), fg=TEXT, bg=BG).pack(pady=(24, 0))
    tk.Label(win, text="Name each tile, point it at its .exe, add new games, or remove ones you don't need",
             font=(FONT, 11), fg=MUTED, bg=BG).pack(pady=(2, 16))

    panel = tk.Frame(win, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
    panel.pack(fill="both", expand=True, padx=30)
    inner = tk.Frame(panel, bg=CARD)
    inner.pack(fill="both", expand=True, padx=22, pady=16)
    inner.columnconfigure(2, weight=1)

    tk.Label(inner, text="NAME", font=(FONT, 9, "bold"), fg=MUTED, bg=CARD,
             anchor="w").grid(row=0, column=1, sticky="w")
    tk.Label(inner, text="PROGRAM (.EXE)", font=(FONT, 9, "bold"), fg=MUTED, bg=CARD,
             anchor="w").grid(row=0, column=2, sticky="w", padx=8)

    rows = []

    def regrid():
        """Re-place every row in its current order (after a move or a removal)."""
        for i, rw in enumerate(rows, start=1):
            for wdg in rw["widgets"]:
                wdg.grid_configure(row=i)

    def add_row(name="", path="", logo=""):
        r = len(rows) + 1
        accent = accent_for(name or "?", len(rows))
        strip = tk.Frame(inner, bg=accent, width=4, height=26)
        strip.grid(row=r, column=0, padx=(0, 12), pady=7)
        name_e = tk.Entry(inner, font=(FONT, 11, "bold"), width=16, bg="#0f1922", fg=TEXT,
                          insertbackground=TEXT, relief="flat", highlightthickness=1,
                          highlightbackground=CARD_BORDER, highlightcolor=accent)
        name_e.insert(0, name)
        name_e.grid(row=r, column=1, pady=7, ipady=6, sticky="w")
        path_e = tk.Entry(inner, font=(FONT, 10), width=34, bg="#0f1922", fg=TEXT,
                          insertbackground=TEXT, relief="flat", highlightthickness=1,
                          highlightbackground=CARD_BORDER, highlightcolor=accent)
        path_e.insert(0, path)
        path_e.grid(row=r, column=2, padx=8, pady=7, ipady=6, sticky="ew")

        def browse():
            chosen = filedialog.askopenfilename(
                parent=win, title="Select program",
                filetypes=[("Windows programs", "*.exe"), ("All files", "*.*")])
            if chosen:
                path_e.delete(0, tk.END)
                path_e.insert(0, chosen)
                if not name_e.get().strip():
                    name_e.insert(0, Path(chosen).stem)

        b = tk.Button(inner, text="Browse", command=browse, width=9, font=(FONT, 10, "bold"),
                      bg="#2d7dd2", fg="white", activebackground="#3c8de0",
                      activeforeground="white", relief="flat", cursor="hand2")
        b.grid(row=r, column=3, pady=7)
        b.bind("<Enter>", lambda e, b=b: b.config(bg="#3c8de0"))
        b.bind("<Leave>", lambda e, b=b: b.config(bg="#2d7dd2"))

        row = {"logo": logo}

        def refresh_logo_btn():
            has = bool(row["logo"])
            logo_b.config(text="Logo ✓" if has else "Logo…", bg="#1f6f4a" if has else "#3a4b5a",
                          activebackground="#278a5d" if has else "#4a5d6f")

        def choose_logo():
            chosen = filedialog.askopenfilename(
                parent=win, title="Select a logo image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")])
            if not chosen:
                return
            try:
                with Image.open(chosen) as im:
                    im.verify()
            except Exception:
                messagebox.showerror("Not an image", "That file couldn't be opened as an image.\n\n"
                                     "Use a PNG, JPG, GIF, BMP or WebP file.", parent=win)
                return
            row["logo"] = chosen
            refresh_logo_btn()

        def clear_logo():
            row["logo"] = ""
            refresh_logo_btn()

        def logo_click():
            if not row["logo"]:
                choose_logo()
                return
            m = tk.Menu(win, tearoff=0, bg=CARD, fg=TEXT, activebackground="#2d7dd2",
                        activeforeground="white", relief="flat", font=(FONT, 10))
            m.add_command(label="Choose a different image…", command=choose_logo)
            m.add_command(label="Remove logo", command=clear_logo)
            try:
                m.tk_popup(logo_b.winfo_rootx(), logo_b.winfo_rooty() + logo_b.winfo_height())
            finally:
                m.grab_release()

        logo_b = tk.Button(inner, text="Logo…", command=logo_click, width=8, font=(FONT, 10, "bold"),
                           bg="#3a4b5a", fg="white", activeforeground="white", relief="flat",
                           cursor="hand2")
        logo_b.grid(row=r, column=4, padx=(8, 0), pady=7)
        refresh_logo_btn()

        def remove():
            for widget in row["widgets"]:
                widget.destroy()
            rows.remove(row)
            regrid()

        def move(delta):
            i = rows.index(row)
            j = i + delta
            if 0 <= j < len(rows):
                rows[i], rows[j] = rows[j], rows[i]
                regrid()

        arrows = tk.Frame(inner, bg=CARD)
        arrows.grid(row=r, column=5, padx=(8, 0), pady=7)
        for txt, d in (("▲", -1), ("▼", 1)):
            tk.Button(arrows, text=txt, command=lambda d=d: move(d), width=2, font=(FONT, 9, "bold"),
                      bg="#3a4b5a", fg="white", activebackground="#4a5d6f", activeforeground="white",
                      relief="flat", cursor="hand2").pack(side="left", padx=(0, 3))

        x = tk.Button(inner, text="✕", command=remove, width=3, font=(FONT, 10, "bold"),
                      bg="#7d3030", fg="white", activebackground="#a04141",
                      activeforeground="white", relief="flat", cursor="hand2")
        x.grid(row=r, column=6, padx=(8, 0), pady=7)
        # row['logo'] holds the chosen image path; row['widgets'] are re-gridded when rows move
        row.update(name=name_e, path=path_e, widgets=[strip, name_e, path_e, b, logo_b, arrows, x])
        rows.append(row)
        return name_e

    for g in config["games"]:
        add_row(g["name"], g.get("path", ""), g.get("logo", ""))

    add_btn = tk.Button(win, text="＋  Add game", font=(FONT, 11, "bold"), bg="#248f45", fg="white",
                        activebackground="#2ca653", activeforeground="white", relief="flat",
                        padx=18, pady=7, cursor="hand2",
                        command=lambda: add_row().focus_set())
    add_btn.pack(anchor="w", padx=30, pady=(12, 0))

    # ---- background ----
    bg_path = [config.get("background", "")]
    bg_panel = tk.Frame(win, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
    bg_panel.pack(fill="x", padx=30, pady=(14, 0))
    bg_in = tk.Frame(bg_panel, bg=CARD)
    bg_in.pack(fill="x", padx=22, pady=14)
    bg_in.columnconfigure(1, weight=1)

    tk.Label(bg_in, text="BACKGROUND", font=(FONT, 9, "bold"), fg=MUTED, bg=CARD,
             width=12, anchor="w").grid(row=0, column=0, sticky="w")
    bg_label = tk.Label(bg_in, font=(FONT, 10), fg=TEXT, bg=CARD, anchor="w")
    bg_label.grid(row=0, column=1, sticky="w", padx=8)

    def refresh_bg_label():
        if bg_path[0]:
            bg_label.config(text=Path(bg_path[0]).name if Path(bg_path[0]).is_file() else "Custom image (file missing)")
        elif get_bg_source() is not None:
            bg_label.config(text="Default (background.png)")
        else:
            bg_label.config(text="Default (dark green gradient)")

    def choose_bg():
        chosen = filedialog.askopenfilename(
            parent=win, title="Select a background image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")])
        if not chosen:
            return
        try:
            with Image.open(chosen) as im:
                im.verify()
        except Exception:
            messagebox.showerror("Not an image", "That file couldn't be opened as an image.\n\n"
                                 "Use a PNG, JPG, GIF, BMP or WebP file.", parent=win)
            return
        bg_path[0] = chosen
        refresh_bg_label()

    def reset_bg():
        bg_path[0] = ""
        refresh_bg_label()

    tk.Button(bg_in, text="Choose image…", command=choose_bg, width=14, font=(FONT, 10, "bold"),
              bg="#2d7dd2", fg="white", activebackground="#3c8de0", activeforeground="white",
              relief="flat", cursor="hand2").grid(row=0, column=2, padx=(8, 0))
    tk.Button(bg_in, text="Reset", command=reset_bg, width=8, font=(FONT, 10, "bold"),
              bg="#3a4b5a", fg="white", activebackground="#4a5d6f", activeforeground="white",
              relief="flat", cursor="hand2").grid(row=0, column=3, padx=(8, 0))

    tk.Label(bg_in, text="DARKNESS", font=(FONT, 9, "bold"), fg=MUTED, bg=CARD,
             width=12, anchor="w").grid(row=1, column=0, sticky="w", pady=(10, 0))
    dim_scale = tk.Scale(bg_in, from_=0, to=90, orient="horizontal", showvalue=True, resolution=1,
                         bg=CARD, fg=TEXT, troughcolor="#0f1922", highlightthickness=0,
                         activebackground="#77b5fe", bd=0, font=(FONT, 9))
    dim_scale.set(int(round(float(config.get("bg_dim", 0.68)) * 100)))
    dim_scale.grid(row=1, column=1, columnspan=3, sticky="ew", padx=8, pady=(10, 0))
    refresh_bg_label()

    fullscreen_var = tk.BooleanVar(value=config.get("fullscreen", True))
    minimize_var = tk.BooleanVar(value=config.get("minimize_on_launch", False))
    options = tk.Frame(win, bg=BG)
    options.pack(fill="x", padx=32, pady=12)
    for text, var in (("Start launcher full screen", fullscreen_var),
                      ("Minimize launcher after starting a game", minimize_var)):
        tk.Checkbutton(options, text=text, variable=var, font=(FONT, 11), fg=TEXT, bg=BG,
                       selectcolor="#0f1922", activebackground=BG,
                       activeforeground=TEXT).pack(side="left", padx=(0, 25))

    def save_and_close():
        games = []
        for row in rows:
            name, path = row["name"].get().strip(), row["path"].get().strip()
            if not name and not path:
                continue
            games.append({"name": name or Path(path).stem or "Game", "path": path,
                          "logo": store_logo(row["logo"])})
        config["games"] = games
        prune_logo_store(games)
        config["background"] = store_file(bg_path[0], BG_STORE)
        config["bg_dim"] = dim_scale.get() / 100
        prune_store(BG_STORE, [config["background"]])
        config["fullscreen"] = fullscreen_var.get()
        config["minimize_on_launch"] = minimize_var.get()
        save_config()
        set_fullscreen(config["fullscreen"])
        win.destroy()
        draw()

    bottom = tk.Frame(win, bg=BG)
    bottom.pack(fill="x", padx=30, pady=(0, 24))
    tk.Button(bottom, text="Cancel", command=win.destroy, font=(FONT, 11, "bold"),
              bg="#33414d", fg="white", activebackground="#41505d", activeforeground="white",
              relief="flat", padx=22, pady=8, cursor="hand2").pack(side="right", padx=(10, 0))
    tk.Button(bottom, text="Save", command=save_and_close, font=(FONT, 11, "bold"),
              bg="#248f45", fg="white", activebackground="#2ca653", activeforeground="white",
              relief="flat", padx=28, pady=8, cursor="hand2").pack(side="right")

    if add_new:
        add_row().focus_set()

    win.update_idletasks()
    win.minsize(1000, win.winfo_reqheight())
    x = (win.winfo_screenwidth() - max(1000, win.winfo_reqwidth())) // 2
    y = max(10, (win.winfo_screenheight() - win.winfo_reqheight()) // 2 - 20)
    win.geometry(f"+{x}+{y}")


# ------------------------------------------------------------------- drawing
def hover_tile(tag, on, normal, lit, accent, border):
    canvas.itemconfig(tag + "_bg", fill=lit if on else normal, outline=accent if on else border)
    canvas.config(cursor="hand2" if on else "")


def draw(_event=None):
    global _bg_photo
    w, h = canvas.winfo_width(), canvas.winfo_height()
    if w < 100 or h < 100:
        return
    canvas.delete("all")
    _bg_photo = make_background(w, h)
    canvas.create_image(0, 0, image=_bg_photo, anchor="nw")

    # Header
    canvas.create_text(w / 2, 68, text="GOLF SIM", font=(FONT, 40, "bold"), fill=TEXT)
    canvas.create_text(w / 2, 116, text="L A U N C H E R", font=(FONT, 14, "bold"), fill="#77b5fe")
    canvas.create_rectangle(w / 2 - 30, 138, w / 2 + 30, 141, fill="#77b5fe", outline="")

    # Tile layout: up to 5 per row, rows centered
    tiles = list(config["games"])
    n = len(tiles)
    if n == 0:
        canvas.create_text(w / 2, h / 2, text="No games yet", font=(FONT, 22, "bold"), fill=TEXT)
        canvas.create_text(w / 2, h / 2 + 36, text="Open Settings and click  ＋ Add game  to create your first tile",
                           font=(FONT, 12), fill=MUTED)
    cols = max(1, min(n, 5))
    nrows = max(1, -(-n // cols))
    mx, gap = max(40, int(w * 0.06)), max(18, int(w * 0.02))
    cw = min(340, (w - 2 * mx - (cols - 1) * gap) / cols)
    avail = (h - 110) - 170
    ch = min(190, max(110, cw * 0.62))
    ch = min(ch, (avail - (nrows - 1) * gap) / nrows)
    y0 = 170 + (avail - (nrows * ch + (nrows - 1) * gap)) / 2
    _logo_photos.clear()
    _slots.clear()

    for idx, game in enumerate(tiles):
        r, c = divmod(idx, cols)
        in_row = min(cols, n - r * cols)
        row_w = in_row * cw + (in_row - 1) * gap
        x1 = (w - row_w) / 2 + c * (cw + gap)
        y1 = y0 + r * (ch + gap)
        x2, y2 = x1 + cw, y1 + ch
        cx = (x1 + x2) / 2
        tag = f"card{idx}"
        _slots.append((x1, y1, x2, y2))
        rrect(x1 + 2, y1 + 6, x2 + 2, y2 + 6, 20, fill="#070b10", outline="", tags=(tag + "_shadow",))

        name = game["name"]
        accent = accent_for(name, idx)
        rrect(x1, y1, x2, y2, 20, fill=TILE, outline=TILE_BORDER, width=1, tags=(tag, tag + "_bg"))
        rrect(x1 + 28, y1 + 14, x2 - 28, y1 + 17, 2, fill=accent, outline="", tags=tag)

        # logo for known games, otherwise the game's name as text
        photo = logo_image(name, cw - 56, ch * 0.34, game.get("logo", ""))
        ly = y1 + ch * 0.47
        if photo:
            canvas.create_image(cx, ly, image=photo, tags=tag)
        else:
            canvas.create_text(cx, ly, text=name.upper(), width=cw - 30, justify="center",
                               font=(FONT, 16, "bold"), fill=TEXT, tags=tag)

        # status (dot placed just left of the text)
        label, color = status_of(game)
        sy = y1 + ch * 0.84
        t = canvas.create_text(cx + 7, sy, text=label, font=(FONT, 10), fill=MUTED, tags=tag)
        bb = canvas.bbox(t)
        canvas.create_oval(bb[0] - 15, sy - 4, bb[0] - 7, sy + 4, fill=color, outline="", tags=tag)

        canvas.tag_bind(tag, "<Enter>", lambda e, t=tag, a=accent: hover_tile(t, True, TILE, TILE_HOVER, a, TILE_BORDER))
        canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: hover_tile(t, False, TILE, TILE_HOVER, None, TILE_BORDER))
        canvas.tag_bind(tag, "<ButtonPress-1>", lambda e, i=idx: drag_start(e, i))
        canvas.tag_bind(tag, "<B1-Motion>", drag_move)
        canvas.tag_bind(tag, "<ButtonRelease-1>", lambda e, g=game: drag_end(e, g))
        for right_click in ("<Button-3>", "<Button-2>"):
            canvas.tag_bind(tag, right_click, lambda e, i=idx: show_tile_menu(e, i))

    # Footer
    pill(mx, h - 70, 170, 44, "⚙   SETTINGS", "#2a3844", "#374a5a", open_settings, "settings", anchor="w")
    pill(w - mx, h - 70, 130, 44, "EXIT", "#7d3030", "#a04141", close_launcher, "exit", anchor="e")
    canvas.create_text(w / 2, h - 48, text="Click to launch   •   Drag to reorder   •   Right-click for more   •   Esc: windowed   •   F11: full screen",
                       font=(FONT, 10), fill=GREY)


def pill(x, y, bw, bh, text, fill, hover, cmd, tag, anchor="w"):
    x1 = x if anchor == "w" else x - bw
    rrect(x1, y, x1 + bw, y + bh, 20, fill=fill, outline="", tags=(tag, tag + "_bg"))
    canvas.create_text(x1 + bw / 2, y + bh / 2, text=text, font=(FONT, 11, "bold"),
                       fill=TEXT, tags=tag)


def bind_interactions():
    """Footer buttons are bound once — tag bindings survive redraws."""
    def hover(tag, on, normal, lit):
        canvas.itemconfig(tag + "_bg", fill=lit if on else normal)
        canvas.config(cursor="hand2" if on else "")

    for tag, normal, lit, cmd in (("settings", "#2a3844", "#374a5a", open_settings),
                                  ("exit", "#7d3030", "#a04141", close_launcher)):
        canvas.tag_bind(tag, "<Enter>", lambda e, t=tag, n=normal, l=lit: hover(t, True, n, l))
        canvas.tag_bind(tag, "<Leave>", lambda e, t=tag, n=normal, l=lit: hover(t, False, n, l))
        canvas.tag_bind(tag, "<Button-1>", lambda e, c=cmd: c())


_resize_job = None


def on_resize(_event=None):
    global _resize_job
    if _resize_job:
        root.after_cancel(_resize_job)
    _resize_job = root.after(40, draw)


set_fullscreen(config.get("fullscreen", True))
bind_interactions()
canvas.bind("<Configure>", on_resize)
root.bind("<Escape>", lambda e: set_fullscreen(False))
root.bind("<F11>", lambda e: set_fullscreen(not root.attributes("-fullscreen")))
root.mainloop()
