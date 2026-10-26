# 加法混色パズル
# A: 同色3つ揃い → 消えずに「光源」になり、次の手番で上下左右へ照射して自分は消える
# C: 照射で白になる（足りない色が当たる）と消去。同じ色を当てても変化なし
# D: 連続した手番で消去が続くとコンボ倍率が上がる
import js
import random

win_w = js.window.innerWidth
win_h = js.window.innerHeight
yoko = 0
tate = 1
if win_w > win_h:
    UI_mode = yoko
else:
    UI_mode = tate

# Canvas取得
canvas = js.document.querySelector("#canvas")
context = canvas.getContext("2d")

COL = 8
ROW = 10
SPAWN_NUM = 1  # 1手番ごとに上から降ってくるランダムブロックの数（難易度調整用）

if UI_mode == tate:
    TILE_SIZE = min((win_w - 30) // COL, (win_h - 30) // (ROW + 2))
    UI_height = int(TILE_SIZE * 2)
else:
    TILE_SIZE = min((win_w - 30) // (COL + 3), (win_h - 30) // ROW)
    UI_width = int(TILE_SIZE * 3)

# Canvasサイズ変更
if UI_mode == tate:
    canvas.width = TILE_SIZE * COL
    canvas.height = TILE_SIZE * ROW + UI_height
else:
    canvas.width = TILE_SIZE * COL + UI_width
    canvas.height = TILE_SIZE * ROW

# UI領域の始点
UI_x = COL * TILE_SIZE
UI_y = ROW * TILE_SIZE

# マウス変数
cursor_x = 0
cursor_y = 0
mouse_c = 0

# 色定数（ビットフラグ）
BLACK = 0b000
RED = 0b100
GREEN = 0b010
BLUE = 0b001
YELLOW = RED | GREEN
MAGENTA = RED | BLUE
CYAN = GREEN | BLUE
WHITE = RED | GREEN | BLUE
PRIMARY = [RED, GREEN, BLUE]

COLOR = {
    0b100: "#ff0000",
    0b010: "#00ff00",
    0b001: "#0000ff",
    0b110: "#ffff00",
    0b101: "#ff00ff",
    0b011: "#00ffff",
    0b111: "#ffffff"
}

# 盤面（masu: 色 / lit: 光源かどうか）
masu = [[BLACK for _ in range(COL)] for _ in range(ROW)]
lit = [[False for _ in range(COL)] for _ in range(ROW)]

# その他変数
index = 0
phase = 0          # 0: 照射前の落下  1: 照射後の落下
score = 0
high_score = 0
timer = 0
tsugi = 0
combo = 0
turn_cleared = False  # この手番で消去が起きたか

# 入力
def mouse_move(e):
    global cursor_x, cursor_y
    rect = canvas.getBoundingClientRect()
    mx = int(e.clientX - rect.left)
    my = int(e.clientY - rect.top)
    cursor_x = mx // TILE_SIZE
    cursor_y = my // TILE_SIZE

def mouse_press(e):
    global mouse_c
    mouse_c = 1

canvas.addEventListener("mousemove", mouse_move)
canvas.addEventListener("mousedown", mouse_press)

# ---------- 描画 ----------
def draw_txt(txt, x, y, siz, col, tg):
    context.fillStyle = "black"
    context.font = f"bold {siz}px Noto Sans"
    context.fillText(txt, x + 1, y + 1)

    context.fillStyle = col
    context.fillText(txt, x, y)

def draw_bg():
    context.clearRect(0, 0, canvas.width, canvas.height)
    context.fillStyle = "#000000"
    context.fillRect(0, 0, canvas.width, canvas.height)

    context.beginPath()
    context.strokeStyle = "#ffffff"
    context.lineWidth = 2
    if UI_mode == tate:
        context.moveTo(0, UI_y)
        context.lineTo(canvas.width, UI_y)
    else:
        context.moveTo(UI_x, 0)
        context.lineTo(UI_x, canvas.height)
    context.stroke()

def draw_UI():
    T = TILE_SIZE
    if UI_mode == tate:
        draw_txt(f"SCORE {score}", T * 0.5, (ROW + 0.5) * T, T * 0.4, "#ffffff", "")
        draw_txt(f"HISC {high_score}", T * 0.5, (ROW + 1.5) * T, T * 0.4, "#ffffff", "")
        draw_txt("NEXT", T * 4.5, (ROW + 0.5) * T, T * 0.4, "#ffffff", "")
        draw_txt(f"COMBO x{max(combo, 1)}", T * 4.5, (ROW + 1.5) * T, T * 0.4, "#ffffff", "")
        if tsugi in COLOR:
            context.fillStyle = COLOR[tsugi]
            context.fillRect(T * 6, (ROW + 0.2) * T, T * 0.5, T * 0.5)
    else:
        draw_txt(f"SCORE {score}", (COL + 0.5) * T, T * 1.5, T * 0.4, "#ffffff", "")
        draw_txt(f"HISC {high_score}", (COL + 0.5) * T, T * 2.5, T * 0.4, "#ffffff", "")
        draw_txt(f"COMBO x{max(combo, 1)}", (COL + 0.5) * T, T * 3.5, T * 0.4, "#ffffff", "")
        draw_txt("NEXT", (COL + 0.5) * T, T * 4.5, T * 0.4, "#ffffff", "")
        if tsugi in COLOR:
            context.fillStyle = COLOR[tsugi]
            context.fillRect((COL + 2) * T, T * 4.1, T * 0.5, T * 0.5)
        draw_txt("3つ揃え→光源に", (COL + 0.5) * T, T * 6.0, T * 0.28, "#cccccc", "")
        draw_txt("次の手で隣4マスへ照射", (COL + 0.5) * T, T * 6.6, T * 0.28, "#cccccc", "")
        draw_txt("足りない色で白→消去", (COL + 0.5) * T, T * 7.2, T * 0.28, "#cccccc", "")

def draw_block():
    T = TILE_SIZE
    for y in range(ROW):
        for x in range(COL):
            n = masu[y][x]
            if n == BLACK or n not in COLOR:
                continue
            context.fillStyle = COLOR[n]
            context.fillRect(x * T + 1, y * T + 1, T - 2, T - 2)

            if lit[y][x]:
                # 光源：白い枠と中心の白い点
                context.strokeStyle = "#ffffff"
                context.lineWidth = 3
                context.strokeRect(x * T + 3, y * T + 3, T - 6, T - 6)
                context.fillStyle = "#ffffff"
                context.fillRect(x * T + T * 0.35, y * T + T * 0.35, T * 0.3, T * 0.3)
            elif n in (YELLOW, MAGENTA, CYAN):
                # CMY：白にするために足りない色を右下に表示
                need = WHITE ^ n
                context.fillStyle = COLOR[need]
                context.fillRect(x * T + T * 0.62, y * T + T * 0.62, T * 0.28, T * 0.28)
                context.strokeStyle = "#000000"
                context.lineWidth = 1
                context.strokeRect(x * T + T * 0.62, y * T + T * 0.62, T * 0.28, T * 0.28)

def draw_light_preview():
    # 次に光源が照射したときの結果を予告表示
    T = TILE_SIZE
    add = compute_light()
    for y in range(ROW):
        for x in range(COL):
            if add[y][x] == BLACK:
                continue
            result = masu[y][x] | add[y][x]
            if result == masu[y][x]:
                continue
            if result == WHITE:
                # 消える予告
                context.globalAlpha = 0.6
                context.fillStyle = "#ffffff"
                context.fillRect(x * T + 1, y * T + 1, T - 2, T - 2)
                context.globalAlpha = 1.0
            else:
                context.fillStyle = COLOR[result]
                context.fillRect(x * T + T * 0.35, y * T + T * 0.35, T * 0.3, T * 0.3)
                context.strokeStyle = "#000000"
                context.lineWidth = 1
                context.strokeRect(x * T + T * 0.35, y * T + T * 0.35, T * 0.3, T * 0.3)

# ---------- 判定・処理 ----------
NEIGHBORS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def compute_light():
    # 現在の光源すべてが照射したときに各マスへ加わる光（ビット）を計算
    add = [[BLACK for _ in range(COL)] for _ in range(ROW)]
    for y in range(ROW):
        for x in range(COL):
            if lit[y][x]:
                color = masu[y][x]
                for dy, dx in NEIGHBORS:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < ROW and 0 <= nx < COL:
                        # 空マスと他の光源には当たらない
                        if masu[ny][nx] != BLACK and not lit[ny][nx]:
                            add[ny][nx] |= color
    return add

def fire_sources():
    # 光源が一斉に照射し、自身は消える。白になったブロックを消去して数を返す
    add = compute_light()

    for y in range(ROW):
        for x in range(COL):
            if lit[y][x]:
                lit[y][x] = False
                masu[y][x] = BLACK

    cleared = 0
    for y in range(ROW):
        for x in range(COL):
            if add[y][x] != BLACK:
                masu[y][x] |= add[y][x]
                if masu[y][x] == WHITE:
                    masu[y][x] = BLACK
                    cleared += 1
    return cleared

def check_block():
    # RGBの同色3つ揃い（縦・横・斜め）を光源にする。光源になった数を返す
    mark = [[False for _ in range(COL)] for _ in range(ROW)]

    def ok(y, x, n):
        return masu[y][x] == n and not lit[y][x]

    for y in range(ROW):
        for x in range(COL):
            n = masu[y][x]
            if n not in PRIMARY or lit[y][x]:
                continue
            # 縦
            if y >= 1 and y < ROW - 1 and ok(y - 1, x, n) and ok(y + 1, x, n):
                mark[y - 1][x] = mark[y][x] = mark[y + 1][x] = True
            # 横
            if x >= 1 and x < COL - 1 and ok(y, x - 1, n) and ok(y, x + 1, n):
                mark[y][x - 1] = mark[y][x] = mark[y][x + 1] = True
            # 斜め
            if 1 <= y < ROW - 1 and 1 <= x < COL - 1:
                if ok(y - 1, x - 1, n) and ok(y + 1, x + 1, n):
                    mark[y - 1][x - 1] = mark[y][x] = mark[y + 1][x + 1] = True
                if ok(y + 1, x - 1, n) and ok(y - 1, x + 1, n):
                    mark[y + 1][x - 1] = mark[y][x] = mark[y - 1][x + 1] = True

    count = 0
    for y in range(ROW):
        for x in range(COL):
            if mark[y][x]:
                lit[y][x] = True
                count += 1
    return count

def drop_block():
    flg = False
    for y in range(ROW - 2, -1, -1):
        for x in range(COL):
            if masu[y][x] != BLACK and masu[y + 1][x] == BLACK:
                masu[y + 1][x] = masu[y][x]
                lit[y + 1][x] = lit[y][x]
                masu[y][x] = BLACK
                lit[y][x] = False
                flg = True
    return flg

def over_block():
    for x in range(COL):
        if masu[0][x] != BLACK:
            return True
    return False

def spawn_blocks(num):
    cols = [x for x in range(COL) if masu[0][x] == BLACK]
    # random.shuffle が使えない環境でも動くよう、choiceだけで列を選ぶ
    for _ in range(num):
        if len(cols) == 0:
            break
        x = random.choice(cols)
        cols.remove(x)
        masu[0][x] = random.choice(PRIMARY)
        lit[0][x] = False

def landing_y(x):
    # 列xでブロックが着地するマス（満杯なら -1）
    for y in range(ROW - 1, -1, -1):
        if masu[y][x] == BLACK:
            return y
    return -1

def reset_board():
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = BLACK
            lit[y][x] = False

# ---------- メインループ ----------
def game_main():
    global index, phase, timer, tsugi, score, high_score
    global combo, turn_cleared, mouse_c

    draw_bg()
    draw_UI()
    draw_block()
    if index in (2, 3, 4, 5):
        draw_light_preview()

    if index == 0 or index == 1:
        draw_txt("Color Puzzle", TILE_SIZE, TILE_SIZE * 3, TILE_SIZE, "#ffffff", "TITLE")
        draw_txt("Click to Start", TILE_SIZE, TILE_SIZE * 6, TILE_SIZE * 0.5, "#ffffff", "TITLE")
        index = 1

        if mouse_c == 1:
            mouse_c = 0
            reset_board()
            score = 0
            combo = 0
            tsugi = random.choice(PRIMARY)
            spawn_blocks(3)
            phase = 0
            index = 2

    elif index == 2:
        # ブロックの落下
        if not drop_block():
            if phase == 0:
                index = 3
            else:
                index = 4

    elif index == 3:
        # 前の手番で作られた光源が一斉に照射
        cleared = fire_sources()
        if cleared > 0:
            turn_cleared = True
            combo += 1
            score += cleared * 10 * combo
            if score > high_score:
                high_score = score
        phase = 1
        index = 2  # 消去後の落下へ

    elif index == 4:
        # 新しい3つ揃いを光源に変える（照射は次の手番）
        check_block()

        if not turn_cleared:
            combo = 0  # 消去のない手番でコンボ終了

        if over_block():
            index = 6
            timer = 0
        else:
            tsugi = random.choice(PRIMARY)
            mouse_c = 0
            index = 5

    elif index == 5:
        # 操作フェーズ：クリックした列の一番下にNEXTブロックを置く
        if 0 <= cursor_x < COL and 0 <= cursor_y < ROW:
            ly = landing_y(cursor_x)
            if ly >= 0 and tsugi in COLOR:
                context.fillStyle = COLOR[tsugi]
                context.globalAlpha = 0.6
                context.fillRect(cursor_x * TILE_SIZE, ly * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                context.globalAlpha = 1.0

                if mouse_c == 1:
                    mouse_c = 0
                    masu[ly][cursor_x] = tsugi
                    lit[ly][cursor_x] = False
                    spawn_blocks(SPAWN_NUM)
                    turn_cleared = False
                    phase = 0
                    index = 2
        mouse_c = 0

    elif index == 6:
        timer += 1
        draw_txt("GAME OVER", TILE_SIZE, TILE_SIZE * 5, TILE_SIZE, "red", "")
        if timer >= 50:
            index = 0

    js.setTimeout(game_main, 100)

game_main()