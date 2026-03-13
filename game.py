import pygame
import random
import sys

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 600, 800
FPS = 60

# Colors (retro palette)
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (80,  80,  80)
DARK_GRAY  = (40,  40,  40)
YELLOW     = (255, 220,   0)
RED        = (200,  30,  30)
BLUE       = (30,  100, 200)
GREEN      = (30,  180,  60)
ORANGE     = (230, 120,  20)
ROAD_COLOR = (50,  50,  50)
GRASS_L    = (30,  120,  30)
GRASS_D    = (20,   90,  20)
LINE_COLOR = (230, 200,   0)

ROAD_LEFT  = 100
ROAD_RIGHT = 500
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

# ── Helper: draw a retro car ───────────────────────────────────────────────────
def draw_car(surface, x, y, color, is_player=False):
    """Draw a pixel-art style car centered at (x, y)."""
    cw, ch = 40, 60
    cx = x - cw // 2
    cy = y - ch // 2

    # Body
    pygame.draw.rect(surface, color,       (cx + 5,  cy + 10, cw - 10, ch - 15))
    pygame.draw.rect(surface, color,       (cx + 10, cy,      cw - 20, 20))
    # Windows
    win_color = (160, 220, 255) if is_player else (180, 180, 180)
    pygame.draw.rect(surface, win_color,   (cx + 12, cy + 3,  cw - 24, 14))
    # Wheels
    wheel = DARK_GRAY
    pygame.draw.rect(surface, wheel,       (cx,      cy + 12, 8,  14))
    pygame.draw.rect(surface, wheel,       (cx + cw - 8, cy + 12, 8, 14))
    pygame.draw.rect(surface, wheel,       (cx,      cy + ch - 26, 8, 14))
    pygame.draw.rect(surface, wheel,       (cx + cw - 8, cy + ch - 26, 8, 14))
    # Headlights / tail-lights
    light = YELLOW if is_player else RED
    pygame.draw.rect(surface, light,       (cx + 7,  cy + ch - 8, 8, 5))
    pygame.draw.rect(surface, light,       (cx + cw - 15, cy + ch - 8, 8, 5))

# ── Road dashes ────────────────────────────────────────────────────────────────
DASH_H    = 60
DASH_GAP  = 40
DASH_W    = 8
NUM_LANES = 3   # dividing lines

