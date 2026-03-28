"""
Generates standings card images using Pillow + Geist fonts.
Fonts are converted from woff to TTF at Docker build time (see Dockerfile).
Player headshots are fetched from the MLB CDN; the placeholder silhouette
is detected by hash comparison and treated as absent.
"""
from __future__ import annotations

import hashlib
import io
from datetime import date
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove as rembg_remove

from typing import Optional

from db import SombreroStandingsEntry

HEADSHOT_CACHE_DIR = Path("/data/headshots")
HEADSHOT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# u2netp is ~4MB; session is created lazily on first headshot fetch
_rembg_session = None


def _get_rembg_session():
    global _rembg_session
    if _rembg_session is None:
        _rembg_session = new_session("u2netp")
    return _rembg_session

FONT_MONO  = "/app/assets/fonts/GeistMono-Regular.ttf"
FONT_BOLD  = "/app/assets/fonts/Geist-Bold.ttf"

BG         = (255, 255, 255, 255)
HEADER_BG  = (248, 248, 250, 255)
TEXT       = (15,  15,  20,  255)
SUBTEXT    = (120, 120, 140, 255)
GOLD       = (170, 120, 0,   255)
RULE       = (210, 210, 218, 255)
WATERMARK  = (150, 150, 165, 255)

MIN_DISPLAY_ROWS = 5
MAX_DISPLAY_ROWS = 10
MAX_RANK_GROUPS  = 5

SCALE           = 2
WIDTH           = 530  * SCALE
H_PAD           = 32   * SCALE
HEADER_H        = 110  * SCALE
DATE_BOTTOM_PAD = 6    * SCALE   # extra space between date and header rule
RULE_PAD        = 20   * SCALE   # horizontal margin for table row rules
TABLE_TOP_PAD   = 13   * SCALE   # extra space between header rule and first row
ROW_H           = 73   * SCALE
FOOTER_H        = 36   * SCALE
PORTRAIT_H      = 65   * SCALE
PORTRAIT_W      = 49   * SCALE
MINI_PORTRAIT_W = 30   * SCALE
MINI_PORTRAIT_H = int(PORTRAIT_H * MINI_PORTRAIT_W / PORTRAIT_W)

# Column x-positions
X_RANK     = H_PAD
X_PORTRAIT = H_PAD + 34 * SCALE
X_NAME     = X_PORTRAIT + PORTRAIT_W + 10 * SCALE
X_COUNT    = WIDTH - H_PAD - 20 * SCALE

HEADSHOT_URL = "https://securea.mlb.com/mlb/images/players/head_shot/{mlb_id}.jpg"

# Lazily populated: hash of the placeholder image the CDN returns for unknown players
_placeholder_hash: Optional[str] = None


def _get_placeholder_hash() -> Optional[str]:
    """Fetch the placeholder once using a known-absent player ID and cache its hash."""
    global _placeholder_hash
    if _placeholder_hash is None:
        try:
            r = requests.get(HEADSHOT_URL.format(mlb_id=0), timeout=5)
            if r.status_code == 200:
                _placeholder_hash = hashlib.md5(r.content).hexdigest()
        except Exception:
            pass
    return _placeholder_hash


def _fetch_headshot(mlb_id: str) -> Optional[Image.Image]:
    cache_path = HEADSHOT_CACHE_DIR / f"{mlb_id}.png"
    if cache_path.exists():
        try:
            return Image.open(cache_path).convert("RGBA")
        except Exception:
            cache_path.unlink(missing_ok=True)

    try:
        r = requests.get(HEADSHOT_URL.format(mlb_id=mlb_id), timeout=4)
        if r.status_code != 200:
            return None
        placeholder = _get_placeholder_hash()
        if placeholder and hashlib.md5(r.content).hexdigest() == placeholder:
            return None
        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        img = rembg_remove(img, session=_get_rembg_session())
        img.thumbnail((PORTRAIT_W, PORTRAIT_H), Image.LANCZOS)
        img.save(cache_path, format="PNG")
        return img
    except Exception:
        return None


