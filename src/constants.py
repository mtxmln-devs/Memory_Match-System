# ──────────────────────────────────────────────
#  constants.py  —  Game-wide configuration
# ──────────────────────────────────────────────

import os

# ── Window ────────────────────────────────────
WINDOW_TITLE  = "Memory Match"
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 640
FPS           = 60

# ── Grid ──────────────────────────────────────
GRID_COLS    = 4
GRID_ROWS    = 4
NUM_PAIRS    = (GRID_COLS * GRID_ROWS) // 2   # 8

# ── Card geometry ─────────────────────────────
CARD_WIDTH   = 110
CARD_HEIGHT  = 130
CARD_MARGIN  = 18        # gap between cards
CARD_RADIUS  = 12        # corner rounding

# Compute grid origin so the board is centred
BOARD_PIXEL_W = GRID_COLS * (CARD_WIDTH  + CARD_MARGIN) - CARD_MARGIN
BOARD_PIXEL_H = GRID_ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
BOARD_X = (SCREEN_WIDTH  - BOARD_PIXEL_W) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_PIXEL_H) // 2 + 28   # shift down a bit for HUD

# ── Timing ────────────────────────────────────
FLIP_SPEED        = 12    # degrees per frame during the flip animation
MISMATCH_HOLD_MS  = 900   # ms to show a non-matching pair before flipping back

# ── Colours  (R, G, B) ────────────────────────
C_BG            = (15,  20,  40)    # deep navy background
C_BOARD_BG      = (20,  28,  55)    # slightly lighter board area
C_CARD_BACK     = (35,  60, 120)    # face-down card fill
C_CARD_BACK_HI  = (50,  85, 160)    # hover highlight
C_CARD_BORDER   = (70, 110, 200)    # card border
C_CARD_FACE     = (240, 240, 255)   # face-up background
C_MATCHED       = (30,  180, 100)   # matched card tint
C_MATCHED_BDR   = (50,  220, 130)   # matched card border
C_TEXT_LIGHT    = (220, 225, 255)
C_TEXT_DIM      = (120, 130, 175)
C_ACCENT        = (100, 160, 255)
C_WIN_OVERLAY   = (0,   0,   0,  180)   # semi-transparent black (RGBA)
C_STAR          = (255, 215,   0)

# ── Card symbols (fallback when no image assets) ──
#    One emoji / symbol per pair  (8 total)
CARD_SYMBOLS = ["🦊", "🐬", "🌙", "⚡", "🍄", "🎯", "💎", "🔥"]

# ── Paths ─────────────────────────────────────
ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR  = os.path.join(ROOT_DIR, "assets")
IMAGES_DIR  = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR  = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR   = os.path.join(ASSETS_DIR, "fonts")