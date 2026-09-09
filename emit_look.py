"""Emit the studio's block-appearance table from the measured catalogue.

What the studio takes from this folder is the derived table, never the assets — the same division
`BlockPaletteData`'s mean colours were already committed under. The generator lives here because the jar
does; nothing in `pgm-studio` can re-run it, and nothing needs to.

    python3 emit_look.py > /media/sf_repos/pgm-studio/src/PgmStudio.Minecraft/Palette/BlockLookData.cs
"""
import json, pathlib, sys
import faces, namemap

HERE = pathlib.Path(__file__).parent
CAT = json.load(open(HERE / "block-texture-catalogue.json"))
PAINT = json.load(open(HERE / "terrain-blocks.json"))

# The flags a caller can act on. `noise` is the absence of the others and says nothing a reader needs.
KEEP = ("inlaid", "masonry", "tiled", "panelled", "bevelled", "dithered", "ramped",
        "grained-x", "grained-y", "flat")


def look(texture):
    v = CAT.get(texture)
    if v is None:
        # A sprite the full-cube sweep never reached — grass and slime are modelled with a tinted overlay
        # and a translucent body, so no cube model names them — measured here on its own terms. The flags
        # come out of the same reading `catalogue.py` runs.
        import catalogue, features
        f, e = features.features(texture), features.edges(texture)
        s = features.seams(texture) or {"seamRows": 0, "seamCols": 0}
        if not f or not e:
            return None
        flags = []
        if max(f["rowPeriod"], f["colPeriod"]) >= 0.40: flags.append("tiled")
        if max(s["seamRows"], s["seamCols"]) >= 1: flags.append("masonry")
        if min(f["rowRank"], f["colRank"]) <= 12: flags.append("panelled")
        if e["bevel"] >= 0.50: flags.append("bevelled")
        if f["contrast"] < 8: flags.append("flat")
        if f["colours"] >= 150: flags.append("dithered")
        elif f["colours"] <= 12: flags.append("ramped")
        if abs(f["anisotropy"]) >= 0.35: flags.append("grained-x" if f["anisotropy"] > 0 else "grained-y")
        v = {"contrast": round(f["contrast"], 1), "colours": f["colours"], "flags": flags}
    flags = [f for f in v["flags"] if f in KEEP]
    return texture, v["contrast"], v["colours"], flags


def main():
    rows, missing = [], []
    for b in PAINT:
        top, side = faces.faces(b["id"], b["data"])
        lt, ls = look(top), look(side)
        if lt is None or ls is None:
            missing.append((b["id"], b["data"], b["name"], top, side))
            continue
        rows.append((b["id"], b["data"], b["name"], lt, ls))
    rows.sort(key=lambda r: (r[0], r[1]))

    out = sys.stdout
    out.write('''namespace PgmStudio.Minecraft.Palette;

/// <summary>
/// What a block <b>looks like</b> beyond the one colour it averages to — the measured table behind
/// <see cref="BlockLook"/>.
///
/// <para><b>Where it comes from.</b> Each row is measured off that block's own 1.8 texture, on the face it
/// shows: <c>contrast</c> is the standard deviation of luma over the opaque pixels, <c>colours</c> the count
/// of distinct RGB values in the sprite's 256, and the flags name how the sprite is constructed. A block
/// whose top and sides are one sprite answers the same on both; one whose faces differ answers differently,
/// which is the whole reason both are here — a terrain theme paints the surface bucket on the top face and
/// the wall bucket on the side, so two blocks can be interchangeable in one and distinct in the other.</para>
///
/// <para><b>Why it is a table and not a computation.</b> The textures are Mojang's and are not in this
/// repository, so nothing here can re-derive these numbers — which is exactly what makes them a result worth
/// committing, the same division <see cref="BlockPaletteData"/>'s mean colours already sit under.</para>
/// </summary>
internal static class BlockLookData
{
    /// <summary>A block\'s look on one face: the sprite it shows there and what that sprite reads as.</summary>
    internal readonly record struct Face(string Texture, double Contrast, int Colours, string[] Construction);

    /// <summary>Keyed <c>(id &lt;&lt; 4) | data</c>, the same key <see cref="BlockPalette"/> uses.</summary>
    internal static readonly Dictionary<int, (Face Top, Face Side)> ByBlock = new()
    {
''')
    for bid, data, name, lt, ls in rows:
        def face(f):
            tex, contrast, colours, flags = f
            cs = ", ".join(f'"{x}"' for x in flags)
            return f'new("{tex}", {contrast}, {colours}, [{cs}])'
        same = "" if lt != ls else "   // one sprite on every face"
        out.write(f'        [({bid} << 4) | {data}] = ({face(lt)},\n'
                  f'{" " * 12}{face(ls)}),{same}   // {name}\n')
    out.write("    };\n}\n")

    if missing:
        sys.stderr.write(f"{len(missing)} paintable blocks had no catalogue entry:\n")
        for m in missing:
            sys.stderr.write(f"  {m}\n")
    sys.stderr.write(f"emitted {len(rows)} rows\n")


if __name__ == "__main__":
    main()
