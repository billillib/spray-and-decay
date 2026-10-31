"""
RUST SECTOR (Python version)
============================
A small first-person shooter made with a RAYCASTER, the same trick the 1992
game Wolfenstein 3D used to look 3D on very slow computers.

How to run it:
    pip install pygame
    python3 rust_sector.py

Controls:
    W A S D     move
    Mouse       turn (arrow keys work too)
    Click/Space shoot
    R           restart after you win or lose
    Esc         quit
"""

import math
import random
import pygame

# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 960, 540        # size of the window in pixels
COLUMN = 4                      # each ray draws a strip this many pixels wide
NUM_RAYS = WIDTH // COLUMN      # 240 rays, one per strip
FOV = 0.66                      # how wide you can see (about 66 degrees)
HALF = HEIGHT // 2              # the horizon line, halfway down the screen

# ---------------------------------------------------------------------------
# THE MAP
# Each letter is one square of the world, seen from above.
#   1 2 3  walls (different colours)     .  empty floor
#   P      where you start               R  an enemy robot
#   B      your recruit buddy            +  a medkit
# ---------------------------------------------------------------------------
MAP = [
    "1111111111111111",
    "1P.....1.......1",
    "1..B...1...R...1",
    "1......2.......1",
    "1..........33..1",
    "1112.111...33..1",
    "1..............1",
    "1...R......R...1",
    "1......222.....1",
    "1+.....2.2...+.1",
    "1......2.2.....1",
    "1..R...........1",
    "1.........R....1",
    "1111111111111111",
]

WALL_COLOURS = {
    "1": (120, 116, 108),   # grey stone
    "2": (150, 70, 45),     # rusty brick
    "3": (70, 95, 135),     # blue steel
}


def is_wall(x, y):
    """True if the square at world position (x, y) is a wall."""
    col, row = int(x), int(y)
    if row < 0 or row >= len(MAP) or col < 0 or col >= len(MAP[0]):
        return True
    return MAP[row][col] in WALL_COLOURS


# ---------------------------------------------------------------------------
# THE RAYCASTER
# Imagine standing in the map and shooting a laser straight ahead.
# We step the laser one grid line at a time until it hits a wall.
# The further away the wall, the SHORTER we draw it. That's the whole trick!
# ---------------------------------------------------------------------------
def cast_ray(px, py, dx, dy):
    """
    Walk along a ray from (px, py) in direction (dx, dy) until it hits a wall.
    Uses the "DDA" method: always jump to whichever grid line is closer,
    the next vertical one or the next horizontal one.
    Returns (distance, wall letter, side) where side 0 or 1 says which face we hit.
    """
    map_x, map_y = int(px), int(py)
    # How far along the ray we travel to cross one whole square in x or in y.
    step_dist_x = abs(1 / dx) if dx != 0 else 1e30
    step_dist_y = abs(1 / dy) if dy != 0 else 1e30
    # Which way we step (+1 or -1), and how far to the FIRST grid line.
    if dx < 0:
        step_x, side_dist_x = -1, (px - map_x) * step_dist_x
    else:
        step_x, side_dist_x = 1, (map_x + 1 - px) * step_dist_x
    if dy < 0:
        step_y, side_dist_y = -1, (py - map_y) * step_dist_y
    else:
        step_y, side_dist_y = 1, (map_y + 1 - py) * step_dist_y

    while True:
        if side_dist_x < side_dist_y:       # the vertical grid line is closer
            side_dist_x += step_dist_x
            map_x += step_x
            side = 0
        else:                               # the horizontal grid line is closer
            side_dist_y += step_dist_y
            map_y += step_y
            side = 1
        tile = MAP[map_y][map_x]
        if tile in WALL_COLOURS:
            # Back up one step to get the distance to the wall we just reached.
            dist = side_dist_x - step_dist_x if side == 0 else side_dist_y - step_dist_y
            return max(dist, 0.0001), tile, side


