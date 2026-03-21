# ──────────────────────────────────────────────
#  tests/test_logic.py  —  Unit tests
# ──────────────────────────────────────────────
#
#  Run with:  python -m pytest tests/
#
import sys
import os
import types

# ── Minimal pygame stub so tests run without a display ────────────────────────
def _make_pygame_stub():
    pg = types.ModuleType("pygame")
    pg.SRCALPHA = 65536

    class Rect:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.width, self.height = x, y, w, h
        def collidepoint(self, pos):
            return self.x <= pos[0] < self.x + self.width and \
                   self.y <= pos[1] < self.y + self.height

    class Surface:
        def __init__(self, size, flags=0): pass
        def fill(self, *a, **kw): pass
        def blit(self, *a, **kw): pass

    class _Draw:
        @staticmethod
        def rect(*a, **kw): pass
        @staticmethod
        def circle(*a, **kw): pass
        @staticmethod
        def polygon(*a, **kw): pass
        @staticmethod
        def line(*a, **kw): pass

    class _Font:
        def render(self, *a, **kw): return Surface((1, 1))
        def get_height(self): return 10

    class _FontModule:
        @staticmethod
        def SysFont(*a, **kw): return _Font()
        @staticmethod
        def Font(*a, **kw): return _Font()

    class _Time:
        @staticmethod
        def get_ticks(): return 0

    class _Transform:
        @staticmethod
        def scale(surf, size): return surf
        @staticmethod
        def smoothscale(surf, size): return surf

    pg.Rect      = Rect
    pg.Surface   = Surface
    pg.draw      = _Draw
    pg.font      = _FontModule
    pg.time      = _Time
    pg.transform = _Transform
    pg.image     = types.SimpleNamespace(load=lambda p: Surface((1,1)))
    sys.modules["pygame"] = pg
    return pg

_make_pygame_stub()

# Now safe to import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.card import Card, CardState
from src.game_manager import GameManager
from src import constants as C


# ══════════════════════════════════════════════
#  Card tests
# ══════════════════════════════════════════════

class TestCardInitialState:
    def _make_card(self):
        return Card(pair_id=0, symbol="🔥", col=0, row=0, x=0, y=0)

    def test_starts_face_down(self):
        card = self._make_card()
        assert card.state == CardState.FACE_DOWN

    def test_starts_not_face_up(self):
        card = self._make_card()
        assert not card.is_face_up

    def test_starts_flippable(self):
        card = self._make_card()
        assert card.is_flippable

    def test_rect_position(self):
        card = Card(pair_id=1, symbol="⚡", col=2, row=1, x=50, y=80)
        assert card.rect.x == 50
        assert card.rect.y == 80
        assert card.rect.width  == C.CARD_WIDTH
        assert card.rect.height == C.CARD_HEIGHT


class TestCardFlipUp:
    def _make_card(self):
        return Card(pair_id=0, symbol="🎯", col=0, row=0, x=0, y=0)

    def test_flip_up_changes_state(self):
        card = self._make_card()
        card.flip_up()
        assert card.state == CardState.FLIPPING_UP

    def test_flip_up_not_flippable_while_animating(self):
        card = self._make_card()
        card.flip_up()
        assert not card.is_flippable

    def test_flip_up_completes_after_enough_updates(self):
        card = self._make_card()
        card.flip_up()
        for _ in range(100):   # well beyond 90 / FLIP_SPEED frames
            card.update()
        assert card.state == CardState.FACE_UP

    def test_face_up_after_animation(self):
        card = self._make_card()
        card.flip_up()
        for _ in range(100):
            card.update()
        assert card.is_face_up


class TestCardFlipDown:
    def _flipped_up_card(self):
        card = Card(pair_id=0, symbol="💎", col=0, row=0, x=0, y=0)
        card.flip_up()
        for _ in range(100):
            card.update()
        return card

    def test_flip_down_from_face_up(self):
        card = self._flipped_up_card()
        card.flip_down()
        assert card.state == CardState.FLIPPING_DOWN

    def test_flip_down_completes(self):
        card = self._flipped_up_card()
        card.flip_down()
        for _ in range(100):
            card.update()
        assert card.state == CardState.FACE_DOWN

    def test_flippable_again_after_flip_down(self):
        card = self._flipped_up_card()
        card.flip_down()
        for _ in range(100):
            card.update()
        assert card.is_flippable


class TestCardMatchedState:
    def test_mark_matched(self):
        card = Card(pair_id=0, symbol="🍄", col=0, row=0, x=0, y=0)
        card.flip_up()
        for _ in range(100):
            card.update()
        card.mark_matched()
        assert card.state == CardState.MATCHED
        assert card.is_face_up
        assert not card.is_flippable
        assert not card.is_animating


# ══════════════════════════════════════════════
#  GameManager tests
# ══════════════════════════════════════════════

