# 🃏 Memory Match System
A classic card-matching memory game built with **Python** and **Pygame**.  
Flip cards, find all 8 pairs, and beat your best time! 🎮

[▶ How to Run](#-setup--installation) · [🎮 How to Play](#-how-to-play) · [🏗 Architecture](#-architecture) · [🧪 Tests](#-running-tests)

</div>

---

## 📸 Preview

```
┌─────────────────────────────────────────┐
│  ⏱ 00:42    🎯 Moves: 14    ✅ 6/8 pairs │
├─────────────────────────────────────────┤
│                                         │
│  [🦊][🐬][??][??]                       │
│  [??][🌙][🌙][??]                       │
│  [⚡][??][🦊][??]                       │
│  [??][🐬][??][⚡]                       │
│                                         │
│        R — Restart  •  ESC — Quit       │
└─────────────────────────────────────────┘
```

---

## ✨ Features

- 🎴 **4×4 grid** — 16 cards, 8 matching pairs, shuffled every game
- 🔄 **Smooth flip animation** — pseudo-3D card flip using surface squishing
- 🧠 **5-state card machine** — `FACE_DOWN → FLIPPING_UP → FACE_UP → FLIPPING_DOWN → MATCHED`
- ⏳ **Mismatch hold** — non-matching cards stay visible for 900ms before flipping back
- 📊 **Live HUD** — move counter, MM:SS timer, pairs-found tracker
- 🏆 **Win screen** — animated rotating stars with final move count and time
- 🔊 **Sound effects** — flip and match sounds (optional `.mp3`/`.wav` files)
- 🖼 **Custom card images** — drop PNG files in `assets/images/` to replace emoji symbols
- ✅ **21 unit tests** — headless test suite, no display required

---

## 📁 Project Structure

```
memory_match_game/
├── assets/
│   ├── images/          # Card face icons: icon_1.png … icon_8.png (optional)
│   ├── sounds/          # flip.mp3, match.wav (optional)
│   └── fonts/           # Custom fonts (optional)
├── src/
│   ├── __init__.py      # Makes src a Python package
│   ├── main.py          # Entry point — game loop, HUD, win screen
│   ├── constants.py     # All config: colours, sizes, grid, timing, paths
│   ├── card.py          # Card class with 5-state flip animation
│   └── game_manager.py  # Deck creation, matching logic, scoring, timer
├── tests/
│   └── test_logic.py    # 21 unit tests (runs headlessly)
├── .gitignore
├── README.md
└── requirements.txt     # pygame==2.5.2
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.8+** — download from [python.org](https://python.org) *(check "Add Python to PATH" on Windows)*
- **VS Code** *(recommended)* — download from [code.visualstudio.com](https://code.visualstudio.com)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/mtxmln-devs/Memory_Match-System.git
cd Memory_Match-System
```

---

### Step 2 — Create a virtual environment

```bash
python -m venv venv
```

> 💡 VS Code will show a popup: *"We noticed a new environment..."* — click **Yes**

---

### Step 3 — Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

> ⚠️ If you get an execution policy error on Windows, run this first:
> ```bash
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Run the game

```bash
python src/main.py
```

An **800×640** game window will open. That's it — you're playing! 🎉

---

### ⚡ Quick-start (all commands at once)

```bash
git clone https://github.com/mtxmln-devs/Memory_Match-System.git
cd Memory_Match-System
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/main.py
```

---

## 🎮 How to Play

1. All **16 cards** start face-down in a 4×4 grid
2. **Click** any card to flip it and reveal its symbol
3. **Click a second card** to try to find its match
4. ✅ **Match** — both cards turn green and stay face-up permanently
5. ❌ **No match** — cards are shown for 0.9 seconds, then flip back face-down
6. Match all **8 pairs** to win!
7. The **win screen** shows your total moves and time — press `R` to play again

### Controls

| Key / Action | Effect |
|---|---|
| `Left Click` | Flip a card |
| `R` | Restart the game (new shuffle) |
| `ESC` | Quit |

---

## 🏗 Architecture

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `constants.py` | Single source of truth for every config value — grid, colours, timing, paths |
| `card.py` | Card class — owns its own state machine and flip animation |
| `game_manager.py` | Deck builder, click validator, pair evaluator, score tracker |
| `main.py` | Pygame event loop, HUD rendering, win overlay |

---

### Card State Machine

```
FACE_DOWN ──(click)──► FLIPPING_UP ──(animation done)──► FACE_UP
    ▲                                                         │
    │                                                   (mismatch)
    └────────── FLIPPING_DOWN ◄──(hold 900ms)────────────────┘
                                        
FACE_UP ──(pair matched)──► MATCHED  ✅ (permanent)
```

| State | Description |
|---|---|
| `FACE_DOWN` | Default. Shows decorative back. Clickable. |
| `FLIPPING_UP` | Animating to face-up. Card width squishes to 0 then expands. |
| `FACE_UP` | Face visible. Not clickable. Waiting to be matched. |
| `FLIPPING_DOWN` | Animating back to face-down after a mismatch. |
| `MATCHED` | Permanently face-up with green tint. Pair counted. |

---

### Matching Logic Flow

```
Player clicks Card A  →  Card A animates to FACE_UP
Player clicks Card B  →  Card B animates to FACE_UP  →  moves++

         ┌── pair_id matches? ──┐
         │ YES                  │ NO
         ▼                      ▼
   mark_matched()         start 900ms timer
   matches++              → flip both back to FACE_DOWN

matches == 8?  →  YOU WIN 🎉
```

---

## 🧪 Running Tests

The test suite uses a **headless pygame stub** — no display or window required.

### With pytest
```bash
pip install pytest
python -m pytest tests/ -v
```

### With unittest
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Expected output
```
[PASS] card_starts_face_down
[PASS] card_starts_flippable
[PASS] flip_up_changes_state
[PASS] flip_up_completes
[PASS] flip_down_completes
[PASS] mark_matched
[PASS] gm_card_count
[PASS] gm_pairs_correct
[PASS] gm_match_works
[PASS] gm_win_condition
[PASS] gm_reset
... (21 tests total)

21 passed, 0 failed ✅
```

---

## 🖼 Adding Custom Assets *(optional)*

The game works **out of the box with emoji symbols**. To use your own graphics or sounds:

**Card images** — place PNG files in `assets/images/`:
```
assets/images/icon_1.png
assets/images/icon_2.png
...
assets/images/icon_8.png
```

**Sound effects** — place audio files in `assets/sounds/`:
```
assets/sounds/flip.mp3    ← played when a card is flipped
assets/sounds/match.wav   ← played when a pair is matched
```

If any file is missing, the game silently falls back to emoji / no sound.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognized | Reinstall Python and check **Add to PATH**. Try `py` instead of `python`. |
| `venv\Scripts\activate` fails | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first |
| `ModuleNotFoundError: pygame` | Make sure `(venv)` is showing before running `pip install` |
| `ModuleNotFoundError: src` | You're inside `src/` — `cd` back to `Memory_Match-System` |
| `import pygame` red underline in VS Code | Press `Ctrl+Shift+P` → **Python: Select Interpreter** → choose **venv** |
| Black window / display error | Update graphics drivers. Try `pip install pygame --upgrade` |

---

## 🔁 Every-Session Workflow

Each time you reopen VS Code:

```bash
cd Memory_Match-System
venv\Scripts\activate        # if (venv) isn't already showing
python src/main.py
```

> 💡 VS Code often auto-activates the venv when you reopen the folder — if `(venv)` is already showing, just run the game directly.

---

## 📄 License

This project is licensed under the **MIT License** — see below for details.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙌 Acknowledgements
- Built with [Pygame](https://www.pygame.org/)
- Emoji rendering via system fonts (Segoe UI Emoji on Windows)

---

<div align="center">

Made with ❤️ by [mtxmln-devs](https://github.com/mtxmln-devs)

⭐ Star this repo if you found it helpful!

</div>
