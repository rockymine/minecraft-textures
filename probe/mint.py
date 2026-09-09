"""Mint a fresh, unthemed run board from the master, so no run writes to an authored map.

The subject is a real hand-authored board rather than a synthetic fixture: ten layers, tunnels under a
cover, a pillar-and-rim structure, two wool rooms, a bedrock approach wall and a rot_180 fan. What a run
does to it — fill `themes`, name one on each shape — is the whole of what is being measured, and it is done
to a copy that can be thrown away.

    python3 mint.py plains-a          # -> map slug `probe-plains-a`, a pristine copy
    python3 mint.py --refresh         # re-read the master's documents from the source map
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
MASTER = HERE / "master"
SOURCE = "untitled-plan-16"          # the authored board. Read only, never written.
API = "http://localhost:7894/api"


def refresh():
    """Take the master's three documents off the source map. The layout comes from the artifact store
    rather than GET /sketch, which answers a partial view."""
    MASTER.mkdir(exist_ok=True)
    sql = ("SELECT CONVERT(a.data USING utf8mb4) FROM map_artifact a JOIN map m ON m.id=a.map_id "
           f"WHERE m.slug='{SOURCE}' AND a.kind='sketch_layout_json';")
    layout = subprocess.run(["mysql", "-upgm", "-ppgm_dev_pw", "pgm_studio", "-N", "-B", "--raw", "-e", sql],
                            capture_output=True, text=True).stdout
    (MASTER / "layout.json").write_text(layout)
    for kind in ("intent", "plan"):
        out = subprocess.run(["curl", "-sS", "--max-time", "30", f"{API}/map/{SOURCE}/{kind}"],
                             capture_output=True, text=True).stdout
        (MASTER / f"{kind}.json").write_text(out)
    doc = json.loads(layout)
    print(f"master refreshed: {len(doc['layers'])} layers, "
          f"{sum(len((l.get('layout') or {}).get('shapes') or []) for l in doc['layers'])} shapes, "
          f"themes={doc.get('themes') or '{}'}")


def mint(name):
    layout = json.loads((MASTER / "layout.json").read_text())
    # Unthemed by construction, whatever the master happens to carry: the run's job is to fill this.
    layout.pop("themes", None)
    layout.pop("mapTheme", None)
    slug = f"probe-{name}"
    body = {"layout": layout,
            "intent": json.loads((MASTER / "intent.json").read_text()),
            "plan": json.loads((MASTER / "plan.json").read_text()),
            "name": f"Colour probe — {name}", "slug": slug}
    req = HERE / "_mint.json"
    req.write_text(json.dumps(body))
    out = subprocess.run(["curl", "-sS", "--max-time", "180", "-X", "POST", f"{API}/map/from-documents",
                          "-H", "Content-Type: application/json", "-d", f"@{req}"],
                         capture_output=True, text=True).stdout
    req.unlink(missing_ok=True)
    got = json.loads(out)
    if "slug" not in got:
        print("refused:", out[:300]); return 1
    print(f"{got['slug']}  cells {got['cells']}  islands {got['islands']}  "
          f"warnings: {', '.join(w['rule'] for w in got.get('warnings') or []) or 'none'}")
    print(f"  http://localhost:7894/maps/{got['slug']}/sketch")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--refresh":
        refresh()
    else:
        sys.exit(mint(args[0]))
