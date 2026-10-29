# PDF Compress

Utilitaire portable (Windows / Linux) pour compresser des PDF. Un seul fichier, aucune installation.

## Utilisation

**Interface graphique** : double-cliquez sur `pdfcompress` (Linux) ou `pdfcompress.exe` (Windows).
Ajoutez des PDF, choisissez le niveau, cliquez sur *Compresser*. Les fichiers compresses sont
enregistres a cote des originaux avec le suffixe `_compresse` (ou dans le dossier choisi).

**Ligne de commande** :

```
pdfcompress fichier.pdf                       # niveau moyen -> fichier_compresse.pdf
pdfcompress a.pdf b.pdf -n forte -o sortie/   # plusieurs fichiers vers un dossier
pdfcompress scan.pdf -n extreme -g -o petit.pdf
```

| Niveau   | Images      | Usage                         |
|----------|-------------|-------------------------------|
| faible   | 200 dpi, JPEG 85 | impression, meilleure qualite |
| moyenne  | 130 dpi, JPEG 70 | recommande                    |
| forte    | 90 dpi, JPEG 50  | ecran, e-mail                 |
| extreme  | 72 dpi, JPEG 35  | plus petit possible           |

`-g` convertit les images en niveaux de gris.

Ce qui est fait : reechantillonnage et recompression des images, sous-ensemble des polices,
suppression des objets inutilises et des metadonnees XML. Le texte reste du texte (selectionnable).
Si le resultat n'est pas plus petit, l'original est copie tel quel. Les PDF proteges par mot de
passe sont refuses. L'original n'est jamais modifie.

## Construire les executables

- **Windows** : installer Python 3.10+ (python.org), puis double-cliquer sur `build_windows.bat`.
- **Linux** : `sudo apt install python3-tk python3-venv binutils` puis `./build_linux.sh`.
- **Les deux automatiquement** : pousser ce dossier sur GitHub et creer un tag `v1.0.0` ;
  `.github/workflows/build.yml` construit les executables a chaque push sur `main` et les publie
  dans la release `v<VERSION>` (version lue dans `pdfcompress.py`).

PyInstaller ne fait pas de compilation croisee : l'executable Windows doit etre construit sous Windows
(ou par la CI).

## Antivirus

Les executables PyInstaller sont parfois signales a tort (faux positifs). Mesures prises :

- **Bootloader recompile** depuis les sources (le bootloader precompile est partage par de nombreux
  logiciels malveillants, c'est la premiere cause de detection).
- **Pas de compression UPX**, elle aussi typique des logiciels malveillants.
- **Fiche d'identite Windows** (editeur, description, version : `version_info.txt`).
- **Version dossier** `pdfcompress-windows-dossier.zip` : elle ne se decompresse pas au lancement et
  est beaucoup moins souvent signalee que le `.exe` unique.
- **Empreintes SHA-256** publiees avec chaque release (`SHA256SUMS.txt`).

Ce qui reste hors de portee sans frais : seule une **signature de code** (certificat payant, ou
SignPath gratuit pour les projets open source) supprime l'avertissement SmartScreen "editeur inconnu".
En cas de faux positif, le fichier peut etre soumis a Microsoft :
https://www.microsoft.com/wdsi/filesubmission

Licence : PyMuPDF est sous AGPL-3.0 ; redistribuer l'outil implique de fournir ce code source.
