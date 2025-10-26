"""
VOID RUNNER — a (easier) bullet-hell shooter in pure Python (turtle)

Run:
    python void_runner.py

Controls:
    Arrow keys or WASD  -> Move
    Space               -> Fire (hold to autofire)
    B                   -> Bomb (clears nearby bullets/enemies; limited)
    P                   -> Pause / Resume
    R                   -> Restart after Game Over
    H                   -> Toggle help
"""

import turtle as tt
import math, random, time

# -------------------- Config (EASIER) --------------------
WIDTH, HEIGHT = 1000, 700
DT_MS = 33  # ~30 fps
PLAYER_SPEED = 8.0
PLAYER_RADIUS = 12
BULLET_RADIUS = 4
ENEMY_RADIUS = 14

# Easier limits
ENEMY_BULLET_RADIUS = 5
MAX_ENEMIES = 32            # was 40
MAX_BULLETS = 120
MAX_ENEMY_BULLETS = 120     # was 220

# -------------------- Screen & Layers --------------------
screen = tt.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("VOID RUNNER — Bullet Hell (turtle) [Easier]")
screen.tracer(0, 0)
screen.bgcolor(0.03, 0.03, 0.05)

# Drawing layers
pen = tt.Turtle(visible=False); pen.penup(); pen.speed(0)
ui  = tt.Turtle(visible=False); ui.penup();  ui.speed(0)
bg  = tt.Turtle(visible=False); bg.penup();  bg.speed(0)