def _build_display_rows(entries: list[SombreroStandingsEntry]) -> list[dict]:
    """
    Groups entries by sombrero_count and returns a list of display row dicts.

    Only rank 1 (first-place) expands beyond MIN_DISPLAY_ROWS rows. All other
    rank groups share whatever space remains up to the target row count.

    Row dict keys:
      type      "individual" | "combined" | "empty"
      rank      int
      is_tied   bool  (individual and combined only)
      entry     SombreroStandingsEntry  (individual only)
      group     list[SombreroStandingsEntry]  (combined only)
    """
    # Group consecutive entries with the same sombrero_count
    groups: list[tuple[int, list[SombreroStandingsEntry]]] = []
    for entry in entries:
        if groups and groups[-1][0] == entry.sombrero_count:
            groups[-1][1].append(entry)
        else:
            groups.append((entry.sombrero_count, [entry]))

    rows: list[dict] = []
    rank = 1

    if not groups:
        # No entries at all — fall through to padding
        pass
    else:
        # ── Rank 1 group ──────────────────────────────────────────────────────
        _, rank1_entries = groups[0]
        is_tied = len(rank1_entries) > 1
        if len(rank1_entries) <= MAX_DISPLAY_ROWS:
            for entry in rank1_entries:
                rows.append({"type": "individual", "rank": rank, "is_tied": is_tied, "entry": entry})
        else:
            rows.append({"type": "combined", "rank": rank, "is_tied": is_tied, "group": rank1_entries})
        rank += len(rank1_entries)

        # Target total rows: rank 1 may expand beyond MIN_DISPLAY_ROWS
        target = max(MIN_DISPLAY_ROWS, len(rows))
        remaining = target - len(rows)

        # ── Rank 2+ groups ────────────────────────────────────────────────────
        rank_groups_shown = 1
        for _, group_entries in groups[1:]:
            if remaining <= 0 or rank_groups_shown >= MAX_RANK_GROUPS:
                break
            is_tied = len(group_entries) > 1
            if len(group_entries) <= remaining:
                for entry in group_entries:
                    rows.append({"type": "individual", "rank": rank, "is_tied": is_tied, "entry": entry})
                remaining -= len(group_entries)
            else:
                rows.append({"type": "combined", "rank": rank, "is_tied": is_tied, "group": group_entries})
                remaining -= 1
            rank += len(group_entries)
            rank_groups_shown += 1

    # ── Pad to target (at least MIN_DISPLAY_ROWS) ─────────────────────────────
    target = max(MIN_DISPLAY_ROWS, len(rows))
    while len(rows) < target:
        rows.append({"type": "empty", "rank": rank})
        rank += 1

    return rows


