# Punball

Ball-shooting boss battle built with pygame.

## Run
    pip install -r requirements.txt
    python main.py

## Controls
- Start phase: Left/Right (or A/D) or click the bottom strip to place the hero.
- Move the mouse to aim; left-click above the bottom strip to fire.
- Attack phase: hold SPACE or click FAST >> (top right) to fast-forward.
- Stage clear: SPACE / click for the next stage.
- Game over: R to restart.

## Structure
    main.py                     entry point
    game/
      settings.py               constants, tuning values, State names
      display.py                window sizing: fits the screen, scales the 480x800 game, maps the mouse
      skills.py                 every skill (special ball) as a small class
      app.py                    game state, input, turn logic, effects, fast-forward
      renderer.py               all drawing and visual effects
      entities/                 Ball, Hero, Boss, Block, Item
      systems/
        ball_manager.py         ball movement, collisions, volleys, hit callbacks
        field.py                block + item grid (spawn, move down, hero collision)
        aiming.py               aim angle from mouse position

## Window size
The game draws at 480x800 and the window shrinks automatically to fit your screen height
(you can also drag the window edges to resize it). `SCREEN_MARGIN_Y` in `game/display.py` is the
space kept free for the title bar and taskbar.

## Skills
Blocks and items can now be a gold star **skill item**. Collect one with any ball; when the
volley ends (and the boss has attacked) you pick 1 of 3 random skills. Each pick adds +1 of
that special ball to every volley (picks stack, and the HUD under the boss shows your counts).

- **Fire Ball**: sets the block on fire; it takes damage at the end of each turn for 5 turns.
- **Ice Ball**: freezes the block; it skips the next 2 move-downs (blocks above it wait).
- **Lightning Ball**: also damages every block touching the hit block (8 neighbours).
- **Boss Bounce Ball**: rebounds off the boss every time it touches it (no limit); it only disappears when it hits the floor.

Collecting several skill items in one volley gives several picks in a row. A skill item
collected on the volley that kills the boss is offered when you press NEXT STAGE.
Pick with a click or the 1 / 2 / 3 keys. Tuning values (burn turns, freeze turns, spawn
chance, ...) are in `game/settings.py`.

All skill code lives in `game/skills.py`: one small class per skill (hooks `on_block_hit`,
`on_boss_hit`, `on_turn_end`, plus its icon). Add a class with `@register` and it appears on the
choice screen, in the HUD and in volleys automatically.

## Added effects
- Boss attack glow, beam, hero shockwave, blinking, and floating damage number.
- Screen shake from boss attacks and boss hits.
- Block hit flash and block-break particles.
- Delayed HP bar showing recently lost health.
- FAST >> button and SPACE hold to speed up the attack phase.

## Tuning
Edit `game/settings.py` to adjust gameplay and visual-effect constants.
