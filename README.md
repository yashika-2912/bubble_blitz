# 🫧 Bubble Blitz

A fast-paced arcade game built with Python and Pygame. Pop falling bubbles with your paddle before they escape — but watch out, every hit splits them into faster child bubbles!


## Gameplay

Bubbles of varying sizes fall from the top of the screen. Hit one with your paddle and it **splits into two smaller, faster bubbles**. Those split once more into tiny ones before finally disappearing. Let a bubble slip past the bottom and you lose a life. Survive as long as you can — the spawn rate increases every 20 seconds.

**Scoring**

| Bubble size | Points |
|-------------|--------|
| Large (gen 0) | 10 |
| Medium (gen 1) | 20 |
| Small (gen 2) | 30 |

Smaller bubbles are harder to catch and worth more — chain your pops strategically.

---

## Getting Started

**Requirements:** Python 3.8+ and Pygame 2.x

```bash
# Install pygame
pip install pygame

# Clone and run
git clone https://github.com/your-username/bubble-blitz.git
cd bubble-blitz
python bubble_blitz.py
```

---

## Controls

| Key | Action |
|-----|--------|
| `←` / `A` | Move paddle left |
| `→` / `D` | Move paddle right |
| `R` | Restart after game over |
| `ESC` | Quit |

---

## Project Structure

```
bubble_blitz.py
│
├── Bubble          — position, velocity, wobble animation, split logic
├── Paddle          — player-controlled, keyboard input, collision rect
├── Particle        — pop burst effect, gravity-affected, alpha fade
├── reset_game()    — returns a fresh state dict (score, lives, level)
├── draw_hud()      — score, level label, lives displayed as bubble icons
└── main()          — game loop: input → update → draw at 60 fps
```

---

## How the Split Mechanic Works

Each bubble tracks a `generation` value (0, 1, or 2). On paddle contact:

1. The bubble is marked dead and 14 particles burst from its center.
2. If `generation < 2`, two child bubbles spawn at the same position with half the radius, horizontal velocities mirrored, and slightly reduced vertical speed.
3. Generation 2 bubbles pop cleanly with no children.

This creates chain reactions where a single well-timed hit can suddenly fill the screen with fast-moving small bubbles.

---

## Future Improvements

### Gameplay
- [ ] **Power-ups** — timed drops that grant a wider paddle, slow-motion, or a one-hit shield
- [ ] **Bubble variants** — bomb bubbles that destroy neighbours on pop; armoured bubbles requiring two hits; magnet bubbles that drift toward the paddle
- [ ] **Combo multiplier** — consecutive pops within a short window multiply score (x2, x3, x4...)
- [ ] **Boss waves** — every 5 levels spawn a giant bubble that takes multiple hits and releases a swarm on death
- [ ] **Pause menu** — `P` key to pause with resume / restart / quit options

### Visuals & Polish
- [ ] **Screen shake** on life loss for physical feedback
- [ ] **Animated background** — slow-drifting star field or parallax layers to replace the static grid
- [ ] **Bubble trail** — short fading trail behind fast-moving bubbles showing their trajectory
- [ ] **Pop sound effects and background music** using `pygame.mixer`
- [ ] **Level transition banner** — brief full-screen flash with "Level X" text on level up

### Progression & Persistence
- [ ] **High score file** — save top 5 scores locally with `json` or `pickle`
- [ ] **Leaderboard screen** — dedicated screen showing saved scores, accessible from game over
- [ ] **Difficulty presets** — Easy / Normal / Hard adjusting starting spawn rate and bubble speed caps
- [ ] **Endless mode vs timed mode** — survive as long as possible vs clear a fixed wave count in the shortest time

### Code Quality
- [ ] **Config file** (`config.py` or `settings.json`) to centralise constants like `WIDTH`, `HEIGHT`, `spawn_rate`, `lives`
- [ ] **Scene manager** — decouple `"play"` / `"gameover"` states into proper scene classes for easier expansion (add a main menu, pause screen, leaderboard)
- [ ] **Unit tests** — test `Bubble.split()`, collision detection, and scoring with `pytest`
- [ ] **Type hints** throughout all classes and functions

---