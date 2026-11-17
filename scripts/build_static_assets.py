#!/usr/bin/env python3
"""
Deterministic Dual-Theme SVG Asset Builder for @evilninja6726 Profile Repository.

Generates crisp, self-contained Light ("Drafting Vellum") and Dark ("Graphite Telemetry")
architectural SVGs with zero external network dependencies (GitHub Camo/img sandbox safe)
and validates every output file via xml.etree.ElementTree.
"""

from __future__ import annotations

import html
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": {
        "canvas": "#0D1117",
        "card": "#111822",
        "inset": "#16202E",
        "inset_alt": "#0F1620",
        "border": "#223042",
        "border_strong": "#2E4159",
        "grid_dot": "#334155",
        "grid_opacity": "0.35",
        "text_primary": "#F1F5F9",
        "text_secondary": "#CBD5E1",
        "text_tertiary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#22D3EE",
        "accent_soft": "#0E2A38",
        "accent_border": "#155E75",
        "emerald": "#10B981",
        "emerald_soft": "#09261E",
        "amber": "#F59E0B",
        "amber_soft": "#2B1F0A",
        "wire": "#2A3B52",
    },
    "light": {
        "canvas": "#FFFFFF",
        "card": "#F8FAFC",
        "inset": "#F1F5F9",
        "inset_alt": "#FFFFFF",
        "border": "#CBD5E1",
        "border_strong": "#94A3B8",
        "grid_dot": "#94A3B8",
        "grid_opacity": "0.28",
        "text_primary": "#0F172A",
        "text_secondary": "#334155",
        "text_tertiary": "#475569",
        "text_muted": "#64748B",
        "accent": "#0284C7",
        "accent_soft": "#E0F2FE",
        "accent_border": "#7DD3FC",
        "emerald": "#059669",
        "emerald_soft": "#D1FAE5",
        "amber": "#D97706",
        "amber_soft": "#FEF3C7",
        "wire": "#CBD5E1",
    },
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def validate_and_write(path: Path, svg: str) -> None:
    ET.fromstring(svg.encode("utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def corner_ticks(x: int, y: int, w: int, h: int, color: str) -> str:
    """Subtle architectural registration ticks at card corners."""
    pts = [(x + 12, y + 12), (x + w - 12, y + 12), (x + 12, y + h - 12), (x + w - 12, y + h - 12)]
    lines = []
    for cx, cy in pts:
        lines.append(
            f'<path d="M{cx - 4} {cy} H{cx + 4} M{cx} {cy - 4} V{cy + 4}" '
            f'stroke="{color}" stroke-width="1" opacity="0.55" />'
        )
    return "\n  ".join(lines)


def build_hero(theme_name: str, t: dict[str, str]) -> str:
    pills = [
        ("JAVA · SPRING BOOT", 132),
        ("KAFKA · FASTAPI", 114),
        ("PG · MONGO · LIBSQL", 136),
        ("FFMPEG · APPLIED AI", 132),
    ]
    px = 36
    pill_nodes = []
    for label, pw in pills:
        pill_nodes.append(
            f'<g transform="translate({px}, 228)">'
            f'<rect width="{pw}" height="28" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1"/>'
            f'<text x="{pw / 2}" y="18" text-anchor="middle" class="mono" font-size="10" font-weight="600" '
            f'fill="{t["text_secondary"]}" letter-spacing="0.4">{esc(label)}</text>'
            f"</g>"
        )
        px += pw + 6

    pill_svg = "\n  ".join(pill_nodes)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 292" width="100%" role="img" aria-labelledby="hero-title-{theme_name} hero-desc-{theme_name}">
  <title id="hero-title-{theme_name}">Rajat — Senior Software Engineer</title>
  <desc id="hero-desc-{theme_name}">Senior Software Engineer with 6 years of experience building distributed Java Spring Boot and Python FastAPI backend systems, Kafka event pipelines, polyglot storage, and real-time media and AI workflows.</desc>
  <defs>
    <pattern id="grid-{theme_name}" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="12" cy="12" r="0.85" fill="{t["grid_dot"]}" opacity="{t["grid_opacity"]}" />
    </pattern>
    <linearGradient id="accent-line-{theme_name}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{t["accent"]}" stop-opacity="0.95" />
      <stop offset="65%" stop-color="{t["emerald"]}" stop-opacity="0.75" />
      <stop offset="100%" stop-color="{t["accent"]}" stop-opacity="0.0" />
    </linearGradient>
  </defs>
  <style>
    .sans {{ font-family: {FONT_SANS}; }}
    .mono {{ font-family: {FONT_MONO}; font-variant-numeric: tabular-nums; }}
    .signal {{
      stroke-dasharray: 0.16 0.84;
      stroke-dashoffset: 1;
      animation: flow-{theme_name} 5.5s linear infinite;
    }}
    .signal-delayed {{
      stroke-dasharray: 0.16 0.84;
      stroke-dashoffset: 1;
      animation: flow-{theme_name} 5.5s linear infinite;
      animation-delay: -2.4s;
    }}
    @keyframes flow-{theme_name} {{
      from {{ stroke-dashoffset: 1; }}
      to {{ stroke-dashoffset: 0; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .signal, .signal-delayed {{ animation: none; stroke-dasharray: none; opacity: 0.35; }}
    }}
  </style>

  <!-- Blueprint Outer Frame -->
  <rect x="1" y="1" width="898" height="290" rx="12" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1" />
  <rect x="2" y="2" width="896" height="288" rx="11" fill="url(#grid-{theme_name})" />
  <rect x="36" y="1" width="380" height="2" fill="url(#accent-line-{theme_name})" />
  {corner_ticks(1, 1, 898, 290, t["border_strong"])}

  <!-- Left Column: Architectural Identity -->
  <g>
    <rect x="36" y="30" width="252" height="24" rx="12" fill="{t["emerald_soft"]}" stroke="{t["border"]}" stroke-width="1" />
    <circle cx="50" cy="42" r="3.5" fill="{t["emerald"]}" />
    <text x="61" y="46" class="mono" font-size="10" font-weight="600" fill="{t["text_secondary"]}" letter-spacing="0.8">SENIOR SOFTWARE ENGINEER · 6 YRS</text>
    <text x="302" y="46" class="mono" font-size="10" font-weight="500" fill="{t["text_muted"]}" letter-spacing="0.8">// DELHI NCR, IN</text>

    <text x="36" y="98" class="sans" font-size="40" font-weight="700" fill="{t["text_primary"]}" letter-spacing="-0.9">Rajat</text>
    <text x="36" y="128" class="sans" font-size="15" font-weight="600" fill="{t["accent"]}" letter-spacing="-0.15">Distributed Systems · Event-Driven Backends · Media &amp; Applied AI</text>

    <text x="36" y="162" class="sans" font-size="13.2" font-weight="400" fill="{t["text_secondary"]}">Designing fault-tolerant microservices, event pipelines, and low-latency data layers</text>
    <text x="36" y="183" class="sans" font-size="13.2" font-weight="400" fill="{t["text_secondary"]}">across Java/Spring Boot, Python FastAPI, TypeScript, and multimodal media engines.</text>
    <text x="36" y="208" class="mono" font-size="10.5" font-weight="500" fill="{t["text_muted"]}">FOCUS // Service boundaries · Polyglot consistency · Real-time media &amp; search</text>
  </g>

  {pill_svg}

  <!-- Right Column: Live Distributed Topology Schematic -->
  <g transform="translate(584, 24)">
    <rect x="0" y="0" width="288" height="244" rx="8" fill="{t["inset_alt"]}" stroke="{t["border"]}" stroke-width="1" />
    <line x1="0" y1="30" x2="288" y2="30" stroke="{t["border"]}" stroke-width="1" />
    <text x="14" y="19" class="mono" font-size="9.5" font-weight="600" fill="{t["text_tertiary"]}" letter-spacing="0.7">SYS.TOPOLOGY // PIPELINE</text>
    <text x="274" y="19" text-anchor="end" class="mono" font-size="9.5" font-weight="600" fill="{t["accent"]}">SPEC v2.6</text>

    <!-- Base Wires -->
    <path d="M76 80 V106 M212 80 V106 M144 142 V166 M76 166 H212 M76 166 V174 M212 166 V174" stroke="{t["wire"]}" stroke-width="1.5" fill="none" />
    <!-- Animated Signal Pulses -->
    <path pathLength="1" class="signal" d="M76 80 V106 H144 V166 H76 V174" stroke="{t["accent"]}" stroke-width="1.8" fill="none" stroke-linecap="round" />
    <path pathLength="1" class="signal-delayed" d="M212 80 V106 H144 V166 H212 V174" stroke="{t["emerald"]}" stroke-width="1.8" fill="none" stroke-linecap="round" />

    <!-- Top Nodes -->
    <rect x="16" y="42" width="120" height="38" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="76" y="58" text-anchor="middle" class="sans" font-size="11" font-weight="600" fill="{t["text_primary"]}">API &amp; Auth Gate</text>
    <text x="76" y="72" text-anchor="middle" class="mono" font-size="9" fill="{t["text_tertiary"]}">REST · Feign · RBAC</text>

    <rect x="152" y="42" width="120" height="38" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="212" y="58" text-anchor="middle" class="sans" font-size="11" font-weight="600" fill="{t["text_primary"]}">Stream Proxy</text>
    <text x="212" y="72" text-anchor="middle" class="mono" font-size="9" fill="{t["text_tertiary"]}">L1/L2 · SSRF Guard</text>

    <!-- Event Spine -->
    <rect x="16" y="106" width="256" height="36" rx="6" fill="{t["accent_soft"]}" stroke="{t["accent_border"]}" stroke-width="1" />
    <text x="144" y="122" text-anchor="middle" class="mono" font-size="10" font-weight="700" fill="{t["accent"]}" letter-spacing="0.6">EVENT &amp; ORCHESTRATION SPINE</text>
    <text x="144" y="135" text-anchor="middle" class="mono" font-size="8.8" fill="{t["text_secondary"]}">Kafka Topics · Single-Flight · Async Workers</text>

    <!-- Bottom Nodes -->
    <rect x="16" y="174" width="120" height="42" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="76" y="191" text-anchor="middle" class="sans" font-size="11" font-weight="600" fill="{t["text_primary"]}">Media &amp; AI</text>
    <text x="76" y="206" text-anchor="middle" class="mono" font-size="9" fill="{t["text_tertiary"]}">FFmpeg · ASR · LLM</text>

    <rect x="152" y="174" width="120" height="42" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1" />
    <text x="212" y="191" text-anchor="middle" class="sans" font-size="11" font-weight="600" fill="{t["text_primary"]}">Polyglot State</text>
    <text x="212" y="206" text-anchor="middle" class="mono" font-size="9" fill="{t["text_tertiary"]}">PG · Mongo · LibSQL</text>

    <text x="144" y="233" text-anchor="middle" class="mono" font-size="8.4" fill="{t["text_muted"]}">idempotent edges · strict schemas · bounded latency</text>
  </g>
</svg>
"""


def build_systems(theme_name: str, t: dict[str, str]) -> str:
    quads = [
        (
            24,
            48,
            "01 // SERVICE & API ARCHITECTURE",
            t["accent"],
            "Java (8–17) · Spring Boot 3 · FastAPI · TypeScript",
            "Domain microservices, declarative Feign orchestration, REST contracts,",
            "JWT/Scrypt authentication, role-based access control & AOP telemetry.",
        ),
        (
            458,
            48,
            "02 // EVENT STREAMS, MEDIA & APPLIED AI",
            t["emerald"],
            "Apache Kafka · FFmpeg · Whisper ASR · Gemini & TTS",
            "Asynchronous producer/consumer pipelines, live 4K container remuxing,",
            "OCR/speech extraction, and zero-DB 9-stage hybrid MMR ranking.",
        ),
        (
            24,
            152,
            "03 // POLYGLOT PERSISTENCE & CACHING",
            t["accent"],
            "PostgreSQL · MongoDB · Redis · MSSQL · Turso LibSQL",
            "Indexed relational & document models, cross-service transactions,",
            "Single-Flight L1/L2 caching, and 3NF cloud-replicated SQLite.",
        ),
        (
            458,
            152,
            "04 // RUNTIME, SECURITY & VERIFICATION",
            t["amber"],
            "Docker · Kubernetes · JUnit 5 · WireMock · Vitest · React",
            "Multi-stage non-root containers, RFC1918/metadata SSRF filtering,",
            "contract simulation, E2E security suites, and web/desktop UIs.",
        ),
    ]

    q_svg = []
    for x, y, code, dot_color, stack, line1, line2 in quads:
        q_svg.append(
            f'<g transform="translate({x}, {y})">'
            f'<rect width="418" height="92" rx="8" fill="{t["inset_alt"]}" stroke="{t["border"]}" stroke-width="1" />'
            f'<circle cx="16" cy="20" r="3" fill="{dot_color}" />'
            f'<text x="26" y="24" class="mono" font-size="10" font-weight="700" fill="{t["text_tertiary"]}" letter-spacing="0.6">{esc(code)}</text>'
            f'<text x="16" y="46" class="sans" font-size="12.4" font-weight="700" fill="{t["text_primary"]}">{esc(stack)}</text>'
            f'<text x="16" y="66" class="sans" font-size="11.2" fill="{t["text_secondary"]}">{esc(line1)}</text>'
            f'<text x="16" y="82" class="sans" font-size="11.2" fill="{t["text_secondary"]}">{esc(line2)}</text>'
            f"</g>"
        )

    quads_joined = "\n  ".join(q_svg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 264" width="100%" role="img" aria-labelledby="sys-title-{theme_name}">
  <title id="sys-title-{theme_name}">Core Production Technology Ecosystem Stratified by Architectural Layer</title>
  <style>
    .sans {{ font-family: {FONT_SANS}; }}
    .mono {{ font-family: {FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>
  <rect x="1" y="1" width="898" height="262" rx="12" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1" />
  <text x="24" y="31" class="mono" font-size="10.5" font-weight="700" fill="{t["text_secondary"]}" letter-spacing="0.8">ARCHITECTURE MATRIX // TECHNOLOGY ECOSYSTEM BY SYSTEM LAYER</text>
  <text x="876" y="31" text-anchor="end" class="mono" font-size="10" fill="{t["text_muted"]}">PRODUCTION + INDEPENDENT BUILDS</text>
  <line x1="24" y1="39" x2="876" y2="39" stroke="{t["border"]}" stroke-width="1" />
  {quads_joined}
</svg>
"""


def build_project_card(
    slug: str,
    theme_name: str,
    t: dict[str, str],
    *,
    index_tag: str,
    status_label: str,
    status_kind: str,
    title: str,
    stack_line: str,
    metrics: list[tuple[str, str]],
) -> str:
    status_color = t["emerald"] if status_kind == "live" else (t["amber"] if status_kind == "lab" else t["accent"])
    status_bg = t["emerald_soft"] if status_kind == "live" else (t["amber_soft"] if status_kind == "lab" else t["accent_soft"])

    metric_boxes = []
    mx = 528
    for val, caption in metrics:
        metric_boxes.append(
            f'<g transform="translate({mx}, 20)">'
            f'<rect width="110" height="72" rx="6" fill="{t["inset"]}" stroke="{t["border"]}" stroke-width="1" />'
            f'<text x="55" y="39" text-anchor="middle" class="mono" font-size="15.5" font-weight="700" fill="{t["text_primary"]}">{esc(val)}</text>'
            f'<text x="55" y="57" text-anchor="middle" class="mono" font-size="8.8" font-weight="600" fill="{t["text_tertiary"]}" letter-spacing="0.5">{esc(caption)}</text>'
            f"</g>"
        )
        mx += 118

    metrics_svg = "\n  ".join(metric_boxes)
    pill_w = max(116, len(status_label) * 6.4 + 26)
    idx_w = len(index_tag) * 6.5

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 112" width="100%" role="img" aria-labelledby="card-{slug}-{theme_name}">
  <title id="card-{slug}-{theme_name}">{esc(title)} — {esc(stack_line)}</title>
  <style>
    .sans {{ font-family: {FONT_SANS}; }}
    .mono {{ font-family: {FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>
  <rect x="1" y="1" width="898" height="110" rx="10" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1" />
  <rect x="1" y="22" width="3" height="68" rx="1.5" fill="{status_color}" />

  <text x="24" y="33" class="mono" font-size="10" font-weight="700" fill="{t["text_muted"]}" letter-spacing="0.7">{esc(index_tag)}</text>
  <g transform="translate({int(24 + idx_w + 12)}, 19)">
    <rect width="{pill_w:.0f}" height="20" rx="10" fill="{status_bg}" stroke="{t["border"]}" stroke-width="1" />
    <circle cx="11" cy="10" r="3" fill="{status_color}" />
    <text x="20" y="13.5" class="mono" font-size="9" font-weight="600" fill="{t["text_secondary"]}" letter-spacing="0.4">{esc(status_label)}</text>
  </g>

  <text x="24" y="66" class="sans" font-size="22" font-weight="700" fill="{t["text_primary"]}" letter-spacing="-0.4">{esc(title)}</text>
  <text x="24" y="90" class="mono" font-size="11" font-weight="500" fill="{t["text_tertiary"]}">{esc(stack_line)}</text>

  {metrics_svg}
</svg>
"""


def main() -> None:
    projects = [
        {
            "slug": "fablearc",
            "index_tag": "01 // FULL-STACK STREAMING & AI",
            "status_label": "LIVE · WEB + ELECTRON",
            "status_kind": "live",
            "title": "FABLEARC Cinema & Hybrid Recommender",
            "stack_line": "TypeScript · React 18 · FFmpeg 4K · Turso 3NF LibSQL · 9-Stage MMR",
            "metrics": [("~378 B", "3NF / USER"), ("4K + AAC", "LIVE REMUX"), ("41 / 41", "E2E + UNIT")],
        },
        {
            "slug": "smartload",
            "index_tag": "02 // BACKEND OPTIMIZATION SERVICE",
            "status_label": "MICROSERVICE · DOCKER",
            "status_kind": "arch",
            "title": "SmartLoad Multi-Constraint Optimizer",
            "stack_line": "Java 17 · Spring Boot 3.2 · Branch & Bound DFS · Jakarta Validation",
            "metrics": [("JAVA 17", "SPRING 3.2"), ("DFS B&B", "SUFFIX PRUNE"), ("18 / 18", "JUNIT SUITE")],
        },
        {
            "slug": "frontier",
            "index_tag": "03 // COMPUTATIONAL PHYSICS LAB",
            "status_label": "EXPLORATION · COLAB",
            "status_kind": "lab",
            "title": "Project Frontier — Cosmology & Ringdown",
            "stack_line": "Python 3.12 · SymPy · SciPy · Chebyshev Spectral · DESI DR2 BAO",
            "metrics": [("PY 3.12", "SYMPY · SCIPY"), ("DESI DR2", "BAO + SNE IA"), ("17 / 17", "PYTEST GATES")],
        },
        {
            "slug": "dsa",
            "index_tag": "04 // ALGORITHMIC FOUNDATIONS",
            "status_label": "ARCHIVE · JAVA",
            "status_kind": "arch",
            "title": "Algorithms & Competitive Programming",
            "stack_line": "Java · Codeforces Rounds · LeetCode Hard/Med · Graphs, DP & Trees",
            "metrics": [("461", "JAVA FILES"), ("450+", "LEETCODE"), ("6 STAR", "HACKERRANK")],
        },
    ]

    generated = []
    for theme_name, theme_tokens in THEMES.items():
        hero_path = ASSETS_DIR / f"hero-{theme_name}.svg"
        validate_and_write(hero_path, build_hero(theme_name, theme_tokens))
        generated.append(hero_path.name)

        sys_path = ASSETS_DIR / f"systems-{theme_name}.svg"
        validate_and_write(sys_path, build_systems(theme_name, theme_tokens))
        generated.append(sys_path.name)

        for proj in projects:
            card_path = ASSETS_DIR / f"card-{proj['slug']}-{theme_name}.svg"
            svg = build_project_card(
                proj["slug"],
                theme_name,
                theme_tokens,
                index_tag=proj["index_tag"],
                status_label=proj["status_label"],
                status_kind=proj["status_kind"],
                title=proj["title"],
                stack_line=proj["stack_line"],
                metrics=proj["metrics"],
            )
            validate_and_write(card_path, svg)
            generated.append(card_path.name)

    print(f"Generated and XML-validated {len(generated)} SVG assets in {ASSETS_DIR}:")
    for name in generated:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
