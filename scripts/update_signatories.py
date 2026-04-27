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


def fetch_all_submissions(api_key):
    submissions = []
    page = 1
    while True:
        url = f"{API_BASE}/forms/{FORM_ID}/submissions?page={page}&limit=200"
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {api_key}"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Tally API error: {e.code} {e.reason}")

        batch = data.get("data", [])
        if not batch:
            break
        submissions.extend(batch)
        if len(submissions) >= data.get("total", 0):
            break
        page += 1

    return submissions


def get_field(fields, label):
    label_lower = label.lower()
    for f in fields:
        if label_lower in f.get("label", "").lower():
            v = f.get("value")
            return str(v).strip() if v else ""
    return ""


def build_html(submissions):
    items = []
    for sub in submissions:
        fields = sub.get("fields", [])

        # Skip if consent not given
        if not get_field(fields, "souhlas"):
            continue

        jmeno    = get_field(fields, "jméno")
        prijmeni = get_field(fields, "příjmení")
        name     = f"{jmeno} {prijmeni}".strip()

        if not name:
            continue

        instituce = get_field(fields, "instituce")
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

    submissions = fetch_all_submissions(api_key)
    list_html = build_html(submissions)
    count = list_html.count('<li class="signatory">')

    if count == 0:
        print("No consented submissions yet — index.html left unchanged")
    else:
        update_index(list_html, count)
