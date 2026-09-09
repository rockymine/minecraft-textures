"""The baseline: every spec board's theme registry, scored.

These boards were authored under `AUTHORING-BRIEF.md` as it stands — which already carries the prose
advice about pattern width and voronoi placement — and with no texture data available to the agent beyond
one mean colour per block. They are the control arm, and they cost nothing because they already exist.
"""
import json, pathlib, collections, sys
import scorer

SPECS = pathlib.Path("/media/sf_repos/pgm-studio-mapgen/specs")


def registries():
    for d in sorted(p for p in SPECS.iterdir() if p.is_dir()):
        for f in sorted(d.glob("*.layout.json")):
            try:
                doc = json.loads(f.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            themes = doc.get("themes")
            if isinstance(themes, dict) and themes:
                yield d.name, themes
            break


def main():
    boards, rows = 0, []
    tot_pairs = tot_unknown = 0
    per_board = {}
    for name, themes in registries():
        found, pairs, unknown = scorer.score_registry(themes)
        boards += 1
        tot_pairs += pairs
        tot_unknown += unknown
        per_board[name] = {"themes": len(themes), "pairs": pairs, "unknown": unknown,
                           "findings": collections.Counter(f["kind"] for f in found)}
        for f in found:
            f["board"] = name
            rows.append(f)

    kinds = collections.Counter(r["kind"] for r in rows)
    print(f"boards scored          {boards}")
    print(f"block pairs examined   {tot_pairs}")
    print(f"unreadable blocks      {tot_unknown}"
          f"  ({100*tot_unknown/max(1,tot_unknown+2*tot_pairs):.1f}% of block slots)")
    print()
    for k in ("repeat", "collapse", "mush", "clash"):
        n = kinds[k]
        hit = sum(1 for b in per_board.values() if b["findings"][k])
        print(f"  {k:9s} {n:4d} pairs   on {hit:3d}/{boards} boards"
              f"   {100*n/max(1,tot_pairs):5.1f}% of pairs")
    clean = sum(1 for b in per_board.values() if not sum(b["findings"].values()))
    print(f"\n  boards with no finding at all: {clean}/{boards}")

    json.dump({"perBoard": {k: {**v, "findings": dict(v["findings"])}
                            for k, v in per_board.items()}, "rows": rows},
              open(pathlib.Path(__file__).parent / "baseline.json", "w"), indent=1)
    return rows, per_board


if __name__ == "__main__":
    rows, per_board = main()
    if "-v" in sys.argv:
        print("\n== worst boards ==")
        for n, b in sorted(per_board.items(), key=lambda kv: -sum(kv[1]["findings"].values()))[:10]:
            print(f"  {n:28s} {dict(b['findings'])}  ({b['themes']} themes, {b['pairs']} pairs)")