class RoadDash:
    def __init__(self, x, y):
        self.x = x
        self.y = float(y)

    def update(self, speed):
        self.y += speed
        if self.y > SCREEN_H + DASH_H:
            self.y -= SCREEN_H + DASH_H + DASH_GAP

    def draw(self, surface):
        pygame.draw.rect(surface, LINE_COLOR,
                         (self.x - DASH_W // 2, int(self.y), DASH_W, DASH_H))

# ── Roadside scenery (trees) ───────────────────────────────────────────────────
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = float(y)

    def update(self, speed):
        self.y += speed * 0.8
        if self.y > SCREEN_H + 40:
            self.y -= SCREEN_H + 80
            side = random.choice([-1, 1])
            self.x = random.randint(10, 85) if side == -1 else random.randint(515, 580)

    def draw(self, surface):
        # trunk
        pygame.draw.rect(surface, (100, 60, 20), (self.x - 4, int(self.y) - 10, 8, 20))
        # foliage
        pygame.draw.circle(surface, GREEN, (self.x, int(self.y) - 20), 16)
        pygame.draw.circle(surface, (20, 140, 40), (self.x - 6, int(self.y) - 15), 10)

# ── Enemy car ──────────────────────────────────────────────────────────────────
ENEMY_COLORS = [RED, BLUE, ORANGE, (180, 0, 180), (0, 180, 180)]
LANE_CENTERS = [175, 300, 425]   # 3 lanes

class Enemy:
    W, H = 40, 60

    def __init__(self):
        self.reset(start=True)

    def reset(self, start=False):
        self.lane   = random.randint(0, 2)
        self.x      = float(LANE_CENTERS[self.lane])
        self.y      = float(random.randint(-300, -60) if start else -60)
        self.color  = random.choice(ENEMY_COLORS)
        self.speed  = random.uniform(1.5, 3.5)   # own movement

    def update(self, road_speed):
        self.y += road_speed + self.speed
        if self.y > SCREEN_H + self.H:
            self.reset()

    def draw(self, surface):
        draw_car(surface, int(self.x), int(self.y), self.color)

    def rect(self):
        return pygame.Rect(self.x - self.W // 2 + 4, self.y - self.H // 2 + 5,
                           self.W - 8, self.H - 10)

# ── Explosion particles ────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 0)
        self.life = random.randint(20, 45)
        self.color = random.choice([RED, ORANGE, YELLOW, WHITE])
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, self.life * 5)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# ── Main Game ─────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("RetroRacer  |  Arrow keys to drive")
    clock   = pygame.time.Clock()

    font_big   = pygame.font.SysFont("Courier New", 52, bold=True)
    font_med   = pygame.font.SysFont("Courier New", 28, bold=True)
    font_small = pygame.font.SysFont("Courier New", 20)

    # ── Grass strips (alternate color for motion effect) ──
    grass_offset = 0.0
    GRASS_STRIP_H = 40

    # ── Road dashes ──
    lane_xs = [233, 367]   # two dividing lines (3 lanes)
    dashes = []
    for lx in lane_xs:
        y = 0
        while y < SCREEN_H:
            dashes.append(RoadDash(lx, y))
            y += DASH_H + DASH_GAP

    # ── Trees ──
    trees = []
    for _ in range(10):
        side = random.choice([-1, 1])
        tx = random.randint(10, 85) if side == -1 else random.randint(515, 580)
        trees.append(Tree(tx, random.randint(0, SCREEN_H)))

    # ── Enemies ──
    enemies = [Enemy() for _ in range(5)]

    # ── Player ──
    player_x    = float(SCREEN_W // 2)
    player_y    = float(SCREEN_H - 130)
    player_lane = 1         # not strictly lane-locked; free steering
    PLAYER_SPEED = 4.0

    # ── Game state ──
    road_speed  = 4.0       # pixels/frame scroll speed
    MAX_SPEED   = 18.0
    MIN_SPEED   = 0.0
    ACCEL       = 0.06
    DECEL       = 0.10
    score       = 0
    best_score  = 0
    particles   = []
    game_over   = False
    started     = False

    def reset():
        nonlocal road_speed, score, game_over, started, player_x, particles
        road_speed = 4.0
        score = 0
        player_x = float(SCREEN_W // 2)
        particles.clear()
        for e in enemies:
            e.reset(start=True)
        game_over = False
        started   = True

    # ── Draw road scene ──────────────────────────────────────────────────────
    def draw_scene():
        # Grass (alternating strips for motion)
        strip_count = SCREEN_H // GRASS_STRIP_H + 2
        for i in range(strip_count):
            yy = int((i * GRASS_STRIP_H - grass_offset) % (SCREEN_H + GRASS_STRIP_H) - GRASS_STRIP_H)
            color = GRASS_L if i % 2 == 0 else GRASS_D
            screen.fill(color, (0, yy, ROAD_LEFT, GRASS_STRIP_H + 1))
            screen.fill(color, (ROAD_RIGHT, yy, SCREEN_W - ROAD_RIGHT, GRASS_STRIP_H + 1))

        # Road
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_W, SCREEN_H))

        # Road edge lines
        pygame.draw.rect(screen, WHITE, (ROAD_LEFT,      0, 5, SCREEN_H))
        pygame.draw.rect(screen, WHITE, (ROAD_RIGHT - 5, 0, 5, SCREEN_H))

        # Lane dashes
        for d in dashes:
            d.draw(screen)

        # Trees
        for t in trees:
            t.draw(screen)

    # ── HUD ─────────────────────────────────────────────────────────────────
    def draw_hud():
        speed_kmh = int(road_speed / MAX_SPEED * 220)
        score_surf = font_med.render(f"SCORE {score:06d}", True, WHITE)
        speed_surf = font_med.render(f"{speed_kmh:3d} km/h", True, YELLOW)
        best_surf  = font_small.render(f"BEST {best_score:06d}", True, GRAY)
        screen.blit(score_surf, (10, 10))
        screen.blit(speed_surf, (10, 44))
        screen.blit(best_surf,  (10, 74))

        # Speed bar
        bar_w = int((road_speed / MAX_SPEED) * 120)
        pygame.draw.rect(screen, DARK_GRAY, (SCREEN_W - 140, 14, 120, 16))
        pygame.draw.rect(screen, GREEN,     (SCREEN_W - 140, 14, bar_w, 16))
        pygame.draw.rect(screen, WHITE,     (SCREEN_W - 140, 14, 120, 16), 1)
        label = font_small.render("SPEED", True, WHITE)
        screen.blit(label, (SCREEN_W - 140, 34))

    # ── Overlay screens ─────────────────────────────────────────────────────
    def draw_title():
        screen.fill(BLACK)
        t1 = font_big.render("RETRO", True, YELLOW)
        t2 = font_big.render("RACER", True, RED)
        t3 = font_med.render("PRESS  ENTER  TO  START", True, WHITE)
        t4 = font_small.render("UP/DOWN = speed    LEFT/RIGHT = steer", True, GRAY)
        screen.blit(t1, t1.get_rect(centerx=SCREEN_W//2, y=200))
        screen.blit(t2, t2.get_rect(centerx=SCREEN_W//2, y=270))
        screen.blit(t3, t3.get_rect(centerx=SCREEN_W//2, y=400))
        screen.blit(t4, t4.get_rect(centerx=SCREEN_W//2, y=450))

    def draw_game_over():
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        t1 = font_big.render("GAME OVER", True, RED)
        t2 = font_med.render(f"SCORE  {score:06d}", True, YELLOW)
        t3 = font_med.render(f"BEST   {best_score:06d}", True, WHITE)
        t4 = font_small.render("ENTER = restart     ESC = quit", True, GRAY)
        screen.blit(t1, t1.get_rect(centerx=SCREEN_W//2, y=250))
        screen.blit(t2, t2.get_rect(centerx=SCREEN_W//2, y=330))
        screen.blit(t3, t3.get_rect(centerx=SCREEN_W//2, y=370))
        screen.blit(t4, t4.get_rect(centerx=SCREEN_W//2, y=450))

    # ── Game loop ─────────────────────────────────────────────────────────────
    while True:
        clock.tick(FPS)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_RETURN:
                    if not started or game_over:
                        reset()

        keys = pygame.key.get_pressed()

        if not started:
            draw_title()
            pygame.display.flip()
            continue

        if not game_over:
            # ── Speed control ──
            if keys[pygame.K_UP]:
                road_speed = min(MAX_SPEED, road_speed + ACCEL)
            elif keys[pygame.K_DOWN]:
                road_speed = max(MIN_SPEED, road_speed - DECEL)
            else:
                # natural friction
                road_speed = max(2.0, road_speed - ACCEL * 0.3)

            # ── Steering ──
            if keys[pygame.K_LEFT]:
                player_x = max(ROAD_LEFT, player_x - PLAYER_SPEED)
            if keys[pygame.K_RIGHT]:
                player_x = min(ROAD_RIGHT, player_x + PLAYER_SPEED)

            # ── Scroll scene ──
            grass_offset = (grass_offset + road_speed * 0.5) % GRASS_STRIP_H
            for d in dashes:
                d.update(road_speed)
            for t in trees:
                t.update(road_speed)
            for e in enemies:
                e.update(road_speed)

            # ── Score ──
            score += int(road_speed * 0.5)

            # ── Collision ──
            player_rect = pygame.Rect(player_x - 16, player_y - 25, 32, 50)
            for e in enemies:
                if player_rect.colliderect(e.rect()):
                    # Spawn explosion
                    for _ in range(60):
                        particles.append(Particle(player_x, player_y))
                    if score > best_score:
                        best_score = score
                    game_over = True

            # ── Edge crash ──
            if player_x <= ROAD_LEFT + 5 or player_x >= ROAD_RIGHT - 5:
                for _ in range(60):
                    particles.append(Particle(player_x, player_y))
                if score > best_score:
                    best_score = score
                game_over = True

        # ── Particles ──
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ── Draw ──
        draw_scene()
        for e in enemies:
            e.draw(screen)
        draw_car(screen, int(player_x), int(player_y), (220, 220, 220), is_player=True)
        for p in particles:
            p.draw(screen)
        draw_hud()

        if game_over:
            draw_game_over()

        pygame.display.flip()


if __name__ == "__main__":
    main()
