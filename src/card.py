# ──────────────────────────────────────────────
#  card.py  —  Card class & individual rendering
# ──────────────────────────────────────────────

from __future__ import annotations
import pygame
from src.constants import (
    CARD_WIDTH, CARD_HEIGHT, CARD_RADIUS,
    C_CARD_BACK, C_CARD_BACK_HI, C_CARD_BORDER,
    C_CARD_FACE, C_MATCHED, C_MATCHED_BDR,
    C_TEXT_LIGHT, FLIP_SPEED,
)


class CardState:
    """Simple enum-style constants for card state."""
    FACE_DOWN  = "face_down"
    FLIPPING_UP   = "flipping_up"    # animating → face-up
    FACE_UP    = "face_up"
    FLIPPING_DOWN = "flipping_down"  # animating → face-down
    MATCHED    = "matched"


class Card:
    """
    Represents a single memory-match card.

    Attributes
    ----------
    pair_id : int
        Shared by exactly two cards in the deck (0–7).
    image : pygame.Surface | None
        The card-face graphic. If None the symbol string is rendered instead.
    symbol : str
        Fallback text/emoji symbol when no image is available.
    col, row : int
        Grid position (0-based).
    rect : pygame.Rect
        Pixel bounding rectangle on screen.
    state : str
        One of CardState.*
    flip_angle : float
        Current pseudo-3-D flip angle (0 = face-down, 90 = fully flipped).
        Rendered by horizontally squishing the card surface.
    hovered : bool
        True while the mouse cursor is over this card.
    """

    def __init__(
        self,
        pair_id: int,
        symbol: str,
        col: int,
        row: int,
        x: int,
        y: int,
        image: pygame.Surface | None = None,
    ) -> None:
        self.pair_id   = pair_id
        self.symbol    = symbol
        self.image     = image
        self.col       = col
        self.row       = row
        self.rect      = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.state     = CardState.FACE_DOWN
        self.flip_angle: float = 0.0    # 0 → 90 → 0 during a flip cycle
        self.hovered   = False

        # Pre-render the back & face surfaces at full size
        self._surf_back = self._make_back_surface(highlighted=False)
        self._surf_back_hi = self._make_back_surface(highlighted=True)
        self._surf_face = self._make_face_surface()

    # ── Public API ────────────────────────────────

    def flip_up(self) -> None:
        """Start animating towards face-up."""
        if self.state == CardState.FACE_DOWN:
            self.state = CardState.FLIPPING_UP

    def flip_down(self) -> None:
        """Start animating towards face-down."""
        if self.state == CardState.FACE_UP:
            self.state = CardState.FLIPPING_DOWN

    def mark_matched(self) -> None:
        self.state = CardState.MATCHED
        self.flip_angle = 0.0
        self._surf_face = self._make_face_surface(matched=True)

    @property
    def is_face_up(self) -> bool:
        return self.state in (CardState.FACE_UP, CardState.MATCHED)

    @property
    def is_animating(self) -> bool:
        return self.state in (CardState.FLIPPING_UP, CardState.FLIPPING_DOWN)

    @property
    def is_flippable(self) -> bool:
        """Can the player click this card right now?"""
        return self.state == CardState.FACE_DOWN

    # ── Update / Draw ─────────────────────────────

    def update(self) -> None:
        """Advance the flip animation by one frame."""
        if self.state == CardState.FLIPPING_UP:
            self.flip_angle += FLIP_SPEED
            if self.flip_angle >= 90:
                self.flip_angle = 0.0
                self.state = CardState.FACE_UP

        elif self.state == CardState.FLIPPING_DOWN:
            self.flip_angle += FLIP_SPEED
            if self.flip_angle >= 90:
                self.flip_angle = 0.0
                self.state = CardState.FACE_DOWN

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the card onto *surface* with pseudo-3-D squish effect."""
        # Choose which side to show
        if self.state == CardState.FACE_DOWN:
            src = self._surf_back_hi if self.hovered else self._surf_back
        elif self.state == CardState.FLIPPING_UP:
            # First half: shrink back surface → then switch to face
            src = self._surf_back if self.flip_angle < 45 else self._surf_face
        elif self.state == CardState.FLIPPING_DOWN:
            src = self._surf_face if self.flip_angle < 45 else self._surf_back
        else:  # FACE_UP or MATCHED
            src = self._surf_face

        # Squish the width to simulate 3-D rotation
        if self.is_animating:
            half = 45.0
            progress = abs(self.flip_angle - half) / half   # 1 → 0 → 1
            drawn_w = max(4, int(CARD_WIDTH * progress))
        else:
            drawn_w = CARD_WIDTH

        scaled = pygame.transform.scale(src, (drawn_w, CARD_HEIGHT))
        dest_x = self.rect.x + (CARD_WIDTH - drawn_w) // 2
        surface.blit(scaled, (dest_x, self.rect.y))

    # ── Private helpers ───────────────────────────

    def _make_back_surface(self, highlighted: bool) -> pygame.Surface:
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        fill  = C_CARD_BACK_HI if highlighted else C_CARD_BACK
        bdr   = C_CARD_BORDER
        pygame.draw.rect(surf, fill, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=CARD_RADIUS)
        pygame.draw.rect(surf, bdr,  (0, 0, CARD_WIDTH, CARD_HEIGHT), width=2, border_radius=CARD_RADIUS)

        # Simple decorative pattern on the back
        cx, cy = CARD_WIDTH // 2, CARD_HEIGHT // 2
        for r in (40, 28, 16):
            pygame.draw.circle(surf, (*bdr, 60), (cx, cy), r, 1)
        # Diamond
        pts = [(cx, cy - 22), (cx + 16, cy), (cx, cy + 22), (cx - 16, cy)]
        pygame.draw.polygon(surf, (*bdr, 80), pts, 1)
        return surf

    def _make_face_surface(self, matched: bool = False) -> pygame.Surface:
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        fill = C_MATCHED      if matched else C_CARD_FACE
        bdr  = C_MATCHED_BDR  if matched else C_CARD_BORDER
        pygame.draw.rect(surf, fill, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=CARD_RADIUS)
        pygame.draw.rect(surf, bdr,  (0, 0, CARD_WIDTH, CARD_HEIGHT), width=2, border_radius=CARD_RADIUS)

        if self.image:
            img = pygame.transform.smoothscale(self.image, (72, 72))
            surf.blit(img, ((CARD_WIDTH - 72) // 2, (CARD_HEIGHT - 72) // 2))
        else:
            # Render emoji / text symbol
            font_size = 52
            try:
                font = pygame.font.SysFont("segoeuiemoji,applesymbolsfallback,symbola,notoemoji", font_size)
            except Exception:
                font = pygame.font.SysFont(None, font_size)
            text_surf = font.render(self.symbol, True, C_TEXT_LIGHT)
            tx = (CARD_WIDTH  - text_surf.get_width())  // 2
            ty = (CARD_HEIGHT - text_surf.get_height()) // 2
            surf.blit(text_surf, (tx, ty))

        return surf