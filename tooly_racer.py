# TOOLY Racer - Endless Racing Game for Pimoroni Tufty 2040
# Created by Owen Edwards / ACS "a creative solution" as an open source game for everyone to enjoy
# v.1.3.05072026 

import time
import random
import gc
from machine import Pin, I2C
from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from qwstpad import QwSTPad
from qwstpad import DEFAULT_ADDRESS as QWST_ADDR
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
WIDTH, HEIGHT = display.get_bounds()
_bl = Pin(2, Pin.OUT)
_bl.value(1)
# Tufty buttons(high by default) 
_btn_a    = Pin(7,  Pin.IN, Pin.PULL_DOWN)
_btn_b    = Pin(8,  Pin.IN, Pin.PULL_DOWN)
_btn_c    = Pin(9,  Pin.IN, Pin.PULL_DOWN)
_btn_up   = Pin(22, Pin.IN, Pin.PULL_DOWN)
_btn_down = Pin(6,  Pin.IN, Pin.PULL_DOWN)
# QwSTPad ~/qwstpad library
_i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100_000)
try:
    _pad = QwSTPad(_i2c, QWST_ADDR)
    _pad.set_led(1, False)
    _pad.set_led(2, False)
    _pad.set_led(3, False)
    _pad.set_led(4, False)
    _qwst_ok = True
    print("QwSTPad: Connected")
except OSError:
    _qwst_ok = False
    print("QwSTPad: Not found, using Tufty buttons only")

def read_buttons():
    if _qwst_ok:
        q = _pad.read_buttons()
        _pad.set_led(1, any(q.values()))
    else:
        q = {}

    return (
        bool(_btn_a.value()    or q.get('L', False)),  # left
        bool(_btn_b.value()    or q.get('R', False)),  # right
        bool(_btn_c.value()    or q.get('A', False)),  # action
        bool(_btn_up.value()   or q.get('U', False)),  # up
        bool(_btn_down.value() or q.get('D', False)),  # down
    )

def wait_for_any_button():
    while True:
        b = read_buttons()
        if b[0] or b[1] or b[2] or b[3] or b[4]:
            break
        time.sleep_ms(30)
    while True:
        b = read_buttons()
        if not (b[0] or b[1] or b[2] or b[3] or b[4]):
            break
        time.sleep_ms(30)
def left_pressed(b):   return b[0]
def right_pressed(b):  return b[1]
def action_pressed(b): return b[2]
def up_pressed(b):     return b[3]
def down_pressed(b):   return b[4]
# Colours
BLACK  = display.create_pen(0,   0,   0)
WHITE  = display.create_pen(255, 255, 255)
GREY   = display.create_pen(80,  80,  80)
DKGREY = display.create_pen(40,  40,  40)
YELLOW = display.create_pen(255, 220, 0)
RED    = display.create_pen(220, 30,  30)
BLUE   = display.create_pen(30,  80,  220)
GREEN  = display.create_pen(30,  180, 30)
ORANGE = display.create_pen(255, 140, 0)
CYAN   = display.create_pen(0,   220, 220)
# Road layout 
ROAD_LEFT  = 40
ROAD_RIGHT = 280
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
DASH_HEIGHT = 30
DASH_GAP    = 20
DASH_X      = WIDTH // 2 - 3
DASH_W      = 6
#Player car
CAR_W = 45
CAR_H = 62
CAR_Y = HEIGHT - CAR_H - 10
# Game constants
MIN_SPEED     = 12
MAX_SPEED     = 16
SPEED_STEP    = 0.5
OBSTACLE_W    = 45
OBSTACLE_H    = 62
MAX_OBSTACLES = 7
STRIPE_WRAP   = 1000

OBS_COLOURS = [RED, ORANGE, CYAN, GREEN, WHITE, YELLOW, BLACK]

_obs_pool = [[0, 0, 0, False] for _ in range(MAX_OBSTACLES)]