class TestGameManagerInit:
    def test_correct_number_of_cards(self):
        gm = GameManager()
        assert len(gm.cards) == C.GRID_COLS * C.GRID_ROWS

    def test_correct_number_of_pairs(self):
        gm = GameManager()
        from collections import Counter
        counts = Counter(card.pair_id for card in gm.cards)
        assert len(counts) == C.NUM_PAIRS
        assert all(v == 2 for v in counts.values())

    def test_all_cards_face_down(self):
        gm = GameManager()
        assert all(card.state == CardState.FACE_DOWN for card in gm.cards)

    def test_starts_with_zero_moves(self):
        gm = GameManager()
        assert gm.moves == 0

    def test_starts_with_zero_matches(self):
        gm = GameManager()
        assert gm.matches == 0

    def test_not_won_at_start(self):
        gm = GameManager()
        assert not gm.is_won


class TestGameManagerCardLayout:
    def test_all_cards_have_unique_positions(self):
        gm = GameManager()
        positions = [(c.rect.x, c.rect.y) for c in gm.cards]
        assert len(set(positions)) == len(positions)

    def test_cards_within_board_bounds(self):
        gm = GameManager()
        for card in gm.cards:
            assert card.rect.x >= C.BOARD_X
            assert card.rect.y >= C.BOARD_Y
            assert card.rect.right  <= C.BOARD_X + C.BOARD_PIXEL_W + C.CARD_WIDTH
            assert card.rect.bottom <= C.BOARD_Y + C.BOARD_PIXEL_H + C.CARD_HEIGHT


class TestGameManagerClick:
    def _click_card(self, gm, card):
        """Simulate clicking the centre of a card."""
        pos = (card.rect.centerx, card.rect.centery)
        gm.handle_click(pos)

    def test_click_flips_card(self):
        gm = GameManager()
        card = gm.cards[0]
        self._click_card(gm, card)
        assert card.state in (CardState.FLIPPING_UP, CardState.FACE_UP)

    def test_click_increments_moves_on_second_card(self):
        gm = GameManager()
        # Finish first card's animation
        card0 = gm.cards[0]
        self._click_card(gm, card0)
        for _ in range(100): gm.update()

        card1 = gm.cards[1]
        self._click_card(gm, card1)
        for _ in range(100): gm.update()

        assert gm.moves == 1

    def test_cant_click_same_card_twice(self):
        gm = GameManager()
        card = gm.cards[0]
        self._click_card(gm, card)
        for _ in range(100): gm.update()
        # Click same card again — should not change state
        state_before = card.state
        self._click_card(gm, card)
        assert card.state == state_before

    def test_cant_click_third_card_while_two_up(self):
        gm = GameManager()
        c0, c1, c2 = gm.cards[0], gm.cards[1], gm.cards[2]
        self._click_card(gm, c0)
        for _ in range(100): gm.update()
        self._click_card(gm, c1)
        # Don't run update (hold state with 2 cards up)
        state_before = c2.state
        self._click_card(gm, c2)
        assert c2.state == state_before


class TestGameManagerMatching:
    def _find_pair(self, gm) -> tuple[Card, Card]:
        """Return two cards that share a pair_id."""
        seen: dict[int, Card] = {}
        for card in gm.cards:
            if card.pair_id in seen:
                return seen[card.pair_id], card
            seen[card.pair_id] = card
        raise RuntimeError("No pair found")

    def _click_pos(self, gm, card):
        gm.handle_click((card.rect.centerx, card.rect.centery))

    def test_matching_pair_increments_matches(self):
        gm = GameManager()
        a, b = self._find_pair(gm)
        self._click_pos(gm, a)
        for _ in range(200): gm.update()
        self._click_pos(gm, b)
        for _ in range(200): gm.update()
        assert gm.matches == 1

    def test_matching_pair_marked_matched(self):
        gm = GameManager()
        a, b = self._find_pair(gm)
        self._click_pos(gm, a)
        for _ in range(200): gm.update()
        self._click_pos(gm, b)
        for _ in range(200): gm.update()
        assert a.state == CardState.MATCHED
        assert b.state == CardState.MATCHED

    def test_win_condition(self):
        gm = GameManager()
        from collections import defaultdict
        pairs: dict[int, list[Card]] = defaultdict(list)
        for card in gm.cards:
            pairs[card.pair_id].append(card)

        for pid, (a, b) in pairs.items():
            self._click_pos(gm, a)
            for _ in range(200): gm.update()
            self._click_pos(gm, b)
            for _ in range(200): gm.update()

        assert gm.is_won


class TestGameManagerReset:
    def test_reset_resets_moves(self):
        gm = GameManager()
        gm.moves = 42
        gm.reset()
        assert gm.moves == 0

    def test_reset_resets_matches(self):
        gm = GameManager()
        gm.matches = 5
        gm.reset()
        assert gm.matches == 0

    def test_reset_all_cards_face_down(self):
        gm = GameManager()
        for card in gm.cards:
            card.flip_up()
            for _ in range(100): card.update()
        gm.reset()
        assert all(c.state == CardState.FACE_DOWN for c in gm.cards)

    def test_reset_not_won(self):
        gm = GameManager()
        gm.matches = 8
        gm.reset()
        assert not gm.is_won