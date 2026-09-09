from _template import TEMPLATE
"""Render the texture catalogue as a single self-contained HTML page.

Every sprite is embedded as a data URI, so the page is one file that works with no asset directory beside
it and no network. 182 sprites of 16x16 come to well under a megabyte.
"""
import base64, json, pathlib, collections
import faces, namemap

HERE = pathlib.Path(__file__).parent
BLOCKS = HERE / "assets-1.8.9/assets/minecraft/textures/blocks"

FLAG_HELP = {
    "inlaid": "another sprite with a material painted into it — the host is named",
    "masonry": "straight mortar lines: rows or columns that run flat and step away from their neighbours",
    "tiled": "the sprite repeats at a period of 2, 4 or 8",
    "panelled": "few distinct rows or columns — regular structure with no clean period",
    "bevelled": "a chamfered edge: one border lit, another shaded",
    "dithered": "150+ distinct colours in 256 pixels — a generated field",
    "ramped": "12 or fewer colours — drawn from a small hand-picked set",
    "grained-x": "runs visibly across",
    "grained-y": "runs visibly down",
    "flat": "contrast under 8",
    "noise": "irregular all over, with no structure above",
}


def data_uri(name):
    p = BLOCKS / f"{name}.png"
    if not p.exists():
        return None
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def build():
    cat = json.load(open(HERE / "block-texture-catalogue.json"))
    blocks = json.load(open(HERE / "terrain-blocks.json"))

    # Which paintable blocks each texture serves, and on which face.
    serves = collections.defaultdict(list)
    for b in blocks:
        top, side = faces.faces(b["id"], b["data"])
        if top == side:
            serves[top].append((b, "all faces"))
        else:
            serves[top].append((b, "top"))
            serves[side].append((b, "side"))

    cards = []
    for name in sorted(cat):
        v = cat[name]
        uri = data_uri(name)
        if not uri:
            continue
        used = serves.get(name, [])
        chips = "".join(f'<span class="chip f-{f}">{f}</span>' for f in v["flags"])
        host = f'<div class="host">painted on <b>{v["host"]}</b></div>' if v["host"] else ""
        usedby = ""
        if used:
            usedby = '<div class="used">' + "".join(
                f'<span class="use"><i style="background:{b["hex"]}"></i>{b["name"]}'
                f'<em>{where}</em></span>' for b, where in used) + "</div>"
        cards.append(f'''<article class="card" data-flags="{' '.join(v['flags'])}"
   data-name="{name}" data-contrast="{v['contrast']}" data-colours="{v['colours']}"
   data-paint="{1 if used else 0}" data-faces="{' '.join(v['faces'])}">
  <img src="{uri}" alt="{name}" width="72" height="72">
  <div class="meta">
    <h3>{name}</h3>
    <div class="chips">{chips}</div>
    <dl><div><dt>contrast</dt><dd>{v['contrast']}</dd></div>
        <div><dt>colours</dt><dd>{v['colours']}</dd></div>
        <div><dt>grain</dt><dd>{v['grain']}</dd></div>
        <div><dt>faces</dt><dd>{'/'.join(v['faces'])}</dd></div></dl>
    {host}{usedby}
  </div>
</article>''')

    # Blocks that collapse onto one sprite in a bucket.
    def collapse(idx):
        g = collections.defaultdict(list)
        for b in blocks:
            g[faces.faces(b["id"], b["data"])[idx]].append(b)
        return {t: bs for t, bs in g.items() if len(bs) > 1}
    surf, wall = collapse(0), collapse(1)

    def collapse_rows(d, other):
        out = []
        for t, bs in sorted(d.items()):
            names = ", ".join(b["name"] for b in bs)
            splits = [b["name"] for b in bs
                      if not any(b in o for o in other.values())]
            out.append(f"<tr><td><code>{t}</code></td><td>{bs[0]['group']}</td><td>{names}</td>"
                       f"<td>{', '.join(splits) if splits else '—'}</td></tr>")
        return "\n".join(out)

    # Contrast spread inside each tone family.
    fam = collections.defaultdict(list)
    for b in blocks:
        v = cat.get(faces.faces(b["id"], b["data"])[0])
        if v and b["inFamily"]:
            fam[b["group"]].append((b["name"], v["contrast"], b["hex"]))
    fam_rows = []
    for g, xs in sorted(fam.items(), key=lambda kv: -(max(x[1] for x in kv[1]) /
                                                      max(0.1, min(x[1] for x in kv[1])))):
        if len(xs) < 2:
            continue
        lo, hi = min(x[1] for x in xs), max(x[1] for x in xs)
        ratio = hi / max(0.1, lo)
        band = "wide" if ratio >= 6 else "mid" if ratio >= 2 else "tight"
        members = " ".join(
            f'<span class="use"><i style="background:{h}"></i>{n}<em>{c:g}</em></span>'
            for n, c, h in sorted(xs, key=lambda x: x[1]))
        fam_rows.append(f'<tr class="{band}"><td><b>{g}</b></td><td class="num">{lo:g}–{hi:g}</td>'
                        f'<td class="num">{ratio:.1f}×</td><td>{members}</td></tr>')

    flag_rows = "\n".join(
        f'<tr><td><span class="chip f-{k}">{k}</span></td><td>{v}</td></tr>'
        for k, v in FLAG_HELP.items())

    toggles = "".join(f'<button class="tog" data-flag="{f}">{f}</button>' for f in FLAG_HELP)
    return TEMPLATE.format(cards="\n".join(cards), n=len(cards), toggles=toggles,
                           surf=collapse_rows(surf, wall), wall=collapse_rows(wall, surf),
                           fam="\n".join(fam_rows), flags=flag_rows)


if __name__ == "__main__":
    html = build()
    out = HERE / "block-textures.html"
    out.write_text(html)
    print(f"{out}  {len(html)/1024:.0f} KB")
