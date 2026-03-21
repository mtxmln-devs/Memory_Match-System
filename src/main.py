# ──────────────────────────────────────────────
#  main.py  —  Entry point & main game loop
# ──────────────────────────────────────────────

from __future__ import annotations
import os
import sys
import math
import pygame

# Allow running as `python src/main.py` OR `python -m src.main`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import (
    WINDOW_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    C_BG, C_BOARD_BG, C_TEXT_LIGHT, C_TEXT_DIM, C_ACCENT,
    C_WIN_OVERLAY, C_STAR, C_CARD_BORDER,
    BOARD_X, BOARD_Y, BOARD_PIXEL_W, BOARD_PIXEL_H,
    SOUNDS_DIR, FONTS_DIR,
)
from src.game_manager import GameManager


# ── Sound loader ──────────────────────────────

def _load_sound(filename: str) -> pygame.mixer.Sound | None:
    path = os.path.join(SOUNDS_DIR, filename)
    if os.path.isfile(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    return None


# ── Font helper ───────────────────────────────

def _load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Try a nice system font; fall back to the built-in."""
    candidates = ["Baloo2", "Nunito", "Quicksand", "Comfortaa", "Verdana", "Arial"]
    for name in candidates:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            return font
        except Exception:
            continue
    return pygame.font.Font(None, size)


# ── HUD drawing ───────────────────────────────

def draw_hud(
    surface: pygame.Surface,
    moves: int,
    elapsed: float,
    matches: int,
    total_pairs: int,
    font_md: pygame.font.Font,
    font_sm: pygame.font.Font,
) -> None:
    # Top bar
    pygame.draw.rect(surface, (20, 28, 55), (0, 0, SCREEN_WIDTH, 52))
    pygame.draw.line(surface, C_CARD_BORDER, (0, 52), (SCREEN_WIDTH, 52), 1)

    minutes = int(elapsed) // 60
    seconds = int(elapsed) % 60
    time_str  = f"⏱  {minutes:02d}:{seconds:02d}"
    moves_str = f"🎯  Moves: {moves}"
    pairs_str = f"✅  {matches}/{total_pairs} pairs"

    for i, (txt, xpos) in enumerate([
        (time_str,  SCREEN_WIDTH // 2 - 200),
        (moves_str, SCREEN_WIDTH // 2 - 30),
        (pairs_str, SCREEN_WIDTH // 2 + 140),
    ]):
        label = font_sm.render(txt, True, C_TEXT_LIGHT)
        surface.blit(label, (xpos, 14))

    # Title
    title = font_md.render("Memory Match", True, C_ACCENT)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

    # Bottom hint
    hint = font_sm.render("R — Restart  •  ESC — Quit", True, C_TEXT_DIM)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 26))


# ── Win screen ────────────────────────────────

def draw_win_screen(
    surface: pygame.Surface,
    moves: int,
    elapsed: float,
    font_lg: pygame.font.Font,
    font_md: pygame.font.Font,
    font_sm: pygame.font.Font,
    tick: int,
) -> None:
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(C_WIN_OVERLAY)
    surface.blit(overlay, (0, 0))

    cx = SCREEN_WIDTH // 2

    # Floating stars animation
    for i in range(7):
        angle = tick * 0.04 + i * (2 * math.pi / 7)
        sx = int(cx + math.cos(angle) * 110)
        sy = int(SCREEN_HEIGHT // 2 + math.sin(angle) * 60 - 30)
        size = 8 + int(4 * math.sin(tick * 0.08 + i))
        pts = _star_points(sx, sy, size, size // 2, 5)
        pygame.draw.polygon(surface, C_STAR, pts)

    # Panel
    pw, ph = 420, 260
    px, py = cx - pw // 2, SCREEN_HEIGHT // 2 - ph // 2 - 10
    pygame.draw.rect(surface, (20, 28, 60), (px, py, pw, ph), border_radius=18)
    pygame.draw.rect(surface, C_ACCENT,    (px, py, pw, ph), width=2, border_radius=18)

    y = py + 30
    for txt, font, color in [
        ("🎉  You Won!",              font_lg, C_STAR),
        (f"Moves: {moves}",          font_md, C_TEXT_LIGHT),
        (f"Time:  {int(elapsed)//60:02d}:{int(elapsed)%60:02d}", font_md, C_TEXT_LIGHT),
        ("Press  R  to play again",  font_sm, C_TEXT_DIM),
    ]:
        surf = font.render(txt, True, color)
        surface.blit(surf, (cx - surf.get_width() // 2, y))
        y += surf.get_height() + 12


def _star_points(cx, cy, outer, inner, n):
    """Return vertices for an n-pointed star."""
    import math
    pts = []
    for i in range(2 * n):
        angle = math.pi / n * i - math.pi / 2
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


# ── Main ──────────────────────────────────────

def main() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    # Fonts
    font_lg = _load_font(46, bold=True)
    font_md = _load_font(28, bold=True)
    font_sm = _load_font(19)

    # Sounds
    snd_flip  = _load_sound("flip.mp3")
    snd_match = _load_sound("match.wav")

    # Game
    manager = GameManager()

    # Track previously selected count to trigger sound on new flip
    prev_sel_count = 0
    prev_match_count = 0

    tick = 0

    while True:
        dt = clock.tick(FPS)
        tick += 1

        # ── Events ────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    manager.reset()
                    prev_sel_count = 0
                    prev_match_count = 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                manager.handle_click(event.pos)

        # ── Update ────────────────────────────────
        manager.set_hovered(pygame.mouse.get_pos())
        manager.update()

        # Sound triggers
        sel = sum(1 for c in manager.cards if c.is_face_up and not c.state == "matched")
        new_match = manager.matches > prev_match_count

        if new_match:
            if snd_match:
                snd_match.play()
            prev_match_count = manager.matches

        # Flip sound: a new card just became face-up
        if not new_match and manager.moves > 0:
            cur_up = sum(1 for c in manager.cards if c.is_face_up)
            if cur_up > prev_sel_count:
                if snd_flip:
                    snd_flip.play()
        prev_sel_count = sum(1 for c in manager.cards if c.is_face_up)

        # ── Draw ──────────────────────────────────
        screen.fill(C_BG)

        # Board background panel
        pad = 14
        pygame.draw.rect(
            screen, (20, 28, 55),
            (BOARD_X - pad, BOARD_Y - pad, BOARD_PIXEL_W + pad * 2, BOARD_PIXEL_H + pad * 2),
            border_radius=16,
        )
        pygame.draw.rect(
            screen, C_CARD_BORDER,
            (BOARD_X - pad, BOARD_Y - pad, BOARD_PIXEL_W + pad * 2, BOARD_PIXEL_H + pad * 2),
            width=1, border_radius=16,
        )

        manager.draw(screen)

        draw_hud(
            screen,
            manager.moves,
            manager.elapsed_seconds,
            manager.matches,
            8,
            font_md,
            font_sm,
        )

        if manager.is_won:
            draw_win_screen(
                screen,
                manager.moves,
                manager.elapsed_seconds,
                font_lg, font_md, font_sm,
                tick,
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()