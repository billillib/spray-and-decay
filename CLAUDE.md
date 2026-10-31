# Spray and Decay

(Called Rust Sector until 2026-10-30; localStorage keys and some code names still say rust-sector.)

A first-person shooter designed by Ernie, Bill's 12-year-old son, who asks for features in quick, short messages
and plays the result. Bill (the account owner) jumps in occasionally to guide. Write for the son by default:
simple, warm, short and skimmable. Answer Bill directly when a message is clearly from him.

## Repo and hosting

- GitHub: `billillib/spray-and-decay` (branch `main`). GitHub Pages serves `main` at
  https://billillib.github.io/spray-and-decay/, so pushing to `main` changes the live site. Commit and push only
  when asked.
- The claude.ai artifact (below) is a second copy; publish it only when asked.

## Files

- `index.html` — the whole game: one page, plain JavaScript, no build step, ~3,300 lines.
  Published as a claude.ai artifact: https://claude.ai/artifact/FuLk74BNQ9gAvJAGZjtedZ
  (version 22 is current). Republish by publishing this same file path with `files` for arcade.html and pilot.html;
  only publish when the user asks.
- `arcade.html` — the Mini games page (opened in an iframe from the title menu): Cherry Tomb (a zombie parody of the
  PICO-8 shmup Cherry Bomb), Brain Snake, Grave Whacker, Zombie Dash, Bone Breaker. 128×128 PICO-8 palette, high
  scores in localStorage `rust-sector-arcade`.
- `pilot.html` — the Pilot Edition: the very first version of the game, untouched. Unlocked (until reload) by
  beating the Zombie King; opens in the same iframe overlay.
- `rust_sector.py` — a much smaller pygame version written to explain how raycasting works. It does not
  have the newer features. Run: `python3 rust_sector.py`.
- Play locally: `open -a "Google Chrome" /Users/bill/ernie/first_game/index.html`.

## How index.html is built (sections are marked `// ---------- name ----------`)

- **Renderer**: CPU column raycaster into an 800×450 buffer (`W`, `H`), with per-pixel depth (`dbuf`).
  Each column walks the grid front to back, drawing floors, ceilings, wall faces (`drawFace`) and tops,
  clipping with `yTop`/`yBot`. Blocks have heights (`HEIGHT[c]`): office towers 3–5 storeys, brick 1–3,
  cars 0.55, crates 0.8, hedges 0.5. Doors (tile 9) have a lintel above them (`LINTEL`, `LTEX`) and
  `DOORINFO` bits (1 door, 2 faces along y, 4 second half). Sprites are billboards tested against `dbuf`.
  The image goes through a WebGL post-process shader (`present`, toggle V) with a 2D fallback.
- **Textures**: 128×128 (`TS`). World textures use `makeHD` + seamless `vnoise`/`fbm`. Sprites are drawn
  on 64×64 canvases and doubled with `smooth2x`. Bright red/orange sprite pixels glow (ignore fog).
- **Theme**: zombies (changed from robots on 2026-10-30). Code names stayed the same: `KINDS` codes, `drawBoss`,
  `drawDrone`, `e.k.sentinel` etc. still use the old robot names, only the art and text changed.
- **Maps** (`MAPS`): Rust City (boss Butcher `B`), The Scrapyard (Hive Mother `O`), Neon Docks (Tank `C`),
  The Core (final boss Zombie King `K`, appears at 20 kills), Test Arena (always open, endless ammo,
  T opens a spawn menu). Beating a boss unlocks the next map; unlocks reset when the page reloads (by request).
  Each map: generator, sky kind, haze colour, district names. 9 districts per map; entering a new one spawns 13.
- **Enemies** (`KINDS`): walker `g`, brute `h`, rot bat `d`, runner `m` (melee), puker `u` (bile blinds you: `P.blind`),
  spitter `S` (red aim line, then a visible acid glob in `spits`), bosses B/O/C/K. Zombie art: `zHead`/`zTorso`/`zLegs`/`zArm`, `drawZombie`. Walkers/brutes carry a
  random gun (`ENEMY_GUNS`, own sprites per gun, plus `aim`/`aimfire` frames that point the gun at the camera
  when shooting at you) and may drop it. Side-on sprites mirror (`faceLeft`) toward their target or walk direction. Killed sentries respawn. Boss at 30 kills (20 on The Core).
- **Player weapons**: 1 pistol, 2 shotgun, 3 flamethrower, 4 minigun (spin-up), 5 bazooka, 6 assault rifle,
  7 sniper (pierces 3), 8 orbital railgun (`fireRail` → `strikes` → 1000 damage blue blast, radius 6);
  G grenade launcher (G fire, G reload); Q EMP (stuns). Rifle/sniper/railgun pickups are placed by `newGame`. Armor vests soak 60% of damage. Health regenerates.
- **Recruits** Skid and Moe follow, wander, fight, revive each other, keep better guns for themselves and
  carry other dropped guns to you (`a.carry`, `giveGun`).
- **Menus**: full title screen (blood-red logo, tips, animated horde canvas `#horde`), buttons Play → map picker,
  Almanac (Enemies/Weapons tabs), Controls, Settings (music/sfx volume, mouse sensitivity, music/shaders/radar
  toggles, bug log; saved in localStorage `rust-sector-settings`), Mini games, Pilot edition. Pause has Quit game.
