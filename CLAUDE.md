# Stojíme s univerzitami – projekt

Statický web studentského hnutí za zachování nezávislosti českých vysokých škol před politickými zásahy.

## Struktura projektu

```
stojimezauniverzitami/
├── index.html              # Hlavní stránka (hero + seznam signatářů)
├── otevreny-dopis.html     # Otevřený dopis vedení Univerzity Karlovy
├── podepiste.html          # Podpisový formulář (Tally.so embed)
├── pravni-informace.html   # Ochrana osobních údajů (GDPR)
├── css/
│   └── style.css           # Sdílený stylesheet
├── js/
│   └── cookie-notice.js    # Dismissible cookie notice (localStorage)
├── assets/
│   ├── logo-mark.svg       # Ikonické logo (48×48)
│   └── logo.svg            # Horizontální logo s wordmarkem (210×48)
├── scripts/
│   └── update_signatories.py  # GitHub Actions skript – stahuje podpisy z Tally API
├── signatories.csv         # Ručně spravovaný seznam dříve sesbíraných podpisů
└── .github/workflows/
    └── update-signatories.yml  # Hodinový cron – aktualizuje seznam signatářů
```

## Technický stack

- **Čistý HTML5 + CSS + minimální JS** – žádný build step, žádný framework
- **Font:** Inter (Google Fonts CDN)
- **Formulář:** Tally.so embed (iframe, form ID: `2Eb7Rb`)
- **Hosting:** GitHub Pages (org: `stojimezauniverzitami`, repo: `web`, branch: `main`)

## Spuštění lokálně

```bash
cd /home/marek/Projects/stojimezauniverzitami
python3 -m http.server 8080
# otevřít http://localhost:8080
```

## Nasazení (GitHub Pages)

Repo: `git@github.com-szu:stojimezauniverzitami/web.git`

SSH je konfigurováno přes host alias `github.com-szu` v `~/.ssh/config`:
```
Host github.com-szu
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_szu
  IdentitiesOnly yes
```

**Postup při každém pushnutí:**
```bash
git pull --rebase origin main && git push origin main
```
Nutné kvůli hodinovému GitHub Actions cronu, který commituje změny v `index.html`.

## Automatická aktualizace signatářů

GitHub Actions workflow (`.github/workflows/update-signatories.yml`) běží každou hodinu:
1. Stáhne všechna podání z Tally API (`TALLY_API_KEY` uložen jako GitHub secret)
2. Filtruje pouze ta se souhlasem (`souhlas` pole)
3. Sloučí s `signatories.csv` (ručně spravovaný seznam starších podpisů)
4. Přepíše sekci `<!-- SIGNATORIES:START -->…<!-- SIGNATORIES:END -->` v `index.html`
5. Aktualizuje počítadlo `<!-- COUNT:START -->N<!-- COUNT:END -->`
6. Commituje a pushuje změny, pokud k nim došlo

Tally API struktura: submissions jsou pod klíčem `responses` (ne `fields`), pole jsou `questionId` a `answer`.

## Design – barevné schéma

Všechny barvy jsou CSS custom properties v `:root` v `css/style.css`:

| Proměnná | Hodnota | Použití |
|---|---|---|
| `--accent` | `#185602` | Tlačítka, odkazy, logo (tmavě zelená) |
| `--accent-hover` | `#1f6e03` | Hover stav |
| `--bg` | `#f7aed0` | Pozadí stránky (tmavší růžová) |
| `--text` | `#111111` | Tělo textu |
| `--text-muted` | `#5a3a4a` | Sekundární text |
| `--border` | `#e888b8` | Oddělovače, okraje |
| `--surface` | `#fde8ee` | Alternativní sekce (světlejší růžová) |

## Přístupnost (a11y)

- Skip link (`Přeskočit na obsah`) na všech stránkách
- `id="main-content"` na všech `<main>` elementech
- `aria-current="page"` na aktivních nav odkazech
- Globální `:focus-visible` styly
- Paginace: focus management po kliknutí, `aria-label` na prev/next, správné `aria-current`
- Tally iframe má `aria-label`
- Dekorativní šipky (`→`, `←`) obaleny `aria-hidden="true"`

## GDPR / právní

- Kontaktní e-mail správce: `stojimesuniverzitami@gmail.com`
- Tally.so je uveden jako datový procesor (čl. 28 GDPR) v `pravni-informace.html`
- Google Fonts a GitHub Pages jsou uvedeny jako třetí strany
- Cookie notice (dismissible banner) na všech stránkách
- Věková hranice 15+ uvedena v `podepiste.html`
- **TODO:** Podepsat DPA s Tally.so (zkontrolovat nastavení účtu nebo kontaktovat support)
- Licence obsahu: **CC BY-SA 4.0**

## Zbývající placeholdery

| Placeholder | Kde | Co doplnit |
|---|---|---|
| `[datum zveřejnění]` | otevreny-dopis.html | Datum podpisu/zveřejnění dopisu |
| `[PDF ke stažení]` | otevreny-dopis.html | Odkaz na PDF verzi dopisu |

## Struktura stránky index.html – signatáři

Signatáři se zobrazují po 30 na stránku (client-side JS paginace).
Paginace se aktivuje pouze při více než 30 záznamech.
Kliknutí na stránku odscrolluje na sekci signatářů a přesune focus na aktivní tlačítko.
Načtení/refresh stránky vždy začíná nahoře.
