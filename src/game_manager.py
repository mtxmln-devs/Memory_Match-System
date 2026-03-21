# ──────────────────────────────────────────────
#  game_manager.py  —  Deck, matching & scoring
# ──────────────────────────────────────────────

from __future__ import annotations
import os
import random
import time
from typing import Optional

import pygame

from src.constants import (
    GRID_COLS, GRID_ROWS, NUM_PAIRS,
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN,
    BOARD_X, BOARD_Y,
    CARD_SYMBOLS, IMAGES_DIR,
    MISMATCH_HOLD_MS,
)
from src.card import Card, CardState


class GameManager:
    """
    Owns the deck of cards, handles game state transitions,
    and tracks the player's score (moves + elapsed time).

    State machine
    -------------
    IDLE       — waiting for the first card click
    ONE_UP     — one card is face-up, waiting for second click
    TWO_UP     — two cards visible; checking match or waiting for hide delay
    WON        — all pairs matched
    """

    # ── Construction / Reset ──────────────────────

    def __init__(self) -> None:
        self._images: list[Optional[pygame.Surface]] = self._load_images()
        self.reset()

    def reset(self) -> None:
        """Shuffle a fresh deck and reset all counters."""
        self.cards: list[Card] = self._build_deck()
        self.moves        = 0
        self.matches      = 0
        self._selected: list[Card] = []      # 0, 1, or 2 cards currently flipped
        self._mismatch_timer: Optional[float] = None   # timestamp (ms) when mismatch was detected
        self._start_time  = time.time()
        self._elapsed     = 0.0
        self._game_over   = False

    # ── Properties ────────────────────────────────

    @property
    def is_won(self) -> bool:
        return self.matches == NUM_PAIRS

    @property
    def elapsed_seconds(self) -> float:
        if self._game_over:
            return self._elapsed
        return time.time() - self._start_time

    @property
    def any_animating(self) -> bool:
        return any(c.is_animating for c in self.cards)

    # ── Public methods ────────────────────────────

    def handle_click(self, pos: tuple[int, int]) -> None:
        """
        Called when the player clicks the screen.
        Ignores clicks while:
          - an animation is running
          - two cards are already up (mismatch hold)
          - the game is won
        """
        if self.is_won:
            return
        if self.any_animating:
            return
        if len(self._selected) == 2:
            return   # still in mismatch-hold; update() will clear them

        card = self._card_at(pos)
        if card is None:
            return
        if not card.is_flippable:
            return
        if card in self._selected:
            return  # same card double-clicked

        card.flip_up()
        self._selected.append(card)

        if len(self._selected) == 2:
            self.moves += 1
            self._evaluate_pair()

    def update(self) -> None:
        """
        Called once per frame.
        Advances card animations and handles the mismatch delay.
        """
        for card in self.cards:
            card.update()

        # After mismatch hold expires, flip both cards back
        if self._mismatch_timer is not None:
            now = pygame.time.get_ticks()
            if now - self._mismatch_timer >= MISMATCH_HOLD_MS:
                for card in self._selected:
                    card.flip_down()
                self._selected.clear()
                self._mismatch_timer = None

        if self.is_won and not self._game_over:
            self._game_over = True
            self._elapsed = time.time() - self._start_time

    def set_hovered(self, pos: tuple[int, int]) -> None:
        """Update hover highlight for all cards."""
        for card in self.cards:
            card.hovered = (
                card.is_flippable
                and card.rect.collidepoint(pos)
                and len(self._selected) < 2
                and not self.any_animating
            )

    def draw(self, surface: pygame.Surface) -> None:
        for card in self.cards:
            card.draw(surface)

    # ── Private helpers ───────────────────────────

    def _evaluate_pair(self) -> None:
        a, b = self._selected
        if a.pair_id == b.pair_id:
            # Match! Mark them immediately (animation completes naturally)
            # We wait until animations finish in update; for now just schedule
            self._schedule_match(a, b)
        else:
            # Mismatch — start the hold timer
            self._mismatch_timer = pygame.time.get_ticks()

    def _schedule_match(self, a: Card, b: Card) -> None:
        """
        Marks both cards as matched after their flip animations finish.
        We poll in update() — when neither is animating, we mark them.
        """
        # Simple approach: mark matched right away (they're already flipping up)
        # The visual is "face-up + green tint" which is fine once they land.
        # We use a small coroutine-like check instead.
        self._pending_match = (a, b)
        self._selected.clear()
        self._check_pending_match()

    def _check_pending_match(self) -> None:
        a, b = self._pending_match
        a.mark_matched()
        b.mark_matched()
        self.matches += 1
        self._pending_match = None

    def update(self) -> None:  # noqa: F811  (intentional override for match check)
        for card in self.cards:
            card.update()

        # Resolve pending match once animations settle
        if hasattr(self, "_pending_match") and self._pending_match:
            a, b = self._pending_match
            if not a.is_animating and not b.is_animating:
                self._check_pending_match()

        # After mismatch hold expires, flip both cards back
        if self._mismatch_timer is not None:
            now = pygame.time.get_ticks()
            if now - self._mismatch_timer >= MISMATCH_HOLD_MS:
                if not self.any_animating:
                    for card in self._selected:
                        card.flip_down()
                    self._selected.clear()
                    self._mismatch_timer = None

        if self.is_won and not self._game_over:
            self._game_over = True
            self._elapsed = time.time() - self._start_time

    def _card_at(self, pos: tuple[int, int]) -> Optional[Card]:
        for card in self.cards:
            if card.rect.collidepoint(pos):
                return card
        return None

    def _build_deck(self) -> list[Card]:
        """
        Create 2×NUM_PAIRS cards, shuffle, assign grid positions.
        """
        pairs: list[tuple[int, str, Optional[pygame.Surface]]] = []
        for i in range(NUM_PAIRS):
            symbol = CARD_SYMBOLS[i % len(CARD_SYMBOLS)]
            img    = self._images[i] if i < len(self._images) else None
            pairs.append((i, symbol, img))

        # Duplicate each pair
        deck_data = pairs + pairs
        random.shuffle(deck_data)

        cards: list[Card] = []
        for idx, (pair_id, symbol, img) in enumerate(deck_data):
            col = idx % GRID_COLS
            row = idx // GRID_COLS
            x = BOARD_X + col * (CARD_WIDTH  + CARD_MARGIN)
            y = BOARD_Y + row * (CARD_HEIGHT + CARD_MARGIN)
            cards.append(Card(pair_id, symbol, col, row, x, y, image=img))

        return cards

    @staticmethod
    def _load_images() -> list[Optional[pygame.Surface]]:
        """
        Try to load icon_1.png … icon_8.png from assets/images/.
        Returns a list with None for any missing file.
        """
        images: list[Optional[pygame.Surface]] = []
        for i in range(1, NUM_PAIRS + 1):
            path = os.path.join(IMAGES_DIR, f"icon_{i}.png")
            if os.path.isfile(path):
                try:
                    images.append(pygame.image.load(path).convert_alpha())
                except Exception:
                    images.append(None)
            else:
                images.append(None)
        return images