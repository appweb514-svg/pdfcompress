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
VERSION = "1.4.0"
CREDIT = "D'après une proposition de Marie"

# Icône PDF (PNG encodé en base64, générée par tools/make_icon.py)
ICON64_PNG = "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"
ICON48_PNG = "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"

# niveau -> (dpi cible, qualité JPEG)
PRESETS = {
    "faible": (200, 75),
    "moyenne": (150, 55),
    "forte": (110, 40),
    "extreme": (72, 30),
}
PRESET_LABELS = {
    "faible": "Faible - meilleure qualité (200 dpi)",
    "moyenne": "Moyenne - recommandé (150 dpi)",
    "forte": "Forte - écran / e-mail (110 dpi)",
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


def expand_pdfs(paths) -> list[str]:
    """Transforme une liste de fichiers et de dossiers en liste de PDF.

    Les dossiers sont parcourus avec leurs sous-dossiers. Les fichiers deja
    compresses (*_compresse.pdf) trouves dans un dossier sont ignores, pour
    ne pas recompresser un resultat precedent. Ordre stable, sans doublon.
    """
    out, seen = [], set()

    def push(f):
        f = os.path.abspath(f)
        if f not in seen:
            seen.add(f)
            out.append(f)

    for p in paths:
        if os.path.isdir(p):
            for d, subdirs, names in os.walk(p):
                subdirs[:] = sorted(s for s in subdirs if not s.startswith("."))
                for name in sorted(names, key=str.lower):
                    low = name.lower()
                    if low.endswith(".pdf") and not low.endswith("_compresse.pdf"):
                        push(os.path.join(d, name))
        elif os.path.isfile(p):
            push(p)
    return out


def unique_path(path: str, taken: set) -> str:
    """Renvoie `path`, ou `nom (2).pdf`, `nom (3).pdf`... s'il est deja pris
    dans ce lot. Evite que deux PDF de meme nom s'ecrasent dans un meme
    dossier de sortie."""
    base, ext = os.path.splitext(path)
    cand, i = path, 2
    while os.path.normcase(os.path.abspath(cand)) in taken:
        cand = f"{base} ({i}){ext}"
        i += 1
    taken.add(os.path.normcase(os.path.abspath(cand)))
    return cand


def _downsample_images(doc, dpi: int, quality: int, grayscale: bool) -> set:
    """Réduit chaque photo à la résolution exacte voulue et la recompresse en JPEG.

    PyMuPDF ne sait réduire que par moitiés ; ici on calcule la taille exacte à
    partir de la taille affichée sur la page. Renvoie les xref traités.
    Les images à transparence, 1 bit ou exotiques sont laissées à rewrite_images.
    """
    done, seen = set(), set()
    for page in doc:
        for im in page.get_images(full=True):
            xref, smask, bpc = im[0], im[1], im[4]
            if xref in seen:
                continue
            seen.add(xref)
            if smask or bpc != 8:
                continue
            try:
                # plus grande taille d'affichage sur l'ensemble du document
                width_pt = 0.0
                for pg in doc:
                    for r in pg.get_image_rects(xref):
                        width_pt = max(width_pt, r.width, r.height * im[2] / max(im[3], 1))
                if width_pt <= 0:
                    continue
                pix = pymupdf.Pixmap(doc, xref)
                eff = pix.width / (width_pt / 72)
                recolor = grayscale and pix.colorspace is not None and pix.colorspace.n != 1
                if eff <= dpi * 1.15 and not recolor:
                    continue
                if pix.alpha:
                    pix = pymupdf.Pixmap(pix, 0)
                if grayscale and (pix.colorspace is None or pix.colorspace.n != 1):
                    pix = pymupdf.Pixmap(pymupdf.csGRAY, pix)
                elif pix.colorspace is None or pix.colorspace.n not in (1, 3):
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                if eff > dpi * 1.15:
                    k = dpi / eff
                    pix = pymupdf.Pixmap(pix, max(1, round(pix.width * k)), max(1, round(pix.height * k)), None)
                data = pix.tobytes("jpg", jpg_quality=quality)
                if len(data) >= len(doc.xref_stream_raw(xref) or b""):
                    continue
                page.replace_image(xref, stream=data)
                done.add(xref)
            except Exception:  # noqa: BLE001 - image exotique : on la laisse
                continue
    return done


def compress_pdf(src: str, dst: str, level: str = "moyenne", grayscale: bool = False) -> dict:
    """Compresse src vers dst. Renvoie un dict avec les tailles.

    Si le résultat n'est pas plus petit que l'original, l'original est copié
    tel quel (on ne livre jamais un fichier plus gros).
    """
    if level not in PRESETS:
        raise ValueError(f"Niveau inconnu : {level}")
    if os.path.abspath(src) == os.path.abspath(dst):
        raise ValueError("Le fichier de sortie doit être différent du fichier d'origine.")
    dpi_target, quality = PRESETS[level]
    before = os.path.getsize(src)

    doc = pymupdf.open(src)
    try:
        if doc.needs_pass:
            raise ValueError("PDF protégé par mot de passe : impossible de le compresser.")
        if not doc.is_pdf:
            raise ValueError("Ce fichier n'est pas un PDF.")
        # 1. images : réduction précise + JPEG, puis rewrite_images pour le reste
        try:
            _downsample_images(doc, dpi_target, quality, grayscale)
        except Exception:  # noqa: BLE001
            pass
        try:
            doc.rewrite_images(
                dpi_threshold=round(dpi_target * 1.15) + 1,
                dpi_target=dpi_target,
                quality=quality,
                lossy=True,
                lossless=True,
                bitonal=True,
                color=True,
                gray=True,
                set_to_gray=grayscale,
            )
        except Exception:  # noqa: BLE001
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
    p.add_argument("fichiers", nargs="+", help="PDF ou dossiers à compresser (sous-dossiers inclus)")
    p.add_argument("-n", "--niveau", choices=list(PRESETS), default="moyenne")
    p.add_argument("-o", "--sortie", help="fichier de sortie (un seul PDF) ou dossier")
    p.add_argument("-g", "--gris", action="store_true", help="convertir les images en niveaux de gris")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION} - {CREDIT}")
    a = p.parse_args(argv)
    rc = 0
    for f in a.fichiers:
        if not os.path.exists(f):
            print(f"{f} : ERREUR - introuvable", file=sys.stderr)
            rc = 1
    pdfs = expand_pdfs(a.fichiers)
    if not pdfs:
        print("Aucun PDF trouvé.", file=sys.stderr)
        return 1
    single = len(pdfs) == 1 and not any(os.path.isdir(x) for x in a.fichiers)
    taken: set = set()
    for f in pdfs:
        if a.sortie and os.path.isdir(a.sortie):
            out = os.path.join(a.sortie, os.path.basename(default_output(f)))
        elif a.sortie and single:
            out = a.sortie
        else:
            out = default_output(f)
        out = unique_path(out, taken)
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


