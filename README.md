# 🃏 Memory Match Game

A classic card-matching memory game built with Python and Pygame.

## Features
- 4×4 grid of 16 cards (8 matching pairs)
- Smooth card flip animations
- Sound effects for flips and matches
- Score tracking (moves counter)
- Timer display
- Win screen with final stats

## Project Structure

```
memory_match_game/
├── assets/
│   ├── images/        # Card face icons (PNG/JPG)
│   ├── sounds/        # flip.mp3, match.wav
│   └── fonts/         # Custom fonts (optional)
├── src/
│   ├── __init__.py
│   ├── main.py        # Entry point & game loop
│   ├── constants.py   # Colors, sizes, FPS
│   ├── card.py        # Card class
│   └── game_manager.py# Match logic & scoring
├── tests/
│   └── test_logic.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your assets (optional)
- Place card images named `icon_1.png` through `icon_8.png` in `assets/images/`
- Place `flip.mp3` and `match.wav` in `assets/sounds/`
- If assets are missing, the game auto-generates colorful emoji-style card faces

### 3. Run the game
```bash
python src/main.py
```
Or from the project root:
```bash
cd memory_match_game
python -m src.main
```

## How to Play
1. Click any face-down card to flip it
2. Click a second card to try to find its match
3. Matching pairs stay face-up ✅
4. Non-matching pairs flip back after a short delay ❌
5. Match all 8 pairs to win!

## Controls
- **Left Click** — Flip a card
- **R** — Restart the game
- **ESC** — Quit

## Running Tests
```bash
python -m pytest tests/
```

## Requirements
- Python 3.8+
- pygame 2.5.2