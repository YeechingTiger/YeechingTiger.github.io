#!/usr/bin/env python3
"""Rebuild the Publications section of index.html from papers.yml.

    python3 build.py

Each paper may have an optional `image:` (path under images/thumbs/) and `summary:`.
"""
import html, os, re, yaml

ME = "He X"
P = yaml.safe_load(open("papers.yml"))
esc = html.escape
SCHOLAR = "https://scholar.google.com/citations?user=LN0Utm0AAAAJ&amp;hl=en"
ORCID = "https://orcid.org/0000-0003-0290-8058"


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


def pub(p):
    tag = ' <span class="tag">short paper</span>' if p["type"] == "short" else ""
    title = esc(p["title"])
    if p.get("url"):
        title = f'<a href="{esc(p["url"])}">{title}</a>'
    img = p.get("image")
    media = ""
    if img and os.path.exists(img):
        media = f'<div class="pub-media"><img src="{esc(img)}" alt="" loading="lazy" decoding="async"></div>\n'
    gname = {"nlp": "Clinical record", "trials": "Trials", "rwe": "Causal evidence", "foundations": "Foundations", "workflow": "Workflows"}.get(p.get("line"), "")
    glabel = f' <span class="gl g-{p.get("line")}">{gname}</span>' if gname else ""
    body = [f'<div class="t">{title}</div>',
            f'<div class="a">{authors(p)}</div>',
            f'<div class="v">{esc(p["venue"])}, {p["year"]}{tag}{glabel}</div>']
    if p.get("summary"):
        body.append(f'<p class="s">{esc(p["summary"])}</p>')
    if p.get("url"):
        body.append(f'<div class="l"><a href="{esc(p["url"])}">Paper</a></div>')
    cls = "pub has-media" if media else "pub"
    return (f'<article class="{cls}" data-line="{p.get("line","")}">\n{media}'
            f'<div class="pub-body">\n' + "\n".join(body) + "\n</div></article>")


order = {"journal": 0, "proceedings": 1, "short": 2}
papers = sorted(P, key=lambda p: (-p["year"], order[p["type"]]))
journal = [p for p in papers if p["type"] == "journal"]
conference = [p for p in papers if p["type"] != "journal"]
n_img = sum(1 for p in papers if p.get("image") and os.path.exists(p["image"]))

block = f"""<h2 id="publications">Publications</h2>
<p class="note">* co-first author, † senior author · also on <a href="{SCHOLAR}">Google Scholar</a> and <a href="{ORCID}">ORCID</a></p>
<p class="filters" id="pubfilters">Filter:
<button data-f="" aria-pressed="true">All</button>
<button data-f="nlp" class="g-nlp">1 Clinical record</button>
<button data-f="trials" class="g-trials">2 Trials</button>
<button data-f="rwe" class="g-rwe">3 Causal evidence</button>
<button data-f="foundations" class="g-foundations">4 Foundations</button>
<button data-f="workflow" class="g-workflow">5 Workflows</button></p>
<div class="pub-list" id="publist">
<h3 class="pub-group">Journal articles <span class="count">({len(journal)})</span></h3>
{chr(10).join(pub(p) for p in journal)}
<h3 class="pub-group">Conference papers <span class="count">({len(conference)})</span></h3>
{chr(10).join(pub(p) for p in conference)}
</div>
<script>
(function(){{
  const bar=document.getElementById('pubfilters'), list=document.getElementById('publist'); if(!bar||!list) return;
  bar.querySelectorAll('button').forEach(btn=>btn.addEventListener('click',()=>{{
    const f=btn.dataset.f;
    bar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b===btn));
    list.querySelectorAll('.pub').forEach(el=>{{el.hidden=!!f&&el.dataset.line!==f;}});
    list.querySelectorAll('.pub-group').forEach(h=>{{let n=h.nextElementSibling,c=0;
      while(n&&!n.classList.contains('pub-group')){{if(n.classList.contains('pub')&&!n.hidden)c++;n=n.nextElementSibling;}}
      h.hidden=c===0; h.querySelector('.count').textContent='('+c+')';}});
  }}));
}})();
</script>"""

idx = open("index.html").read()
idx = re.sub(r"<!-- PUBS:START -->.*?<!-- PUBS:END -->",
             lambda m: f"<!-- PUBS:START -->\n{block}\n<!-- PUBS:END -->", idx, flags=re.S)
open("index.html", "w").write(idx)
print(f"index.html: {len(papers)} papers, {n_img} with figures")
