# TOOLY Racer - Endless Racing Game for Pimoroni Tufty 2040
# Created by Owen Edwards as an open source game for everyone to enjoy
# v.1.2.050526: GC pressure, I2C reads cached, float overflow, pre-allocated obstacles
#
# Set USE_QWSTPAD = True  → Pimoroni QwSTPad via QwST connector
# Set USE_QWSTPAD = False → Built-in Tufty 2040 buttons
USE_QWSTPAD = True   # ← Tufty built-in buttons
USE_QWSTPAD = False    # ← Pimoroni QwSTPad via QwST connector

import time
import random
import gc
from machine import Pin, I2C
from picographics import PicoGraphics, DISPLAY_TUFTY_2040

# ── Display ───────────────────────────────────────────────────
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
WIDTH, HEIGHT = display.get_bounds()  # 320 x 240

# ══════════════════════════════════════════════════════════════
# INPUT SETUP
# ══════════════════════════════════════════════════════════════
if not USE_QWSTPAD:
    _btn_a    = Pin(7,  Pin.IN, Pin.PULL_DOWN)
    _btn_b    = Pin(8,  Pin.IN, Pin.PULL_DOWN)
    _btn_c    = Pin(9,  Pin.IN, Pin.PULL_DOWN)
    _btn_up   = Pin(22, Pin.IN, Pin.PULL_DOWN)
    _btn_down = Pin(6,  Pin.IN, Pin.PULL_DOWN)

    # FIX: Read all buttons once per frame into a cached tuple
    def read_buttons():
        return (
            _btn_a.value(),
            _btn_b.value(),
            _btn_c.value(),
            _btn_up.value(),
            _btn_down.value()
        )

    def any_pressed(btns): return any(btns)
    def left_pressed(btns):  return btns[0]
    def right_pressed(btns): return btns[2]
    def up_pressed(btns):    return btns[3]
    def down_pressed(btns):  return btns[4]

else:
    QWSTPAD_ADDR = 0x3C
    QWSTPAD_REG  = 0x01
    _i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

    # FIX: Read I2C ONCE per frame, return cached byte
    def read_buttons():
        try:
            _i2c.writeto(QWSTPAD_ADDR, bytes([QWSTPAD_REG]))
            data = _i2c.readfrom(QWSTPAD_ADDR, 1)
            return data[0]
        except OSError:
            return 0xFF

    def any_pressed(b):   return (b & 0x3F) != 0x3F
    def left_pressed(b):  return (b & 0x04) == 0
    def right_pressed(b): return (b & 0x08) == 0
    def up_pressed(b):    return (b & 0x01) == 0
    def down_pressed(b):  return (b & 0x02) == 0


# ── Colours ───────────────────────────────────────────────────
BLACK   = display.create_pen(0,   0,   0)
WHITE   = display.create_pen(255, 255, 255)
GREY    = display.create_pen(80,  80,  80)
DKGREY  = display.create_pen(40,  40,  40)
YELLOW  = display.create_pen(255, 220, 0)
RED     = display.create_pen(220, 30,  30)
BLUE    = display.create_pen(30,  80,  220)
GREEN   = display.create_pen(30,  180, 30)
ORANGE  = display.create_pen(255, 140, 0)
CYAN    = display.create_pen(0,   220, 220)

# ── Road Layout ───────────────────────────────────────────────
ROAD_LEFT  = 40
ROAD_RIGHT = 280
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

DASH_HEIGHT = 30
DASH_GAP    = 20
DASH_X      = WIDTH // 2 - 3
DASH_W      = 6

# ── Player Car ────────────────────────────────────────────────
CAR_W = 45
CAR_H = 62
CAR_Y = HEIGHT - CAR_H - 10

# ── Game Constants ────────────────────────────────────────────
MIN_SPEED     = 5
MAX_SPEED     = 12
SPEED_STEP    = 0.5
OBSTACLE_W    = 45
OBSTACLE_H    = 62
MAX_OBSTACLES = 5

# FIX: stripe scroll wraps at this value to prevent float overflow
STRIPE_WRAP = 1000

OBS_COLOURS = [RED, ORANGE, CYAN, GREEN, WHITE, YELLOW, BLACK]

