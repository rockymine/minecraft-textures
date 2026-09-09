TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>1.8.9 Block Textures</title>
<style>
:root{{
  --bg:#f7f6f3; --panel:#fff; --ink:#1b1a18; --dim:#6a6660; --line:#e2ded7;
  --accent:#8a5a2b; --tight:#3f7a4a; --mid:#9a7a20; --wide:#a24a3a;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{
  --bg:#16151a; --panel:#1e1d23; --ink:#eceaf2; --dim:#9b96a6; --line:#312f39;
  --accent:#d9a066; --tight:#7fc48f; --mid:#d9bb62; --wide:#e08a78;
}}}}
:root[data-theme=dark]{{
  --bg:#16151a; --panel:#1e1d23; --ink:#eceaf2; --dim:#9b96a6; --line:#312f39;
  --accent:#d9a066; --tight:#7fc48f; --mid:#d9bb62; --wide:#e08a78;
}}
*{{box-sizing:border-box}}
[hidden]{{display:none!important}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 20px 80px}}
header{{padding:56px 0 28px;border-bottom:1px solid var(--line);margin-bottom:28px}}
h1{{margin:0 0 10px;font-size:30px;letter-spacing:-.02em;font-weight:650}}
h2{{margin:44px 0 6px;font-size:20px;letter-spacing:-.01em;font-weight:640}}
h2:first-of-type{{margin-top:8px}}
p{{margin:0 0 14px;max-width:74ch;color:var(--dim)}}
p.lead{{color:var(--ink)}}
code{{font-family:var(--mono);font-size:.9em;background:color-mix(in srgb,var(--ink) 7%,transparent);
  padding:1px 5px;border-radius:4px}}
a{{color:var(--accent)}}
.bar{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:12px 0;margin-bottom:20px;
  display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.tog{{font:inherit;font-size:12px;padding:4px 10px;border:1px solid var(--line);border-radius:999px;
  background:var(--panel);color:var(--dim);cursor:pointer}}
.tog[aria-pressed=true]{{background:var(--accent);border-color:var(--accent);color:#fff}}
input[type=search],select{{font:inherit;font-size:13px;padding:5px 10px;border:1px solid var(--line);
  border-radius:8px;background:var(--panel);color:var(--ink)}}
.count{{font-size:12px;color:var(--dim);margin-left:auto}}
.grid{{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(310px,1fr))}}
.card{{display:flex;gap:14px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:12px}}
.card img{{image-rendering:pixelated;border-radius:6px;border:1px solid var(--line);
  align-self:flex-start;flex:none}}
.meta{{min-width:0;flex:1}}
.card h3{{margin:0 0 6px;font-size:13px;font-family:var(--mono);font-weight:600;
  word-break:break-all;letter-spacing:-.01em}}
.chips{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}}
.chip{{font-size:10.5px;padding:1.5px 7px;border-radius:999px;font-weight:600;letter-spacing:.02em;
  background:color-mix(in srgb,var(--ink) 9%,transparent);color:var(--dim)}}
.f-inlaid{{background:color-mix(in srgb,var(--wide) 22%,transparent);color:var(--wide)}}
.f-masonry,.f-tiled{{background:color-mix(in srgb,var(--accent) 22%,transparent);color:var(--accent)}}
.f-bevelled{{background:color-mix(in srgb,var(--mid) 22%,transparent);color:var(--mid)}}
.f-dithered,.f-ramped{{background:color-mix(in srgb,var(--tight) 20%,transparent);color:var(--tight)}}
dl{{display:flex;flex-wrap:wrap;gap:2px 14px;margin:0 0 6px;font-size:11.5px}}
dl div{{display:flex;gap:5px}} dt{{color:var(--dim)}} dd{{margin:0;font-family:var(--mono);font-weight:600}}
.host{{font-size:11.5px;color:var(--dim);margin-top:4px}}
.host b{{font-family:var(--mono);color:var(--ink);font-weight:600}}
.used{{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;
  padding-top:8px;border-top:1px dashed var(--line)}}
.use{{display:inline-flex;align-items:center;gap:4px;font-size:11px;color:var(--dim)}}
.use i{{width:9px;height:9px;border-radius:2px;border:1px solid rgba(128,128,128,.45);flex:none}}
.use em{{font-style:normal;opacity:.65;font-size:10px}}
.tbl{{width:100%;border-collapse:collapse;margin:10px 0 6px;font-size:13.5px;
  display:block;overflow-x:auto}}
.tbl th{{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--dim);border-bottom:1px solid var(--line);padding:7px 12px 7px 0;font-weight:600}}
.tbl td{{border-bottom:1px solid var(--line);padding:9px 12px 9px 0;vertical-align:top}}
.tbl td.num{{font-family:var(--mono);white-space:nowrap}}
tr.wide td:first-child b{{color:var(--wide)}}
tr.mid td:first-child b{{color:var(--mid)}}
tr.tight td:first-child b{{color:var(--tight)}}
.note{{border-left:3px solid var(--accent);padding:2px 0 2px 16px;margin:18px 0;
  color:var(--ink);max-width:74ch}}
footer{{margin-top:56px;padding-top:20px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--dim)}}
</style></head><body><div class="wrap">
<header>
<h1>Minecraft 1.8.9 block textures, and what they are made of</h1>
<p class="lead">Every texture a full cube wears in 1.8.9 — {n} of them — described by where it sits on the
block, how it is drawn, and what it reads as. The face layout is read from the jar's own block models,
which are the authority. Everything else is measured off the pixels.</p>
<p>Sprites are 16&times;16 and shown at 72px, so what you see is the pixel grid rather than a filtered
image. Where a texture serves a block the studio paints terrain with, that block is listed on the card
with its palette swatch and the face it appears on.</p>
</header>

