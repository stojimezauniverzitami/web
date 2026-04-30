#!/usr/bin/env python3
"""
Generate English HTML files from translations.yaml.

Usage:
    cd /home/marek/Projects/stojimezauniverzitami
    python3 scripts/build_en.py

Output:
    en/index.html
    en/otevreny-dopis.html
    en/podepiste.html
    en/pravni-informace.html
    en/js/cookie-notice.js

Requirements:
    pip install pyyaml beautifulsoup4
"""

import os
import re
import yaml
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).parent.parent
OUT  = ROOT / "en"


def load_translations():
    with open(ROOT / "translations.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def t(tr, section, key):
    return tr[section][key]["en"]


def set_html(el, html_str):
    """Replace an element's innerHTML."""
    el.clear()
    fragment = BeautifulSoup(html_str, "html.parser")
    for child in list(fragment.children):
        el.append(child.__copy__())


def replace_text_by_prefix(elements, mapping):
    """
    Given a list of BS4 elements and a dict {cs_prefix: (en_value, is_html)},
    replace each element whose stripped text starts with a matching prefix.
    """
    for el in elements:
        text = el.get_text(strip=True)
        for cs_prefix, (en_value, is_html) in mapping.items():
            if text.startswith(cs_prefix[:60]):
                if is_html:
                    set_html(el, en_value)
                else:
                    el.string = en_value
                break


def translate_shared(soup, tr):
    """Apply nav, footer, and meta translations common to all pages."""
    html_tag = soup.find("html")
    if html_tag:
        html_tag["lang"] = "en"

    skip = soup.select_one("a.skip-link")
    if skip:
        skip.string = t(tr, "shared", "skip_link")

    nav = soup.select_one("nav.nav")
    if nav:
        nav["aria-label"] = t(tr, "shared", "nav_aria")

    brand = soup.select_one("a.nav__brand")
    if brand:
        brand.clear()
        brand.append(NavigableString(t(tr, "shared", "nav_brand")))

    toggle = soup.select_one("button.nav__toggle")
    if toggle:
        toggle["aria-label"] = t(tr, "shared", "nav_toggle")

    nav_link_map = {
        "Otevřený dopis": t(tr, "shared", "nav_open_letter"),
        "Podepište":      t(tr, "shared", "nav_sign"),
        "Ochrana údajů":  t(tr, "shared", "nav_privacy"),
    }
    for a in soup.select(".nav__list a"):
        text = a.get_text(strip=True)
        if text in nav_link_map:
            a.string = nav_link_map[text]

    footer_span = soup.select_one(".footer__inner > span")
    if footer_span:
        cc_link = footer_span.find("a")
        if cc_link:
            footer_span.clear()
            footer_span.append(NavigableString(t(tr, "shared", "footer_license") + " "))
            footer_span.append(cc_link.__copy__())

    footer_link_map = {
        "Otevřený dopis": t(tr, "shared", "nav_open_letter"),
        "Podepište":      t(tr, "shared", "nav_sign"),
        "Ochrana údajů":  t(tr, "shared", "nav_privacy"),
    }
    for a in soup.select(".footer__links a"):
        text = a.get_text(strip=True)
        if text in footer_link_map:
            a.string = footer_link_map[text]

    # Flip the language toggle: CS current + EN link → CS link + EN current
    lang_li = soup.select_one("li.lang-switch")
    if lang_li:
        en_link = lang_li.select_one("a[hreflang='en']")
        if en_link:
            en_href = en_link.get("href", "en/index.html")
            filename = en_href[3:]           # "en/index.html" → "index.html"
            cs_href  = "../" + filename      # → "../index.html"

            lang_li.clear()
            cs_a = soup.new_tag("a", href=cs_href, hreflang="cs")
            cs_a["class"] = "lang-switch__link"
            cs_a["lang"] = "cs"
            cs_a.string = "CS"
            sep = soup.new_tag("span")
            sep["aria-hidden"] = "true"
            sep.string = "/"
            en_span = soup.new_tag("span")
            en_span["class"] = "lang-switch__current"
            en_span.string = "EN"
            lang_li.append(cs_a)
            lang_li.append(sep)
            lang_li.append(en_span)


def fix_paths(soup):
    """Rewrite relative asset paths so they work from inside en/.
    css/, assets/, fonts/ live in parent → ../
    js/cookie-notice.js is translated into en/js/ → keep as js/
    """
    for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
        for el in soup.find_all(tag, **{attr: True}):
            val = el[attr]
            if val and not val.startswith(("http", "//", "#", "mailto", "data")):
                if val == "js/cookie-notice.js":
                    pass  # translated copy lives in en/js/
                else:
                    el[attr] = "../" + val


# ── Per-page translators ──────────────────────────────────────────────────────

def translate_index(soup, tr):
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        meta_desc["content"] = t(tr, "index", "meta_description")
    title = soup.find("title")
    if title:
        title.string = t(tr, "index", "meta_title")

    hero_title = soup.select_one("h1.hero__title")
    if hero_title:
        set_html(hero_title, t(tr, "index", "hero_title_html"))

    hero_sub = soup.select_one("p.hero__subtitle")
    if hero_sub:
        set_html(hero_sub, t(tr, "index", "hero_subtitle_html"))

    for a in soup.select(".hero__actions a"):
        href = a.get("href", "")
        if "podepiste" in href:
            a.string = t(tr, "index", "hero_btn_sign")
        elif "otevreny" in href:
            a.string = t(tr, "index", "hero_btn_letter")

    sig_label = soup.select_one("p.section__label")
    if sig_label:
        count_span = sig_label.find("span", id="sig-count")
        note_span  = sig_label.find("span", class_="sig-count__note")
        if count_span and note_span:
            note_span["data-tooltip"] = t(tr, "index", "sig_tooltip")
            sig_label.clear()
            sig_label.append(NavigableString(t(tr, "index", "sig_label_prefix")))
            sig_label.append(count_span.__copy__())
            sig_label.append(NavigableString(t(tr, "index", "sig_label_suffix") + " "))
            note_span_copy = note_span.__copy__()
            sig_label.append(note_span_copy)




def translate_sign(soup, tr):
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        meta_desc["content"] = t(tr, "sign", "meta_description")
    title = soup.find("title")
    if title:
        title.string = t(tr, "sign", "meta_title")

    label = soup.select_one("p.page-header__label")
    if label:
        label.string = t(tr, "sign", "header_label")

    h1 = soup.select_one("h1.page-header__title")
    if h1:
        h1.string = t(tr, "sign", "header_title")

    lead = soup.select_one("p.page-header__lead")
    if lead:
        lead.string = t(tr, "sign", "header_lead")

    iframe = soup.find("iframe")
    if iframe:
        iframe["aria-label"] = t(tr, "sign", "iframe_aria")
        iframe["title"]      = t(tr, "sign", "iframe_title")

    note = soup.select_one("p.form__note")
    if note:
        set_html(note, t(tr, "sign", "note_html"))


def translate_privacy(soup, tr):
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        meta_desc["content"] = t(tr, "privacy", "meta_description")
    title = soup.find("title")
    if title:
        title.string = t(tr, "privacy", "meta_title")

    label = soup.select_one("p.page-header__label")
    if label:
        label.string = t(tr, "privacy", "header_label")

    h1 = soup.select_one("h1.page-header__title")
    if h1:
        set_html(h1, t(tr, "privacy", "header_title_html"))

    lead = soup.select_one("p.page-header__lead")
    if lead:
        lead.string = t(tr, "privacy", "header_lead")

    legal = soup.select_one("div.legal")
    if not legal:
        return

    h2_map = {
        "1. Správce": (t(tr, "privacy", "h2_1"), False),
        "2. Jaké":    (t(tr, "privacy", "h2_2"), False),
        "3. Účel":    (t(tr, "privacy", "h2_3"), False),
        "4. Doba":    (t(tr, "privacy", "h2_4"), False),
        "5. Příjemci": (t(tr, "privacy", "h2_5"), False),
        "6. Vaše":    (t(tr, "privacy", "h2_6"), False),
        "7. Zabezpečení": (t(tr, "privacy", "h2_7"), False),
        "8. Změny":   (t(tr, "privacy", "h2_8"), False),
    }
    replace_text_by_prefix(legal.find_all("h2"), h2_map)

    h3_map = {
        "Petice": (t(tr, "privacy", "h3_petition"), False),
        "Zveřejnění": (t(tr, "privacy", "h3_publication"), False),
    }
    replace_text_by_prefix(legal.find_all("h3"), h3_map)

    para_map = {
        "Správcem osobních údajů": (t(tr, "privacy", "p_controller_html"), True),
        "V rámci podpisové petice": (t(tr, "privacy", "p_data_intro"), False),
        "Tato webová stránka neobsahuje": (t(tr, "privacy", "p_no_analytics"), False),
        "Věková hranice":  (t(tr, "privacy", "p_age_html"), True),
        "Osobní údaje zadané v podpisovém": (t(tr, "privacy", "p_petition_html"), True),
        "Jméno a příjmení signatáře": (t(tr, "privacy", "p_publication"), False),
        "Chcete-li své jméno": (t(tr, "privacy", "p_removal"), False),
        "Osobní údaje uchováváme": (t(tr, "privacy", "p_retention"), False),
        "Údaje nejsou předávány": (t(tr, "privacy", "p_recipients"), False),
        "Jako subjekt údajů": (t(tr, "privacy", "p_rights"), False),
        "Svá práva uplatňujte": (t(tr, "privacy", "p_exercise_html"), True),
        "Máte rovněž právo podat": (t(tr, "privacy", "p_supervisory_html"), True),
        "Přijímáme přiměřená": (t(tr, "privacy", "p_security"), False),
        "Tyto zásady mohou být": (t(tr, "privacy", "p_changes_html"), True),
    }
    replace_text_by_prefix(legal.find_all("p"), para_map)

    li_map = {
        "Jméno a příjmení":  (t(tr, "privacy", "li_name"), False),
        "E-mailová adresa":  (t(tr, "privacy", "li_email"), False),
        "Instituce (nepovinné)": (t(tr, "privacy", "li_institution"), False),
        "Role – studující":  (t(tr, "privacy", "li_role"), False),
        "Vzkaz (nepovinné)": (t(tr, "privacy", "li_message"), False),
        "Adresátovi otevřeného dopisu": (t(tr, "privacy", "li_addressee_html"), True),
        "Tally.so –":        (t(tr, "privacy", "li_tally_html"), True),
        "Google LLC":        (t(tr, "privacy", "li_google_html"), True),
        "GitHub, Inc.":      (t(tr, "privacy", "li_github_html"), True),
        "na přístup":        (t(tr, "privacy", "li_access_html"), True),
        "na opravu":         (t(tr, "privacy", "li_rectification_html"), True),
        "na výmaz":          (t(tr, "privacy", "li_erasure_html"), True),
        "na omezení zpracování": (t(tr, "privacy", "li_restriction_html"), True),
        "na přenositelnost": (t(tr, "privacy", "li_portability_html"), True),
        "vznést námitku":    (t(tr, "privacy", "li_objection_html"), True),
        "odvolat souhlas":   (t(tr, "privacy", "li_withdraw_html"), True),
    }
    replace_text_by_prefix(legal.find_all("li"), li_map)


def build_cookie_js(tr):
    text_html = t(tr, "shared", "cookie_text_html")
    btn_text  = t(tr, "shared", "cookie_btn")
    btn_aria  = t(tr, "shared", "cookie_btn_aria")
    aria_label = t(tr, "shared", "cookie_aria")

    with open(ROOT / "js" / "cookie-notice.js", encoding="utf-8") as f:
        src = f.read()

    src = src.replace(
        "Informace o cookies", aria_label
    ).replace(
        "'<p>Web používá <strong>Google Fonts</strong> (sdílení IP s Googlem) a formulář ' +\n    '<strong>Tally.so</strong>, který může ukládat cookies. ' +\n    '<a href=\"pravni-informace.html\">Více informací</a></p>'",
        f"'<p>{text_html}</p>'"
    ).replace(
        "Potvrdit a zavřít upozornění", btn_aria
    ).replace(
        ">Rozumím<", f">{btn_text}<"
    )

    return src


# ── Pages config ──────────────────────────────────────────────────────────────

PAGES = [
    ("index.html",            translate_index),
    # en/otevreny-dopis.html is edited manually — not generated by this script
    ("podepiste.html",        translate_sign),
    ("pravni-informace.html", translate_privacy),
]


def main():
    tr = load_translations()

    OUT.mkdir(exist_ok=True)
    (OUT / "js").mkdir(exist_ok=True)

    for filename, page_fn in PAGES:
        src = ROOT / filename
        print(f"  {filename} → en/{filename}")
        html = src.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        translate_shared(soup, tr)
        page_fn(soup, tr)
        fix_paths(soup)

        (OUT / filename).write_text(str(soup), encoding="utf-8")

    print("  cookie-notice.js → en/js/cookie-notice.js")
    (OUT / "js" / "cookie-notice.js").write_text(
        build_cookie_js(tr), encoding="utf-8"
    )

    print(f"\nDone — English files written to {OUT}/")


if __name__ == "__main__":
    main()