- **Easter eggs**: per game each has a 1-in-3 chance to be hidden far out: ? block (Mario, +50 max health), diamond
  (Minecraft, full armor), rusty chest (Risk of Rain, fire 15% faster via `P.rate`), loot llama (Fortnite, ammo).
  Codes typed on the title screen (silent: no message, only a sound or effect, by request): `creeper`, `dance`, `wahoo` (super jump), `triple t` (unlocks a Tung Tung Tung
  Sahur skin for the recruits, in memory only: reloading forgets it and turns the skin off (by request); drawn by `drawHuman` with `tung: true`).
  Ernie asked for no Tung enemy.
- **Recruits screen**: rename Skid/Moe and pick skin, helmet and uniform colours (`CREW_COLORS`, `buildRecruit`), saved in
  localStorage `rust-sector-recruits`. Zombies sometimes show their brain.

## Controls (as the user asked for them)

WASD move · mouse aims (also without pointer lock; push to an edge to keep turning) · click or Space fire ·
E jump · Shift sprints for 4 s (R also sprints right now; see open question) · 1–8 weapons · G grenade ·
Q EMP · T spawn menu in the arena · M radar · N music · V shaders · Esc/P pause and resume.

- **Boss death cutscene**: `startCine`/`cineStep`/`drawCine` freeze the game, turn the camera to the boss, show
  movie bars and "<boss> IS DEAD", then `endGame(true)`.
- **Death screen**: shows who killed you (`hitFrom` is set by every enemy attack, stored as `P.killer`), with its
  Almanac picture and a tip from `KILLERS`. The title is random: Eaten 40%, You ded 30%, Get wrecked lol 30%.
- **Zombie deaths**: regular zombies explode (`gibs`: burst, flying gib/bone puffs with `vz`) and leave a blood
  puddle (`PUFF.pool`) instead of a body. Bosses keep their bodies and the cutscene.
- **Tung skin** eyes glance around: extra `lookL`/`lookR` frames in `HUMAN_FRAMES`.
- **Orbital railgun cutscene** (10 s): `startOrbital` → `orbitalStep`/`drawOrbital`; alert, lock-on + 3-2-1, camera rises
  (`camLift`), beam, blast at 4.6 s (`railBlast`, 1000 damage within 9), shockwave rings, smoke, "TARGET ELIMINATED".
  A boss killed by it gets its own cutscene afterwards (`cine.bossAfter`).
- **Sniper scope**: Shift+Q or F toggles, right mouse holds; `drawScope` magnifies the middle 3x. Zombies die with a synthesized "bleh".
- **Map names**: Dead End City, The Boneyard, Ghoul Harbor, The Necropolis, Test Arena.

- **Phones** (`coarse` pointer → `html.touch`): touch controls only while playing (stick, Fire, Jump, Nade, Swap, Pause,
  Run toggle `touchRun`, Scope when the sniper is out), a "turn your phone sideways" screen in portrait (`#rotate`),
  bigger menu buttons, a Full screen button, no pinch zoom. The arcade has a D-pad and A/B buttons (A = Z, B = X).
  Not yet checked on a real phone (only emulated); the CPU renderer may be slow on older phones.

## Bug log

The game saves errors and a line per game in localStorage (`rust-sector-log`, last 80 entries). Controls →
Copy bug log copies them. The main loop catches errors so one bad frame can't freeze the game.

## Testing notes

- Known fixed freezes: a crash in the radar when guns dropped (froze the loop), and the music scheduler trying to
  play every missed note after the page was busy. Distant walls fog into the plain sky gradient (`SKYFOG`), not the
  sky picture, or skyline windows show through them as dots.
- When the Mac is busy, headless test runs time out or the page crashes. Kill leftover headless Chrome first.

- Headless test bot (doesn't touch the user's browser): `puppeteer-core` + installed Chrome. Scripts lived in
  the session scratchpad (`runner/`: `mkcopy.py` makes an instrumented copy, `bot.js` plays, `run.mjs` runs
  every map + the arena and reports crashes, NaNs, stuck bodies, leaks). Recreate them if they're gone.

- Test in the built-in browser pane, but ask first if the user might be using it — they have rejected
  tool calls that took over the pane. Show it with the view tool before taking screenshots.
- When the pane is hidden, `requestAnimationFrame` stops: screenshots are stale and the game does not
  update. For logic tests, temporarily add before the final `})();`:
  `window.__dbg = () => ({ P, enemies, items, allies, start, makeEnemy, step: n => { for (let i = 0; i < n; i++) update(1 / 60); } });`
  and always remove it before publishing (`grep -c __dbg index.html` should print 0).
- The game pauses itself when the page loses focus; resume via `document.getElementById('mBtn').click()`.
- Quick syntax check: extract the `<script>` body and run it through `new Function(...)` in node.

## Open question

The user once asked to drop R as a sprint key ("just make shift the sprint key") but then rejected the
edit. R and Shift both sprint, and the HUD label reads "Sprint · hold R". Ask before changing it.
