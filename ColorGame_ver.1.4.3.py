# 加法混色パズル ver.1.4.3（適応レイアウト対応）
# ルール
#  ・クリックすると、NEXTの色の光を「クリック位置を中心とする3x3マス」に照射できる（ブロックは加法混色される）
#  ・R+G+B で白になったブロックは消える
#  ・同じ色のブロックが3つ以上つながると、その方向にレーザーが放出される。
#    レーザーは盤面の端から端まで届き、軌道上のブロックを混色する。つながっていたブロックは消える
#  ・お邪魔ブロック（黒 = RGBすべて0）が降ってくる。光を当てるとその色になり、白にするには3色すべてが必要
#    黒は光を出さないので、黒どうしがつながってもレーザーは出ない
#
# 適応レイアウト（ver.1.4.3）
#  ・canvasをウィンドウ全体に広げ、盤面の周囲の余白を背景とパネル（スコア・ルール説明など）で使う
#  ・ウィンドウサイズが変わるたびに、レイアウト候補（SIDE：盤面の左右にパネル / BOTTOM：盤面の下にパネル）を
#    それぞれ評価し、盤面のマスが最も大きくなるものを選ぶ
#  ・パネルは、空き領域に収まる情報だけを優先度順に表示する（スコア > ルール > 混色の凡例）。
#    パネルが横に広いときは2列にするなど、パネル内部の配置も空き領域に合わせて切り替える
#  ・最後に使われた入力方式（マウス/タッチ）に合わせて、操作説明の文言を切り替える
import js
import random

# ---------- 設定 ----------
COL = 8
ROW = 10
SPAWN_NUM = 8      # 1手ごとに上から降ってくるブロックの数（難易度調整用）
OJAMA_RATE = 30    # 降ってくるブロックのうち、お邪魔ブロック（黒）になる確率（%）
START_NUM = 5      # ゲーム開始時に降ってくるブロックの数
LASER_FRAMES = 6   # レーザー表示の長さ（1フレーム=0.1秒）
TOUCH_OFFSET_TILES = 1.5  # タッチ操作時、照射範囲を指より上にずらすマス数（指で隠れないように）。0でずらさない

# レイアウト関連
MARGIN = 10          # 画面端・パネル間の余白(px)
PANEL_MIN_W = 150    # SIDEレイアウトで、左右のパネルに最低限確保する幅(px)
PANEL_MIN_H = 150    # BOTTOMレイアウトで、下のパネルに最低限確保する高さ(px)
SHOW_LAYOUT_INFO = True  # Trueにすると、選ばれたレイアウトと画面サイズを小さく表示する（研究・デバッグ用）

# 配色
BG_COLOR = "#10131c"
PANEL_BG = "#1a2030"
PANEL_BORDER = "#3a4560"
TEXT_SUB = "#8a94a8"
TEXT_MAIN = "#e6ebf5"
FONT = "'Noto Sans JP', 'Noto Sans', sans-serif"

# ---------- Canvas準備 ----------
canvas = js.document.querySelector("#canvas")
context = canvas.getContext("2d")

# canvasをウィンドウ全体に広げる（ページ側の余白やスクロールが出ないようにする）
try:
    js.document.body.style.margin = "0"
    js.document.body.style.background = BG_COLOR
    js.document.body.style.overflow = "hidden"
    js.document.documentElement.style.overflow = "hidden"
    canvas.style.display = "block"
    canvas.style.position = "fixed"
    canvas.style.left = "0px"
    canvas.style.top = "0px"
except Exception:
    pass

# タッチ操作中に画面がスクロール・拡大されないようにする
canvas.style.touchAction = "none"
canvas.style.userSelect = "none"
canvas.style.webkitUserSelect = "none"

# レイアウト変数（relayout()で更新される）
W = 0
H = 0
TILE_SIZE = 0
BX = 0            # 盤面の左上x
BY = 0            # 盤面の左上y
BW = 0            # 盤面の幅
BH = 0            # 盤面の高さ
LAYOUT = ""       # 選ばれたレイアウトの名前
TOUCH_OFFSET = 0
PANELS = []       # [{"kind", "x", "y", "w", "h"}, ...]
wrap_cache = {}

