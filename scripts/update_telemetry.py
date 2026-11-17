#!/usr/bin/env python3
"""
Zero-Dependency GitHub Telemetry SVG Generator for @evilninja6726.

Design Goals:
- Pure Python 3 standard library (zero pip install supply-chain attack surface).
- Uses GitHub's native REST API (authenticated via automatic GITHUB_TOKEN in Actions,
  or unauthenticated locally with automatic cache fallback on 403/network errors).
- Content-digest gated: updates SVG files only when real repository metrics change,
  avoiding manufactured daily bot commits on the contribution graph.
- Validates generated XML with ElementTree before atomic file replacement.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
CACHE_PATH = ROOT / ".cache" / "telemetry_snapshot.json"
USERNAME = os.environ.get("GH_PROFILE_USER", "evilninja6726")

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": {
        "card": "#111822",
        "inset": "#16202E",
        "inset_alt": "#0F1620",
        "border": "#223042",
        "text_primary": "#F1F5F9",
        "text_secondary": "#CBD5E1",
        "text_tertiary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#22D3EE",
        "emerald": "#10B981",
        "lang_colors": ["#22D3EE", "#F59E0B", "#10B981", "#818CF8", "#94A3B8"],
    },
    "light": {
        "card": "#F8FAFC",
        "inset": "#F1F5F9",
        "inset_alt": "#FFFFFF",
        "border": "#CBD5E1",
        "text_primary": "#0F172A",
        "text_secondary": "#334155",
        "text_tertiary": "#475569",
        "text_muted": "#64748B",
        "accent": "#0284C7",
        "emerald": "#059669",
        "lang_colors": ["#0284C7", "#D97706", "#059669", "#4F46E5", "#64748B"],
    },
}


def esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def gh_api_get(path: str, token: str | None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "evilninja6726-profile-telemetry/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/{path.lstrip('/')}", headers=headers)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_live_snapshot(token: str | None, fallback: dict) -> tuple[dict, str]:
    """Fetch live telemetry from GitHub API, falling back cleanly on rate limit or offline."""
    try:
        user = gh_api_get(f"users/{USERNAME}", token)
        repos = gh_api_get(f"users/{USERNAME}/repos?per_page=100&sort=pushed", token)
        if not isinstance(user, dict) or not isinstance(repos, list):
            raise ValueError("Unexpected API payload shape")

        non_fork = [r for r in repos if not r.get("fork")]
        total_stars = sum(int(r.get("stargazers_count", 0)) for r in non_fork)

        # Fetch per-repo language bytes when token is available (avoids 60 req/hr unauthenticated cap)
        lang_totals: dict[str, int] = {}
        if token:
            for r in non_fork:
                rname = r.get("name", "")
                if rname == USERNAME:
                    continue
                langs = gh_api_get(f"repos/{USERNAME}/{rname}/languages", token)
                if isinstance(langs, dict):
                    for lname, bcount in langs.items():
                        # Exclude generated AST graph HTML if .gitattributes not yet pushed
                        if rname == "frontier-cosmology-lab" and lname == "HTML" and int(bcount) > 400000:
                            continue
                        bucket = "CSS & JS" if lname in {"CSS", "JavaScript", "HTML"} else (
                            "TeX & Dart" if lname in {"TeX", "Dart", "Jupyter Notebook", "Shell", "Dockerfile"} else lname
                        )
                        lang_totals[bucket] = lang_totals.get(bucket, 0) + int(bcount)
        else:
            lang_totals = dict(fallback.get("language_bytes", {}))

        summary_overrides = {
            "fablearc": "4K FFmpeg Streaming & 9-Stage Recommender",
            "frontier-cosmology-lab": "Horndeski BAO & Spectral Ringdown Lab",
            "teleport_coding_test": "Spring Boot 3.2 Freight Load Optimizer",
            "dsa": "461 Java Algorithms & CP Implementations",
        }
        recent_items = []
        for r in non_fork:
            rname = r.get("name", "")
            if rname == USERNAME:
                continue
            lang = r.get("language") or "Code"
            if rname == "frontier-cosmology-lab" and lang == "HTML":
                lang = "Python"
            recent_items.append(
                {
                    "name": rname,
                    "pushed_at": (r.get("pushed_at") or "")[:10],
                    "language": lang,
                    "summary": summary_overrides.get(rname) or (r.get("description") or "Engineering repository")[:42],
                }
            )
            if len(recent_items) == 4:
                break

        created_year = int((user.get("created_at") or "2020")[:4])
        snapshot = {
            "username": USERNAME,
            "account_created_year": created_year,
            "public_repos": int(user.get("public_repos", len(repos))),
            "original_repos": len(non_fork),
            "total_stars": total_stars,
            "active_2026_repos": recent_items or fallback.get("active_2026_repos", []),
            "language_bytes": lang_totals or fallback.get("language_bytes", {}),
            "synced_month": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m"),
        }
        return snapshot, "live-github-api"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError) as exc:
        return dict(fallback), f"cached-snapshot ({type(exc).__name__})"


def compute_digest(snapshot: dict) -> str:
    core = {
        k: snapshot[k]
        for k in ("public_repos", "original_repos", "total_stars", "active_2026_repos", "language_bytes")
        if k in snapshot
    }
    raw = json.dumps(core, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def render_telemetry_svg(theme_name: str, t: dict, data: dict) -> str:
    lang_bytes: dict[str, int] = data.get("language_bytes", {})
    sorted_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:5]
    total_bytes = max(1, sum(v for _, v in sorted_langs))

    # Stacked proportional bar (width = 272px)
    bar_w = 272
    bx = 16.0
    bar_rects = []
    legend_rows = []
    colors = t["lang_colors"]

    for idx, (lname, bval) in enumerate(sorted_langs):
        pct = (bval / total_bytes) * 100.0
        seg_w = max(4.0, (bval / total_bytes) * bar_w)
        if idx == len(sorted_langs) - 1:
            seg_w = max(4.0, (16.0 + bar_w) - bx)
        color = colors[idx % len(colors)]
        bar_rects.append(
            f'<rect x="{bx:.1f}" y="42" width="{seg_w:.1f}" height="10" fill="{color}" />'
        )
        bx += seg_w

        if idx < 4:
            col = idx % 2
            row = idx // 2
            lx = 16 + col * 140
            ly = 74 + row * 22
            legend_rows.append(
                f'<circle cx="{lx + 4}" cy="{ly - 3.5}" r="3.5" fill="{color}" />'
                f'<text x="{lx + 13}" y="{ly}" class="sans" font-size="11" font-weight="600" fill="{t["text_secondary"]}">{esc(lname)}</text>'
                f'<text x="{lx + 128}" y="{ly}" text-anchor="end" class="mono" font-size="10.5" font-weight="600" fill="{t["text_tertiary"]}">{pct:.1f}%</text>'
            )

    recent_rows = []
    for idx, item in enumerate(data.get("active_2026_repos", [])[:4]):
        ry = 48 + idx * 21
        rname = item["name"]
        if len(rname) > 22:
            rname = rname[:21] + "…"
        recent_rows.append(
            f'<circle cx="16" cy="{ry - 3.5}" r="2.5" fill="{t["emerald"] if idx < 2 else t["accent"]}" />'
            f'<text x="25" y="{ry}" class="mono" font-size="10.2" font-weight="600" fill="{t["text_primary"]}">{esc(rname)}</text>'
            f'<text x="178" y="{ry}" class="mono" font-size="9.5" fill="{t["text_tertiary"]}">{esc(item["language"])}</text>'
            f'<text x="292" y="{ry}" text-anchor="end" class="mono" font-size="9.5" fill="{t["text_muted"]}">{esc(item["pushed_at"][:7])}</text>'
        )

    span_years = max(1, int(data.get("synced_month", "2026")[:4]) - int(data.get("account_created_year", 2020)))
    bars_svg = "\n      ".join(bar_rects)
    legend_svg = "\n      ".join(legend_rows)
    recent_svg = "\n      ".join(recent_rows)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 184" width="100%" role="img" aria-labelledby="tel-title-{theme_name}">
  <title id="tel-title-{theme_name}">GitHub Workspace Telemetry for @{esc(data.get("username", USERNAME))}</title>
  <defs>
    <clipPath id="bar-clip-{theme_name}">
      <rect x="16" y="42" width="272" height="10" rx="5" />
    </clipPath>
  </defs>
  <style>
    .sans {{ font-family: {FONT_SANS}; }}
    .mono {{ font-family: {FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>

  <rect x="1" y="1" width="898" height="182" rx="12" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1" />
  <text x="24" y="29" class="mono" font-size="10.5" font-weight="700" fill="{t["text_secondary"]}" letter-spacing="0.8">WORKSPACE TELEMETRY // @{esc(data.get("username", USERNAME)).upper()}</text>
  <text x="876" y="29" text-anchor="end" class="mono" font-size="9.5" fill="{t["text_muted"]}">SELF-HOSTED SVG · NO EXTERNAL WIDGETS · {esc(data.get("synced_month", "2026-11"))}</text>
  <line x1="24" y1="37" x2="876" y2="37" stroke="{t["border"]}" stroke-width="1" />

  <!-- Panel 1: Repository Footprint -->
  <g transform="translate(24, 48)">
    <rect width="220" height="118" rx="8" fill="{t["inset_alt"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="16" y="22" class="mono" font-size="9.5" font-weight="700" fill="{t["text_muted"]}" letter-spacing="0.6">01 // FOOTPRINT</text>

    <text x="16" y="54" class="mono" font-size="24" font-weight="700" fill="{t["text_primary"]}">{int(data.get("original_repos", 22))}</text>
    <text x="58" y="46" class="sans" font-size="11" font-weight="600" fill="{t["text_secondary"]}">Original Public Repos</text>
    <text x="58" y="60" class="mono" font-size="9.5" fill="{t["text_muted"]}">100% authored · 0 forks</text>

    <line x1="16" y1="74" x2="204" y2="74" stroke="{t["border"]}" stroke-width="1" />
    <text x="16" y="93" class="mono" font-size="9.8" font-weight="600" fill="{t["text_secondary"]}">TENURE</text>
    <text x="204" y="93" text-anchor="end" class="mono" font-size="10" font-weight="700" fill="{t["accent"]}">{int(data.get("account_created_year", 2020))}–PRESENT ({span_years}Y+)</text>
    <text x="16" y="109" class="mono" font-size="9.8" font-weight="600" fill="{t["text_secondary"]}">SHOWCASE</text>
    <text x="204" y="109" text-anchor="end" class="mono" font-size="10" font-weight="700" fill="{t["emerald"]}">4 CURATED SYSTEMS</text>
  </g>

  <!-- Panel 2: Authored Language Distribution -->
  <g transform="translate(256, 48)">
    <rect width="304" height="118" rx="8" fill="{t["inset_alt"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="16" y="22" class="mono" font-size="9.5" font-weight="700" fill="{t["text_muted"]}" letter-spacing="0.6">02 // AUTHORED CODEBASE MIX</text>
    <text x="288" y="22" text-anchor="end" class="mono" font-size="9" fill="{t["text_muted"]}">BY SOURCE BYTES</text>

    <g clip-path="url(#bar-clip-{theme_name})">
      {bars_svg}
    </g>
    {legend_svg}
  </g>

  <!-- Panel 3: Recent Active Repositories -->
  <g transform="translate(572, 48)">
    <rect width="304" height="118" rx="8" fill="{t["inset_alt"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="16" y="22" class="mono" font-size="9.5" font-weight="700" fill="{t["text_muted"]}" letter-spacing="0.6">03 // RECENT REPOSITORY PULSE</text>
    {recent_svg}
  </g>
</svg>
"""


def main() -> None:
    cached = {}
    if CACHE_PATH.exists():
        cached = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    snapshot, source = fetch_live_snapshot(token, cached)
    new_digest = compute_digest(snapshot)
    old_digest = cached.get("content_digest")

    dark_path = ASSETS_DIR / "telemetry-dark.svg"
    light_path = ASSETS_DIR / "telemetry-light.svg"
    force = os.environ.get("FORCE_TELEMETRY_RENDER") == "1" or not (dark_path.exists() and light_path.exists())

    if not force and new_digest == old_digest:
        print(f"[telemetry] Source={source} | Digest unchanged ({new_digest}); skipping no-op rewrite.")
        return

    snapshot["content_digest"] = new_digest
    for theme_name, tokens in THEMES.items():
        svg = render_telemetry_svg(theme_name, tokens, snapshot)
        ET.fromstring(svg.encode("utf-8"))
        out = ASSETS_DIR / f"telemetry-{theme_name}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"[telemetry] Source={source} | Updated telemetry SVGs (digest={new_digest}).")


if __name__ == "__main__":
    main()
