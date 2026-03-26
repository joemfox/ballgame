"""
Generates standings card images using Pillow + Geist fonts.
Fonts are converted from woff to TTF at Docker build time (see Dockerfile).
Player headshots are fetched from the MLB CDN; the placeholder silhouette
is detected by hash comparison and treated as absent.
"""
import hashlib
import io
from datetime import date

import requests
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove as rembg_remove

from db import SombreroStandingsEntry

# u2netp is ~4MB and fast on CPU; session is created once per process
_rembg_session = new_session("u2netp")

FONT_MONO  = "/app/assets/fonts/GeistMono-Regular.ttf"
FONT_BOLD  = "/app/assets/fonts/Geist-Bold.ttf"

BG         = (255, 255, 255, 255)
HEADER_BG  = (248, 248, 250, 255)
TEXT       = (15,  15,  20,  255)
SUBTEXT    = (120, 120, 140, 255)
GOLD       = (170, 120, 0,   255)
RULE       = (210, 210, 218, 255)
WATERMARK  = (150, 150, 165, 255)

TOP_N           = 5

SCALE           = 2
WIDTH           = 530  * SCALE
H_PAD           = 32   * SCALE
HEADER_H        = 110  * SCALE
DATE_BOTTOM_PAD = 6    * SCALE   # extra space between date and header rule
RULE_PAD        = 20   * SCALE   # horizontal margin for table row rules
TABLE_TOP_PAD   = 14   * SCALE   # extra space between header rule and first row
ROW_H           = 64   * SCALE
FOOTER_H        = 36   * SCALE
PORTRAIT_H      = 65   * SCALE
PORTRAIT_W      = 49   * SCALE

# Column x-positions
X_RANK     = H_PAD
X_PORTRAIT = H_PAD + 34 * SCALE
X_NAME     = X_PORTRAIT + PORTRAIT_W + 10 * SCALE
X_COUNT    = WIDTH - H_PAD - 20 * SCALE

HEADSHOT_URL = "https://securea.mlb.com/mlb/images/players/head_shot/{mlb_id}.jpg"

# Lazily populated: hash of the placeholder image the CDN returns for unknown players
_placeholder_hash: str | None = None


def _get_placeholder_hash() -> str | None:
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


def _fetch_headshot(mlb_id: str) -> Image.Image | None:
    try:
        r = requests.get(HEADSHOT_URL.format(mlb_id=mlb_id), timeout=4)
        if r.status_code != 200:
            return None
        placeholder = _get_placeholder_hash()
        if placeholder and hashlib.md5(r.content).hexdigest() == placeholder:
            return None
        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        img = rembg_remove(img, session=_rembg_session)
        img.thumbnail((PORTRAIT_W, PORTRAIT_H), Image.LANCZOS)
        return img
    except Exception:
        return None


def generate_standings_image(
    entries: list[SombreroStandingsEntry],
    season: int,
    as_of: date,
) -> bytes:
    entries  = entries[:TOP_N]
    n_rows   = TOP_N
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

    date_y    = rule_y - 30
    subhead_y = date_y - 34
    title_y   = subhead_y - 76
    draw.text((WIDTH // 2, title_y),   f"{season} Sombrero Cup",       fill=TEXT,    font=font_header,    anchor="mm")
    draw.text((WIDTH // 2, subhead_y), "Most games with 4+ Ks",        fill=SUBTEXT, font=font_subheader, anchor="mm")
    draw.text((WIDTH // 2, date_y),    as_of.strftime("as of %B %-d, %Y"), fill=SUBTEXT, font=font_subheader, anchor="mm")

    # ── Rows ──────────────────────────────────────────────────────────────────
    font_name  = ImageFont.truetype(FONT_MONO, 24 * SCALE)
    font_count = ImageFont.truetype(FONT_BOLD, 32 * SCALE)
    font_rank  = ImageFont.truetype(FONT_MONO, 18 * SCALE)

    for i in range(n_rows):
        y  = table_y + i * ROW_H
        cy = y + ROW_H // 2

        # Rule above each row (skip first — already have header rule)
        if i > 0:
            draw.line([(RULE_PAD, y), (WIDTH - RULE_PAD, y)], fill=RULE, width=1)

        if i >= len(entries):
            draw.text((X_RANK, cy), f"{i + 1}.", fill=SUBTEXT, font=font_rank, anchor="lm")
            if i == len(entries):
                draw.text((X_NAME, cy), "Everyone Else", fill=SUBTEXT, font=font_name, anchor="lm")
                draw.text((X_COUNT, cy), "0", fill=SUBTEXT, font=font_count, anchor="rm")
            continue

        entry = entries[i]

        # Rank
        draw.text((X_RANK, cy), f"{i + 1}.", fill=SUBTEXT, font=font_rank, anchor="lm")

        # Portrait (blank space reserved if unavailable)
        portrait = _fetch_headshot(entry.player_id)
        if portrait:
            pw, ph = portrait.size
            portrait_x = X_PORTRAIT
            portrait_y = cy - ph // 2
            img.paste(portrait, (portrait_x, portrait_y), mask=portrait)

        # Name + org
        org = f" ({entry.mlb_org})" if entry.mlb_org else ""
        draw.text((X_NAME, cy), f"{entry.player_name}{org}", fill=TEXT, font=font_name, anchor="lm")

        # Count
        draw.text((X_COUNT, cy), str(entry.sombrero_count), fill=GOLD, font=font_count, anchor="rm")

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
    for i, e in enumerate(entries, 1):
        org = f" ({e.mlb_org})" if e.mlb_org else ""
        lines.append(f"{i}. {e.player_name}{org} — {e.sombrero_count}")
    return " ".join(lines)