# -------------------- State --------------------
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.running = True
        self.paused = False
        self.frame = 0
        self.time_start = time.time()
        self.score = 0
        self.hiscore = getattr(self, "hiscore", 0)
        self.level = 1
        self.difficulty = 1.0
        self.key = {"up":False, "down":False, "left":False, "right":False, "fire":False}
        self.player = {
            "x": 0.0, "y": -HEIGHT/2+80, "vx": 0.0, "vy": 0.0,
            "lives": 3, "bombs": 2, "invuln": 0, "power": 1, "rof_cd": 0
        }
        self.bullets  = []  # player bullets
        self.enemies  = []  # enemies
        self.ebullets = []  # enemy bullets
        self.powerups = []  # {'x','y','type','vy'}
        self.particles = []
        self.spawn_cd = 30
        self.help = True
        pen.clear(); ui.clear()
        self.draw_starfield()

    def draw_starfield(self):
        random.seed(7)
        bg.clear()
        bg.color(0.35,0.4,0.55)
        for _ in range(130):
            x = random.randint(-WIDTH//2+10, WIDTH//2-10)
            y = random.randint(-HEIGHT//2+10, HEIGHT//2-10)
            bg.goto(x, y); bg.dot(2)
        bg.color(0.6,0.65,0.85)
        for _ in range(45):
            x = random.randint(-WIDTH//2+10, WIDTH//2-10)
            y = random.randint(-HEIGHT//2+10, HEIGHT//2-10)
            bg.goto(x, y); bg.dot(2)

G = Game()

# -------------------- Helpers --------------------
def clamp(v, lo, hi): return max(lo, min(hi, v))
def within_bounds(x, y, pad=20):
    return (-WIDTH/2-pad <= x <= WIDTH/2+pad) and (-HEIGHT/2-pad <= y <= HEIGHT/2+pad)
def circle_hit(ax, ay, ar, bx, by, br):
    dx, dy = ax-bx, ay-by
    return dx*dx + dy*dy <= (ar+br)*(ar+br)

# -------------------- Spawning --------------------
def spawn_enemy():
    edge = random.choice(["top","left","right"])
    if edge=="top":
        x = random.uniform(-WIDTH/2+60, WIDTH/2-60); y = HEIGHT/2 + 20
        vx = random.uniform(-1.0, 1.0) * (0.8 + G.difficulty*0.2)
        vy = -random.uniform(2.0, 4.0) * (0.8 + G.difficulty*0.25)
    elif edge=="left":
        x = -WIDTH/2 - 20; y = random.uniform(-HEIGHT/2+80, HEIGHT/2-120)
        vx = random.uniform(2.2, 3.6) * (0.8 + G.difficulty*0.2); vy = random.uniform(-0.6, 0.6)
    else:
        x = WIDTH/2 + 20; y = random.uniform(-HEIGHT/2+80, HEIGHT/2-120)
        vx = -random.uniform(2.2, 3.6) * (0.8 + G.difficulty*0.2); vy = random.uniform(-0.6, 0.6)

    t = random.random()
    kind = "chaser" if t < 0.35 else ("sine" if t < 0.7 else "turret")
    hp = 1 + int(G.difficulty*0.6) + (0 if kind!="chaser" else 1)
    enemy = {"x":x,"y":y,"vx":vx,"vy":vy,"hp":hp,"kind":kind,"cd":int(20+random.random()*20),"t":0.0}
    G.enemies.append(enemy)

def spawn_powerup(x, y):
    roll = random.random()
    if roll < 0.5:
        typ = "power"
    elif roll < 0.8:
        typ = "bomb"
    else:
        typ = "life"
    G.powerups.append({"x":x,"y":y,"type":typ,"vy":-1.0})

def explode(x, y, dots=16):
    for i in range(dots):
        ang = (2*math.pi)*i/dots
        spd = random.uniform(2.0, 4.0)
        G.particles.append({"x":x,"y":y,"vx":math.cos(ang)*spd,"vy":math.sin(ang)*spd,"life":20})

# -------------------- Input --------------------
def key_down(k):
    if k in ("Up","w","W"): G.key["up"]=True
    if k in ("Down","s","S"): G.key["down"]=True
    if k in ("Left","a","A"): G.key["left"]=True
    if k in ("Right","d","D"): G.key["right"]=True
    if k in ("space",): G.key["fire"]=True

def key_up(k):
    if k in ("Up","w","W"): G.key["up"]=False
    if k in ("Down","s","S"): G.key["down"]=False
    if k in ("Left","a","A"): G.key["left"]=False
    if k in ("Right","d","D"): G.key["right"]=False
    if k in ("space",): G.key["fire"]=False

def toggle_pause():
    G.paused = not G.paused
def toggle_help():
    G.help = not G.help
def do_bomb():
    if not G.running or G.paused: return
    if G.player["bombs"] <= 0: return
    G.player["bombs"] -= 1
    px, py = G.player["x"], G.player["y"]
    # clear bullets in radius
    nb = []
    for b in G.ebullets:
        if not circle_hit(px, py, 160, b["x"], b["y"], ENEMY_BULLET_RADIUS):
            nb.append(b)
    G.ebullets = nb
    # damage enemies in radius
    for e in G.enemies[:]:
        if circle_hit(px, py, 200, e["x"], e["y"], ENEMY_RADIUS):
            e["hp"] -= 3
            if e["hp"] <= 0:
                G.enemies.remove(e)
                G.score += 50
                explode(e["x"], e["y"])
                if random.random() < 0.2: spawn_powerup(e["x"], e["y"])

def restart():
    G.reset()

# -------------------- Update --------------------
def update_player():
    p = G.player
    if p["invuln"] > 0: p["invuln"] -= 1
    vx = (G.key["right"] - G.key["left"]) * PLAYER_SPEED
    vy = (G.key["up"] - G.key["down"]) * PLAYER_SPEED
    p["x"] = clamp(p["x"] + vx, -WIDTH/2+20, WIDTH/2-20)
    p["y"] = clamp(p["y"] + vy, -HEIGHT/2+20, HEIGHT/2-40)
    # shooting
    if p["rof_cd"] > 0: p["rof_cd"] -= 1
    if G.key["fire"] and p["rof_cd"] <= 0:
        fire_player()

def fire_player():
    p = G.player
    power = clamp(p["power"], 1, 5)
    p["rof_cd"] = max(5, 12 - power*2)
    spread = (power-1) * 0.15
    # center
    G.bullets.append({"x":p["x"], "y":p["y"]+16, "vx":0, "vy":9.0, "dmg":1+power//2})
    # sides
    for i in range(power-1):
        off = (i//2+1)*12 * (1 if i%2==0 else -1)
        ang = (0.0 if power<3 else (spread if off>0 else -spread))
        vx = math.sin(ang)*9.0; vy = math.cos(ang)*9.0
        G.bullets.append({"x":p["x"]+off, "y":p["y"]+14, "vx":vx, "vy":vy, "dmg":1+power//2})
    if len(G.bullets) > MAX_BULLETS:
        G.bullets = G.bullets[-MAX_BULLETS:]

def update_bullets():
    nb = []
    for b in G.bullets:
        b["x"] += b["vx"]; b["y"] += b["vy"]
        if within_bounds(b["x"], b["y"], pad=40): nb.append(b)
    G.bullets = nb

def update_enemies():
    for e in G.enemies[:]:
        e["t"] += 0.05
        if e["kind"] == "sine":
            e["x"] += e["vx"]*0.6
            e["y"] += e["vy"]
            e["x"] += math.sin(e["t"]*3.0) * (1.8+G.difficulty*0.3)
        elif e["kind"] == "chaser":
            dx, dy = G.player["x"]-e["x"], G.player["y"]-e["y"]
            d = math.hypot(dx, dy)+1e-6
            e["vx"] += (dx/d)*0.05*(1+0.2*G.difficulty)
            e["vy"] += (dy/d)*0.05*(1+0.2*G.difficulty)
            e["x"] += e["vx"]; e["y"] += e["vy"]
        else:  # turret
            e["x"] += e["vx"]*0.8; e["y"] += e["vy"]*0.8

        # Easier: enemies fire less often
        e["cd"] -= 1
        if e["cd"] <= 0 and len(G.ebullets) < MAX_ENEMY_BULLETS:
            e["cd"] = int(56 - min(20, G.difficulty*2)) + random.randint(-4, 10)
            shoot_pattern(e)

        if not within_bounds(e["x"], e["y"], pad=120):
            G.enemies.remove(e)

def shoot_pattern(e):
    """Easier patterns: fewer bullets per volley, slower speeds."""
    ex, ey = e["x"], e["y"]
    px, py = G.player["x"], G.player["y"]
    mode = e["kind"]

    spd_mul = 0.75   # bullets travel slower
    rad_mul = 0.55   # fewer bullets in radial patterns

    if mode == "turret":
        base_n = 6 + int(G.difficulty*0.8)
        n = max(4, int(base_n * rad_mul))   # fewer bullets
        for i in range(n):
            a  = 2*math.pi*i/n
            vx = math.cos(a) * (2.5 + 0.2*G.difficulty) * spd_mul
            vy = math.sin(a) * (2.5 + 0.2*G.difficulty) * spd_mul
            G.ebullets.append({"x":ex, "y":ey, "vx":vx, "vy":vy})

    elif mode == "sine":
        # aimed DOUBLE (was triple)
        dx, dy = px-ex, py-ey
        ang = math.atan2(dy, dx)
        for da in (-0.12, 0.12):
            vx = math.cos(ang+da) * (3.0 + 0.2*G.difficulty) * spd_mul
            vy = math.sin(ang+da) * (3.0 + 0.2*G.difficulty) * spd_mul
            G.ebullets.append({"x":ex, "y":ey, "vx":vx, "vy":vy})
    else:
        # chaser: gentle spiral, still 2 bullets, slower
        base = G.frame*0.08
        for i in range(2):
            a  = base + i*math.pi
            vx = math.cos(a) * (2.0 + 0.15*G.difficulty) * spd_mul
            vy = math.sin(a) * (2.0 + 0.15*G.difficulty) * spd_mul
            G.ebullets.append({"x":ex, "y":ey, "vx":vx, "vy":vy})

def update_enemy_bullets():
    nb = []
    for b in G.ebullets:
        b["x"] += b["vx"]; b["y"] += b["vy"]
        if within_bounds(b["x"], b["y"], pad=60): nb.append(b)
    G.ebullets = nb

def update_powerups():
    for p in G.powerups[:]:
        p["y"] += p.get("vy",-1.0)
        if not within_bounds(p["x"], p["y"], pad=20):
            G.powerups.remove(p)

def update_particles():
    for pt in G.particles[:]:
        pt["x"] += pt["vx"]; pt["y"] += pt["vy"]
        pt["vx"] *= 0.96; pt["vy"] *= 0.96
        pt["life"] -= 1
        if pt["life"] <= 0:
            G.particles.remove(pt)

def handle_collisions():
    # bullets hit enemies
    for b in G.bullets[:]:
        for e in G.enemies[:]:
            if circle_hit(b["x"], b["y"], BULLET_RADIUS, e["x"], e["y"], ENEMY_RADIUS):
                e["hp"] -= b["dmg"]
                if b in G.bullets: G.bullets.remove(b)
                if e["hp"] <= 0:
                    if e in G.enemies:
                        G.enemies.remove(e)
                        G.score += 25
                        explode(e["x"], e["y"])
                        if random.random() < 0.15: spawn_powerup(e["x"], e["y"])
                break

    # enemy bullets / enemies hit player
    p = G.player
    if p["invuln"] <= 0 and G.running:
        for b in G.ebullets[:]:
            if circle_hit(p["x"], p["y"], PLAYER_RADIUS, b["x"], b["y"], ENEMY_BULLET_RADIUS):
                player_hit()
                if b in G.ebullets: G.ebullets.remove(b)
                break
        for e in G.enemies[:]:
            if circle_hit(p["x"], p["y"], PLAYER_RADIUS+4, e["x"], e["y"], ENEMY_RADIUS):
                player_hit()
                if e in G.enemies: G.enemies.remove(e)
                explode(e["x"], e["y"])
                break

    # powerups
    for pw in G.powerups[:]:
        if circle_hit(p["x"], p["y"], PLAYER_RADIUS+6, pw["x"], pw["y"], 10):
            if pw["type"]=="power":
                p["power"] = min(5, p["power"]+1)
            elif pw["type"]=="bomb":
                p["bombs"] = min(5, p["bombs"]+1)
            else:
                p["lives"] = min(6, p["lives"]+1)
            G.powerups.remove(pw)

def player_hit():
    p = G.player
    p["lives"] -= 1
    p["invuln"] = 90
    p["power"] = max(1, p["power"]-1)
    explode(p["x"], p["y"], dots=24)
    if p["lives"] < 0:
        game_over()

def game_over():
    G.running = False
    if G.score > G.hiscore:
        G.hiscore = G.score

# -------------------- Difficulty & Spawning (EASIER) --------------------
def step_difficulty():
    # Slower ramp
    if G.frame % 60 == 0:
        elapsed = time.time() - G.time_start
        G.difficulty = 1.0 + elapsed / 35.0  # was /25.0
        G.level = 1 + int(elapsed // 20)

    # More breathing room between spawns
    G.spawn_cd -= 1
    min_cd = max(12, 30 - int(G.difficulty*2))  # was max(8, 26 - int(G.difficulty*3))
    if G.spawn_cd <= 0 and len(G.enemies) < MAX_ENEMIES:
        spawn_enemy()
        G.spawn_cd = random.randint(min_cd, min_cd+10)

# -------------------- Draw --------------------
def draw_game():
    pen.clear()
    # particles (behind)
    pen.color(1, 0.7, 0.2)
    for pt in G.particles:
        pen.goto(pt["x"], pt["y"]); pen.dot(3)

    # enemies
    for e in G.enemies:
        if e["kind"]=="turret": pen.color(0.8, 0.2, 0.8)
        elif e["kind"]=="sine": pen.color(0.9, 0.5, 0.1)
        else:                   pen.color(0.6, 0.9, 0.2)
        pen.goto(e["x"], e["y"]); pen.dot(ENEMY_RADIUS*2)

    # enemy bullets
    pen.color(0.95, 0.3, 0.3)
    for b in G.ebullets:
        pen.goto(b["x"], b["y"]); pen.dot(ENEMY_BULLET_RADIUS*2)

    # player bullets
    pen.color(0.4, 0.9, 1.0)
    for b in G.bullets:
        pen.goto(b["x"], b["y"]); pen.dot(BULLET_RADIUS*2)

    # powerups
    for pw in G.powerups:
        if pw["type"]=="power": pen.color(0.3, 1.0, 0.5)
        elif pw["type"]=="bomb": pen.color(1.0, 0.95, 0.3)
        else: pen.color(0.5, 0.8, 1.0)
        pen.goto(pw["x"], pw["y"]); pen.dot(12)

    # player
    p = G.player
    if p["invuln"] > 0 and (G.frame//6)%2==0:
        pass  # blink
    else:
        pen.color(0.2, 0.95, 0.85)
        pen.goto(p["x"], p["y"]); pen.dot(PLAYER_RADIUS*2)

    draw_ui()
    screen.update()

def draw_ui():
    ui.clear()
    ui.goto(-WIDTH//2+14, HEIGHT//2-28)
    ui.color(0.85, 0.92, 1.0)
    ui.write(
        f"Score: {G.score}   Hi: {G.hiscore}   Lives: {G.player['lives']}   "
        f"Bombs: {G.player['bombs']}   Power: {G.player['power']}   Lv: {G.level}",
        align="left", font=("Consolas", 12, "normal")
    )
    if G.help and G.running:
        ui.sety(ui.ycor()-22)
        ui.write("Move: WASD/Arrows | Fire: Space | Bomb: B | Pause: P | Help: H",
                 align="left", font=("Consolas", 11, "normal"))
    if not G.running:
        ui.goto(0, 30); ui.color(1.0,0.85,0.2)
        ui.write("GAME OVER", align="center", font=("Consolas", 24, "bold"))
        ui.goto(0, -5); ui.color(0.9,0.95,1.0)
        ui.write("Press R to restart", align="center", font=("Consolas", 14, "normal"))
    if G.paused and G.running:
        ui.goto(0, 0); ui.color(1.0,1.0,0.7)
        ui.write("PAUSED", align="center", font=("Consolas", 22, "bold"))

# -------------------- Main Loop --------------------
def tick():
    if not G.paused and G.running:
        G.frame += 1
        update_player()
        update_bullets()
        update_enemies()
        update_enemy_bullets()
        update_powerups()
        update_particles()
        handle_collisions()
        if G.frame % 15 == 0: G.score += 1
        step_difficulty()
    draw_game()
    screen.ontimer(tick, DT_MS)

# -------------------- Bindings --------------------
def bind_keys():
    # Key down
    screen.onkeypress(lambda: key_down("Up"), "Up")
    screen.onkeypress(lambda: key_down("Down"), "Down")
    screen.onkeypress(lambda: key_down("Left"), "Left")
    screen.onkeypress(lambda: key_down("Right"), "Right")
    screen.onkeypress(lambda: key_down("w"), "w")
    screen.onkeypress(lambda: key_down("W"), "W")
    screen.onkeypress(lambda: key_down("s"), "s")
    screen.onkeypress(lambda: key_down("S"), "S")
    screen.onkeypress(lambda: key_down("a"), "a")
    screen.onkeypress(lambda: key_down("A"), "A")
    screen.onkeypress(lambda: key_down("d"), "d")
    screen.onkeypress(lambda: key_down("D"), "D")
    screen.onkeypress(lambda: key_down("space"), "space")
    # Key up
    screen.onkeyrelease(lambda: key_up("Up"), "Up")
    screen.onkeyrelease(lambda: key_up("Down"), "Down")
    screen.onkeyrelease(lambda: key_up("Left"), "Left")
    screen.onkeyrelease(lambda: key_up("Right"), "Right")
    screen.onkeyrelease(lambda: key_up("w"), "w")
    screen.onkeyrelease(lambda: key_up("W"), "W")
    screen.onkeyrelease(lambda: key_up("s"), "s")
    screen.onkeyrelease(lambda: key_up("S"), "s")
    screen.onkeyrelease(lambda: key_up("a"), "a")
    screen.onkeyrelease(lambda: key_up("A"), "A")
    screen.onkeyrelease(lambda: key_up("d"), "d")
    screen.onkeyrelease(lambda: key_up("D"), "D")
    screen.onkeyrelease(lambda: key_up("space"), "space")
    # Actions
    screen.onkey(toggle_pause, "p"); screen.onkey(toggle_pause, "P")
    screen.onkey(toggle_help,  "h"); screen.onkey(toggle_help,  "H")
    screen.onkey(do_bomb,      "b"); screen.onkey(do_bomb,      "B")
    screen.onkey(restart,      "r"); screen.onkey(restart,      "R")
    screen.listen()

bind_keys()
tick()
screen.mainloop()
