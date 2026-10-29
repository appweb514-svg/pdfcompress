#!/usr/bin/env python3
"""PDF Compress - utilitaire portable de compression de PDF (Windows / Linux).

Sans argument : ouvre l'interface graphique.
Avec arguments : mode ligne de commande, par ex.
    pdfcompress fichier.pdf -n moyenne -o sortie.pdf
"""
from __future__ import annotations

import argparse
import os
import sys
import threading

import pymupdf

APP_NAME = "PDF Compress"
VERSION = "1.0.0"
CREDIT = "D'après une proposition de Marie"

# niveau -> (dpi cible, seuil dpi, qualité JPEG)
PRESETS = {
    "faible": (200, 250, 85),
    "moyenne": (130, 160, 70),
    "forte": (90, 110, 50),
    "extreme": (72, 80, 35),
}
PRESET_LABELS = {
    "faible": "Faible - meilleure qualité (200 dpi)",
    "moyenne": "Moyenne - recommandé (130 dpi)",
    "forte": "Forte - écran / e-mail (90 dpi)",
    "extreme": "Extrême - plus petit possible (72 dpi)",
}


def human(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024 or unit == "Go":
            return f"{n:.0f} {unit}" if unit == "o" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def default_output(path: str) -> str:
    base, _ = os.path.splitext(path)
    return base + "_compresse.pdf"


def compress_pdf(src: str, dst: str, level: str = "moyenne", grayscale: bool = False) -> dict:
    """Compresse src vers dst. Renvoie un dict avec les tailles.

    Si le résultat n'est pas plus petit que l'original, l'original est copié
    tel quel (on ne livre jamais un fichier plus gros).
    """
    if level not in PRESETS:
        raise ValueError(f"Niveau inconnu : {level}")
    if os.path.abspath(src) == os.path.abspath(dst):
        raise ValueError("Le fichier de sortie doit être différent du fichier d'origine.")
    dpi_target, dpi_threshold, quality = PRESETS[level]
    before = os.path.getsize(src)

    doc = pymupdf.open(src)
    try:
        if doc.needs_pass:
            raise ValueError("PDF protégé par mot de passe : impossible de le compresser.")
        if not doc.is_pdf:
            raise ValueError("Ce fichier n'est pas un PDF.")
        # 1. images : rééchantillonnage + recompression JPEG
        try:
            doc.rewrite_images(
                dpi_threshold=dpi_threshold,
                dpi_target=dpi_target,
                quality=quality,
                lossy=True,
                lossless=True,
                bitonal=True,
                color=True,
                gray=True,
                set_to_gray=grayscale,
            )
        except Exception:
            pass  # PDF exotique : on garde au moins le nettoyage ci-dessous
        # 2. polices : ne garder que les glyphes utilisés
        try:
            doc.subset_fonts()
        except Exception:
            pass
        # 3. métadonnées XML inutiles
        try:
            doc.del_xml_metadata()
        except Exception:
            pass
        tmp = dst + ".tmp"
        doc.save(
            tmp,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True,
            use_objstms=1,
        )
    finally:
        doc.close()

    after = os.path.getsize(tmp)
    if after >= before:
        os.remove(tmp)
        with open(src, "rb") as fi, open(dst, "wb") as fo:
            fo.write(fi.read())
        after = before
        improved = False
    else:
        os.replace(tmp, dst)
        improved = True
    return {"src": src, "dst": dst, "before": before, "after": after, "improved": improved}


def summary(r: dict) -> str:
    if not r["improved"]:
        return f"{os.path.basename(r['src'])} : déjà optimisé ({human(r['before'])}), copié tel quel."
    gain = 100 * (1 - r["after"] / r["before"])
    pct = f"{gain:.1f}" if gain >= 99.5 else f"{gain:.0f}"
    return (f"{os.path.basename(r['src'])} : {human(r['before'])} -> "
            f"{human(r['after'])} (-{pct} %)")


# ----------------------------------------------------------------- CLI

def cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="pdfcompress", description="Compresse des fichiers PDF.")
    p.add_argument("fichiers", nargs="+", help="PDF à compresser")
    p.add_argument("-n", "--niveau", choices=list(PRESETS), default="moyenne")
    p.add_argument("-o", "--sortie", help="fichier de sortie (un seul PDF) ou dossier")
    p.add_argument("-g", "--gris", action="store_true", help="convertir les images en niveaux de gris")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION} - {CREDIT}")
    a = p.parse_args(argv)
    rc = 0
    for f in a.fichiers:
        if a.sortie and os.path.isdir(a.sortie):
            out = os.path.join(a.sortie, os.path.basename(default_output(f)))
        elif a.sortie and len(a.fichiers) == 1:
            out = a.sortie
        else:
            out = default_output(f)
        try:
            print(summary(compress_pdf(f, out, a.niveau, a.gris)))
        except Exception as e:  # noqa: BLE001
            print(f"{f} : ERREUR - {e}", file=sys.stderr)
            rc = 1
    return rc


