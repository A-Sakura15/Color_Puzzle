# 加法混色パズル ver.1.4.1
# ルール
#  ・クリックすると、NEXTの色の光を「クリック位置を中心とする3x3マス」に照射できる（ブロックは加法混色される）
#  ・R+G+B で白になったブロックは消える
#  ・同じ色のブロックが3つ以上つながると、その方向にレーザーが放出される。
#    レーザーは盤面の端から端まで届き、軌道上のブロックを混色する。つながっていたブロックは消える
#  ・お邪魔ブロック（黒 = RGBすべて0）が降ってくる。
#    プレイヤーの照射では混色できず、レーザーでのみ混色できる（レーザーが当たるとその色になる）
#    黒は光を出さないので、黒どうしがつながってもレーザーは出ない

# 難易度が高かったため不採用
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
SPAWN_NUM = 3      # 1手ごとに上から降ってくるブロックの数（難易度調整用）
OJAMA_RATE = 30    # 降ってくるブロックのうち、お邪魔ブロック（黒）になる確率（%）
START_NUM = 5      # ゲーム開始時に降ってくるブロックの数
LASER_FRAMES = 6   # レーザー表示の長さ（1フレーム=0.1秒）

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
EMPTY = -1       # 空マス（ブロックなし）
BLACK = 0b000    # 黒ブロック（お邪魔）。空マスとは別物
RED = 0b100
GREEN = 0b010
BLUE = 0b001
YELLOW = RED | GREEN
MAGENTA = RED | BLUE
CYAN = GREEN | BLUE
WHITE = RED | GREEN | BLUE
PRIMARY = [RED, GREEN, BLUE]

COLOR = {
    0b000: "#2a2a2a",
    0b100: "#ff0000",
    0b010: "#00ff00",
    0b001: "#0000ff",
    0b110: "#ffff00",
    0b101: "#ff00ff",
    0b011: "#00ffff",
    0b111: "#ffffff"
}

# 盤面
masu = [[EMPTY for _ in range(COL)] for _ in range(ROW)]

# その他変数
index = 0
score = 0
high_score = 0
timer = 0
tsugi = 0
lasers = []  # 発射するレーザーの情報（cells, run, color, dy, dx）

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
    mouse_move(e)  # タップ操作でも位置が確実に更新されるようにする
    mouse_c = 1

canvas.addEventListener("mousemove", mouse_move)
canvas.addEventListener("mousedown", mouse_press)

# ---------- 描画関連 ----------
def draw_txt(txt, x, y, siz, col, tg):
    context.fillStyle = "black"
    context.font = f"bold {siz}px Noto Sans"
    context.fillText(txt, x + 1, y + 1)

    context.fillStyle = col
    context.fillText(txt, x, y)

