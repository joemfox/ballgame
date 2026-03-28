"""
Generates example standings images for each scenario without Docker/rembg.
Saves to /tmp/scenario_*.png.
Run from the repo root: python3 bluesky-bot/test_standings.py
"""
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import io

# ── Stub out modules that aren't available on the host ───────────────────────

# Stub rembg
rembg_stub = types.ModuleType("rembg")
rembg_stub.new_session = lambda name: None
rembg_stub.remove = lambda img, session=None: img
sys.modules["rembg"] = rembg_stub

# Stub requests (we'll replace _fetch_headshot anyway)
import unittest.mock as mock
requests_stub = mock.MagicMock()
sys.modules["requests"] = requests_stub

# Stub db with just SombreroStandingsEntry
@dataclass
class SombreroStandingsEntry:
    player_id: str
    player_name: str
    mlb_org: str
    sombrero_count: int

db_stub = types.ModuleType("db")
db_stub.SombreroStandingsEntry = SombreroStandingsEntry
sys.modules["db"] = db_stub

# Make HEADSHOT_CACHE_DIR point to /tmp so no /data path is needed
import tempfile
_tmp_cache = Path(tempfile.mkdtemp())

# ── Override font paths to use system fonts available on the host ─────────────
_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ── Now import images (will use our stubs) ────────────────────────────────────
# Suppress the module-level mkdir("/data/headshots") which requires Docker
sys.path.insert(0, str(Path(__file__).parent / "app"))
from unittest.mock import patch as _patch
with _patch("pathlib.Path.mkdir"):
    import images
images.HEADSHOT_CACHE_DIR = _tmp_cache
images.FONT_MONO = _MONO
images.FONT_BOLD = _BOLD

# ── Fake headshot: a simple colored circle silhouette ────────────────────────
_COLORS = [
    (180, 100, 80),
    (80, 140, 180),
    (120, 180, 80),
    (180, 80, 160),
    (180, 160, 60),
    (60, 160, 160),
    (160, 100, 180),
    (100, 180, 120),
    (180, 120, 60),
    (60, 120, 180),
    (160, 60, 80),
    (80, 160, 60),
]

def _fake_headshot(mlb_id: str) -> Image.Image:
    idx = int(mlb_id) % len(_COLORS)
    color = _COLORS[idx]
    w, h = images.PORTRAIT_W, images.PORTRAIT_H
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    # Draw a filled circle as a person silhouette placeholder
    r = min(w, h) // 2 - 2
    cx, cy = w // 2, h // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, 220))
    return img

images._fetch_headshot = _fake_headshot

# ── Build entry lists ─────────────────────────────────────────────────────────
def make_entries(spec):
    """spec: list of (sombrero_count, name, org, id_offset)"""
    return [
        SombreroStandingsEntry(
            player_id=str(i),
            player_name=name,
            mlb_org=org,
            sombrero_count=count,
        )
        for i, (count, name, org) in enumerate(spec)
    ]

from datetime import date
AS_OF = date(2026, 4, 15)
SEASON = 2026

scenarios = {
    "A_normal": make_entries([
        (4, "Josh Lowe", "TB"),
        (3, "Bo Bichette", "TOR"),
        (2, "Anthony Volpe", "NYY"),
        (2, "Gunnar Henderson", "BAL"),
        (1, "Max Kepler", "BOS"),
    ]),
    "B_small_tie": make_entries([
        (4, "Josh Lowe", "TB"),
        (4, "Bo Bichette", "TOR"),
        (4, "Anthony Volpe", "NYY"),
        (3, "Gunnar Henderson", "BAL"),
        (2, "Max Kepler", "BOS"),
    ]),
    "C_rank1_expands_5": make_entries([
        (5, "Player A", "ATL"),
        (5, "Player B", "BOS"),
        (5, "Player C", "CHC"),
        (5, "Player D", "DET"),
        (5, "Player E", "HOU"),
        (4, "Player F", "LAD"),
        (4, "Player G", "MIL"),
        (3, "Player H", "NYM"),
        (3, "Player I", "OAK"),
    ]),
    "D_large_tie_collapsed": make_entries(
        [(1, f"Player {chr(65+i)}", "MLB") for i in range(12)]
    ),
    "E_rank1_3_rank2_9": make_entries([
        (3, "Player A", "ATL"),
        (3, "Player B", "BOS"),
        (3, "Player C", "CHC"),
        (2, "Player D", "DET"),
        (2, "Player E", "HOU"),
        (2, "Player F", "LAD"),
        (2, "Player G", "MIL"),
        (2, "Player H", "NYM"),
        (2, "Player I", "OAK"),
        (2, "Player J", "PHI"),
        (2, "Player K", "SEA"),
        (2, "Player L", "STL"),
    ]),
    "F_rank1_3_rank2_7_no_expand": make_entries([
        (3, "Player A", "ATL"),
        (3, "Player B", "BOS"),
        (3, "Player C", "CHC"),
        (2, "Player D", "DET"),
        (2, "Player E", "HOU"),
        (2, "Player F", "LAD"),
        (2, "Player G", "MIL"),
        (2, "Player H", "NYM"),
        (2, "Player I", "OAK"),
        (2, "Player J", "PHI"),
    ]),
    "G_rank1_8_expands": make_entries(
        [(1, f"Player {chr(65+i)}", "MLB") for i in range(8)]
    ),
    "H_rank1_collapsed_then_more": make_entries(
        [(1, f"Player {chr(65+i)}", "MLB") for i in range(12)]
        + [(0, "Player M", "NYY"), (0, "Player N", "BOS")]
    ),
}

# ── Generate and save ─────────────────────────────────────────────────────────
out_dir = Path("/tmp/standings_test")
out_dir.mkdir(exist_ok=True)

for name, entries in scenarios.items():
    img_bytes = images.generate_standings_image(entries, SEASON, AS_OF)
    out_path = out_dir / f"scenario_{name}.png"
    out_path.write_bytes(img_bytes)
    rows = images._build_display_rows(entries)
    print(f"{name}: {len(rows)} rows → {out_path}")

print(f"\nAll images saved to {out_dir}/")