# FIX: Pre-allocate obstacle pool as fixed-size list of lists
# Each obstacle: [x, y, colour_index, active]
# This avoids creating/destroying lists every frame
_obs_pool = [[0, 0, 0, False] for _ in range(MAX_OBSTACLES)]


# ══════════════════════════════════════════════════════════════
# Wait for any button
# ══════════════════════════════════════════════════════════════
def wait_for_any_button():
    while not any_pressed(read_buttons()):
        time.sleep_ms(50)
    while any_pressed(read_buttons()):
        time.sleep_ms(50)


# ══════════════════════════════════════════════════════════════
# Draw car
# ══════════════════════════════════════════════════════════════
def draw_car(x, y, w, h, body_colour, detail_colour):
    display.set_pen(body_colour)
    display.rectangle(x, y + 6, w, h - 12)

    display.set_pen(detail_colour)
    margin = w // 5
    display.rectangle(x + margin, y + h // 4, w - margin * 2, h // 2)

    display.set_pen(body_colour)
    display.rectangle(x + 4, y, w - 8, 8)
    display.rectangle(x + 4, y + h - 8, w - 8, 8)

    display.set_pen(BLACK)
    ww, wh = 5, 10
    display.rectangle(x - ww + 2, y + 6,          ww, wh)
    display.rectangle(x + w - 2,  y + 6,          ww, wh)
    display.rectangle(x - ww + 2, y + h - 6 - wh, ww, wh)
    display.rectangle(x + w - 2,  y + h - 6 - wh, ww, wh)


# ══════════════════════════════════════════════════════════════
# Draw road
# ══════════════════════════════════════════════════════════════
def draw_road(stripe_offset):
    display.set_pen(DKGREY)
    display.clear()

    display.set_pen(GREEN)
    display.rectangle(0, 0, ROAD_LEFT, HEIGHT)
    display.rectangle(ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT)

    display.set_pen(GREY)
    display.rectangle(ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT)

    stripe_h = 20
    kerb_colours = [RED, WHITE]
    for i in range(HEIGHT // stripe_h + 2):
        y = i * stripe_h - stripe_offset % stripe_h
        display.set_pen(kerb_colours[i % 2])
        display.rectangle(ROAD_LEFT,      y, 8, stripe_h - 1)
        display.rectangle(ROAD_RIGHT - 8, y, 8, stripe_h - 1)

    total = DASH_HEIGHT + DASH_GAP
    for i in range(HEIGHT // total + 2):
        y = i * total - stripe_offset % total
        display.set_pen(YELLOW)
        display.rectangle(DASH_X, y, DASH_W, DASH_HEIGHT)


# ══════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════
def draw_hud(score, speed):
    display.set_pen(WHITE)
    display.text("SCORE: {}".format(score), 2, 4, scale=2.5)
    display.set_pen(YELLOW)
    display.text("SPD:{:.0f}".format(speed), 2, 22, scale=3)


# ══════════════════════════════════════════════════════════════
# Collision (AABB)
# ══════════════════════════════════════════════════════════════
def collides(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and ax + aw > bx and
            ay < by + bh and ay + ah > by)


# ══════════════════════════════════════════════════════════════
# Title screen
# ══════════════════════════════════════════════════════════════
def title_screen():
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(YELLOW)
    display.text("TOOLY RACER", 50, 50, scale=4)
    display.set_pen(YELLOW)
    display.text("Avoid the dumbasses!", 65, 110, scale=2)
    display.set_pen(WHITE)
    display.text("LEFT = Left  RIGHT = Right", 10, 145, scale=2)
    display.set_pen(GREEN)
    display.text("UP = Faster  DOWN = Slower", 10, 168, scale=2)
    mode_str = "QwSTPad" if USE_QWSTPAD else "Tufty Buttons"
    display.set_pen(CYAN)
    display.text("Input: {}".format(mode_str), 10, 191, scale=2)
    display.set_pen(YELLOW)
    display.text("Press any button", 75, 214, scale=2)
    display.update()
    wait_for_any_button()


# ══════════════════════════════════════════════════════════════
# Game Over screen
# ══════════════════════════════════════════════════════════════
def game_over_screen(score):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(RED)
    display.text("DUMBASS", 80, 70, scale=4)
    display.set_pen(WHITE)
    display.text("Score: {}".format(score), 95, 130, scale=3)
    display.set_pen(YELLOW)
    display.text("Go again hotshot?", 65, 185, scale=2)
    display.update()
    wait_for_any_button()


# ══════════════════════════════════════════════════════════════
# Reset obstacle pool between games
# ══════════════════════════════════════════════════════════════
def reset_obstacles():
    for obs in _obs_pool:
        obs[3] = False  # mark all inactive


# ══════════════════════════════════════════════════════════════
# Spawn one obstacle into the pool (if a slot is free)
# ══════════════════════════════════════════════════════════════
def spawn_obstacle():
    for obs in _obs_pool:
        if not obs[3]:  # find inactive slot
            obs[0] = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - OBSTACLE_W - 10)
            obs[1] = -OBSTACLE_H
            obs[2] = random.randint(0, len(OBS_COLOURS) - 1)
            obs[3] = True
            return


# ══════════════════════════════════════════════════════════════
# Main game loop
# ══════════════════════════════════════════════════════════════
def run_game():
    car_x = WIDTH // 2 - CAR_W // 2
    speed = 8.0
    score = 0
    stripe_offset = 0   # FIX: use int, wrap with modulo
    spawn_timer = 0
    spawn_interval = 60
    frame = 0

    reset_obstacles()

    # FIX: Run GC before starting to start with a clean heap
    gc.collect()

    while True:
        frame += 1

        # FIX: Periodic GC every 120 frames (~2 sec) to prevent
        # unpredictable mid-frame GC pauses
        if frame % 120 == 0:
            gc.collect()

        # ── Input: read ONCE per frame ────────────────────────
        btns = read_buttons()

        if left_pressed(btns):
            car_x -= 4
        if right_pressed(btns):
            car_x += 4
        if up_pressed(btns):
            speed = min(speed + SPEED_STEP, MAX_SPEED)
        if down_pressed(btns):
            speed = max(speed - SPEED_STEP, MIN_SPEED)

        # Clamp to road
        car_x = max(ROAD_LEFT + 8, min(car_x, ROAD_RIGHT - CAR_W - 8))

        # ── Scroll & score ────────────────────────────────────
        # FIX: wrap stripe_offset to prevent int/float overflow
        stripe_offset = (stripe_offset + int(speed)) % STRIPE_WRAP
        score += int(speed)

        # ── Spawn obstacles ───────────────────────────────────
        spawn_timer += 1
        dynamic_interval = max(15, spawn_interval - int(speed) * 3)
        if spawn_timer >= dynamic_interval:
            spawn_timer = 0
            spawn_obstacle()  # uses pre-allocated pool, no heap alloc

        # ── Move & deactivate obstacles ───────────────────────
        # FIX: mutate in-place, no new list created
        for obs in _obs_pool:
            if obs[3]:
                obs[1] += int(speed)
                if obs[1] >= HEIGHT:
                    obs[3] = False  # deactivate instead of deleting

        # ── Collision ─────────────────────────────────────────
        crashed = False
        for obs in _obs_pool:
            if obs[3]:
                if collides(car_x + 4, CAR_Y + 4, CAR_W - 8, CAR_H - 8,
                            obs[0] + 4, obs[1] + 4, OBSTACLE_W - 8, OBSTACLE_H - 8):
                    crashed = True
                    break

        if crashed:
            display.set_pen(RED)
            display.clear()
            display.update()
            time.sleep_ms(300)
            return score

        # ── Draw ──────────────────────────────────────────────
        draw_road(stripe_offset)

        for obs in _obs_pool:
            if obs[3]:
                draw_car(obs[0], obs[1], OBSTACLE_W, OBSTACLE_H,
                         OBS_COLOURS[obs[2]], DKGREY)

        draw_car(car_x, CAR_Y, CAR_W, CAR_H, BLUE, WHITE)
        draw_hud(score // 10, speed)
        display.update()

        time.sleep_ms(16)


# ══════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════
gc.collect()
title_screen()

while True:
    final_score = run_game()
    game_over_screen(final_score // 10)