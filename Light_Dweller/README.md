# Light Dweller

A top-down dungeon-crawler / wave-survival game built from scratch in **Python with Pygame**. Fight through waves of enemies, collect coins, upgrade your gear at the tower shop, and defeat the boss to win.

Everything in this project — the game design, architecture, mechanics, and code — is my own work.

## Gameplay

- Battle through escalating **waves** across multiple hand-designed levels.
- Defeat six distinct enemy types — **Muddy, Imp, Goblin, Zombie, Skeleton**, and a final **Boss** — each with its own health, speed, and behavior.
- Collect **coins** from fallen enemies and spend them at the **tower shop** to upgrade your bow, arrows, fire rate, and damage. Upgrades persist as you advance.
- Survive with a **heart-based health system** and heal with potions.
- Beat the boss (which **enrages and speeds up** when low on health) to win the run.

## Controls

| Action | Input |
|--------|-------|
| Move | `W` `A` `S` `D` |
| Shoot | Left Mouse Button (aim with cursor) |
| Enter shop | `E` (while in the shop area) |
| Leave shop | `Q` |

## Technical Highlights

The game is built with a clean **object-oriented architecture**:

- **Inheritance hierarchy** — a base `Character` class extends into `Hero` and `Enemy`, which further specializes into each monster type and the `Boss`.
- **Enemy AI** — enemies track and pursue the hero with obstacle-aware movement.
- **Tile-based worlds** — levels are loaded from CSV tilemaps with collision detection against obstacle tiles.
- **Camera scrolling** — the world scrolls relative to the player within bounded walls.
- **Game-state management** — intro / death / victory fade transitions, a restart/exit flow, and a persistent upgrade system across levels.
- **Polish** — animated sprite frames (idle/run), floating damage-text popups, background music, and sound effects.

## Project Structure

| File | Responsibility |
|------|----------------|
| `main.py` | Entry point — instantiates and runs the game. |
| `game.py` | Main game loop, state management, rendering, and HUD. |
| `character.py` | `Character` / `Hero` / `Enemy` / `Boss` and all monster types. |
| `weapon.py` | Bow, arrows, and damage logic. |
| `tower.py` | Shop / upgrade system. |
| `world.py` | Level loading from CSV tilemaps and world rendering. |
| `items.py` | Coins, hearts, and potions. |
| `fade.py` | Screen fade transitions (intro / death / victory). |
| `button.py`, `texts.py`, `constants.py` | UI buttons, text rendering, and shared constants. |
| `assets/` | Sprites, tiles, fonts, levels (CSV), music, and sound effects. |

## Running the Game

```bash
pip install pygame
python main.py
```

## Tech Stack

- **Python** — Pygame (sprites, mixer, collision, event handling)