# ----------------------------------------------------------------- GUI

def _open_folder(path: str) -> None:
    """Ouvre un dossier dans l'explorateur du système."""
    import subprocess
    try:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            env = dict(os.environ)
            # exécutable PyInstaller : rendre à xdg-open les bibliothèques du système
            if "LD_LIBRARY_PATH_ORIG" in env:
                env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
            else:
                env.pop("LD_LIBRARY_PATH", None)
            cmd = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.Popen([cmd, path], env=env)
    except Exception:  # noqa: BLE001
        pass


def _pct(before: int, after: int) -> str:
    gain = 100 * (1 - after / before) if before else 0
    return f"{gain:.1f}" if gain >= 99.5 else f"{gain:.0f}"


def gui() -> None:
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import filedialog, messagebox, ttk

    if sys.platform == "win32":  # texte net sur les écrans haute résolution
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass

    C = {
        "bg": "#F3F5F9", "card": "#FFFFFF", "border": "#E2E8F0",
        "ink": "#0F172A", "muted": "#64748B", "faint": "#94A3B8",
        "accent": "#2563EB", "accent_hover": "#1D4ED8", "accent_soft": "#EAF1FE",
        "header": "#0F172A", "ok": "#15803D", "err": "#B91C1C", "stripe": "#F8FAFC",
    }

    root = tk.Tk()
    root.withdraw()
    root.title(f"{APP_NAME} {VERSION}")
    root.configure(bg=C["bg"])

    fams = set(tkfont.families(root))
    base = next((f for f in ("Segoe UI", "Inter", "Cantarell", "Ubuntu", "Noto Sans", "DejaVu Sans")
                 if f in fams), "TkDefaultFont")

    def F(size: int, weight: str = "normal"):
        return (base, size, weight)

    # icône de fenêtre dessinée (pas de fichier externe)
    ico = tk.PhotoImage(width=32, height=32)
    ico.put(C["accent"], to=(5, 2, 27, 30))
    ico.put(C["accent_hover"], to=(20, 2, 27, 9))
    for y in (12, 17, 22):
        ico.put("#FFFFFF", to=(10, y, 22, y + 2))
    root.iconphoto(True, ico)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    row_h = tkfont.Font(root, font=F(10)).metrics("linespace") + 14
    style.configure("Files.Treeview", background=C["card"], fieldbackground=C["card"],
                    foreground=C["ink"], rowheight=row_h, borderwidth=0, font=F(10))
    style.layout("Files.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure("Files.Treeview.Heading", background=C["card"], foreground=C["muted"],
                    font=F(9, "bold"), borderwidth=0, relief="flat", padding=(4, 6))
    style.map("Files.Treeview", background=[("selected", C["accent_soft"])],
              foreground=[("selected", C["ink"])])
    style.map("Files.Treeview.Heading", background=[("active", C["card"])])
    style.configure("Accent.Horizontal.TProgressbar", troughcolor=C["border"], background=C["accent"],
                    bordercolor=C["border"], lightcolor=C["accent"], darkcolor=C["accent"], thickness=6)
    style.configure("Card.TCheckbutton", background=C["card"], foreground=C["ink"], font=F(10))
    style.map("Card.TCheckbutton", background=[("active", C["card"])])

    class Btn(tk.Label):
        """Bouton plat avec survol, utilisable au clavier (Tab puis Entrée/Espace)."""
        KINDS = {
            "primary": (C["accent"], "#FFFFFF", C["accent_hover"]),
            "soft": (C["accent_soft"], C["accent"], "#DCE7FD"),
            "ghost": (C["card"], C["ink"], "#F1F5F9"),
        }

        def __init__(self, parent, text, command, kind="ghost"):
            bg, fg, hover = self.KINDS[kind]
            big = kind == "primary"
            super().__init__(parent, text=text, bg=bg, fg=fg, cursor="hand2", takefocus=1,
                             font=F(11 if big else 10, "bold" if big else "normal"),
                             padx=28 if big else 12, pady=10 if big else 5,
                             highlightthickness=1, highlightcolor=C["accent"],
                             highlightbackground=C["border"] if kind == "ghost" else bg)
            self._bg, self._fg, self._hover, self._kind = bg, fg, hover, kind
            self._cmd = command
            self.enabled = True
            self.bind("<Enter>", lambda e: self.enabled and self.configure(bg=self._hover))
            self.bind("<Leave>", lambda e: self._paint())
            for ev in ("<Button-1>", "<Return>", "<space>"):
                self.bind(ev, self._click)

        def _click(self, _e=None):
            if self.enabled:
                self._cmd()

        def _paint(self):
            if self.enabled:
                self.configure(bg=self._bg, fg=self._fg, cursor="hand2")
            elif self._kind == "primary":
                self.configure(bg="#93B4F5", fg="#FFFFFF", cursor="arrow")
            else:
                self.configure(bg=self._bg, fg=C["faint"], cursor="arrow")

        def set_enabled(self, on: bool):
            self.enabled = on
            self._paint()

    def card(parent, **pack):
        f = tk.Frame(parent, bg=C["card"], highlightthickness=1, highlightbackground=C["border"])
        f.pack(**pack)
        return f

    def heading(parent, num, text):
        row = tk.Frame(parent, bg=C["card"])
        cv = tk.Canvas(row, width=24, height=24, bg=C["card"], highlightthickness=0)
        cv.create_oval(1, 1, 23, 23, fill=C["accent"], outline="")
        cv.create_text(12, 12, text=str(num), fill="#FFFFFF", font=F(9, "bold"))
        cv.pack(side="left")
        tk.Label(row, text=text, bg=C["card"], fg=C["ink"], font=F(12, "bold")).pack(side="left", padx=(8, 0))
        return row

    files: dict[str, str] = {}      # id de ligne -> chemin
    row_state: dict[str, str] = {}  # id de ligne -> ok / err / same / busy
    state = {"busy": False, "folder": None}
    level = tk.StringVar(value="moyenne")
    gray = tk.BooleanVar(value=False)
    outdir = tk.StringVar(value="")
    out_text = tk.StringVar()
    status = tk.StringVar(value="Ajoutez un ou plusieurs PDF pour commencer.")

    # ---- en-tête
    header = tk.Frame(root, bg=C["header"])
    header.pack(side="top", fill="x")
    hin = tk.Frame(header, bg=C["header"])
    hin.pack(fill="x", padx=24, pady=16)
    logo = tk.Canvas(hin, width=36, height=42, bg=C["header"], highlightthickness=0)
    logo.create_polygon(2, 2, 24, 2, 34, 12, 34, 40, 2, 40, fill=C["accent"], outline="")
    logo.create_polygon(24, 2, 34, 12, 24, 12, fill="#93B4F5", outline="")
    logo.create_text(18, 28, text="PDF", fill="#FFFFFF", font=F(8, "bold"))
    logo.pack(side="left")
    titles = tk.Frame(hin, bg=C["header"])
    titles.pack(side="left", padx=14)
    tk.Label(titles, text=APP_NAME, font=F(16, "bold"), fg="#FFFFFF", bg=C["header"]).pack(anchor="w")
    tk.Label(titles, text="Allégez vos PDF sur votre ordinateur, sans rien envoyer en ligne.",
             font=F(10), fg=C["faint"], bg=C["header"]).pack(anchor="w")
    tk.Label(hin, text=f"v{VERSION}", font=F(9), fg=C["faint"], bg=C["header"]).pack(side="right", anchor="n")

    # ---- pied : progression + bouton principal (emballé avant le corps pour rester visible)
    footer = tk.Frame(root, bg=C["card"], highlightthickness=1, highlightbackground=C["border"])
    footer.pack(side="bottom", fill="x")
    tk.Label(footer, text=CREDIT, bg=C["card"], fg=C["faint"], font=F(9, "italic"),
             anchor="e").pack(side="bottom", fill="x", padx=20, pady=(0, 8))
    fin = tk.Frame(footer, bg=C["card"])
    fin.pack(fill="x", padx=20, pady=(14, 6))

    # ---- corps
    body = tk.Frame(root, bg=C["bg"])
    body.pack(side="top", fill="both", expand=True, padx=20, pady=16)

    # 1. fichiers
    fcard = card(body, fill="both", expand=True)
    ftop = tk.Frame(fcard, bg=C["card"])
    ftop.pack(fill="x", padx=16, pady=(14, 10))
    heading(ftop, 1, "Fichiers").pack(side="left")
    count_lbl = tk.Label(ftop, text="", bg=C["card"], fg=C["muted"], font=F(10))
    count_lbl.pack(side="left", padx=10)

    stack = tk.Frame(fcard, bg=C["card"])
    stack.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    empty = tk.Canvas(stack, bg=C["card"], highlightthickness=0, height=150, cursor="hand2")
    empty_hover = {"on": False}

    def draw_empty(_e=None):
        empty.delete("all")
        w, h = empty.winfo_width(), empty.winfo_height()
        if w < 20 or h < 20:
            return
        on = empty_hover["on"]
        empty.create_rectangle(2, 2, w - 3, h - 3, width=2, dash=(6, 4),
                               outline=C["accent"] if on else "#C7D2E0",
                               fill=C["accent_soft"] if on else C["stripe"])
        cx, cy = w // 2, h // 2
        empty.create_polygon(cx - 15, cy - 48, cx + 7, cy - 48, cx + 15, cy - 40, cx + 15, cy - 12,
                             cx - 15, cy - 12, fill=C["card"], outline=C["accent"], width=2)
        empty.create_line(cx, cy - 18, cx, cy - 40, fill=C["accent"], width=2, arrow="last")
        empty.create_text(cx, cy + 10, text="Cliquez ici pour choisir des PDF",
                          font=F(12, "bold"), fill=C["ink"])
        empty.create_text(cx, cy + 32, text="Plusieurs fichiers à la fois · l'original n'est jamais modifié",
                          font=F(9), fill=C["muted"])

    def hover_empty(on):
        empty_hover["on"] = on
        draw_empty()

    empty.bind("<Configure>", draw_empty)
    empty.bind("<Enter>", lambda e: hover_empty(True))
    empty.bind("<Leave>", lambda e: hover_empty(False))
    empty.bind("<Button-1>", lambda e: add())

    tree_wrap = tk.Frame(stack, bg=C["card"], highlightthickness=1, highlightbackground=C["border"])
    tree = ttk.Treeview(tree_wrap, columns=("nom", "taille", "resultat"), show="headings",
                        style="Files.Treeview", selectmode="extended", height=6)
    tree.heading("nom", text="Fichier", anchor="w")
    tree.heading("taille", text="Taille", anchor="e")
    tree.heading("resultat", text="   Résultat", anchor="w")
    tree.column("nom", anchor="w", width=220, minwidth=120, stretch=True)
    tree.column("taille", anchor="e", width=90, minwidth=70, stretch=False)
    tree.column("resultat", anchor="w", width=260, minwidth=140, stretch=True)
    tree.tag_configure("odd", background=C["stripe"])
    tree.tag_configure("ok", foreground=C["ok"])
    tree.tag_configure("err", foreground=C["err"])
    tree.tag_configure("same", foreground=C["muted"])
    tree.tag_configure("busy", foreground=C["accent"])
    vsb = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    def restripe():
        for i, iid in enumerate(tree.get_children()):
            tags = ["odd"] if i % 2 else []
            if iid in row_state:
                tags.append(row_state[iid])
            tree.item(iid, tags=tags)

    def set_row(iid, text, tag=None):
        if not tree.exists(iid):
            return
        tree.set(iid, "resultat", "   " + text)
        if tag:
            row_state[iid] = tag
        else:
            row_state.pop(iid, None)
        restripe()
        if tag == "busy":
            tree.see(iid)

    def show_list():
        if files:
            empty.pack_forget()
            tree_wrap.pack(fill="both", expand=True)
            total = 0
            for f in files.values():
                try:
                    total += os.path.getsize(f)
                except OSError:
                    pass
            n = len(files)
            count_lbl.configure(text=f"{n} fichier{'s' if n > 1 else ''} · {human(total)}")
        else:
            tree_wrap.pack_forget()
            empty.pack(fill="both", expand=True)
            count_lbl.configure(text="")
        restripe()

    def add():
        if state["busy"]:
            return
        sel = filedialog.askopenfilenames(parent=root, title="Choisir des PDF",
                                          filetypes=[("PDF", "*.pdf *.PDF"), ("Tous les fichiers", "*.*")])
        known = set(files.values())
        for f in sel:
            f = os.path.abspath(f)
            if f in known:
                continue
            known.add(f)
            try:
                size = human(os.path.getsize(f))
            except OSError:
                size = "?"
            iid = tree.insert("", "end", values=(os.path.basename(f), size, "   En attente"))
            files[iid] = f
        if sel:
            status.set("Choisissez un niveau, puis cliquez sur Compresser.")
            status_lbl.configure(fg=C["muted"])
        show_list()

    def remove():
        if state["busy"]:
            return
        for iid in tree.selection():
            tree.delete(iid)
            files.pop(iid, None)
            row_state.pop(iid, None)
        show_list()

    def clear():
        if state["busy"]:
            return
        tree.delete(*tree.get_children())
        files.clear()
        row_state.clear()
        open_btn.pack_forget()
        bar.configure(value=0)
        status.set("Ajoutez un ou plusieurs PDF pour commencer.")
        status_lbl.configure(fg=C["muted"])
        show_list()

    tree.bind("<Delete>", lambda e: remove())

    def show_row_detail(e):
        iid = tree.identify_row(e.y)
        if iid and row_state.get(iid) == "err" and not state["busy"]:
            status.set(f"{os.path.basename(files[iid])} : {tree.set(iid, 'resultat').strip()}")
            status_lbl.configure(fg=C["err"])

    tree.bind("<<TreeviewSelect>>", lambda e: None)
    tree.bind("<ButtonRelease-1>", show_row_detail)
    tree.bind("<Double-1>", lambda e: add() if not tree.identify_row(e.y) else None)

    clr_btn = Btn(ftop, "Vider", clear, "ghost")
    clr_btn.pack(side="right")
    rm_btn = Btn(ftop, "Retirer", remove, "ghost")
    rm_btn.pack(side="right", padx=6)
    add_btn = Btn(ftop, "+  Ajouter des PDF", add, "soft")
    add_btn.pack(side="right")

    # 2. niveau
    lcard = card(body, fill="x", pady=(14, 0))
    heading(lcard, 2, "Niveau de compression").pack(anchor="w", padx=16, pady=(14, 10))
    grid = tk.Frame(lcard, bg=C["card"])
    grid.pack(fill="x", padx=16, pady=(0, 16))
    levels = [
        ("faible", "Faible", "Meilleure qualité", "200 dpi"),
        ("moyenne", "Moyenne", "Recommandé", "130 dpi"),
        ("forte", "Forte", "Écran, e-mail", "90 dpi"),
        ("extreme", "Extrême", "Le plus léger", "72 dpi"),
    ]
    tiles = {}
    for i, (key, title, desc, dpi) in enumerate(levels):
        grid.columnconfigure(i, weight=1, uniform="lvl")
        t = tk.Frame(grid, highlightthickness=2, cursor="hand2", takefocus=1)
        t.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
        l1 = tk.Label(t, text=title, font=F(11, "bold"), anchor="w")
        l2 = tk.Label(t, text=desc, font=F(9), anchor="w")
        l3 = tk.Label(t, text=dpi, font=F(9), anchor="w")
        l1.pack(fill="x", padx=12, pady=(10, 0))
        l2.pack(fill="x", padx=12)
        l3.pack(fill="x", padx=12, pady=(2, 10))
        tiles[key] = (t, l1, l2, l3)
        for w in (t, l1, l2, l3):
            w.configure(cursor="hand2")
            w.bind("<Button-1>", lambda e, k=key: level.set(k))
        t.bind("<Return>", lambda e, k=key: level.set(k))
        t.bind("<space>", lambda e, k=key: level.set(k))

    def paint_tiles(*_):
        for k, (t, l1, l2, l3) in tiles.items():
            on = k == level.get()
            bg = C["accent_soft"] if on else C["card"]
            t.configure(bg=bg, highlightbackground=C["accent"] if on else C["border"],
                        highlightcolor=C["accent"])
            l1.configure(bg=bg, fg=C["accent"] if on else C["ink"])
            l2.configure(bg=bg, fg=C["ink"])
            l3.configure(bg=bg, fg=C["muted"])

    level.trace_add("write", paint_tiles)
    paint_tiles()

    # 3. options
    ocard = card(body, fill="x", pady=(14, 0))
    heading(ocard, 3, "Options").pack(anchor="w", padx=16, pady=(14, 8))
    ttk.Checkbutton(ocard, text="Passer les images en niveaux de gris (encore plus léger)",
                    variable=gray, style="Card.TCheckbutton").pack(anchor="w", padx=16)
    orow = tk.Frame(ocard, bg=C["card"])
    orow.pack(fill="x", padx=16, pady=(10, 16))
    tk.Label(orow, text="Enregistrer dans", bg=C["card"], fg=C["ink"], font=F(10)).pack(side="left")

    def refresh_out(*_):
        d = outdir.get().strip()
        out_text.set(d if d else "À côté de chaque original  (nom_compresse.pdf)")
        out_lbl.configure(fg=C["ink"] if d else C["muted"])
        if d:
            reset_btn.pack(side="right", padx=(0, 6), before=dir_btn)
        else:
            reset_btn.pack_forget()

    def choose_dir():
        d = filedialog.askdirectory(parent=root, title="Dossier de sortie")
        if d:
            outdir.set(d)

    dir_btn = Btn(orow, "Changer…", choose_dir, "ghost")
    dir_btn.pack(side="right")
    reset_btn = Btn(orow, "Par défaut", lambda: outdir.set(""), "ghost")
    out_lbl = tk.Label(orow, textvariable=out_text, bg=C["stripe"], anchor="w", font=F(10),
                       padx=10, pady=5, width=1, highlightthickness=1, highlightbackground=C["border"])
    out_lbl.pack(side="left", fill="x", expand=True, padx=10)
    outdir.trace_add("write", refresh_out)
    refresh_out()

    # ordre d'emballage : options et niveaux d'abord (en bas), la liste prend le reste
    for w in (fcard, lcard, ocard):
        w.pack_forget()
    ocard.pack(side="bottom", fill="x", pady=(14, 0))
    lcard.pack(side="bottom", fill="x", pady=(14, 0))
    fcard.pack(side="top", fill="both", expand=True)

    # ---- pied (contenu)
    left = tk.Frame(fin, bg=C["card"])
    status_lbl = tk.Label(left, textvariable=status, bg=C["card"], fg=C["muted"], font=F(10),
                          anchor="w", width=1, justify="left")
    status_lbl.pack(fill="x")
    status_lbl.bind("<Configure>", lambda e: status_lbl.configure(wraplength=max(e.width - 4, 50)))
    bar = ttk.Progressbar(left, style="Accent.Horizontal.TProgressbar", mode="determinate")
    bar.pack(fill="x", pady=(8, 0))

    def start():
        if state["busy"]:
            return
        if not files:
            messagebox.showwarning(APP_NAME, "Ajoutez d'abord au moins un PDF.", parent=root)
            return
        d = outdir.get().strip()
        if d and not os.path.isdir(d):
            messagebox.showerror(APP_NAME, "Le dossier de sortie n'existe pas.", parent=root)
            return
        items = [(iid, files[iid]) for iid in tree.get_children()]
        for iid, _ in items:
            set_row(iid, "En attente")
        set_busy(True)
        open_btn.pack_forget()
        bar.configure(maximum=len(items), value=0)
        status_lbl.configure(fg=C["muted"])
        threading.Thread(target=worker, args=(items, level.get(), gray.get(), d), daemon=True).start()

    go = Btn(fin, "Compresser", start, "primary")
    go.pack(side="right", padx=(16, 0))
    open_btn = Btn(fin, "Ouvrir le dossier", lambda: state["folder"] and _open_folder(state["folder"]), "ghost")
    left.pack(side="left", fill="x", expand=True)

    def set_busy(on: bool):
        state["busy"] = on
        go.set_enabled(not on)
        go.configure(text="Compression…" if on else "Compresser")
        for b in (add_btn, rm_btn, clr_btn, dir_btn, reset_btn):
            b.set_enabled(not on)

    def worker(items, lvl, g, d):
        tb = ta = ok = err = 0
        folder = d or None
        n = len(items)
        for i, (iid, f) in enumerate(items, 1):
            root.after(0, set_row, iid, "Compression…", "busy")
            root.after(0, status.set, f"Compression {i}/{n} : {os.path.basename(f)}")
            dst = default_output(f)
            if d:
                dst = os.path.join(d, os.path.basename(dst))
            try:
                r = compress_pdf(f, dst, lvl, g)
                tb += r["before"]
                ta += r["after"]
                ok += 1
                folder = folder or os.path.dirname(dst)
                if r["improved"]:
                    txt, tag = f"{human(r['after'])}   (-{_pct(r['before'], r['after'])} %)", "ok"
                else:
                    txt, tag = "Déjà optimisé, copié tel quel", "same"
            except Exception as e:  # noqa: BLE001
                err += 1
                txt, tag = f"Erreur : {e}", "err"
            root.after(0, set_row, iid, txt, tag)
            root.after(0, bar.configure, {"value": i})
        root.after(0, done, tb, ta, ok, err, folder)

    def done(tb, ta, ok, err, folder):
        set_busy(False)
        state["folder"] = folder
        parts = []
        if ok:
            s = "s" if ok > 1 else ""
            parts.append(f"Terminé : {ok} fichier{s}, {human(tb)} → {human(ta)} "
                         f"(-{_pct(tb, ta)} %, {human(tb - ta)} gagnés)")
        if err:
            parts.append(f"{err} erreur{'s' if err > 1 else ''} (voir la liste)")
        status.set("  ·  ".join(parts) or "Terminé.")
        status_lbl.configure(fg=C["ok"] if not err else (C["err"] if not ok else C["ink"]))
        if ok and folder:
            open_btn.pack(side="right", padx=(10, 0), before=go)

    def on_close():
        if state["busy"] and not messagebox.askyesno(
                APP_NAME, "Une compression est en cours. Quitter quand même ?", parent=root):
            return
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.bind("<Control-o>", lambda e: add())

    show_list()
    root.update_idletasks()
    w = max(root.winfo_reqwidth(), 760)
    h = max(root.winfo_reqheight(), 660)
    root.minsize(640, root.winfo_reqheight())
    x = max(0, (root.winfo_screenwidth() - w) // 2)
    y = max(0, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.deiconify()
    root.mainloop()


def main() -> int:
    if len(sys.argv) > 1:
        return cli(sys.argv[1:])
    gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
