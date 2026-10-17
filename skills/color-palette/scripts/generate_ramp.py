#!/usr/bin/env python3
"""Generate perceptually uniform color ramps in OKLCH.

Stdlib only. Given one or more base colors (hex or oklch()), builds a ramp
with evenly spaced OKLCH lightness, per-step gamut-clamped chroma, and reports
WCAG contrast, Oklab dE evenness, and colorblind-simulated values.

Usage:
  python3 generate_ramp.py "#3b82f6"
  python3 generate_ramp.py "#3b82f6" "#e11d48" --steps 12 --chroma 90
  python3 generate_ramp.py "oklch(0.62 0.19 255)" --format css

Algorithm (see references/theory.md):
  1. minL = max(0.05, baseL - 0.40); maxL = min(0.95, baseL + 0.40)
  2. Distribute steps from maxL (lightest, label 50) to minL (darkest, 950)
  3. Per step: C = chromaPct/100 * maxChroma(L, hue)   # gamut-clamped
  4. Report dE(Oklab) between adjacent steps, WCAG ratios vs white/black,
     and Viénot protan/deutan/tritan simulated hexes.
"""
import argparse
import json
import math
import re
import sys

# ---------- sRGB <-> linear ----------
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

# ---------- linear sRGB <-> Oklab (Ottosson) ----------
def oklab_from_linear(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = math.copysign(abs(l) ** (1/3), l), math.copysign(abs(m) ** (1/3), m), math.copysign(abs(s) ** (1/3), s)
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285932050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)

def linear_from_oklab(L, a, bb):
    l_ = L + 0.3963377774 * a + 0.2158037573 * bb
    m_ = L - 0.1055613458 * a - 0.0638541728 * bb
    s_ = L - 0.0894841775 * a - 1.2914855480 * bb
    l, m, s = l_**3, m_**3, s_**3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def in_gamut(L, C, H):
    a, bb = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    r, g, b = linear_from_oklab(L, a, bb)
    return all(-1e-6 <= v <= 1 + 1e-6 for v in (r, g, b))

def max_chroma(L, H):
    if not in_gamut(L, 0.0, H):
        return 0.0
    lo, hi = 0.0, 0.4
    for _ in range(24):
        mid = (lo + hi) / 2
        if in_gamut(L, mid, H):
            lo = mid
        else:
            hi = mid
    return lo

def oklch_to_rgb(L, C, H):
    """Return (r, g, b) in sRGB 0-1, gamut-clamped via chroma reduction."""
    a, bb = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    r, g, b = linear_from_oklab(L, a, bb)
    if not all(-1e-6 <= v <= 1 + 1e-6 for v in (r, g, b)):
        C = max_chroma(L, H)
        a, bb = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
        r, g, b = linear_from_oklab(L, a, bb)
    return (min(max(linear_to_srgb(r), 0.0), 1.0),
            min(max(linear_to_srgb(g), 0.0), 1.0),
            min(max(linear_to_srgb(b), 0.0), 1.0))

def rgb_to_oklch(r, g, b):
    L, a, bb = oklab_from_linear(srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b))
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