def shade(colour, distance, side):
    """Make far-away walls darker (fog) and one side of each wall a bit darker."""
    fog = max(0.15, 1 - distance / 12)
    if side == 1:
        fog *= 0.75
    return tuple(int(c * fog) for c in colour)


# ---------------------------------------------------------------------------
# PICTURES FOR ROBOTS, THE BUDDY AND MEDKITS
# We draw them once with simple shapes, then shrink/grow them as needed.
# ---------------------------------------------------------------------------
def make_robot_picture(flash=False):
    pic = pygame.Surface((64, 64), pygame.SRCALPHA)   # SRCALPHA = see-through background
    dark, body, eye = (55, 58, 64), (140, 145, 152), (255, 90, 40)
    pygame.draw.rect(pic, dark, (22, 44, 6, 18))          # legs
    pygame.draw.rect(pic, dark, (36, 44, 6, 18))
    pygame.draw.rect(pic, body, (17, 22, 30, 24))         # body
    pygame.draw.rect(pic, body, (22, 8, 20, 14))          # head
    pygame.draw.rect(pic, dark, (24, 13, 16, 5))          # visor
    pygame.draw.rect(pic, eye, (26, 14, 12, 3))           # glowing eye
    pygame.draw.rect(pic, (30, 30, 32), (43, 32, 13, 8))  # gun arm
    if flash:                                             # muzzle flash when shooting
        pygame.draw.circle(pic, (255, 200, 60), (52, 36), 7)
    return pic


def make_buddy_picture():
    pic = pygame.Surface((64, 64), pygame.SRCALPHA)
    skin, kit, helmet = (208, 160, 122), (91, 107, 69), (77, 90, 58)
    pygame.draw.rect(pic, (74, 86, 56), (24, 42, 7, 16))  # legs
    pygame.draw.rect(pic, (74, 86, 56), (33, 42, 7, 16))
    pygame.draw.rect(pic, (42, 38, 32), (23, 57, 9, 7))   # boots
    pygame.draw.rect(pic, (42, 38, 32), (32, 57, 9, 7))
    pygame.draw.rect(pic, kit, (22, 22, 20, 21))          # jacket
    pygame.draw.rect(pic, skin, (26, 8, 12, 12))          # face
    pygame.draw.rect(pic, (30, 20, 15), (28, 13, 2, 2))   # eyes
    pygame.draw.rect(pic, (30, 20, 15), (34, 13, 2, 2))
    pygame.draw.rect(pic, helmet, (24, 4, 16, 6))         # helmet
    pygame.draw.rect(pic, (27, 27, 29), (18, 35, 36, 4))  # rifle
    return pic


def make_medkit_picture():
    pic = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(pic, (230, 226, 218), (8, 24, 48, 38))
    pygame.draw.rect(pic, (200, 48, 42), (27, 30, 10, 26))
    pygame.draw.rect(pic, (200, 48, 42), (19, 38, 26, 10))
    return pic