def draw_bg():
    context.clearRect(0, 0, canvas.width, canvas.height)

    # 背景全体を黒で塗りつぶす
    context.fillStyle = "#000000"
    context.fillRect(0, 0, canvas.width, canvas.height)

    # UI領域との境界線
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
    if UI_mode == tate:
        draw_txt(f"SCORE {score}", TILE_SIZE * 0.5, (ROW + 0.5) * TILE_SIZE, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt(f"HISC {high_score}", TILE_SIZE * 0.5, (ROW + 1.5) * TILE_SIZE, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt("NEXT", TILE_SIZE * 4.5, (ROW + 0.5) * TILE_SIZE, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt("スマホ用UI", TILE_SIZE * 4.5, (ROW + 1.5) * TILE_SIZE, TILE_SIZE * 0.4, "#ffffff", "")
        if tsugi in COLOR:
            context.fillStyle = COLOR[tsugi]
            context.fillRect(TILE_SIZE * 6, (ROW + 0.2) * TILE_SIZE, TILE_SIZE * 0.5, TILE_SIZE * 0.5)
    else:
        draw_txt(f"SCORE {score}", (COL + 0.5) * TILE_SIZE, TILE_SIZE * 1.5, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt(f"HISC {high_score}", (COL + 0.5) * TILE_SIZE, TILE_SIZE * 2.5, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt("NEXT", (COL + 0.5) * TILE_SIZE, TILE_SIZE * 3.5, TILE_SIZE * 0.4, "#ffffff", "")
        draw_txt("PC用UI", (COL + 0.5) * TILE_SIZE, TILE_SIZE * 4.5, TILE_SIZE * 0.4, "#ffffff", "")
        if tsugi in COLOR:
            context.fillStyle = COLOR[tsugi]
            context.fillRect((COL + 2) * TILE_SIZE, TILE_SIZE * 3, TILE_SIZE * 0.5, TILE_SIZE * 0.5)

def draw_block():
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] != EMPTY and masu[y][x] in COLOR:
                context.fillStyle = COLOR[masu[y][x]]
                context.fillRect(x * TILE_SIZE + 1, y * TILE_SIZE + 1,
                                 TILE_SIZE - 2, TILE_SIZE - 2)
                if masu[y][x] == BLACK:
                    # 黒ブロックは背景と区別できるよう灰色の枠を付ける
                    context.strokeStyle = "#777777"
                    context.lineWidth = 2
                    context.strokeRect(x * TILE_SIZE + 3, y * TILE_SIZE + 3,
                                       TILE_SIZE - 6, TILE_SIZE - 6)

def draw_area_preview():
    # 照射範囲（3x3）の予告表示
    context.fillStyle = COLOR[tsugi]
    context.globalAlpha = 0.4
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = cursor_y + dy
            x = cursor_x + dx
            if 0 <= y < ROW and 0 <= x < COL and masu[y][x] != BLACK:
                context.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    context.globalAlpha = 1.0

def draw_laser():
    # レーザー本体：太い色の帯 + 中心の白い芯
    T = TILE_SIZE
    for cells, run, color, dy, dx in lasers:
        sy, sx = cells[0]
        ey, ex = cells[-1]
        x0 = (sx + 0.5 - dx * 0.5) * T
        y0 = (sy + 0.5 - dy * 0.5) * T
        x1 = (ex + 0.5 + dx * 0.5) * T
        y1 = (ey + 0.5 + dy * 0.5) * T

        context.lineCap = "butt"
        context.globalAlpha = 0.6
        context.strokeStyle = COLOR[color]
        context.lineWidth = T * 0.4
        context.beginPath()
        context.moveTo(x0, y0)
        context.lineTo(x1, y1)
        context.stroke()

        context.globalAlpha = 0.95
        context.strokeStyle = "#ffffff"
        context.lineWidth = T * 0.12
        context.beginPath()
        context.moveTo(x0, y0)
        context.lineTo(x1, y1)
        context.stroke()
        context.globalAlpha = 1.0

# ---------- 判定・処理関数 ----------
def find_lines():
    # 同じ色が3つ以上つながっている並び（縦・横・斜め）をすべて探す
    # 白と空マスは対象外。戻り値: [(つながったマスのリスト, dy, dx, 色), ...]
    lines = []
    for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        for y in range(ROW):
            for x in range(COL):
                n = masu[y][x]
                if n == EMPTY or n == BLACK or n == WHITE:  # 黒は光を出さない
                    continue
                # 並びの先頭マスだけを起点にする
                py = y - dy
                px = x - dx
                if 0 <= py < ROW and 0 <= px < COL and masu[py][px] == n:
                    continue
                run = [(y, x)]
                cy = y + dy
                cx = x + dx
                while 0 <= cy < ROW and 0 <= cx < COL and masu[cy][cx] == n:
                    run.append((cy, cx))
                    cy += dy
                    cx += dx
                if len(run) >= 3:
                    lines.append((run, dy, dx, n))
    return lines

def line_cells(y, x, dy, dx):
    # (y, x) を通る直線上の盤面内のマスを、端から端まで返す
    while 0 <= y - dy < ROW and 0 <= x - dx < COL:
        y -= dy
        x -= dx
    cells = []
    while 0 <= y < ROW and 0 <= x < COL:
        cells.append((y, x))
        y += dy
        x += dx
    return cells

def fire_lasers():
    # すべてのレーザーが同時に発射される
    add = [[0 for _ in range(COL)] for _ in range(ROW)]  # 0 = 光が当たらない
    for cells, run, color, dy, dx in lasers:
        for (y, x) in cells:
            if (y, x) not in run and masu[y][x] != EMPTY:
                add[y][x] |= color

    # つながっていたブロックは消える
    for cells, run, color, dy, dx in lasers:
        for (y, x) in run:
            masu[y][x] = EMPTY

    # 軌道上のブロックを混色
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] != EMPTY:
                masu[y][x] |= add[y][x]

def irradiate(cx, cy, color):
    # プレイヤーの照射：(cx, cy) を中心とする3x3マスのブロックを混色（黒ブロックは混色できない）
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = cy + dy
            x = cx + dx
            if 0 <= y < ROW and 0 <= x < COL:
                if masu[y][x] != EMPTY and masu[y][x] != BLACK:
                    masu[y][x] |= color

def sweep_block():
    num = 0
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] == WHITE:
                masu[y][x] = EMPTY
                num += 1
    return num

def drop_block():
    flg = False
    for y in range(ROW - 2, -1, -1):
        for x in range(COL):
            if masu[y][x] != EMPTY and masu[y + 1][x] == EMPTY:
                masu[y + 1][x] = masu[y][x]
                masu[y][x] = EMPTY
                flg = True
    return flg

def over_block():
    for x in range(COL):
        if masu[0][x] != EMPTY:
            return True
    return False

def set_block(num):
    # 上段の空いている列からnum列をランダムに選んでブロックを降らせる
    cols = [x for x in range(COL) if masu[0][x] == EMPTY]
    for _ in range(num):
        if len(cols) == 0:
            break
        x = random.choice(cols)
        cols.remove(x)
        if random.choice(range(100)) < OJAMA_RATE:
            masu[0][x] = BLACK  # お邪魔ブロック
        else:
            masu[0][x] = random.choice(PRIMARY)

# ---------- メインループ ----------
def game_main():
    global index, timer, tsugi, score, high_score, lasers
    global cursor_x, cursor_y, mouse_c

    draw_bg()
    draw_UI()
    draw_block()

    if index == 0 or index == 1:
        draw_txt("Color Puzzle", TILE_SIZE, TILE_SIZE * 3, TILE_SIZE, "#ffffff", "TITLE")
        draw_txt("Click to Start", TILE_SIZE, TILE_SIZE * 6, TILE_SIZE * 0.5, "#ffffff", "TITLE")
        index = 1

        if mouse_c == 1:
            mouse_c = 0
            for y in range(ROW):
                for x in range(COL):
                    masu[y][x] = EMPTY
            score = 0
            tsugi = random.choice(PRIMARY)
            set_block(START_NUM)
            index = 2

    elif index == 2:
        # ブロックの落下処理
        if not drop_block():
            index = 4

    elif index == 3:
        # 白になったブロックの消去とスコア加算
        sc = sweep_block()
        score += sc * 10
        if score > high_score:
            high_score = score
        index = 2  # 消えた分だけ落下させる

    elif index == 4:
        # 同じ色が3つ以上つながっているか判定
        lines = find_lines()
        if len(lines) > 0:
            lasers = []
            for run, dy, dx, n in lines:
                cells = line_cells(run[0][0], run[0][1], dy, dx)
                lasers.append((cells, run, n, dy, dx))
            timer = 0
            index = 7
        elif not over_block():
            tsugi = random.choice(PRIMARY)
            mouse_c = 0
            index = 5
        else:
            index = 6
            timer = 0

    elif index == 5:
        # 操作フェーズ：クリックした位置を中心に3x3へ照射
        if 0 <= cursor_x < COL and 0 <= cursor_y < ROW:
            if tsugi in COLOR:
                draw_area_preview()

            if mouse_c == 1:
                mouse_c = 0
                irradiate(cursor_x, cursor_y, tsugi)
                set_block(SPAWN_NUM)
                index = 3
        mouse_c = 0

    elif index == 6:
        # ゲームオーバー表示
        timer += 1
        mouse_c = 0
        draw_txt("GAME OVER", TILE_SIZE, TILE_SIZE * 5, TILE_SIZE, "red", "")
        if timer >= 50:
            index = 0

    elif index == 7:
        # レーザー表示 → 発射（混色）
        draw_laser()
        timer += 1
        if timer >= LASER_FRAMES:
            fire_lasers()
            lasers = []
            index = 3  # 白になったブロックの消去へ

    js.setTimeout(game_main, 100)

game_main()