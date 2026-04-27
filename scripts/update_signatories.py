#!/usr/bin/env python3
"""Fetch signatories from Tally and update the list in index.html."""

import json
import os
import re
import urllib.request
import urllib.error
from html import escape

FORM_ID = "2Eb7Rb"
API_BASE = "https://api.tally.so"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; signatories-updater/1.0)",
}


def fetch_all(api_key):
    questions = None
    submissions = []
    page = 1
    while True:
        url = f"{API_BASE}/forms/{FORM_ID}/submissions?page={page}&limit=200"
        req = urllib.request.Request(
            url, headers={**HEADERS, "Authorization": f"Bearer {api_key}"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Tally API error: {e.code} {e.reason}\n{body}")

        if questions is None:
            questions = data.get("questions", [])
            print(f"Questions: {[q.get('title') for q in questions]}")

        batch = data.get("submissions", [])
        submissions.extend(batch)
        print(f"Page {page}: {len(batch)} submissions fetched")

        if not data.get("hasMore", False):
            break
        page += 1

    return questions, submissions


def find_value(values, keyword):
    kw = keyword.lower()
    for k, v in values.items():
        if kw in k.lower():
            return v
    return None


def is_truthy(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, str):
        return value.lower() not in ("", "false", "0")
    return bool(value)


def build_html(questions, submissions):
    q_map = {q["id"]: q.get("title", "") for q in questions}

    items = []
    for i, sub in enumerate(submissions):
        fields = sub.get("fields", [])
        values = {q_map.get(f.get("key", ""), f.get("key", "")): f.get("value") for f in fields}

        if i == 0:
            print(f"First submission fields: {list(values.keys())}")
            print(f"First submission values: {values}")

        souhlas = find_value(values, "souhlas")
        if not is_truthy(souhlas):
            print(f"Skipping submission {i}: consent not given (souhlas={souhlas!r})")
            continue

        jmeno    = str(find_value(values, "jméno")    or find_value(values, "jmeno")    or "").strip()
        prijmeni = str(find_value(values, "příjmení") or find_value(values, "prijmeni") or "").strip()
        name = f"{jmeno} {prijmeni}".strip()

        if not name:
            print(f"Skipping submission {i}: no name found")
            continue

        instituce = str(find_value(values, "instituce") or "").strip()
        aff = (
            f'\n            <span class="signatory__affiliation">{escape(instituce)}</span>'
            if instituce else ""
        )
        items.append(
            f'          <li class="signatory">\n'
            f'            <span class="signatory__name">{escape(name)}</span>'
            f'{aff}\n'
            f'          </li>'
        )

    return "\n".join(items)


def update_index(list_html, count):
    with open("index.html", encoding="utf-8") as f:
        content = f.read()

    new_block = (
        f"<!-- SIGNATORIES:START -->\n"
        f"        <ul class=\"signatories__list\">\n"
        f"{list_html}\n"
        f"        </ul>\n"
        f"        <!-- SIGNATORIES:END -->"
    )
    content = re.sub(
        r"<!-- SIGNATORIES:START -->.*?<!-- SIGNATORIES:END -->",
        new_block,
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<!-- COUNT:START -->\d+<!-- COUNT:END -->",
        f"<!-- COUNT:START -->{count}<!-- COUNT:END -->",
        content,
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ {count} signatories written to index.html")


if __name__ == "__main__":
    api_key = os.environ.get("TALLY_API_KEY")
    if not api_key:
        raise SystemExit("TALLY_API_KEY environment variable not set")

    questions, submissions = fetch_all(api_key)
    print(f"Total submissions: {len(submissions)}")

    list_html = build_html(questions, submissions)
    count = list_html.count('<li class="signatory">')

    if count == 0:
        print("No consented submissions found — index.html left unchanged")
    else:
        update_index(list_html, count)
