import pygame
import random
import math
import sys

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 700, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Blitz")
clock = pygame.time.Clock()

# --- Colors ---
BG        = (15, 12, 30)
PADDLE    = (100, 220, 255)
WHITE     = (255, 255, 255)
SCORE_COL = (200, 180, 255)
LIVES_COL = (255, 120, 130)
TEXT_DIM  = (120, 110, 160)

BUBBLE_COLORS = [
    (255, 100, 160),  # pink
    (100, 210, 255),  # cyan
    (160, 255, 120),  # green
    (255, 200, 80),   # yellow
    (200, 130, 255),  # purple
]

# --- Fonts ---
font_big   = pygame.font.SysFont("consolas", 48, bold=True)
font_med   = pygame.font.SysFont("consolas", 28)
font_small = pygame.font.SysFont("consolas", 20)

# --- Bubble class ---
class Bubble:
    def __init__(self, x=None, y=None, radius=None, vx=None, vy=None, generation=0):
        self.radius     = radius  if radius is not None else random.randint(22, 38)
        self.x          = x      if x      is not None else random.randint(self.radius, WIDTH - self.radius)
        self.y          = y      if y      is not None else -self.radius
        self.vx         = vx     if vx     is not None else random.uniform(-2.5, 2.5)
        self.vy         = vy     if vy     is not None else random.uniform(2.0, 4.5)
        self.generation = generation  # 0=big, 1=medium, 2=small (no more splits)
        self.color      = random.choice(BUBBLE_COLORS)
        self.alive      = True
        # Wobble for visual flair
        self.wobble_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Bounce off side walls
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -abs(self.vx)

    def draw(self, surface, t):
        # Slight wobble on radius for a bubbly feel
        wobble = math.sin(t * 0.06 + self.wobble_offset) * 2
        r = int(self.radius + wobble)
        cx, cy = int(self.x), int(self.y)

        # Shadow
        pygame.draw.circle(surface, (0, 0, 0, 60), (cx + 3, cy + 3), r)
        # Main bubble fill (semi-transparent feel via layered circles)
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # Inner lighter circle for gloss
        inner_r = max(r - 6, 4)
        lighter = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(surface, lighter, (cx - r//5, cy - r//5), inner_r // 2)
        # Outline
        pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)

    def split(self):
        """Return two smaller child bubbles, or nothing if too small."""
        if self.generation >= 2:
            return []
        new_r  = max(12, self.radius // 2)
        speed  = max(2.5, abs(self.vy) * 0.8)
        child1 = Bubble(self.x, self.y, new_r,  speed,  speed * 0.6, self.generation + 1)
        child2 = Bubble(self.x, self.y, new_r, -speed,  speed * 0.6, self.generation + 1)
        return [child1, child2]

    def is_off_screen(self):
        return self.y - self.radius > HEIGHT

# --- Paddle ---
class Paddle:
    W, H = 110, 14

    def __init__(self):
        self.x = WIDTH // 2 - self.W // 2
        self.y = HEIGHT - 50
        self.speed = 7

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        # Clamp to screen
        self.x = max(0, min(WIDTH - self.W, self.x))

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.W, self.H)
        pygame.draw.rect(surface, PADDLE, rect, border_radius=7)
        # Gloss line on paddle
        pygame.draw.rect(surface, WHITE, (self.x + 6, self.y + 3, self.W - 12, 3), border_radius=2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

# --- Particle effect on pop ---
class Particle:
    def __init__(self, x, y, color):
        self.x     = x
        self.y     = y
        self.vx    = random.uniform(-4, 4)
        self.vy    = random.uniform(-5, -1)
        self.life  = random.randint(18, 32)
        self.color = color
        self.size  = random.randint(3, 7)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.2  # gravity
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * self.life / 32))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

# --- Game state ---
def reset_game():
    return {
        "bubbles"   : [],
        "particles" : [],
        "paddle"    : Paddle(),
        "score"     : 0,
        "lives"     : 3,
        "spawn_timer": 0,
        "spawn_rate" : 90,   # frames between spawns (decreases over time)
        "level"      : 1,
        "level_timer": 0,
        "t"          : 0,    # frame counter for animations
        "state"      : "play",  # "play" | "gameover"
    }