# ---------- WCAG ----------
def wcag_luminance(r, g, b):
    R, G, B = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast(rgb1, rgb2):
    l1, l2 = wcag_luminance(*rgb1), wcag_luminance(*rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def wcag_grade(ratio):
    if ratio >= 7: return "AAA"
    if ratio >= 4.5: return "AA"
    if ratio >= 3: return "AA-large"
    return "fail"

# ---------- colorblind simulation (Vienot 1999, linear rgb) ----------
CVD = {
    "protan": [[0.11238, 0.88762, 0.0], [0.11238, 0.88762, 0.0], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.075746, -0.179782], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}

def simulate(rgb, kind):
    lin = [srgb_to_linear(c) for c in rgb]
    m = CVD[kind]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return tuple(min(max(linear_to_srgb(v), 0.0), 1.0) for v in out)

# ---------- parsing / formatting ----------
def parse_color(s):
    s = s.strip()
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", s)
    if m:
        n = int(m.group(1), 16)
        return ((n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255), "hex"
    m = re.fullmatch(r"oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.]+)(?:deg)?\s*\)", s, re.I)
    if m:
        L = float(m.group(1).rstrip("%")) / (100 if m.group(1).endswith("%") else 1)
        C = float(m.group(2).rstrip("%")) / (100 if m.group(2).endswith("%") else 1)
        return (L, C, float(m.group(3)) % 360), "oklch"
    raise ValueError(f"Unsupported color: {s} (use #rrggbb or oklch(L C H))")

def to_hex(rgb):
    return "#" + "".join(f"{round(c*255):02x}" for c in rgb)

def oklch_str(L, C, H):
    return f"oklch({L:.4f} {C:.4f} {H:.2f})"

def default_labels(steps):
    if steps == 11: return [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
    if steps == 9:  return [50, 100, 200, 300, 500, 700, 800, 900, 950]
    if steps == 5:  return [100, 300, 500, 700, 900]
    return [round(i * 1000 / steps) for i in range(steps, 0, -1)]  # generic: light -> dark

def generate_ramp(base, steps=11, chroma_pct=90, hue_drift=0.0):
    """base: (L, C, H) in OKLCH. Returns list of dicts, lightest first."""
    L0, C0, H0 = base
    minL, maxL = max(0.05, L0 - 0.40), min(0.95, L0 + 0.40)
    labels = default_labels(steps)
    ramp = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        L = maxL - t * (maxL - minL)
        H = (H0 + hue_drift * t) % 360  # optional deliberate drift light->dark
        C = (chroma_pct / 100) * max_chroma(L, H)
        if abs(L - L0) < (maxL - minL) / (steps - 1) / 2:
            C = min(C, C0)  # near the base step: don't exceed base chroma
        rgb = oklch_to_rgb(L, C, H)
        ramp.append({"L": round(L, 4), "C": round(C, 4), "H": round(H, 2),
                     "oklch": oklch_str(L, C, H), "hex": to_hex(rgb), "rgb": rgb,
                     "label": labels[i] if i < len(labels) else None})
    # evenness: Oklab dE between adjacent steps
    for i in range(steps):
        lab_i = (ramp[i]["L"], ramp[i]["C"] * math.cos(math.radians(ramp[i]["H"])),
                 ramp[i]["C"] * math.sin(math.radians(ramp[i]["H"])))
        ramp[i]["lab"] = lab_i
        if i > 0:
            prev = ramp[i-1]["lab"]
            ramp[i]["dE_prev"] = round(math.dist(lab_i, prev), 3)
    for step in ramp:
        step["contrast_white"] = round(contrast((1, 1, 1), step["rgb"]), 2)
        step["contrast_black"] = round(contrast((0, 0, 0), step["rgb"]), 2)
        step["wcag_white"] = wcag_grade(step["contrast_white"])
        step["wcag_black"] = wcag_grade(step["contrast_black"])
    return ramp

def min_cross_hue_dE(ramps, min_label=400):
    """Smallest pairwise Oklab dE between same-step colors of different ramps,
    considering only steps at min_label and darker (light steps are near-white
    by construction and always collide)."""
    if len(ramps) < 2:
        return None
    worst = None
    for i in range(len(ramps[0])):
        if (ramps[0][i]["label"] or 0) < min_label:
            continue
        for a in range(len(ramps)):
            for b in range(a + 1, len(ramps)):
                dE = math.dist(ramps[a][i]["lab"], ramps[b][i]["lab"])
                if worst is None or dE < worst[0]:
                    worst = (round(dE, 3), ramps[a][i]["label"], ramps[a][i]["hex"], ramps[b][i]["hex"])
    return worst

# ---------- output ----------
def emit(ramps, fmt, names):
    if fmt == "css":
        lines = [":root {"]
        for name, ramp in zip(names, ramps):
            for step in ramp:
                if step["label"] is None: continue
                lines.append(f"  --{name}-{step['label']}: {step['hex']};")
        lines.append("}")
        lines.append("@supports (color: oklch(0% 0 0)) {")
        lines.append("  :root {")
        for name, ramp in zip(names, ramps):
            for step in ramp:
                if step["label"] is None: continue
                lines.append(f"    --{name}-{step['label']}: {step['oklch']};")
        lines.append("  }")
        lines.append("}")
        return "\n".join(lines)
    # table (default)
    out = []
    for name, ramp in zip(names, ramps):
        out.append(f"== {name} ==")
        out.append("step  hex      oklch                       vs-white  vs-black  dE")
        for step in ramp:
            out.append(f"{str(step['label']):>4}  {step['hex']}  {step['oklch']:27}  "
                       f"{step['contrast_white']:>6} {step['wcag_white']:>8}  "
                       f"{step['contrast_black']:>6} {step['wcag_black']:>8}  "
                       f"{step.get('dE_prev', '-'):>5}")
        out.append("")
    worst = min_cross_hue_dE(ramps)
    if worst:
        dE, lbl, h1, h2 = worst
        out.append(f"min cross-hue dE (steps 400+): {dE} Oklab (step {lbl}: {h1} vs {h2})"
                    + (" — WARNING: under 0.05, hues may be hard to tell apart" if dE < 0.05 else ""))
    return "\n".join(out)

def main():
    p = argparse.ArgumentParser(description="OKLCH color ramp generator")
    p.add_argument("colors", nargs="+", help="base color(s): #rrggbb or oklch(L C H)")
    p.add_argument("--steps", type=int, default=11, help="ramp steps (default 11)")
    p.add_argument("--chroma", type=float, default=90, help="chroma as %% of gamut max per step (default 90)")
    p.add_argument("--hue-drift", type=float, default=0.0, help="optional hue drift light->dark, degrees")
    p.add_argument("--format", choices=["table", "css", "json"], default="table")
    p.add_argument("--cvd", action="store_true", help="include deutan-simulated hex per step")
    p.add_argument("--names", default="", help="comma-separated scale names for css output (default: scale1..N)")
    args = p.parse_args()

    ramps, oklch_bases = [], []
    for c in args.colors:
        val, kind = parse_color(c)
        base = val if kind == "oklch" else rgb_to_oklch(*val)
        oklch_bases.append(base)
        ramps.append(generate_ramp(base, args.steps, args.chroma, args.hue_drift))

    if args.cvd:
        for ramp in ramps:
            for step in ramp:
                step["deutan"] = to_hex(simulate(step["rgb"], "deutan"))

    names = [n.strip() for n in args.names.split(",") if n.strip()] or [f"scale{i+1}" for i in range(len(ramps))]
    if args.format == "json":
        print(json.dumps([{"name": n, "base": {"L": b[0], "C": b[1], "H": b[2]},
                           "steps": [{k: v for k, v in s.items() if k != "rgb"} for s in r]}
                          for n, b, r in zip(names, oklch_bases, ramps)], indent=2))
    else:
        print(emit(ramps, args.format, names))

if __name__ == "__main__":
    main()