# Draw car
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
# Draw road
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
# HUD
def draw_hud(score, speed):
    display.set_pen(WHITE)
    display.text("SCORE: {}".format(score), 2, 4, scale=2)
    display.set_pen(YELLOW)
    display.text("SPD:{:.0f}".format(speed), 2, 22, scale=2)
# Collision (AABB)
def collides(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and ax + aw > bx and
            ay < by + bh and ay + ah > by)
# Title screen
def title_screen():
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(YELLOW)
    display.text("TOOLY RACER", 50, 50, scale=4)
    display.set_pen(WHITE)
    display.text("Avoid the dumbasses!", 65, 110, scale=2)
    display.set_pen(WHITE)
    display.text("A/L = Left   B/R = Right", 10, 140, scale=2)
    display.set_pen(GREEN)
    display.text("UP = Faster  DN = Slower", 10, 163, scale=2)
    display.set_pen(CYAN)
    display.text("Tufty buttons + QwSTPad", 10, 186, scale=2)
    display.set_pen(YELLOW)
    display.text("Press any button!", 75, 214, scale=2)
    display.update()
    wait_for_any_button()
# Game over screen
def game_over_screen(score):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(RED)
    display.text("DUMBASS", 80, 70, scale=4)
    display.set_pen(WHITE)
    display.text("Score: {}".format(score), 95, 130, scale=3)
    display.set_pen(YELLOW)
    display.text("Go again hotshot?", 65, 185, scale=2)
    display.set_pen(WHITE)
    display.text("Press any button!", 65, 210, scale=2)
    display.update()
    wait_for_any_button()
# Reset obstacle pool between games
def reset_obstacles():
    for obs in _obs_pool:
        obs[3] = False
# Spawn one obstacle into the pool (if a slot is free)
def spawn_obstacle():
    for obs in _obs_pool:
        if not obs[3]:
            obs[0] = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - OBSTACLE_W - 20)
            obs[1] = -OBSTACLE_H
            obs[2] = random.randint(0, len(OBS_COLOURS) - 1)
            obs[3] = True
            return
# Main game loop
def run_game():
    car_x = WIDTH // 2 - CAR_W // 2
    speed = 12.0
    score = 0
    stripe_offset = 0
    spawn_timer = 0
    frame = 0

    reset_obstacles()
    gc.collect()

    while True:
        frame += 1
        if frame % 120 == 0:
            gc.collect()

        b = read_buttons()

        if left_pressed(b):
            car_x -= 4
        if right_pressed(b):
            car_x += 4
        if up_pressed(b):
            speed = min(speed + SPEED_STEP, MAX_SPEED)
        if down_pressed(b):
            speed = max(speed - SPEED_STEP, MIN_SPEED)

        # Clamp to road
        car_x = max(ROAD_LEFT + 8, min(car_x, ROAD_RIGHT - CAR_W - 8))

        # Scroll and score
        stripe_offset = (stripe_offset + int(speed)) % STRIPE_WRAP
        score += int(speed)

        # Spawn obstacles
        spawn_timer += 1
        dynamic_interval = max(15, 60 - int(speed) * 3)
        if spawn_timer >= dynamic_interval:
            spawn_timer = 0
            spawn_obstacle()

        # Move and deactivate obstacles
        for obs in _obs_pool:
            if obs[3]:
                obs[1] += int(speed)
                if obs[1] >= HEIGHT:
                    obs[3] = False

        # Collision check
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

        # Draw
        draw_road(stripe_offset)

        for obs in _obs_pool:
            if obs[3]:
                draw_car(obs[0], obs[1], OBSTACLE_W, OBSTACLE_H,
                         OBS_COLOURS[obs[2]], DKGREY)

        draw_car(car_x, CAR_Y, CAR_W, CAR_H, BLUE, WHITE)
        draw_hud(score // 10, speed)
        display.update()

        time.sleep_ms(16)

# Entry point
gc.collect()
title_screen()

while True:
    final_score = run_game()
    game_over_screen(final_score // 10)
