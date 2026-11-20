#!/usr/bin/env python3
"""Rebuild the publication lists from papers.yml.

    python3 build.py

Writes the "Selected publications" block in index.html (between the PUBS markers)
and the full list in publications.html.
"""
import html, re, yaml
from collections import OrderedDict

ME = "He X"
P = yaml.safe_load(open("papers.yml"))
esc = html.escape


def authors(p):
    names = [a.strip() for a in p["authors"].split(",")]
    mark = {"cofirst": "*", "senior": "†"}.get(p["role"], "")
    if len(names) > 12:  # keep long consortium lists readable
        i = names.index(ME) if ME in names else -1
        keep = names[:6]
        if i >= 6:
            keep += ["…", names[i]] if i < len(names) - 1 else ["…"]
        if names[-1] not in keep:
            keep += (["…"] if keep[-1] != "…" else []) + [names[-1]]
        names = keep
    out = []
    for n in names:
        if n == ME:
            out.append(f'<span class="me">He X{mark}</span>')
        else:
            out.append(esc(n))
    return ", ".join(out)


def pub(p):
    title = esc(p["title"])
    if p.get("url"):
        title = f'<a href="{esc(p["url"])}">{title}</a>'
    tag = ' <span class="tag">short paper</span>' if p["type"] == "short" else ""
    led = "yes" if p["role"] in ("first", "cofirst", "senior") else "no"
    return (f'<div class="pub" data-led="{led}">{title}<br>\n{authors(p)}<br>'
            f'<span class="v">{esc(p["venue"])}, {p["year"]}</span>{tag}</div>')


# ---- homepage block -------------------------------------------------------
sel = sorted([p for p in P if p.get("selected")], key=lambda p: p["selected"])
block = ("<h2>Selected publications</h2>\n\n" + "\n\n".join(pub(p) for p in sel) +
         '\n\n<p class="refs" style="margin-top:8px">* co-first author, † senior author. '
         f'<a href="publications.html">All {len(P)} publications →</a></p>')
idx = open("index.html").read()
idx = re.sub(r"<!-- PUBS:START -->.*?<!-- PUBS:END -->",
             lambda m: f"<!-- PUBS:START -->\n{block}\n<!-- PUBS:END -->", idx, flags=re.S)
open("index.html", "w").write(idx)

# ---- full list ------------------------------------------------------------
by_year = OrderedDict()
for p in sorted(P, key=lambda p: (-p["year"], {"journal": 0, "proceedings": 1, "short": 2}[p["type"]])):
    by_year.setdefault(p["year"], []).append(p)
n_led = sum(p["role"] in ("first", "cofirst", "senior") for p in P)

body = []
for y, ps in by_year.items():
    empty = "" if any(p["role"] != "middle" for p in ps) else " empty"
    body.append(f'<div class="year{empty}">{y}</div>')
    body += [pub(p) for p in ps]

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Publications – Xing He</title>
<meta name="description" content="Publications of Xing He, Indiana University School of Medicine.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
<a class="back" href="./">← Xing He</a>
<header style="margin-top:20px">
  <h1>Publications</h1>
</header>
<p class="legend">{len(P)} papers · * co-first author, † senior author ·
<button id="led" aria-pressed="false">show only papers I led ({n_led})</button></p>

{chr(10).join(body)}

<p class="refs" style="margin-top:24px">Also on <a href="https://orcid.org/0000-0003-0290-8058">ORCID</a>.</p>
<footer>Updated {__import__("datetime").date.today():%B %Y}</footer>
</main>
<script>
const b=document.getElementById('led');
b.addEventListener('click',()=>{{const on=document.body.classList.toggle('led');b.setAttribute('aria-pressed',on);b.textContent=on?'show all papers':'show only papers I led ({n_led})';}});
</script>
</body>
</html>
"""
open("publications.html", "w").write(page)
print(f"index.html: {len(sel)} selected · publications.html: {len(P)} papers, {n_led} led")