def generate_standings_image(
    entries: list[SombreroStandingsEntry],
    season: int,
    as_of: date,
) -> bytes:
    display_rows = _build_display_rows(entries)
    n_rows   = len(display_rows)
    rule_y   = HEADER_H + DATE_BOTTOM_PAD
    table_y  = rule_y + TABLE_TOP_PAD
    height   = table_y + ROW_H * n_rows + FOOTER_H

    img  = Image.new("RGBA", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)

    # ── Header ────────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, WIDTH, rule_y], fill=HEADER_BG)
    draw.line([(0, rule_y), (WIDTH, rule_y)], fill=RULE, width=1)

    font_header    = ImageFont.truetype(FONT_BOLD, 32 * SCALE)
    font_subheader = ImageFont.truetype(FONT_MONO, 15 * SCALE)
    font_name      = ImageFont.truetype(FONT_MONO, 24 * SCALE)
    font_count     = ImageFont.truetype(FONT_BOLD, 32 * SCALE)
    font_rank      = ImageFont.truetype(FONT_MONO, 18 * SCALE)

    date_y    = rule_y - 30
    subhead_y = date_y - 34
    title_y   = subhead_y - 76
    draw.text((WIDTH // 2, title_y),   f"{season} Sombrero Cup",           fill=TEXT,    font=font_header,    anchor="mm")
    draw.text((WIDTH // 2, subhead_y), "Most games with 4+ Ks",            fill=SUBTEXT, font=font_subheader, anchor="mm")
    draw.text((WIDTH // 2, date_y),    as_of.strftime("as of %B %-d, %Y"), fill=SUBTEXT, font=font_subheader, anchor="mm")

    # ── Rows ──────────────────────────────────────────────────────────────────
    first_empty_drawn = False

    for i, row in enumerate(display_rows):
        y  = table_y + i * ROW_H
        cy = y + ROW_H // 2

        if i > 0:
            draw.line([(RULE_PAD, y), (WIDTH - RULE_PAD, y)], fill=RULE, width=1)

        rank = row["rank"]

        if row["type"] == "empty":
            draw.text((X_RANK, cy), f"{rank}.", fill=SUBTEXT, font=font_rank, anchor="lm")
            if not first_empty_drawn:
                draw.text((X_NAME, cy), "Everyone Else", fill=SUBTEXT, font=font_name, anchor="lm")
                draw.text((X_COUNT, cy), "0", fill=SUBTEXT, font=font_count, anchor="rm")
                first_empty_drawn = True
            continue

        is_tied = row["is_tied"]
        rank_label = f"T{rank}." if is_tied else f"{rank}."
        draw.text((X_RANK, cy), rank_label, fill=SUBTEXT, font=font_rank, anchor="lm")

        if row["type"] == "individual":
            entry = row["entry"]
            portrait = _fetch_headshot(entry.player_id)
            if portrait:
                pw, ph = portrait.size
                img.paste(portrait, (X_PORTRAIT, cy - ph // 2), mask=portrait)
            draw.text((X_NAME, cy), entry.player_name, fill=TEXT, font=font_name, anchor="lm")
            draw.text((X_COUNT, cy), str(entry.sombrero_count), fill=GOLD, font=font_count, anchor="rm")

        elif row["type"] == "combined":
            group = row["group"]
            n = len(group)
            count_val = group[0].sombrero_count
            count_str = str(count_val)
            label = f"{n} players"

            # Measure text widths to compute headshot area
            count_w = int(font_count.getlength(count_str))
            label_w = int(font_rank.getlength(label))
            gap = 8 * SCALE
            # Headshots fill from X_PORTRAIT up to where the label begins
            avail = X_COUNT - count_w - gap - label_w - gap - X_PORTRAIT
            mini_w = min(MINI_PORTRAIT_W, max(2 * SCALE, avail))
            mini_h = int(PORTRAIT_H * mini_w / PORTRAIT_W)
            step = 0 if n <= 1 else max(2 * SCALE, (avail - mini_w) // (n - 1))

            # Fetch all portraits upfront
            portraits = [_fetch_headshot(e.player_id) for e in group]

            # Draw back-to-front so the leftmost headshot is on top
            for j in range(n - 1, -1, -1):
                p = portraits[j]
                if p:
                    pm = p.resize((mini_w, mini_h), Image.LANCZOS)
                    px = X_PORTRAIT + j * step
                    py = cy - mini_h // 2
                    img.paste(pm, (px, py), mask=pm)

            # "N players" label immediately after the last headshot
            end_x = X_PORTRAIT + (n - 1) * step + mini_w + gap
            draw.text((end_x, cy), label, fill=SUBTEXT, font=font_rank, anchor="lm")
            draw.text((X_COUNT, cy), count_str, fill=GOLD, font=font_count, anchor="rm")

    # ── Watermark ─────────────────────────────────────────────────────────────
    wm_layer = Image.new("RGBA", (WIDTH, height), (0, 0, 0, 0))
    wm_draw  = ImageDraw.Draw(wm_layer)
    font_wm  = ImageFont.truetype(FONT_MONO, 12 * SCALE)
    wm_draw.text(
        (WIDTH - H_PAD, height - FOOTER_H // 2),
        "bsky @sombrero.quest",
        fill=WATERMARK, font=font_wm, anchor="rm",
    )
    img = Image.alpha_composite(img, wm_layer)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def standings_alt_text(
    entries: list[SombreroStandingsEntry], season: int, as_of: date
) -> str:
    date_str = as_of.strftime("%B %-d, %Y")
    lines = [f"{season} Sombrero Leaders as of {date_str}:"]
    for row in _build_display_rows(entries):
        if row["type"] == "empty":
            break
        rank = row["rank"]
        if row["type"] == "individual":
            e = row["entry"]
            label = f"T{rank}" if row["is_tied"] else str(rank)
            org = f" ({e.mlb_org})" if e.mlb_org else ""
            lines.append(f"{label}. {e.player_name}{org} — {e.sombrero_count}")
        elif row["type"] == "combined":
            group = row["group"]
            names = ", ".join(e.player_name for e in group)
            lines.append(f"T{rank}. {len(group)} players ({names}) — {group[0].sombrero_count}")
    return " ".join(lines)
