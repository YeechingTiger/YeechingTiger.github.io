#!/usr/bin/env python3
"""Rebuild the Publications section of index.html from papers.yml.

    python3 build.py
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
    return ", ".join(f'<span class="me">He X{mark}</span>' if n == ME else esc(n) for n in names)


def pub(p, summary=False):
    tag = ' <span class="tag">short paper</span>' if p["type"] == "short" else ""
    out = [f'<div class="pub" data-line="{p.get("line","")}"><div class="t">{esc(p["title"])}</div>',
           f'<div class="a">{authors(p)}</div>',
           f'<div class="v">{esc(p["venue"])}, {p["year"]}{tag}</div>']
    if summary and p.get("summary"):
        out.append(f'<p class="s">{esc(p["summary"])}</p>')
    if p.get("url"):
        out.append(f'<div class="l"><a href="{esc(p["url"])}">Paper</a></div>')
    return "\n".join(out) + "</div>"


sel = sorted([p for p in P if p.get("selected")], key=lambda p: p["selected"])
by_year = OrderedDict()
for p in sorted(P, key=lambda p: (-p["year"], {"journal": 0, "proceedings": 1, "short": 2}[p["type"]])):
    by_year.setdefault(p["year"], []).append(p)

full = []
for y, ps in by_year.items():
    full.append(f'<div class="year">{y}</div>')
    full += [pub(p) for p in ps]

block = f"""<h2 id="publications">Publications</h2>
<p class="note">Selected · * co-first author, † senior author · full list also on <a href="https://orcid.org/0000-0003-0290-8058">ORCID</a></p>

{chr(10).join(pub(p, summary=True) for p in sel)}

<details id="allpubs">
<summary>Show all {len(P)} publications</summary>
<p class="filters">Filter:
<button data-f="" aria-pressed="true">All</button>
<button data-f="nlp">1 Clinical record</button>
<button data-f="trials">2 Trials</button>
<button data-f="rwe">3 Causal evidence</button>
<button data-f="foundations">4 Foundations</button>
<button data-f="workflow">5 Workflows</button></p>
{chr(10).join(full)}
</details>
<script>
(function(){{
  const box=document.getElementById('allpubs'); if(!box) return;
  box.querySelectorAll('.filters button').forEach(btn=>btn.addEventListener('click',()=>{{
    const f=btn.dataset.f;
    box.querySelectorAll('.filters button').forEach(b=>b.setAttribute('aria-pressed',b===btn));
    box.querySelectorAll('.pub').forEach(el=>{{el.hidden=!!f&&el.dataset.line!==f;}});
    box.querySelectorAll('.year').forEach(y=>{{let n=y.nextElementSibling,any=false;
      while(n&&!n.classList.contains('year')){{if(n.classList.contains('pub')&&!n.hidden)any=true;n=n.nextElementSibling;}}
      y.hidden=!any;}});
  }}));
}})();
</script>"""

idx = open("index.html").read()
idx = re.sub(r"<!-- PUBS:START -->.*?<!-- PUBS:END -->",
             lambda m: f"<!-- PUBS:START -->\n{block}\n<!-- PUBS:END -->", idx, flags=re.S)
open("index.html", "w").write(idx)
print(f"index.html: {len(sel)} selected, {len(P)} total")