# 入力方式（"mouse" / "touch"）。最後に使われたものを記録して説明文の切り替えに使う
input_type = "mouse"
try:
    if js.navigator.maxTouchPoints > 0:
        input_type = "touch"
except Exception:
    pass

# マウス変数
cursor_x = 0
cursor_y = 0
mouse_c = 0

# ---------- 色定数（ビットフラグ） ----------
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

# ---------- 適応レイアウト ----------
# レイアウト候補：それぞれ「盤面の1マスの大きさ(px)」を返す。大きいほど良い候補とみなす
def layout_side(w, h):
    # 盤面の左右にパネルを置く
    pw = PANEL_MIN_W + 2 * MARGIN
    return min((w - 2 * pw) / COL, (h - 2 * MARGIN) / ROW)

def layout_bottom(w, h):
    # 盤面の下にパネルを置く。下のパネルは、タッチ時のずらし量（約2マス分）を確保するため2マス以上の高さにする
    return min((w - 2 * MARGIN) / COL,
               (h - 2 * MARGIN) / (ROW + 2),
               (h - 2 * MARGIN - PANEL_MIN_H) / ROW)

LAYOUT_CANDIDATES = [("SIDE", layout_side), ("BOTTOM", layout_bottom)]

def relayout():
    # ウィンドウサイズに合わせて、レイアウトを選び直す
    global W, H, TILE_SIZE, BX, BY, BW, BH, LAYOUT, TOUCH_OFFSET, PANELS

    W = max(int(js.window.innerWidth), 200)
    H = max(int(js.window.innerHeight), 200)
    canvas.width = W
    canvas.height = H
    canvas.style.width = f"{W}px"
    canvas.style.height = f"{H}px"

    # 横長なら SIDE、縦長なら BOTTOM を先に評価（同点のときは先に評価した方が選ばれる）
    cands = LAYOUT_CANDIDATES if W >= H else LAYOUT_CANDIDATES[::-1]
    best_name = ""
    best_t = -1
    for name, fn in cands:
        t = fn(W, H)
        if t > best_t:
            best_name = name
            best_t = t

    LAYOUT = best_name
    TILE_SIZE = max(int(best_t), 8)
    BW = COL * TILE_SIZE
    BH = ROW * TILE_SIZE
    BX = (W - BW) // 2

    if LAYOUT == "SIDE":
        BY = (H - BH) // 2
        right_x = BX + BW + MARGIN
        PANELS = [
            {"kind": "status", "x": MARGIN, "y": MARGIN, "w": BX - 2 * MARGIN, "h": H - 2 * MARGIN},
            {"kind": "rules", "x": right_x, "y": MARGIN, "w": W - right_x - MARGIN, "h": H - 2 * MARGIN},
        ]
        TOUCH_OFFSET = 0  # 盤面の下に余白がないため、ずらさない
    else:
        BY = MARGIN
        top = BY + BH + MARGIN
        PANELS = [
            {"kind": "all", "x": MARGIN, "y": top, "w": W - 2 * MARGIN, "h": H - top - MARGIN},
        ]
        TOUCH_OFFSET = TILE_SIZE * TOUCH_OFFSET_TILES

    wrap_cache.clear()

def on_resize(e):
    relayout()

js.window.addEventListener("resize", on_resize)
relayout()

# ---------- 入力（Pointer Events：マウス・タッチ・ペンを同じ処理で扱う） ----------
#  ・マウス：カーソルに照射範囲が追従し、クリックで照射
#  ・タッチ：画面を押している間、照射範囲が指に追従し、指を離した位置で照射
#            盤面の外で離す、または操作が中断されたときは照射しない（キャンセル）
pressed = False      # 押している最中か
show_cursor = False  # 照射範囲を表示するか

def note_input(e):
    global input_type
    if e.pointerType == "touch":
        input_type = "touch"
    else:
        input_type = "mouse"