def gui(initial: list[str] | None = None, spool: str | None = None, lock=None) -> None:
    """Interface graphique. `initial` : fichiers à charger d'emblée (clic droit).
    `spool` : dossier d'attente surveillé pour les fichiers des lancements suivants.
    `lock` : verrou d'instance, gardé tant que la fenêtre est ouverte."""
    _keep_lock = lock  # noqa: F841 - le verrou vit aussi longtemps que la fenêtre
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

    # glisser-déposer : tkinterdnd2 si disponible, sinon simple sélection par clic
    dnd = None
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        root = TkinterDnD.Tk()
        dnd = DND_FILES
    except Exception:  # noqa: BLE001 - tkdnd absent : fenêtre Tk classique
        dnd = None
        bad = tk._default_root
        if bad is not None:
            try:
                bad.destroy()
            except Exception:  # noqa: BLE001
                pass
        tk._default_root = None
        root = tk.Tk()
    root.withdraw()
    root.title(APP_NAME)
    root.configure(bg=C["bg"])

    fams = set(tkfont.families(root))
    base = next((f for f in ("Segoe UI", "Inter", "Cantarell", "Ubuntu", "Noto Sans", "DejaVu Sans")
                 if f in fams), "TkDefaultFont")

    def F(size: int, weight: str = "normal"):
        return (base, size, weight)

    # icône PDF de la fenêtre et de la barre des tâches (intégrée, pas de fichier externe)
    ico64 = tk.PhotoImage(master=root, data=ICON64_PNG)
    ico48 = tk.PhotoImage(master=root, data=ICON48_PNG)
    root.iconphoto(True, ico64, ico48)
    root._icons = (ico64, ico48)  # garder une référence
    if sys.platform == "win32":
        # sous Windows, l'icône .ico embarquée dans l'exe sert aussi à la barre des tâches
        ico_file = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))),
                                "pdfcompress.ico")
        if os.path.exists(ico_file):
            try:
                root.iconbitmap(default=ico_file)
            except tk.TclError:
                pass

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
    logo = tk.Label(hin, image=ico48, bg=C["header"], bd=0)
    logo.pack(side="left")
    titles = tk.Frame(hin, bg=C["header"])
    titles.pack(side="left", padx=14)
    tk.Label(titles, text=APP_NAME, font=F(16, "bold"), fg="#FFFFFF", bg=C["header"]).pack(anchor="w")
    tk.Label(titles, text="Allégez vos PDF sur votre ordinateur, sans rien envoyer en ligne.",
             font=F(10), fg=C["faint"], bg=C["header"]).pack(anchor="w")

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
        empty.create_text(cx, cy + 10, text=("Glissez vos PDF ici, ou cliquez pour les choisir" if dnd else "Cliquez ici pour choisir des PDF"),
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

    def add_paths(paths):
        """Ajoute des PDF (ou les PDF d'un dossier) à la liste, sans doublon."""
        if state["busy"]:
            return 0
        pdfs = expand_pdfs(paths)
        known = set(files.values())
        added = 0
        for f in pdfs:
            if f in known:
                continue
            known.add(f)
            try:
                size = human(os.path.getsize(f))
            except OSError:
                size = "?"
            iid = tree.insert("", "end", values=(os.path.basename(f), size, "   En attente"))
            files[iid] = f
            added += 1
        if added:
            status.set("Choisissez un niveau, puis cliquez sur Compresser.")
            status_lbl.configure(fg=C["muted"])
        show_list()
        return added

    def add():
        if state["busy"]:
            return
        sel = filedialog.askopenfilenames(parent=root, title="Choisir des PDF",
                                          filetypes=[("PDF", "*.pdf *.PDF"), ("Tous les fichiers", "*.*")])
        add_paths(sel)

    def add_dir():
        if state["busy"]:
            return
        d = filedialog.askdirectory(parent=root, title="Choisir un dossier de PDF (sous-dossiers inclus)",
                                    mustexist=True)
        if not d:
            return
        n = add_paths([d])
        if not n:
            status.set("Aucun nouveau PDF trouvé dans ce dossier.")
            status_lbl.configure(fg=C["err"])
        else:
            status.set(f"{n} PDF ajouté{'s' if n > 1 else ''} depuis {os.path.basename(d) or d}.")
            status_lbl.configure(fg=C["muted"])

    def on_drop(e):
        hover_empty(False)
        paths = [x for x in root.tk.splitlist(e.data)]
        pdfs = [x for x in paths if os.path.isdir(x) or x.lower().endswith(".pdf")]
        if not pdfs:
            status.set("Seuls les fichiers PDF peuvent être déposés.")
            status_lbl.configure(fg=C["err"])
            return e.action
        add_paths(pdfs)
        return e.action

    globals()["_TEST_DROP"] = on_drop  # point d'entrée pour les tests

    if dnd:
        for w in (root, empty, tree):
            try:
                w.drop_target_register(dnd)
                w.dnd_bind("<<Drop>>", on_drop)
            except Exception:  # noqa: BLE001
                pass
        try:
            empty.dnd_bind("<<DropEnter>>", lambda e: (hover_empty(True), e.action)[1])
            empty.dnd_bind("<<DropLeave>>", lambda e: (hover_empty(False), e.action)[1])
        except Exception:  # noqa: BLE001
            pass

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
    dir_add_btn = Btn(ftop, "+  Dossier", add_dir, "soft")
    dir_add_btn.pack(side="right", padx=(6, 0))
    add_btn = Btn(ftop, "+  Ajouter des PDF", add, "soft")
    add_btn.pack(side="right")

    # 2. niveau
    lcard = card(body, fill="x", pady=(14, 0))
    heading(lcard, 2, "Niveau de compression").pack(anchor="w", padx=16, pady=(14, 10))
    grid = tk.Frame(lcard, bg=C["card"])
    grid.pack(fill="x", padx=16, pady=(0, 16))
    levels = [
        ("faible", "Faible", "Meilleure qualité", "200 dpi"),
        ("moyenne", "Moyenne", "Recommandé", "150 dpi"),
        ("forte", "Forte", "Écran, e-mail", "110 dpi"),
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
        for b in (add_btn, dir_add_btn, rm_btn, clr_btn, dir_btn, reset_btn):
            b.set_enabled(not on)

    def worker(items, lvl, g, d):
        tb = ta = ok = err = 0
        folder = d or None
        n = len(items)
        taken: set = set()
        for i, (iid, f) in enumerate(items, 1):
            root.after(0, set_row, iid, "Compression…", "busy")
            root.after(0, status.set, f"Compression {i}/{n} : {os.path.basename(f)}")
            dst = default_output(f)
            if d:
                dst = os.path.join(d, os.path.basename(dst))
            dst = unique_path(dst, taken)
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

    def bring_front():
        try:
            if root.state() == "iconic":
                root.deiconify()
            root.lift()
            root.attributes("-topmost", True)
            root.after(300, lambda: root.attributes("-topmost", False))
            root.focus_force()
        except Exception:  # noqa: BLE001
            pass

    pending: list[str] = []

    def receive(paths):
        """Fichiers arrivés par le clic droit : ajoutés à la liste (ou mis de côté
        si une compression est en cours)."""
        if not paths:
            return
        if state["busy"]:
            pending.extend(paths)
            return
        n = add_paths(paths)
        if n:
            status.set(f"{len(files)} PDF dans la liste. Choisissez un niveau, puis cliquez sur Compresser.")
            status_lbl.configure(fg=C["muted"])
        bring_front()

    def poll_spool():
        got = _spool_take(spool) if spool else []
        if pending and not state["busy"]:
            got = pending[:] + got
            pending.clear()
        receive(got)
        root.after(250, poll_spool)

    globals()["_TEST_RECEIVE"] = receive  # point d'entrée pour les tests

    show_list()
    if initial:
        add_paths(initial)
    if spool:
        root.after(100, poll_spool)
    root.update_idletasks()
    w = max(root.winfo_reqwidth(), 760)
    h = max(root.winfo_reqheight(), 660)
    root.minsize(640, root.winfo_reqheight())
    x = max(0, (root.winfo_screenwidth() - w) // 2)
    y = max(0, (root.winfo_screenheight() - h) // 3)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.deiconify()
    root.mainloop()


# ------------------------------------------------- clic droit / instance unique
#
# L'Explorateur Windows lance le programme une fois par fichier sélectionné
# ("--ouvrir chemin"). Pour tout regrouper dans UNE fenêtre, chaque lancement
# dépose sa liste dans un dossier d'attente local ; la fenêtre ouverte (celle
# qui détient le verrou) la récupère. Aucun port réseau : rien à autoriser
# dans le pare-feu, rien de suspect pour un antivirus.

def _spool_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".cache")
    d = os.path.join(base, "PDFCompress", "attente")
    os.makedirs(d, exist_ok=True)
    return d


class _InstanceLock:
    """Verrou de fichier non bloquant, libéré automatiquement à la fin du processus."""

    def __init__(self, path: str):
        self.path = path
        self.fh = None

    def acquire(self) -> bool:
        fh = open(self.path, "a+")
        try:
            if sys.platform == "win32":
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            return False
        self.fh = fh
        return True


def _spool_put(spool: str, paths: list[str]) -> str:
    import time
    name = os.path.join(spool, f"{time.time_ns()}-{os.getpid()}.txt")
    with open(name + ".tmp", "w", encoding="utf-8") as fh:
        fh.write("\n".join(paths))
    os.replace(name + ".tmp", name)
    return name


def _spool_take(spool: str) -> list[str]:
    """Vide le dossier d'attente et renvoie les chemins qu'il contenait."""
    out: list[str] = []
    try:
        names = sorted(n for n in os.listdir(spool) if n.endswith(".txt"))
    except OSError:
        return out
    for n in names:
        p = os.path.join(spool, n)
        try:
            with open(p, encoding="utf-8") as fh:
                out += [line for line in fh.read().splitlines() if line.strip()]
            os.remove(p)
        except OSError:
            pass
    return out


def _spool_clean(spool: str, max_age: float = 60.0) -> None:
    """Supprime les dépôts abandonnés (plus d'une minute)."""
    import time
    now = time.time()
    try:
        for n in os.listdir(spool):
            p = os.path.join(spool, n)
            if now - os.path.getmtime(p) > max_age:
                os.remove(p)
    except OSError:
        pass


def open_in_window(paths: list[str]) -> int:
    """Ouvre la fenêtre avec ces fichiers, ou les confie à la fenêtre déjà ouverte."""
    import time
    paths = [os.path.abspath(p) for p in paths if p]
    try:
        spool = _spool_dir()
        lock = _InstanceLock(os.path.join(os.path.dirname(spool), "instance.lock"))
    except OSError:  # dossier inaccessible : fenêtre autonome
        gui(initial=paths)
        return 0
    mine = None
    if paths:
        if lock.acquire():  # personne d'autre : on ouvre la fenêtre nous-mêmes
            _spool_clean(spool)
            gui(initial=paths, spool=spool, lock=lock)
            return 0
        mine = _spool_put(spool, paths)
    deadline = time.monotonic() + 5
    while True:
        if lock.acquire():
            if mine is None:
                _spool_clean(spool)
            gui(spool=spool, lock=lock)  # reprend aussi notre dépôt
            return 0
        if mine is None:  # lancement normal alors qu'une fenêtre existe : 2e fenêtre
            gui()
            return 0
        if not os.path.exists(mine) or time.monotonic() > deadline:
            return 0  # la fenêtre ouverte a pris nos fichiers
        time.sleep(0.15)


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--ouvrir":  # menu clic droit de l'Explorateur
        return open_in_window(args[1:])
    if args:
        return cli(args)
    return open_in_window([])


if __name__ == "__main__":
    sys.exit(main())
