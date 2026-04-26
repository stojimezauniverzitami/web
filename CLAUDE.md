# Stojíme za univerzitami – projekt

Statický web studentského hnutí za zachování nezávislosti českých vysokých škol před politickými zásahy.

## Struktura projektu

```
stojimezauniverzitami/
├── index.html              # O nás (hlavní stránka)
├── otevreny-dopis.html     # Otevřený dopis
├── podepiste.html          # Petice / podpisový formulář
├── kontakt.html            # Kontakt
├── dekujeme.html           # Poděkování po odeslání formuláře
├── css/
│   └── style.css           # Sdílený stylesheet
├── assets/                 # Loga, obrázky (zatím prázdné)
└── netlify.toml            # Konfigurace nasazení na Netlify
```

## Technický stack

- **Čistý HTML5 + CSS + minimální JS** – žádný build step, žádný framework
- **Font:** Inter (Google Fonts CDN)
- **Formuláře:** Netlify Forms (`data-netlify="true"`) – fungují automaticky po nasazení na Netlify
- **Hosting:** Netlify (free tier)

## Spuštění lokálně

```bash
cd /home/marek/Projects/stojimezauniverzitami
python3 -m http.server 8080
# otevřít http://localhost:8080
```

## Nasazení na Netlify

**Varianta A – drag & drop:**
1. netlify.com → Log in → Sites → "Add new site" → "Deploy manually"
2. Přetáhnout celou složku projektu do prohlížeče

**Varianta B – přes GitHub (doporučeno pro průběžné úpravy):**
1. Pushnut repozitář na GitHub
2. Netlify → "Import from Git" → připojit repo
3. Každý push na `main` se automaticky nasadí

Po nasazení se formuláře (petice + kontakt) automaticky sbírají v Netlify dashboardu pod záložkou **Forms**. Free tier: 100 podání/měsíc. Při vyšším objemu podpisů zvážit [Tally.so](https://tally.so) embed.

## Co je třeba doplnit (placeholdery)

Všechna místa jsou označena hranatými závorkami:

| Placeholder | Kde | Co doplnit |
|---|---|---|
| `[datum zveřejnění]` | otevreny-dopis.html | Datum podpisu/zveřejnění dopisu |
| `[adresát]` | otevreny-dopis.html, podepiste.html | Jméno/funkce adresáta výzvy |
| `[Popis zásahu č. 1–3]` | otevreny-dopis.html | Konkrétní obavy hnutí |
| `[Konkrétní požadavek č. 1–3]` | otevreny-dopis.html | Konkrétní požadavky |
| `[XXX]` / `[XX]` | podepiste.html | Počty podpisů, institucí, měst |
| `[Citát, jméno autora]` | index.html | Citát do pullquote sekce |
| `kontakt@stojimezauniverzitami.cz` | kontakt.html | Skutečný kontaktní e-mail |
| `[PDF ke stažení]` | otevreny-dopis.html | Odkaz na PDF verzi dopisu |
| sociální sítě `href="#"` | kontakt.html | Skutečné URL profilů |

## Design

- **Accent barva:** `#1d3461` (tmavě modrá, akademická)
- **Pozadí:** `#ffffff`, **Text:** `#111111`
- CSS custom properties jsou v `:root` v `css/style.css` – barvy lze snadno změnit na jednom místě
- Responzivní: hamburger menu pod 640 px, grid přechází na 1 sloupec pod 768 px
- Aktivní stránka v navigaci: třída `active` na příslušném `<a>` tagu (nastavena ručně v každém HTML souboru)

## Logo

Logo zatím neexistuje. Až bude připraveno, přidat do `assets/` a doplnit do `.nav__brand` místo textového názvu.