def spawn_bubble(g):
    g["bubbles"].append(Bubble())

def draw_hud(surface, g):
    # Score
    score_surf = font_med.render(f"Score: {g['score']}", True, SCORE_COL)
    surface.blit(score_surf, (14, 12))
    # Level
    lvl_surf = font_med.render(f"Level {g['level']}", True, TEXT_DIM)
    surface.blit(lvl_surf, (WIDTH // 2 - lvl_surf.get_width() // 2, 12))
    # Lives as bubbles
    for i in range(g["lives"]):
        pygame.draw.circle(surface, LIVES_COL, (WIDTH - 30 - i * 30, 26), 10)
        pygame.draw.circle(surface, WHITE, (WIDTH - 30 - i * 30, 26), 10, 2)
    # Thin divider
    pygame.draw.line(surface, (50, 45, 75), (0, 50), (WIDTH, 50), 1)

def draw_gameover(surface, g):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 8, 22, 200))
    surface.blit(overlay, (0, 0))

    title = font_big.render("GAME OVER", True, LIVES_COL)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 160))

    sc = font_med.render(f"Final Score: {g['score']}", True, SCORE_COL)
    surface.blit(sc, (WIDTH // 2 - sc.get_width() // 2, 240))

    hint = font_small.render("Press  R  to play again   or   ESC  to quit", True, TEXT_DIM)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))

def draw_start_hint(surface, t):
    if t < 200:
        alpha = min(255, t * 4)
        hint = font_small.render("← → or A D  to move paddle", True, TEXT_DIM)
        s = pygame.Surface(hint.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        s.blit(hint, (0, 0))
        s.set_alpha(alpha)
        surface.blit(s, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 28))

# --- Main loop ---
def main():
    g = reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r and g["state"] == "gameover":
                    g = reset_game()

        if g["state"] == "play":
            keys = pygame.key.get_pressed()
            g["paddle"].update(keys)
            g["t"] += 1
            g["spawn_timer"] += 1
            g["level_timer"]  += 1

            # Increase difficulty every 20 s (1200 frames at 60fps)
            if g["level_timer"] > 1200:
                g["level_timer"] = 0
                g["level"] += 1
                g["spawn_rate"] = max(30, g["spawn_rate"] - 10)

            if g["spawn_timer"] >= g["spawn_rate"]:
                g["spawn_timer"] = 0
                spawn_bubble(g)

            # Update bubbles
            new_bubbles = []
            for b in g["bubbles"]:
                b.update()
                if b.is_off_screen():
                    g["lives"] -= 1
                    b.alive = False
                    if g["lives"] <= 0:
                        g["state"] = "gameover"

                # Paddle collision
                if b.alive:
                    pb = b  # use circle-rect check
                    pad_rect = g["paddle"].get_rect()
                    closest_x = max(pad_rect.left, min(b.x, pad_rect.right))
                    closest_y = max(pad_rect.top,  min(b.y, pad_rect.bottom))
                    dist = math.hypot(b.x - closest_x, b.y - closest_y)
                    if dist < b.radius:
                        # Pop!
                        b.alive = False
                        pts = (3 - b.generation) * 10  # bigger = fewer points
                        g["score"] += pts
                        # Particles
                        for _ in range(14):
                            g["particles"].append(Particle(b.x, b.y, b.color))
                        # Split
                        new_bubbles.extend(b.split())

            g["bubbles"] = [b for b in g["bubbles"] if b.alive] + new_bubbles

            # Update particles
            g["particles"] = [p for p in g["particles"] if p.life > 0]
            for p in g["particles"]:
                p.update()

        # --- Draw ---
        screen.fill(BG)

        # Subtle grid background
        for gx in range(0, WIDTH, 40):
            pygame.draw.line(screen, (25, 22, 45), (gx, 0), (gx, HEIGHT))
        for gy in range(0, HEIGHT, 40):
            pygame.draw.line(screen, (25, 22, 45), (0, gy), (WIDTH, gy))

        for b in g["bubbles"]:
            b.draw(screen, g["t"])
        for p in g["particles"]:
            p.draw(screen)
        g["paddle"].draw(screen)

        draw_hud(screen, g)
        draw_start_hint(screen, g["t"])

        if g["state"] == "gameover":
            draw_gameover(screen, g)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