def update_cursor(e):
    global cursor_x, cursor_y
    rect = canvas.getBoundingClientRect()
    if rect.width == 0 or rect.height == 0:
        return
    # 表示サイズと描画サイズが違っていても位置がずれないよう補正
    mx = (e.clientX - rect.left) * canvas.width / rect.width
    my = (e.clientY - rect.top) * canvas.height / rect.height
    if e.pointerType == "touch":
        my -= TOUCH_OFFSET
    cursor_x = int((mx - BX) // TILE_SIZE)
    cursor_y = int((my - BY) // TILE_SIZE)

def pointer_down(e):
    global pressed, show_cursor
    if not e.isPrimary:
        return
    if e.pointerType == "mouse" and e.button != 0:
        return
    note_input(e)
    e.preventDefault()
    try:
        canvas.setPointerCapture(e.pointerId)  # 指が盤面の外に出ても追従させる
    except Exception:
        pass
    pressed = True
    show_cursor = True
    update_cursor(e)

def pointer_move(e):
    global show_cursor
    if not e.isPrimary:
        return
    if e.pointerType == "touch" and not pressed:
        return
    note_input(e)
    if pressed:
        e.preventDefault()
    show_cursor = True
    update_cursor(e)

def pointer_up(e):
    global pressed, show_cursor, mouse_c
    if not e.isPrimary or not pressed:
        return
    update_cursor(e)
    pressed = False
    if e.pointerType == "touch":
        show_cursor = False
    mouse_c = 1  # 離した位置で決定

def pointer_cancel(e):
    global pressed, show_cursor
    pressed = False
    show_cursor = False

def pointer_leave(e):
    global show_cursor
    if e.pointerType == "mouse" and not pressed:
        show_cursor = False

canvas.addEventListener("pointerdown", pointer_down)
canvas.addEventListener("pointermove", pointer_move)
canvas.addEventListener("pointerup", pointer_up)
canvas.addEventListener("pointercancel", pointer_cancel)
canvas.addEventListener("pointerleave", pointer_leave)

# ---------- 描画：共通部品 ----------
def draw_txt(txt, x, y, siz, col, tg):
    # 盤面上のテキスト（影付き。yはベースライン）
    context.font = f"bold {siz}px {FONT}"
    context.fillStyle = "black"
    context.fillText(txt, x + 1, y + 1)

    context.fillStyle = col
    context.fillText(txt, x, y)

def put(txt, x, y, siz, col, bold=True):
    # パネル内のテキスト（yは文字の上端）
    context.font = f"{'bold ' if bold else ''}{siz}px {FONT}"
    context.fillStyle = col
    context.fillText(txt, x, y + siz * 0.85)

def wrap_text(txt, max_w, siz):
    # 指定した幅に収まるよう、文字単位で折り返す（日本語向け）
    key = (txt, int(max_w), int(siz))
    if key in wrap_cache:
        return wrap_cache[key]
    context.font = f"{siz}px {FONT}"
    lines = []
    cur = ""
    for ch in txt:
        if cur != "" and context.measureText(cur + ch).width > max_w:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur != "":
        lines.append(cur)
    wrap_cache[key] = lines
    return lines

def draw_swatch(x, y, s, c):
    context.fillStyle = COLOR[c]
    context.fillRect(x, y, s, s)
    context.strokeStyle = "#555555"
    context.lineWidth = 1
    context.strokeRect(x + 0.5, y + 0.5, s - 1, s - 1)

def ui_font():
    # パネルの基準フォントサイズ。画面の短辺に比例させる（大画面でも文字が大きくなりすぎないよう上限あり）
    return max(12, min(20, int(min(W, H) * 0.03)))

# ---------- 描画：背景とパネル ----------
def draw_bg():
    context.fillStyle = BG_COLOR
    context.fillRect(0, 0, W, H)

    for p in PANELS:
        draw_panel(p)

    # 盤面
    context.fillStyle = "#000000"
    context.fillRect(BX, BY, BW, BH)
    context.strokeStyle = "#ffffff"
    context.lineWidth = 2
    context.strokeRect(BX - 1, BY - 1, BW + 2, BH + 2)

def rule_texts():
    # 最後に使われた入力方式に合わせて、操作の説明を切り替える
    if input_type == "touch":
        first = "画面を押したまま動かし、離した位置の3x3マスに光を照射"
    else:
        first = "クリックした位置を中心に、3x3マスへ光を照射"
    return [
        first,
        "同じ色が3つ並ぶとレーザー発射。軌道上のブロックが混色",
        "R+G+B（白）になったブロックは消える",
        "黒ブロックは光で色が付く（白には3色必要）",
    ]

def draw_status_v(p, y, pad):
    # 縦に並べるスコア表示（SIDEレイアウト用）
    F = ui_font()
    x = p["x"] + pad
    put("SCORE", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    put(str(score), x, y, F * 1.3, "#ffffff")
    y += F * 1.7
    put("HI-SCORE", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    put(str(high_score), x, y, F * 1.3, "#ffffff")
    y += F * 1.7
    put("NEXT", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    if tsugi in COLOR:
        draw_swatch(x, y, F * 1.3, tsugi)
    y += F * 1.7
    return y

def draw_status_c(p, y, pad):
    # 3行に詰めたスコア表示（高さが足りないとき用）
    F = ui_font()
    x = p["x"] + pad
    put(f"SCORE  {score}", x, y, F, "#ffffff")
    put(f"HI-SCORE  {high_score}", x, y + F * 1.4, F, "#ffffff")
    put("NEXT", x, y + F * 2.8, F, TEXT_SUB)
    if tsugi in COLOR:
        draw_swatch(x + F * 3.6, y + F * 2.7, F * 1.1, tsugi)
    return y + F * 4.4

def draw_status(p, y, bottom, pad):
    # 空き高さに合わせて、スコア表示の形式を切り替える
    if y + ui_font() * 7.8 <= bottom:
        return draw_status_v(p, y, pad)
    return draw_status_c(p, y, pad)

def draw_status_h(p, y, pad):
    # 横に並べるスコア表示（BOTTOMレイアウト用）
    F = ui_font()
    x = p["x"] + pad
    put(f"SCORE  {score}", x, y, F * 1.1, "#ffffff")
    put(f"HI-SCORE  {high_score}", x, y + F * 1.5, F * 1.1, "#ffffff")
    x2 = p["x"] + p["w"] * 0.62
    put("NEXT", x2, y, F * 1.1, TEXT_SUB)
    if tsugi in COLOR:
        draw_swatch(x2, y + F * 1.5, F * 1.2, tsugi)
    return y + F * 3.4

def draw_rules(p, y, bottom, pad):
    # ルール説明。空き領域に収まる項目だけを、上から順に表示する
    F = ui_font()
    fr = max(11, int(F * 0.9))
    lh = fr * 1.5
    x = p["x"] + pad
    indent = fr * 1.0
    max_w = p["w"] - 2 * pad - indent
    if max_w < fr * 4:
        return y
    heading_h = F * 1.3
    items = [wrap_text(t, max_w, fr) for t in rule_texts()]
    if y + heading_h + len(items[0]) * lh > bottom:
        return y
    put("ルール", x, y, F * 0.8, TEXT_SUB)
    y += heading_h
    for lines in items:
        h = len(lines) * lh + fr * 0.4
        if y + h > bottom:
            break
        put("・", x, y, fr, TEXT_MAIN, False)
        for ln in lines:
            put(ln, x + indent, y, fr, TEXT_MAIN, False)
            y += lh
        y += fr * 0.4
    return y

def draw_mix_row(x, y, s, parts, res, tail, right):
    cx = x
    for i, c in enumerate(parts):
        if i > 0:
            put("+", cx, y, s, TEXT_SUB)
            cx += s * 0.85
        draw_swatch(cx, y, s, c)
        cx += s * 1.25
    put("=", cx, y, s, TEXT_SUB)
    cx += s * 0.85
    draw_swatch(cx, y, s, res)
    cx += s * 1.25
    if tail != "":
        context.font = f"{int(s * 0.9)}px {FONT}"
        if cx + context.measureText(tail).width <= right:
            put(tail, cx, y, s * 0.9, TEXT_MAIN, False)

def draw_legend(p, y, bottom, pad):
    # 混色の凡例。縦横ともに収まるときだけ表示する
    F = ui_font()
    s = max(12, int(F))
    row_h = s * 1.6
    need = F * 1.3 + 4 * row_h
    if y + need > bottom or 7.6 * s > p["w"] - 2 * pad:
        return y
    x = p["x"] + pad
    put("混色", x, y, F * 0.8, TEXT_SUB)
    y += F * 1.3
    rows = [
        ([RED, GREEN], YELLOW, ""),
        ([GREEN, BLUE], CYAN, ""),
        ([BLUE, RED], MAGENTA, ""),
        ([RED, GREEN, BLUE], WHITE, "消える"),
    ]
    for parts, res, tail in rows:
        draw_mix_row(x, y, s, parts, res, tail, p["x"] + p["w"] - pad)
        y += row_h
    return y

def draw_panel(p):
    x = p["x"]
    y = p["y"]
    w = p["w"]
    h = p["h"]
    context.fillStyle = PANEL_BG
    context.fillRect(x, y, w, h)
    context.strokeStyle = PANEL_BORDER
    context.lineWidth = 1
    context.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1)
    if w < 60 or h < 40:
        return

    # パネルの外にはみ出さないよう、描画範囲を制限する
    context.save()
    context.beginPath()
    context.rect(x, y, w, h)
    context.clip()

    pad = max(8, int(ui_font() * 0.8))
    cy = y + pad
    bottom = y + h - pad
    kind = p["kind"]
    if kind == "status":
        cy = draw_status(p, cy, bottom, pad)
        draw_legend(p, cy, bottom, pad)
    elif kind == "rules":
        draw_rules(p, cy, bottom, pad)
    elif w >= 520:
        # パネルが横に広いときは2列にする（左：スコア、右：ルールと凡例）
        left_w = int(w * 0.36)
        pl = {"x": x, "y": y, "w": left_w, "h": h}
        pr = {"x": x + left_w, "y": y, "w": w - left_w, "h": h}
        draw_status(pl, cy, bottom, pad)
        cy2 = draw_rules(pr, cy, bottom, pad)
        draw_legend(pr, cy2, bottom, pad)
    else:
        cy = draw_status_h(p, cy, pad)
        cy = draw_rules(p, cy, bottom, pad)
        draw_legend(p, cy, bottom, pad)

    if SHOW_LAYOUT_INFO:
        put(f"{LAYOUT} {W}x{H} tile={TILE_SIZE}", x + pad, y + h - pad - 11, 11, "#5c6680", False)

    context.restore()

# ---------- 描画：盤面 ----------
def draw_block():
    T = TILE_SIZE
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] != EMPTY and masu[y][x] in COLOR:
                context.fillStyle = COLOR[masu[y][x]]
                context.fillRect(BX + x * T + 1, BY + y * T + 1, T - 2, T - 2)
                if masu[y][x] == BLACK:
                    # 黒ブロックは背景と区別できるよう灰色の枠を付ける
                    context.strokeStyle = "#777777"
                    context.lineWidth = 2
                    context.strokeRect(BX + x * T + 3, BY + y * T + 3, T - 6, T - 6)

def draw_area_preview():
    # 照射範囲（3x3）の予告表示
    T = TILE_SIZE
    context.fillStyle = COLOR[tsugi]
    context.globalAlpha = 0.4
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = cursor_y + dy
            x = cursor_x + dx
            if 0 <= y < ROW and 0 <= x < COL:
                context.fillRect(BX + x * T, BY + y * T, T, T)
    context.globalAlpha = 1.0

def draw_laser():
    # レーザー本体：太い色の帯 + 中心の白い芯
    T = TILE_SIZE
    for cells, run, color, dy, dx in lasers:
        sy, sx = cells[0]
        ey, ex = cells[-1]
        x0 = BX + (sx + 0.5 - dx * 0.5) * T
        y0 = BY + (sy + 0.5 - dy * 0.5) * T
        x1 = BX + (ex + 0.5 + dx * 0.5) * T
        y1 = BY + (ey + 0.5 + dy * 0.5) * T

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
    # プレイヤーの照射：(cx, cy) を中心とする3x3マスのブロックを混色
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = cy + dy
            x = cx + dx
            if 0 <= y < ROW and 0 <= x < COL:
                if masu[y][x] != EMPTY:
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

    T = TILE_SIZE
    draw_bg()
    draw_block()

    if index == 0 or index == 1:
        start_txt = "Tap to Start" if input_type == "touch" else "Click to Start"
        draw_txt("Color Puzzle", BX + T * 0.4, BY + T * 3, T * 0.95, "#ffffff", "TITLE")
        draw_txt(start_txt, BX + T * 0.4, BY + T * 6, T * 0.5, "#ffffff", "TITLE")
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
            if tsugi in COLOR and show_cursor:
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
        draw_txt("GAME OVER", BX + T * 0.4, BY + T * 5, T * 0.95, "red", "")
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