# ---------------------------------------------------------------------------
# THE GAME
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rust Sector")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("courier", 26, bold=True)
        self.big_font = pygame.font.SysFont("courier", 64, bold=True)
        self.robot_pic = make_robot_picture()
        self.robot_shoot_pic = make_robot_picture(flash=True)
        self.buddy_pic = make_buddy_picture()
        self.medkit_pic = make_medkit_picture()
        pygame.event.set_grab(True)       # keep the mouse inside the window
        pygame.mouse.set_visible(False)
        self.reset()

    def reset(self):
        """Read the map and put everyone in their starting places."""
        self.robots, self.medkits = [], []
        for row, line in enumerate(MAP):
            for col, ch in enumerate(line):
                x, y = col + 0.5, row + 0.5     # +0.5 puts things in the middle of the square
                if ch == "P":
                    self.px, self.py = x, y
                elif ch == "R":
                    self.robots.append({"x": x, "y": y, "hp": 40, "cooldown": 2.0, "flash": 0, "awake": False})
                elif ch == "B":
                    self.buddy = {"x": x, "y": y, "cooldown": 1.0}
                elif ch == "+":
                    self.medkits.append({"x": x, "y": y})
        self.angle = 0.0          # which way you're facing, in radians
        self.health = 100
        self.ammo = 50
        self.kills = 0
        self.gun_kick = 0         # makes the gun jump back when you shoot
        self.hurt_flash = 0       # red screen flash when you get hit
        self.shoot_timer = 0
        self.state = "playing"    # "playing", "won" or "lost"

    # ----- helpers -----
    def can_see(self, ax, ay, bx, by):
        """True if nothing blocks a straight line from a to b."""
        dist = math.hypot(bx - ax, by - ay)
        if dist < 0.01:
            return True
        wall_dist, _, _ = cast_ray(ax, ay, (bx - ax) / dist, (by - ay) / dist)
        return wall_dist >= dist

    def move(self, thing, dx, dy, radius=0.25):
        """Move something, but slide along walls instead of walking through them."""
        if not is_wall(thing["x"] + dx + math.copysign(radius, dx), thing["y"]):
            thing["x"] += dx
        if not is_wall(thing["x"], thing["y"] + dy + math.copysign(radius, dy)):
            thing["y"] += dy

    # ----- shooting -----
    def shoot(self):
        if self.ammo <= 0 or self.shoot_timer > 0:
            return
        self.ammo -= 1
        self.shoot_timer = 0.3
        self.gun_kick = 1
        dx, dy = math.cos(self.angle), math.sin(self.angle)
        wall_dist, _, _ = cast_ray(self.px, self.py, dx, dy)
        # Find the closest living robot that is right in front of us (in the crosshair).
        target, target_dist = None, wall_dist
        for r in self.robots:
            if r["hp"] <= 0:
                continue
            vx, vy = r["x"] - self.px, r["y"] - self.py
            along = vx * dx + vy * dy             # how far in front of us
            sideways = abs(vx * dy - vy * dx)     # how far left/right of the crosshair
            if 0 < along < target_dist and sideways < 0.35:
                target, target_dist = r, along
        if target:
            self.hurt_robot(target, random.randint(14, 20))
        for r in self.robots:                     # the bang wakes up nearby robots
            if math.hypot(r["x"] - self.px, r["y"] - self.py) < 8:
                r["awake"] = True

    def hurt_robot(self, robot, damage):
        robot["hp"] -= damage
        robot["awake"] = True
        if robot["hp"] <= 0:
            self.kills += 1
            if all(r["hp"] <= 0 for r in self.robots):
                self.state = "won"

    # ----- the game rules, run every frame -----
    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_dx, _ = pygame.mouse.get_rel()
        self.angle += mouse_dx * 0.003
        if keys[pygame.K_LEFT]:
            self.angle -= 2.5 * dt
        if keys[pygame.K_RIGHT]:
            self.angle += 2.5 * dt

        # Moving: forward/back uses the facing direction, strafing uses the sideways direction.
        speed = 3.2 * dt
        fx, fy = math.cos(self.angle), math.sin(self.angle)   # forward
        sx, sy = -fy, fx                                       # to the right
        move_x = move_y = 0
        if keys[pygame.K_w]: move_x += fx; move_y += fy
        if keys[pygame.K_s]: move_x -= fx; move_y -= fy
        if keys[pygame.K_d]: move_x += sx; move_y += sy
        if keys[pygame.K_a]: move_x -= sx; move_y -= sy
        me = {"x": self.px, "y": self.py}
        self.move(me, move_x * speed, move_y * speed)
        self.px, self.py = me["x"], me["y"]

        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            self.shoot()
        self.shoot_timer -= dt
        self.gun_kick = max(0, self.gun_kick - dt * 6)
        self.hurt_flash = max(0, self.hurt_flash - dt * 2)

        # Pick up medkits.
        for kit in self.medkits[:]:
            if math.hypot(kit["x"] - self.px, kit["y"] - self.py) < 0.6 and self.health < 100:
                self.health = min(100, self.health + 25)
                self.medkits.remove(kit)

        # Robots: wake up when they see you, walk towards you, and shoot.
        for r in self.robots:
            if r["hp"] <= 0:
                continue
            r["flash"] = max(0, r["flash"] - dt)
            dist = math.hypot(self.px - r["x"], self.py - r["y"])
            sees_you = dist < 14 and self.can_see(r["x"], r["y"], self.px, self.py)
            if sees_you and dist < 8:
                r["awake"] = True
            if not r["awake"]:
                continue
            r["cooldown"] -= dt
            if sees_you and r["cooldown"] <= 0:
                r["cooldown"] = random.uniform(1.2, 2.2)
                r["flash"] = 0.15
                hit_chance = max(0.2, 0.85 - dist * 0.06)   # harder to hit you from far away
                if random.random() < hit_chance:
                    self.health -= random.randint(4, 8)
                    self.hurt_flash = 0.6
                    if self.health <= 0:
                        self.state = "lost"
            elif dist > 1.5:
                self.move(r, (self.px - r["x"]) / dist * 1.6 * dt, (self.py - r["y"]) / dist * 1.6 * dt, 0.3)

        # Your buddy: follow you, and shoot any robot they can see.
        b = self.buddy
        dist = math.hypot(self.px - b["x"], self.py - b["y"])
        if dist > 2:
            self.move(b, (self.px - b["x"]) / dist * 2.8 * dt, (self.py - b["y"]) / dist * 2.8 * dt, 0.3)
        b["cooldown"] -= dt
        if b["cooldown"] <= 0:
            for r in self.robots:
                if r["hp"] > 0 and math.hypot(r["x"] - b["x"], r["y"] - b["y"]) < 12 and self.can_see(b["x"], b["y"], r["x"], r["y"]):
                    b["cooldown"] = random.uniform(0.6, 1.0)
                    if random.random() < 0.6:
                        self.hurt_robot(r, random.randint(7, 12))
                    break

    # ----- drawing -----
    def draw(self):
        # Sky and floor: two big rectangles.
        self.screen.fill((40, 34, 60), (0, 0, WIDTH, HALF))
        self.screen.fill((50, 46, 40), (0, HALF, WIDTH, HALF))

        dir_x, dir_y = math.cos(self.angle), math.sin(self.angle)
        plane_x, plane_y = -dir_y * FOV, dir_x * FOV     # the "camera plane", sideways from where you look
        depth = [0.0] * NUM_RAYS                         # remember how far each wall strip is

        # 1) WALLS: one ray per strip, from the left edge of the screen to the right.
        for i in range(NUM_RAYS):
            camera_x = 2 * i / NUM_RAYS - 1                # -1 = left edge, 0 = middle, +1 = right edge
            ray_x = dir_x + plane_x * camera_x
            ray_y = dir_y + plane_y * camera_x
            dist, tile, side = cast_ray(self.px, self.py, ray_x, ray_y)
            depth[i] = dist
            wall_height = int(HEIGHT / dist)               # THE BIG IDEA: twice as far = half as tall
            top = HALF - wall_height // 2
            pygame.draw.rect(self.screen, shade(WALL_COLOURS[tile], dist, side), (i * COLUMN, top, COLUMN, wall_height))

        # 2) SPRITES (robots, buddy, medkits): flat pictures that always face you.
        things = []
        for r in self.robots:
            if r["hp"] > 0:
                things.append((r["x"], r["y"], self.robot_shoot_pic if r["flash"] > 0 else self.robot_pic, 1.0))
        things.append((self.buddy["x"], self.buddy["y"], self.buddy_pic, 0.95))
        for kit in self.medkits:
            things.append((kit["x"], kit["y"], self.medkit_pic, 0.4))

        inv = 1 / (plane_x * dir_y - dir_x * plane_y)
        drawn = []
        for x, y, pic, size in things:
            # Turn the world position into "how far in front" and "how far to the side" of the camera.
            rel_x, rel_y = x - self.px, y - self.py
            side_amount = inv * (dir_y * rel_x - dir_x * rel_y)
            ahead = inv * (-plane_y * rel_x + plane_x * rel_y)
            if ahead > 0.2:
                drawn.append((ahead, side_amount, pic, size))
        drawn.sort(key=lambda t: -t[0])                  # draw far things first, near things on top

        for ahead, side_amount, pic, size in drawn:
            screen_x = int(WIDTH / 2 * (1 + side_amount / ahead))
            px_size = int(HEIGHT / ahead * size)
            if px_size < 2 or px_size > 4000:
                continue
            bottom = HALF + int(HEIGHT / ahead / 2)      # stand on the floor
            scaled = pygame.transform.scale(pic, (px_size, px_size))
            left = screen_x - px_size // 2
            # Draw the sprite one strip at a time, skipping strips hidden behind a nearer wall.
            for i in range(max(0, left // COLUMN), min(NUM_RAYS, (left + px_size) // COLUMN + 1)):
                if depth[i] > ahead:
                    strip_x = i * COLUMN - left
                    if 0 <= strip_x < px_size:
                        w = min(COLUMN, px_size - strip_x)
                        self.screen.blit(scaled, (i * COLUMN, bottom - px_size), (strip_x, 0, w, px_size))

        # 3) THE GUN at the bottom of the screen.
        gx, gy = WIDTH // 2 - 30, HEIGHT - 150 + int(self.gun_kick * 25)
        if self.gun_kick > 0.6:
            pygame.draw.circle(self.screen, (255, 190, 60), (gx + 30, gy - 10), 22)
        pygame.draw.rect(self.screen, (40, 42, 46), (gx + 12, gy, 36, 110))
        pygame.draw.rect(self.screen, (200, 154, 114), (gx, gy + 70, 60, 80))

        # 4) The HUD: crosshair, health, ammo and kills.
        pygame.draw.line(self.screen, (240, 230, 210), (WIDTH // 2 - 8, HALF), (WIDTH // 2 + 8, HALF), 2)
        pygame.draw.line(self.screen, (240, 230, 210), (WIDTH // 2, HALF - 8), (WIDTH // 2, HALF + 8), 2)
        self.screen.blit(self.font.render(f"HEALTH {self.health}", True, (230, 70, 58)), (20, HEIGHT - 40))
        self.screen.blit(self.font.render(f"AMMO {self.ammo}", True, (243, 178, 58)), (WIDTH - 170, HEIGHT - 40))
        self.screen.blit(self.font.render(f"ROBOTS {self.kills}/{len(self.robots)}", True, (236, 228, 207)), (20, 16))

        if self.hurt_flash > 0:
            red = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red.fill((200, 20, 10, int(120 * self.hurt_flash)))
            self.screen.blit(red, (0, 0))

        if self.state != "playing":
            text = "SECTOR CLEAR!" if self.state == "won" else "SCRAPPED!"
            msg = self.big_font.render(text, True, (208, 96, 47))
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HALF - 30)))
            hint = self.font.render("Press R to play again", True, (236, 228, 207))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HALF + 30)))

        pygame.display.flip()

    # ----- the main loop: read input, update, draw, repeat ~60 times a second -----
    def run(self, max_frames=None):
        frames = 0
        while True:
            dt = min(self.clock.tick(60) / 1000, 0.05)   # seconds since the last frame
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.state != "playing":
                    self.reset()
            if self.state == "playing":
                self.update(dt)
            self.draw()
            frames += 1
            if max_frames and frames >= max_frames:
                pygame.quit()
                return


if __name__ == "__main__":
    Game().run()