<h2>Why a mean colour is not enough</h2>
<p>The studio offers an agent one mean RGB per block. Inside a tone family that number is nearly constant
while the textures are not: <code>stone</code> and <code>cobblestone</code> are four counts apart per
channel and differ by a factor of 2.5 in contrast. <code>andesite</code> and its polished variant are four
counts apart <em>and</em> close in contrast — what separates those two is the bevel, not the noise. That is
why this page carries construction flags and not only a variance number.</p>

<div class="bar">
  <input type="search" id="q" placeholder="search a texture or block…" size="22">
  <span id="togs">{toggles}</span>
  <select id="sort">
    <option value="name">by name</option>
    <option value="contrast">by contrast</option>
    <option value="colours">by colours</option>
  </select>
  <button class="tog" id="paintonly" data-flag="">terrain palette only</button>
  <span class="count" id="count"></span>
</div>

<div class="grid" id="grid">
{cards}
</div>

<h2>The same block, seen from two sides</h2>
<p>A terrain theme paints in buckets, and two of them look at different faces: the <b>surface</b> bucket
writes what a player sees from above, the <b>wall</b> bucket what they see from the side. A block whose top
and sides are one sprite answers both the same way. A block whose faces differ does not — so two blocks can
be interchangeable in one bucket and quite distinct in the other.</p>
<div class="note"><b>Sandstone is the case worth knowing.</b> Sandstone, smooth sandstone and the double
sandstone slab all wear <code>sandstone_top</code>. Put two of them in a <em>surface</em> pattern and the
pattern has one block in it, whatever the document says. Put them in a <em>wall</em> pattern and smooth
sandstone splits off with its own sprite, and the pattern is real.</div>
<table class="tbl"><thead><tr><th>sprite</th><th>family</th><th>blocks that collapse onto it</th>
<th>splits off in the other bucket</th></tr></thead>
<tbody>{surf}</tbody></table>
<p style="margin-top:18px">And the same read taken on the side face:</p>
<table class="tbl"><thead><tr><th>sprite</th><th>family</th><th>blocks that collapse onto it</th>
<th>splits off in the other bucket</th></tr></thead>
<tbody>{wall}</tbody></table>

<h2>A tone family is a colour, not a texture</h2>
<p>The palette groups blocks by the ground they read as, which is a statement about hue. It says nothing
about grain — and inside one family the contrast can span a factor of seventeen. Two blocks drawn from
<code>loam</code> can be a flat stained clay and a coarse soul sand, which do not read as one ground at any
distance. The families at the bottom of this table are texturally coherent; the ones at the top are a
colour bucket holding several different materials.</p>
<table class="tbl"><thead><tr><th>family</th><th>contrast</th><th>spread</th>
<th>members, least to most textured</th></tr></thead>
<tbody>{fam}</tbody></table>

<h2>What the flags mean</h2>
<table class="tbl"><thead><tr><th>flag</th><th>what it means</th></tr></thead>
<tbody>{flags}</tbody></table>
<p style="margin-top:16px">Flags are not exclusive. Stone brick is <span class="chip f-masonry">masonry</span>
and <span class="chip f-bevelled">bevelled</span>, and saying both is more use than picking one word.
<b>contrast</b> is the standard deviation of luma over the opaque pixels — the noise axis. <b>colours</b>
counts distinct RGB values in the 256 pixels: five means a hand-picked ramp, two hundred means a generated
field. <b>grain</b> is neighbour-to-neighbour change over that spread, which separates speckle from blob.</p>

<footer>
Assets from Mojang's published launcher metadata: client jar
<code>3870888a6c3d349d3771a3e9d16c9bf5e076b908</code>, verified by hash. Textures are Mojang's and are not
redistributed with the studio — this page embeds them for reading, and only the derived table is anything
the repository would take. Regenerate with <code>python3 make_html.py</code>.
</footer>
</div>
<script>
const grid=document.getElementById('grid'),cards=[...grid.children];
const q=document.getElementById('q'),sort=document.getElementById('sort'),count=document.getElementById('count');
const togs=[...document.querySelectorAll('#togs .tog')],paint=document.getElementById('paintonly');
let active=new Set(),paintOnly=false;
function apply(){{
  const t=q.value.trim().toLowerCase();
  let shown=0;
  for(const c of cards){{
    const flags=new Set(c.dataset.flags.split(' '));
    let ok=[...active].every(f=>flags.has(f));
    if(ok&&paintOnly&&c.dataset.paint!=='1')ok=false;
    if(ok&&t)ok=c.textContent.toLowerCase().includes(t)||c.dataset.name.includes(t);
    c.hidden=!ok; if(ok)shown++;
  }}
  count.textContent=shown+' of '+cards.length;
}}
function resort(){{
  const k=sort.value;
  const v=c=>k==='name'?c.dataset.name:-parseFloat(c.dataset[k]);
  [...cards].sort((a,b)=>{{const x=v(a),y=v(b);return x<y?-1:x>y?1:0;}}).forEach(c=>grid.appendChild(c));
}}
togs.forEach(b=>b.onclick=()=>{{const f=b.dataset.flag;
  if(active.has(f)){{active.delete(f);b.setAttribute('aria-pressed','false');}}
  else{{active.add(f);b.setAttribute('aria-pressed','true');}} apply();}});
paint.onclick=()=>{{paintOnly=!paintOnly;paint.setAttribute('aria-pressed',paintOnly);apply();}};
q.oninput=apply; sort.onchange=()=>{{resort();apply();}};
apply();
</script></body></html>'''
