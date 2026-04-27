#!/usr/bin/env python3
"""Fetch signatories from Tally, merge with signatories.csv, update index.html."""

import csv
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


def load_csv_signatories(path="signatories.csv"):
    result = []
    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if not row:
                    continue
                name = row[0].strip() if len(row) > 0 else ""
                instituce = row[1].strip() if len(row) > 1 else ""
                if name:
                    result.append({"name": name, "instituce": instituce})
    except FileNotFoundError:
        print("signatories.csv not found, skipping manual list")
    print(f"CSV signatories loaded: {len(result)}")
    return result


def load_tally_signatories(questions, submissions):
    q_map = {q["id"]: q.get("title", "") for q in questions}
    result = []

    for i, sub in enumerate(submissions):
        responses = sub.get("responses", [])
        values = {
            q_map.get(r.get("questionId", ""), r.get("questionId", "")): r.get("answer")
            for r in responses
        }

        souhlas = find_value(values, "souhlas")
        if not is_truthy(souhlas):
            print(f"Skipping Tally submission {i}: consent not given (souhlas={souhlas!r})")
            continue

        jmeno    = str(find_value(values, "jméno")    or find_value(values, "jmeno")    or "").strip()
        prijmeni = str(find_value(values, "příjmení") or find_value(values, "prijmeni") or "").strip()
        name = f"{jmeno} {prijmeni}".strip()

        if not name:
            print(f"Skipping Tally submission {i}: no name found")
            continue

        instituce = str(find_value(values, "instituce") or "").strip()
        result.append({"name": name, "instituce": instituce})

    print(f"Tally signatories with consent: {len(result)}")
    return result


def merge(csv_list, tally_list):
    seen = set()
    merged = []
    for entry in csv_list + tally_list:
        key = entry["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            merged.append(entry)
    return merged


def render_html(signatories):
    items = []
    for entry in signatories:
        aff = (
            f'\n            <span class="signatory__affiliation">{escape(entry["instituce"])}</span>'
            if entry["instituce"] else ""
        )
        items.append(
            f'          <li class="signatory">\n'
            f'            <span class="signatory__name">{escape(entry["name"])}</span>'
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
    print(f"Total Tally submissions: {len(submissions)}")

    csv_list   = load_csv_signatories()
    tally_list = load_tally_signatories(questions, submissions)
    all_sigs   = merge(csv_list, tally_list)
    print(f"Total after merge: {len(all_sigs)}")

    if not all_sigs:
        print("No signatories found — index.html left unchanged")
    else:
        update_index(render_html(all_sigs), len(all_sigs))
