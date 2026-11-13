# 加法混色パズル ver.1.7.1（ランキングの二重登録を防止：送信IDを付けて再送しても1件だけ登録）
# ルール
#  ・クリックすると、NEXTの色の光を「クリック位置を中心とする3x3マス」に照射できる（ブロックは加法混色される）
#  ・R+G+B で白になったブロックは消える
#  ・同じ色のブロックが3つ以上つながると、その方向にレーザーが放出される。
#    レーザーは盤面の端から端まで届き、軌道上のブロックを混色する。つながっていたブロックは消える
#  ・お邪魔ブロック（黒 = RGBすべて0）が降ってくる。光を当てるとその色になり、白にするには3色すべてが必要
#    黒は光を出さないので、黒どうしがつながってもレーザーは出ない
#
# スコア（ver.1.4.5）
#  ・同じ色が3つ以上そろってレーザーが発射されたとき、つながっていたブロック1個につき加点する
#  ・白になって消えたブロック1個につき加点する
#  ・加点はコンボ数に応じた倍率がかかる（1コンボ=×1.0、2コンボ=×1.5、3コンボ=×2.0 ...）
#    プレイヤーの照射だけで白になって消えた場合は、コンボ0なので×1.0
#
# ランキング（ver.1.6.0）
#  ・ゲームオーバー後、スコアが上位10位に入るときだけ名前（8文字まで）を入力する。入力後にスコアボードを表示する
#  ・入らなかったときも、スコアボードを見せてからタイトルに戻る。タイトル画面の「RANKING」ボタンからも見られる
#  ・名前の入力欄は8文字までに制限する（日本語の変換中も超えないよう、入力のたびに切り詰める）
#  ・キーボードは、タッチ操作のときは自動で開かず、入力欄をタップしたときに開く（マウス操作のときは自動で入力欄を選ぶ）
#  ・加法混色と減法混色は同じランキングにまとめる。同じ名前・同じスコアの記録も、すべて別の記録として載せる
#  ・同点のときは、先に記録した方が上位になる
#  ・ver.1.7.0：ランキングはNetlifyのサーバー（/api/ranking）に保存され、全員で共有される
#    - 取得：起動時・ゲーム開始時・ゲームオーバー時・RANKINGボタンを押したときに最新を読み込む
#    - 登録：名前の確定時に送信する。1回の登録ごとに送信IDを付け、再送しても二重に登録されない（ver.1.7.1）。失敗したら「タップで再送信」、3回失敗したら、この端末内にだけ保存する
#    - 最後に読み込んだランキングはlocalStorageにも残し、通信できないときの表示に使う（「オフライン」と表示）
#    - RANK_API = "" にすると、サーバーを使わず、ver.1.6と同じく端末内だけのランキングになる
#
# 文字の縁取り（ver.1.5.3）
#  ・盤面に重なるタイトル・GAME OVERの文字は、背景色の縁取りで囲み、ブロックの上でも読めるようにする（TEXT_OUTLINEで太さを調整）
#
# 効果音（ver.1.5.1）
#  ・レーザー（ビーム）が発射されるたびに、beam_se.wav を鳴らす（Web Audio API）
#  ・コンボが続くほどピッチを上げる（1発ごとに半音ずつ上昇、5発目以降は据え置き。SE_STEPSで変更可）。次の照射でコンボが0に戻ると、ピッチも元に戻る
#  ・ブラウザの制限により、最初に画面を押した（離した）時点で音声を初期化する。音声ファイルが読めなくてもゲームは続行する
#  ・MicroPython（<script type="mpy">）でも動くよう、asyncioは使わず、JavaScriptのPromiseを直接つなぐ。失敗はコンソールに出す
#  ・beam_se.wav はHTMLと同じ場所に置く（PyScriptの設定の [files] にも追加が必要な場合がある）
#
# 色モード（ver.1.5.0）
#  ・ダークモード＝加法混色（黒背景・RGBの光・OR演算）／ライトモード＝減法混色（白背景・CMYのインク・AND演算）
#  ・色は「反射する光のRGB」の3ビットで表す（C=0b011, M=0b101, Y=0b110, 紙の白=0b111）。
#    インクを重ねるとANDになり、C&M=青、M&Y=赤、Y&C=緑、C&M&Y=黒（消える）。お邪魔ブロックは白（紙）
#  ・パネルの切替ボタンでモードを変更する。切替時はタイトル画面に戻り、盤面とスコアはリセット（ハイスコアはモード別）
#  ・選んだモードはlocalStorageに保存され、次回起動時に復元される
#
# 高解像度対応（ver.1.4.8）
#  ・スマホなど画面の物理ピクセルがCSSピクセルより細かい端末（devicePixelRatio > 1）で文字がぼやけないよう、
#    canvasの内部解像度を devicePixelRatio 倍にし、描画は従来どおりCSSピクセルの座標で行う
#
# コンボ（ver.1.4.4）
#  ・プレイヤーが1回照射してから盤面が落ち着くまでの間に、レーザーが連続して発射された回数をコンボとして数える
#  ・パネルにコンボ数を表示し、2コンボ以上になると盤面中央に「N COMBO!」を一瞬表示する
#  ・強調はモノトーンで行う：パネルは灰色→白＋白枠（コンボが増えるほど枠が太くなる）、
#    盤面のポップアップは半透明の黒い箱に白文字＋白枠（コンボが増えるほど文字が大きくなる）
#  ・コンボ数は、次にプレイヤーが照射するまで残り、照射した時点で0に戻る
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

try:
    from pyscript.ffi import create_proxy  # JSからPythonの関数を呼ぶための包み（Pyodide/MicroPython共通）
except Exception:
    def create_proxy(f):
        return f

# ---------- 設定 ----------
COL = 8
ROW = 10
SPAWN_NUM = 8      # 1手ごとに上から降ってくるブロックの数（難易度調整用。最大はCOLの8）
OJAMA_RATE = 30    # 降ってくるブロックのうち、お邪魔ブロック（黒）になる確率（%）
START_NUM = 5      # ゲーム開始時に降ってくるブロックの数
LASER_FRAMES = 6   # レーザー表示の長さ（1フレーム=0.1秒）
COMBO_POPUP_FRAMES = 8  # 「N COMBO!」の表示時間（フレーム数）
COMBO_POPUP_ALPHA = 0.65   # 「N COMBO!」の背景の黒の濃さ（0〜1）。小さいほど盤面が透けて見える
SCORE_PER_LINE_BLOCK = 10  # 同色がそろって消えたブロック1個あたりの得点
SCORE_PER_WHITE = 10       # 白になって消えたブロック1個あたりの得点
COMBO_BONUS_STEP = 0.5     # コンボが1増えるごとに加わる倍率（1コンボ=×1.0、2コンボ=×1.5 ...）
TEXT_OUTLINE = 0.05        # 盤面上の文字の縁取りの太さ（文字サイズに対する比。0で縁取りなし）
SE_ENABLED = True          # Falseにすると効果音を鳴らさない
SE_DIR = "SE/"             # 音声ファイルを入れたフォルダ（index.htmlと同じ場所。末尾は/）
SE_URL = SE_DIR + "beam_se.wav"     # 予備の1ファイル
SE_VOLUME = 1.0            # 音量（0〜1。元の音が小さめなので1.0）
SE_FILES = [SE_DIR + "beam_se_1.wav", SE_DIR + "beam_se_2.wav", SE_DIR + "beam_se_3.wav", SE_DIR + "beam_se_4.wav", SE_DIR + "beam_se_5.wav"]  # コンボ1発目〜の音声ファイル。最後のファイルが以降も続く
SE_STEPS = [0, 2, 4, 6, 8]  # 予備：SE_FILESのファイルが無い番号は、SE_URLの1ファイルをこの半音数だけ上げて鳴らす
SE_TEST = False  # Trueにすると確認用キーが有効：1〜9=その発数目の音を鳴らす／0=順に鳴らす（PCのキーボード用）
TOUCH_OFFSET_TILES = 1.5  # タッチ操作時、照射範囲を指より上にずらすマス数（指で隠れないように）。0でずらさない

# レイアウト関連
MARGIN = 10          # 画面端・パネル間の余白(px)
PANEL_MIN_W = 150    # SIDEレイアウトで、左右のパネルに最低限確保する幅(px)
PANEL_MIN_H = 180    # BOTTOMレイアウトで、下のパネルに最低限確保する高さ(px)（切替ボタンの分を含む）
RANK_MAX = 10      # ランキングに載せる人数
NAME_MAX = 8       # 名前の最大文字数
RANK_API = "/api/ranking"        # ランキングAPIの場所（""にすると端末内だけで動く）
RANK_KEY = "colorgame_ranking"   # localStorageのキー（最後に読み込んだランキング）
NAME_KEY = "colorgame_name"      # localStorageのキー（最後に入力した名前）
SHOW_LAYOUT_INFO = False  # Trueにすると、選ばれたレイアウトと画面サイズを小さく表示する（研究・デバッグ用）

# 配色
BG_COLOR = "#000000"
PANEL_BG = "#101010"
PANEL_BORDER = "#646464"
TEXT_SUB = "#a9a9a9"
TEXT_MAIN = "#f3f3f3"
T_STRONG = "#ffffff"        # 最も強い文字・枠の色
BOARD_BG = "#000000"
SHADOW = "black"            # 文字の影
POPUP_BG = "#000000"        # 「N COMBO!」の箱の色
SWATCH_EDGE = "#555555"
NUISANCE_EDGE = "#777777"   # お邪魔ブロックの枠
LASER_CORE = "#ffffff"      # レーザーの芯
BLOCK_EDGE = None           # ブロックの縁取り（Noneなら描かない）

# モード別のテーマ（キー名はそのままグローバル変数名になる）
THEMES = {
    "dark": dict(BG_COLOR="#000000", PANEL_BG="#101010", PANEL_BORDER="#646464", TEXT_SUB="#a9a9a9",
                 TEXT_MAIN="#f3f3f3", T_STRONG="#ffffff", BOARD_BG="#000000", SHADOW="black",
                 POPUP_BG="#000000", SWATCH_EDGE="#555555", NUISANCE_EDGE="#777777",
                 LASER_CORE="#ffffff", BLOCK_EDGE=None),
    "light": dict(BG_COLOR="#ffffff", PANEL_BG="#f0f0f0", PANEL_BORDER="#9a9a9a", TEXT_SUB="#666666",
                  TEXT_MAIN="#1a1a1a", T_STRONG="#000000", BOARD_BG="#ffffff", SHADOW="#ffffff",
                  POPUP_BG="#ffffff", SWATCH_EDGE="#888888", NUISANCE_EDGE="#888888",
                  LASER_CORE="#333333", BLOCK_EDGE="#8a8a8a"),
}
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
DPR = 1.0       # 物理ピクセル / CSSピクセル の比（スマホでは2〜3程度）
TILE_SIZE = 0
BX = 0            # 盤面の左上x
BY = 0            # 盤面の左上y
BW = 0            # 盤面の幅
BH = 0            # 盤面の高さ
LAYOUT = ""       # 選ばれたレイアウトの名前
TOUCH_OFFSET = 0
PANELS = []       # [{"kind", "x", "y", "w", "h"}, ...]
wrap_cache = {}
BTN = None        # 切替ボタンの位置 (x, y, w, h)。描画のたびに更新される
RBTN = None       # タイトル画面のRANKINGボタンの位置 (x, y, w, h)。タイトル画面のときだけ値が入る

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

# ダークモード（加法混色）：光のRGB。お邪魔ブロック=黒(0)、消える色=白(0b111)
COLOR_DARK = {
    0b000: "#2a2a2a",
    0b100: "#ff0000",
    0b010: "#00ff00",
    0b001: "#0000ff",
    0b110: "#ffff00",
    0b101: "#ff00ff",
    0b011: "#00ffff",
    0b111: "#ffffff"
}
# ライトモード（減法混色）：インクの色。値は「反射する光」なので、C=0b011, M=0b101, Y=0b110
# お邪魔ブロック=白(紙, 0b111)、消える色=黒(0)
COLOR_LIGHT = {
    0b111: "#ffffff",
    0b011: "#00aeef",
    0b101: "#f828af",
    0b110: "#ffe600",
    0b001: "#2e3192",
    0b100: "#dc1c23",
    0b010: "#00a651",
    0b000: "#111111"
}
MODE_DEFS = {
    "dark": dict(MODE="dark", NUISANCE=BLACK, CLEAR=WHITE, PRIMARY=[RED, GREEN, BLUE], COLOR=COLOR_DARK),
    "light": dict(MODE="light", NUISANCE=WHITE, CLEAR=BLACK, PRIMARY=[CYAN, MAGENTA, YELLOW], COLOR=COLOR_LIGHT),
}
MODE = "dark"
NUISANCE = BLACK       # お邪魔ブロックの値（混色しても変化しない「単位元」）
CLEAR = WHITE          # 消える色
PRIMARY = [RED, GREEN, BLUE]
COLOR = COLOR_DARK

def mix(a, b):
    # 混色：ダークモードは加法混色（OR）、ライトモードは減法混色（AND）
    if MODE == "light":
        return a & b
    return a | b

# 盤面
masu = [[EMPTY for _ in range(COL)] for _ in range(ROW)]

# その他変数
index = 0
score = 0
high_score = 0
timer = 0
tsugi = 0
lasers = []  # 発射するレーザーの情報（cells, run, color, dy, dx）
combo = 0         # 連鎖して発射されたレーザーの回数
combo_timer = 0   # 「N COMBO!」を表示する残りフレーム数

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
    global W, H, DPR, TILE_SIZE, BX, BY, BW, BH, LAYOUT, TOUCH_OFFSET, PANELS

    W = max(int(js.window.innerWidth), 200)
    H = max(int(js.window.innerHeight), 200)
    # 内部解像度は物理ピクセルに合わせ、表示サイズ(CSS)は W x H のままにする（上限3倍）
    try:
        DPR = max(1.0, min(float(js.window.devicePixelRatio), 3.0))
    except Exception:
        DPR = 1.0
    canvas.width = int(W * DPR)
    canvas.height = int(H * DPR)
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
    mx = (e.clientX - rect.left) * W / rect.width
    my = (e.clientY - rect.top) * H / rect.height
    if e.pointerType == "touch":
        my -= TOUCH_OFFSET
    cursor_x = int((mx - BX) // TILE_SIZE)
    cursor_y = int((my - BY) // TILE_SIZE)

def hit_rect(e, r):
    # イベントの位置が、矩形 r = (x, y, w, h) の中か
    if r is None:
        return False
    rect = canvas.getBoundingClientRect()
    if rect.width == 0 or rect.height == 0:
        return False
    mx = (e.clientX - rect.left) * W / rect.width
    my = (e.clientY - rect.top) * H / rect.height
    return r[0] <= mx <= r[0] + r[2] and r[1] <= my <= r[1] + r[3]

def hit_button(e):
    # 切替ボタン（パネル内）が押されたか
    return hit_rect(e, BTN)

def pointer_down(e):
    global pressed, show_cursor
    if not e.isPrimary:
        return
    if e.pointerType == "mouse" and e.button != 0:
        return
    note_input(e)
    init_audio()
    e.preventDefault()
    if hit_button(e):
        if index != 8:  # 名前の入力中は、モードを切り替えない
            switch_mode()
        return
    if (index == 0 or index == 1) and hit_rect(e, RBTN):
        reset_rank_state()
        open_scoreboard(-1, -1)
        refresh_ranking()
        return
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
    if e.isPrimary:
        init_audio()  # タッチでは、指を離したときが音声を許可される操作になるブラウザがある
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
def outline_text(txt, x, y, siz):
    # 文字の縁取り（背景色）。文字本体より先に描き、本体を上に重ねる
    if TEXT_OUTLINE <= 0:
        return
    context.lineJoin = "round"  # 角が尖らないようにする
    context.strokeStyle = SHADOW
    context.lineWidth = max(2, siz * TEXT_OUTLINE)
    context.strokeText(txt, x, y)

def draw_txt(txt, x, y, siz, col, tg):
    # 盤面上のテキスト（影付き。yはベースライン）
    context.font = f"bold {siz}px {FONT}"
    outline_text(txt, x, y, siz)
    context.fillStyle = col
    context.fillText(txt, x, y)

def combo_mult():
    # 現在のコンボ数に応じた得点倍率
    return 1.0 + COMBO_BONUS_STEP * (max(combo, 1) - 1)

def add_score(points):
    # 倍率をかけて得点を加算する。加算した得点を返す
    global score, high_score
    gained = int(round(points * combo_mult()))
    score += gained
    if score > high_score:
        high_score = score
    return gained

def combo_label():
    # パネル表示用：2コンボ以上のときは倍率も添える
    if combo >= 2:
        return f"{combo} ×{combo_mult():.1f}"
    return str(combo)

def combo_color():
    # コンボ0〜1は控えめな灰色、2コンボ以上は白（さらに枠で強調する）
    return T_STRONG if combo >= 2 else TEXT_SUB

def draw_combo_frame(x, y, txt, siz):
    # 2コンボ以上のとき、パネルのコンボ表示を白い枠で囲む（枠はコンボが増えるほど太くなる）
    if combo < 2:
        return
    context.font = f"bold {siz}px {FONT}"
    tw = context.measureText(txt).width
    context.strokeStyle = T_STRONG
    context.lineWidth = min(4, combo)
    context.strokeRect(x - 5, y - siz * 0.15, tw + 10, siz * 1.3)

def draw_combo_popup():
    # 盤面中央の「N COMBO!」：半透明の黒い箱に白文字と白枠。下の盤面が透けて見える
    T = TILE_SIZE
    txt = f"{combo} COMBO!  ×{combo_mult():.1f}"
    siz = T * 0.7 * min(1.0 + 0.08 * (combo - 2), 1.4)  # コンボが増えるほど少し大きく（上限あり）
    max_w = BW - T * 0.8
    context.font = f"bold {siz}px {FONT}"
    tw = context.measureText(txt).width
    if tw > max_w:
        siz = siz * max_w / tw
        context.font = f"bold {siz}px {FONT}"
        tw = max_w
    pad = siz * 0.5
    bw = tw + 2 * pad
    bh = siz + 2 * pad
    cx = BX + BW / 2
    cy = BY + BH / 2
    bx = cx - bw / 2
    by = cy - bh / 2

    context.globalAlpha = COMBO_POPUP_ALPHA
    context.fillStyle = POPUP_BG
    context.fillRect(bx, by, bw, bh)
    context.globalAlpha = 1.0

    context.strokeStyle = T_STRONG
    context.lineWidth = max(2, min(5, combo))
    context.strokeRect(bx, by, bw, bh)

    context.textAlign = "center"
    context.fillStyle = T_STRONG
    context.fillText(txt, cx, by + pad + siz * 0.85)
    context.textAlign = "left"

def draw_txt_c(txt, cx, y, siz, col, max_w=None):
    # 中央寄せの影付きテキスト（cxは中心のx、yはベースライン）
    # max_wを指定すると、その幅に収まらないときだけ文字を縮小する
    context.font = f"bold {siz}px {FONT}"
    if max_w is not None:
        tw = context.measureText(txt).width
        if tw > max_w:
            siz = siz * max_w / tw
            context.font = f"bold {siz}px {FONT}"
    context.textAlign = "center"
    outline_text(txt, cx, y, siz)
    context.fillStyle = col
    context.fillText(txt, cx, y)
    context.textAlign = "left"

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
    context.strokeStyle = SWATCH_EDGE
    context.lineWidth = 1
    context.strokeRect(x + 0.5, y + 0.5, s - 1, s - 1)

def ui_font():
    # パネルの基準フォントサイズ。画面の短辺に比例させる（大画面でも文字が大きくなりすぎないよう上限あり）
    return max(12, min(20, int(min(W, H) * 0.03)))

# ---------- 描画：背景とパネル ----------
def draw_bg():
    global BTN
    BTN = None
    context.fillStyle = BG_COLOR
    context.fillRect(0, 0, W, H)

    for p in PANELS:
        draw_panel(p)

    # 盤面
    context.fillStyle = BOARD_BG
    context.fillRect(BX, BY, BW, BH)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(BX - 1, BY - 1, BW + 2, BH + 2)

def rule_texts():
    # 入力方式とモードに合わせて、操作・ルールの説明を切り替える
    light = (MODE == "light")
    what = "インクを吹き付け" if light else "光を照射"
    if input_type == "touch":
        first = f"画面を押したまま動かし、離した位置の3x3マスに{what}"
    else:
        first = f"クリックした位置を中心に、3x3マスへ{what}"
    if light:
        return [
            first,
            "同じ色が3つ並ぶとレーザー発射。軌道上のブロックが混色",
            "C+M+Y（黒）になったブロックは消える",
            "白ブロックはインクで色が付く（黒には3色必要）",
        ]
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
    put(str(score), x, y, F * 1.3, T_STRONG)
    y += F * 1.7
    put("HI-SCORE", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    put(str(high_score), x, y, F * 1.3, T_STRONG)
    y += F * 1.7
    put("NEXT", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    if tsugi in COLOR:
        draw_swatch(x, y, F * 1.3, tsugi)
    y += F * 1.7
    put("COMBO", x, y, F * 0.7, TEXT_SUB)
    y += F * 0.9
    put(combo_label(), x, y, F * 1.3, combo_color())
    draw_combo_frame(x, y, combo_label(), F * 1.3)
    y += F * 1.7
    return y

def draw_status_c(p, y, pad):
    # 4行に詰めたスコア表示（高さが足りないとき用）
    F = ui_font()
    x = p["x"] + pad
    put(f"SCORE  {score}", x, y, F, T_STRONG)
    put(f"HI-SCORE  {high_score}", x, y + F * 1.4, F, T_STRONG)
    put("NEXT", x, y + F * 2.8, F, TEXT_SUB)
    if tsugi in COLOR:
        draw_swatch(x + F * 3.6, y + F * 2.7, F * 1.1, tsugi)
    put(f"COMBO  {combo_label()}", x, y + F * 4.2, F, combo_color())
    draw_combo_frame(x, y + F * 4.2, f"COMBO  {combo_label()}", F)
    return y + F * 5.8

def draw_status(p, y, bottom, pad):
    # 空き高さに合わせて、スコア表示の形式を切り替える
    if y + ui_font() * 10.4 <= bottom:
        return draw_status_v(p, y, pad)
    return draw_status_c(p, y, pad)

def draw_status_h(p, y, pad):
    # 横に並べるスコア表示（BOTTOMレイアウト用）
    F = ui_font()
    x = p["x"] + pad
    put(f"SCORE  {score}", x, y, F * 1.1, T_STRONG)
    put(f"HI-SCORE  {high_score}", x, y + F * 1.5, F * 1.1, T_STRONG)
    x2 = p["x"] + p["w"] * 0.62
    put("NEXT", x2, y, F * 1.1, TEXT_SUB)
    if tsugi in COLOR:
        draw_swatch(x2 + F * 3.6, y - F * 0.05, F * 1.2, tsugi)
    put(f"COMBO {combo_label()}", x2, y + F * 1.5, F * 1.1, combo_color())
    draw_combo_frame(x2, y + F * 1.5, f"COMBO {combo_label()}", F * 1.1)
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
    if MODE == "light":
        rows = [
            ([CYAN, MAGENTA], BLUE, ""),
            ([MAGENTA, YELLOW], RED, ""),
            ([YELLOW, CYAN], GREEN, ""),
            ([CYAN, MAGENTA, YELLOW], BLACK, "消える"),
        ]
    else:
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

def draw_mode_button(p, pad, bottom):
    # パネル下部に、モード切替ボタンを描く。ボタンの上端より上を、内容の表示領域として返す
    global BTN
    F = ui_font()
    bh = max(28, int(F * 2.0))
    bw = min(p["w"] - 2 * pad, int(F * 14))
    bx = p["x"] + pad
    by = p["y"] + p["h"] - pad - bh
    BTN = (bx, by, bw, bh)
    context.fillStyle = BG_COLOR
    context.fillRect(bx, by, bw, bh)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(bx + 1, by + 1, bw - 2, bh - 2)
    label = "ダークモードに切替" if MODE == "light" else "ライトモードに切替"
    fs = F
    context.font = f"bold {fs}px {FONT}"
    tw = context.measureText(label).width
    if tw > bw - 12:
        fs = fs * (bw - 12) / tw
    context.textAlign = "center"
    context.fillStyle = T_STRONG
    context.font = f"bold {fs}px {FONT}"
    context.fillText(label, bx + bw / 2, by + bh / 2 + fs * 0.35)
    context.textAlign = "left"
    return by - pad * 0.5

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
    if kind == "rules" or (kind == "all" and w < 520):
        bottom = draw_mode_button(p, pad, bottom)
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
        # 2列のときは、ボタンを左列（スコア側）に置き、ルール側の高さを減らさない
        bottom_l = draw_mode_button(pl, pad, bottom)
        draw_status(pl, cy, bottom_l, pad)
        cy2 = draw_rules(pr, cy, bottom, pad)
        draw_legend(pr, cy2, bottom, pad)
    else:
        cy = draw_status_h(p, cy, pad)
        cy = draw_rules(p, cy, bottom, pad)
        draw_legend(p, cy, bottom, pad)

    if SHOW_LAYOUT_INFO:
        put(f"{LAYOUT} {W}x{H} tile={TILE_SIZE}", x + pad, y + h - pad - 11, 11, "#707070", False)

    context.restore()

# ---------- 描画：盤面 ----------
def draw_block():
    T = TILE_SIZE
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] != EMPTY and masu[y][x] in COLOR:
                context.fillStyle = COLOR[masu[y][x]]
                context.fillRect(BX + x * T + 1, BY + y * T + 1, T - 2, T - 2)
                if BLOCK_EDGE is not None:
                    context.strokeStyle = BLOCK_EDGE
                    context.lineWidth = 1
                    context.strokeRect(BX + x * T + 1.5, BY + y * T + 1.5, T - 3, T - 3)
                if masu[y][x] == NUISANCE:
                    # お邪魔ブロックは背景と区別できるよう灰色の枠を付ける
                    context.strokeStyle = NUISANCE_EDGE
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
        context.strokeStyle = LASER_CORE
        context.lineWidth = T * 0.12
        context.beginPath()
        context.moveTo(x0, y0)
        context.lineTo(x1, y1)
        context.stroke()
        context.globalAlpha = 1.0

# ---------- 判定・処理関数 ----------
def find_lines():
    # 同じ色が3つ以上つながっている並び（縦・横・斜め）をすべて探す
    # お邪魔ブロック・消える色・空マスは対象外。戻り値: [(つながったマスのリスト, dy, dx, 色), ...]
    lines = []
    for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        for y in range(ROW):
            for x in range(COL):
                n = masu[y][x]
                if n == EMPTY or n == NUISANCE or n == CLEAR:  # お邪魔ブロックは光/インクを出さない
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
    add = [[NUISANCE for _ in range(COL)] for _ in range(ROW)]  # NUISANCE = 何も当たらない（混色の単位元）
    for cells, run, color, dy, dx in lasers:
        for (y, x) in cells:
            if (y, x) not in run and masu[y][x] != EMPTY:
                add[y][x] = mix(add[y][x], color)

    # つながっていたブロックは消える
    for cells, run, color, dy, dx in lasers:
        for (y, x) in run:
            masu[y][x] = EMPTY

    # 軌道上のブロックを混色
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] != EMPTY:
                masu[y][x] = mix(masu[y][x], add[y][x])

def irradiate(cx, cy, color):
    # プレイヤーの照射：(cx, cy) を中心とする3x3マスのブロックを混色
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = cy + dy
            x = cx + dx
            if 0 <= y < ROW and 0 <= x < COL:
                if masu[y][x] != EMPTY:
                    masu[y][x] = mix(masu[y][x], color)

def sweep_block():
    num = 0
    for y in range(ROW):
        for x in range(COL):
            if masu[y][x] == CLEAR:
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
            masu[0][x] = NUISANCE  # お邪魔ブロック
        else:
            masu[0][x] = random.choice(PRIMARY)

# ---------- 効果音 ----------
audio_ctx = None
se_buffers = {}      # 読み込んだ音声。キーは 0〜(SE_FILESの数-1) と "base"（1ファイルの予備）
se_loading = False
se_pending = 0       # 読み込み中のファイル数
se_keep = []         # JSから呼ばれる関数は保持しておく（保持しないと呼ばれる前に消えることがある）

def se_log(msg):
    # 失敗の原因が分かるよう、ブラウザのコンソールに出す
    try:
        js.console.log("[SE] " + msg)
    except Exception:
        pass

def se_done():
    # 1ファイルの読み込みが終わるたびに呼ぶ。1つも読めなかったときは、次の操作でもう一度試す
    global se_pending, se_loading
    se_pending -= 1
    if se_pending <= 0 and len(se_buffers) == 0:
        se_loading = False

def load_one(key, url):
    # url を読み込み、se_buffers[key] に入れる（fetch → arrayBuffer → decodeAudioData）
    def failed(err=None):
        se_log("読み込めませんでした: " + url)
        se_done()
    def decoded(buf):
        se_buffers[key] = buf
        se_log("読み込み完了: " + url)
        se_done()
    def got_data(data):
        audio_ctx.decodeAudioData(data).then(p_dec, p_fail)
    def got_response(res):
        if not res.ok:
            se_log("HTTP " + str(res.status) + "（ファイルの場所を確認してください）: " + url)
            se_done()
            return
        res.arrayBuffer().then(p_data, p_fail)
    p_fail = create_proxy(failed)
    p_dec = create_proxy(decoded)
    p_data = create_proxy(got_data)
    p_resp = create_proxy(got_response)
    se_keep.extend([p_fail, p_dec, p_data, p_resp])
    js.fetch(url).then(p_resp, p_fail)

def load_se():
    global se_pending
    se_pending = len(SE_FILES) + 1
    for i in range(len(SE_FILES)):
        load_one(i, SE_FILES[i])
    load_one("base", SE_URL)

def init_audio():
    # ユーザー操作の中で呼ぶ（スマホなどは、操作の中で初期化しないと音が出ない）
    global audio_ctx, se_loading
    if not SE_ENABLED:
        return
    try:
        if audio_ctx is None:
            audio_ctx = js.AudioContext.new()
        if audio_ctx.state == "suspended":
            audio_ctx.resume()
        if not se_loading:
            se_loading = True
            load_se()
    except Exception as e:
        se_loading = False
        se_log("音声の初期化に失敗: " + str(e))

def play_beam(c):
    # c = 連鎖で何発目か（0始まり）。c発目のファイルを鳴らす（SE_FILESの数を超えたら最後のファイルのまま）
    if not SE_ENABLED or audio_ctx is None:
        return
    try:
        buf = se_buffers.get(min(c, len(SE_FILES) - 1))
        rate = 1.0
        if buf is None:
            # その番号のファイルが無いときは、予備の1ファイルをSE_STEPSの分だけピッチを上げて鳴らす
            buf = se_buffers.get("base")
            rate = 2 ** (SE_STEPS[min(c, len(SE_STEPS) - 1)] / 12)
        if buf is None:
            return
        src = audio_ctx.createBufferSource()
        src.buffer = buf
        src.playbackRate.value = rate
        gain = audio_ctx.createGain()
        gain.gain.value = SE_VOLUME
        src.connect(gain)
        gain.connect(audio_ctx.destination)
        src.start()
    except Exception as e:
        se_log("再生に失敗: " + str(e))

# ---------- SE確認モード（SE_TEST = True のとき有効） ----------
test_seq = 0

def test_seq_step():
    global test_seq
    if test_seq < len(SE_FILES):
        se_log("確認: " + str(test_seq + 1) + "発目")
        play_beam(test_seq)
        test_seq += 1
        js.setTimeout(P_TEST_SEQ, 700)

P_TEST_SEQ = create_proxy(test_seq_step)

def on_key_test(e):
    global test_seq
    init_audio()
    k = str(e.key)
    if k == "0":
        test_seq = 0
        test_seq_step()
    elif k in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
        n = int(k) - 1
        se_log("確認: " + k + "発目")
        play_beam(n)

if SE_TEST:
    js.window.addEventListener("keydown", create_proxy(on_key_test))
    se_log("SE確認モード: 1〜9キー=その発数目の音／0キー=順に再生")

# ---------- 色モードの切替 ----------
hi_scores = {"dark": 0, "light": 0}

def apply_mode(mode):
    # テーマ・色テーブル・混色ルールを切り替える
    global high_score
    globals().update(MODE_DEFS[mode])
    globals().update(THEMES[mode])
    high_score = hi_scores[mode]
    try:
        js.document.body.style.background = BG_COLOR
    except Exception:
        pass
    wrap_cache.clear()

def save_mode():
    try:
        js.localStorage.setItem("colorgame_mode", MODE)
    except Exception:
        pass

def load_mode():
    try:
        m = js.localStorage.getItem("colorgame_mode")
        if m == "light" or m == "dark":
            return m
    except Exception:
        pass
    return "dark"

def switch_mode():
    # モードを切り替え、ゲームをタイトル画面に戻す（盤面・スコアはリセット。ハイスコアはモード別）
    global index, score, combo, combo_timer, lasers, timer, tsugi, mouse_c, pressed, show_cursor
    hi_scores[MODE] = high_score
    apply_mode("light" if MODE == "dark" else "dark")
    save_mode()
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = EMPTY
    index = 0
    score = 0
    combo = 0
    combo_timer = 0
    lasers = []
    timer = 0
    tsugi = 0
    mouse_c = 0
    pressed = False
    show_cursor = False
    hide_name_ui()

# ---------- ランキング（保存先：localStorage） ----------
rank_last = -1     # 直前に登録した記録の順位（0始まり）。スコアボードで強調する。-1なら強調なし
rank_score = -1    # ゲームオーバーから来たときの今回のスコア。-1なら表示しない
name_box = None
name_inp = None
name_keep = []     # JSから呼ばれる関数は保持しておく

def clean_name(txt):
    # 保存形式の区切り文字を除き、前後の空白を取り、長さを制限する。空なら NONAME
    txt = txt.replace(",", " ").replace(";", " ").strip()
    txt = txt[:NAME_MAX].strip()
    if txt == "":
        txt = "NONAME"
    return txt

def rank_decode(raw):
    # "スコア,名前;スコア,名前;..." → [(名前, スコア), ...]
    out = []
    try:
        for item in str(raw).split(";"):
            if "," in item:
                sc, nm = item.split(",", 1)
                out.append((nm, int(sc)))
    except Exception:
        pass
    return out[:RANK_MAX]

def rank_encode(lst):
    return ";".join([str(sc) + "," + nm for nm, sc in lst])

def rank_local_load():
    try:
        raw = js.localStorage.getItem(RANK_KEY)
        if raw:
            return rank_decode(raw)
    except Exception:
        pass
    return []

rank_cache = rank_local_load()   # 表示と判定に使うランキング。サーバーから読み込むたびに更新する
rank_net = "idle"                # 読み込みの状態："idle" / "loading" / "ok" / "offline"
rank_fetching = False
rank_state = "idle"              # 登録の状態："idle" / "sending" / "failed" / "done" / "local"
rank_fail = 0
rank_pending = None              # 送信中の記録 (名前, スコア)

def rank_load():
    return rank_cache

def rank_save(lst):
    try:
        js.localStorage.setItem(RANK_KEY, rank_encode(lst))
    except Exception:
        pass

def rank_position(sc):
    # このスコアを登録したときの順位（0始まり）。同点は先に記録した方が上
    n = 0
    for nm, v in rank_load():
        if v >= sc:
            n += 1
    return n

def rank_qualifies(sc):
    return sc > 0 and rank_position(sc) < RANK_MAX

def rank_add(name, sc):
    # （端末内だけの保存）記録を追加して保存し、その順位（0始まり）を返す。圏外なら -1
    global rank_cache
    lst = list(rank_load())
    pos = rank_position(sc)
    lst.insert(pos, (name, sc))
    lst = lst[:RANK_MAX]
    rank_cache = lst
    rank_save(lst)
    if pos < RANK_MAX:
        return pos
    return -1

def load_name():
    try:
        v = js.localStorage.getItem(NAME_KEY)
        if v:
            return str(v)
    except Exception:
        pass
    return ""

def save_name(nm):
    try:
        js.localStorage.setItem(NAME_KEY, nm)
    except Exception:
        pass

# ---------- ランキングの通信（fetch。JavaScriptのPromiseを直接つなぐ） ----------
def net_log(msg):
    try:
        js.console.log("[RANK] " + msg)
    except Exception:
        pass

def get_resp(res):
    if not res.ok:
        net_log("HTTP " + str(res.status) + "（取得に失敗）")
        get_fail()
        return
    res.text().then(P_GET_TEXT, P_GET_FAIL)

def get_text(txt):
    global rank_cache, rank_net, rank_fetching
    rank_cache = rank_decode(txt)
    rank_save(rank_cache)
    rank_net = "ok"
    rank_fetching = False

def get_fail(err=None):
    global rank_net, rank_fetching
    rank_net = "offline"
    rank_fetching = False

def post_resp(res):
    if not res.ok:
        net_log("HTTP " + str(res.status) + "（登録に失敗）")
        post_fail()
        return
    res.text().then(P_POST_TEXT, P_POST_FAIL)

def post_text(txt):
    # 応答は "順位|記録の文字列"（順位は0始まり。ランク外は -1）
    global rank_cache, rank_last, rank_state, rank_net
    t = str(txt)
    if "|" not in t:
        net_log("想定外の応答: " + t[:60])
        post_fail()
        return
    try:
        pos, lst = t.split("|", 1)
        rank_cache = rank_decode(lst)
        rank_save(rank_cache)
        rank_last = int(pos)
        rank_net = "ok"
        rank_state = "done"
    except Exception as e:
        # 登録は成功しているのに、応答の処理に失敗した場合。再送しても同じIDなので二重登録にはならない
        net_log("応答の処理に失敗: " + str(e))
        post_fail()

def post_fail(err=None):
    global rank_state, rank_fail, rank_last
    net_log("登録に失敗（" + str(rank_fail + 1) + "回目）: " + str(err))
    rank_fail += 1
    if rank_fail >= 3 or rank_pending is None:
        # 何度やっても送れないときは、この端末内にだけ保存する
        if rank_pending is not None:
            rank_last = rank_add(rank_pending[0], rank_pending[1])
        rank_state = "local"
    else:
        rank_state = "failed"

P_GET_RESP = create_proxy(get_resp)
P_GET_TEXT = create_proxy(get_text)
P_GET_FAIL = create_proxy(get_fail)
P_POST_RESP = create_proxy(post_resp)
P_POST_TEXT = create_proxy(post_text)
P_POST_FAIL = create_proxy(post_fail)

def refresh_ranking():
    # サーバーから最新のランキングを読み込む（読み込み中は重ねて呼ばない）
    global rank_net, rank_fetching
    if RANK_API == "" or rank_fetching:
        return
    try:
        rank_fetching = True
        rank_net = "loading"
        opts = js.Object.new()
        opts.cache = "no-store"
        js.fetch(RANK_API, opts).then(P_GET_RESP, P_GET_FAIL)
    except Exception as e:
        net_log("取得を開始できません: " + str(e))
        get_fail()

def new_send_id():
    # 1回の登録に付ける、ランダムな16桁の送信ID（再送しても同じIDを使い、サーバーが二重登録を防ぐ）
    return "".join([random.choice("0123456789abcdef") for _ in range(16)])

def post_ranking():
    # rank_pending の記録をサーバーに送る
    global rank_state
    rank_state = "sending"
    try:
        opts = js.Object.new()
        opts.method = "POST"
        hdr = js.Object.new()
        setattr(hdr, "Content-Type", "text/plain;charset=UTF-8")
        opts.headers = hdr
        opts.body = str(rank_pending[1]) + "\n" + rank_pending[2] + "\n" + rank_pending[0]
        js.fetch(RANK_API, opts).then(P_POST_RESP, P_POST_FAIL)
    except Exception as e:
        net_log("送信を開始できません: " + str(e))
        post_fail()

def reset_rank_state():
    global rank_state, rank_pending, rank_fail
    rank_state = "idle"
    rank_pending = None
    rank_fail = 0

def open_scoreboard(last, sc):
    global index, timer, rank_last, rank_score
    rank_last = last
    rank_score = sc
    index = 9
    timer = 0

def submit_name():
    # 名前を確定してランキングに登録し、スコアボードを表示する
    global index, timer, rank_last, rank_score
    if index != 8 or name_inp is None:
        return
    global rank_state, rank_fail, rank_pending
    nm = clean_name(str(name_inp.value))
    save_name(nm)
    hide_name_ui()
    if RANK_API == "":
        pos = rank_add(nm, score)
        rank_state = "idle"
        open_scoreboard(pos, score)
    else:
        rank_pending = (nm, score, new_send_id())
        rank_fail = 0
        open_scoreboard(-1, score)
        post_ranking()

def on_name_click(e):
    submit_name()

def on_name_key(e):
    e.stopPropagation()  # 入力中の文字を、他のキー操作（SE確認用など）に渡さない
    if e.key == "Enter" and not e.isComposing:  # 日本語入力の変換確定のEnterは除く
        submit_name()

def trim_name(e=None):
    # 入力欄の文字数をNAME_MAX以内にする（変換中は一部のブラウザでmaxlengthが効かないため、確定時にも切り詰める）
    if name_inp is None:
        return
    v = str(name_inp.value)
    if len(v) > NAME_MAX:
        name_inp.value = v[:NAME_MAX]

def on_name_input(e):
    if not e.isComposing:
        trim_name()

def make_name_ui():
    # 名前の入力欄とOKボタン（HTML要素。canvasには文字入力の機能がないため、盤面の上に重ねる）
    global name_box, name_inp
    box = js.document.createElement("div")
    inp = js.document.createElement("input")
    btn = js.document.createElement("button")
    inp.type = "text"
    inp.maxLength = NAME_MAX
    inp.setAttribute("maxlength", str(NAME_MAX))
    inp.placeholder = "なまえ"
    inp.setAttribute("autocomplete", "off")
    inp.setAttribute("enterkeyhint", "done")
    btn.textContent = "OK"
    box.style.position = "fixed"
    box.style.display = "none"
    box.style.gap = "6px"
    box.style.zIndex = "10"
    inp.style.flex = "1"
    inp.style.minWidth = "0"
    inp.style.boxSizing = "border-box"
    inp.style.padding = "6px 8px"
    inp.style.fontFamily = "inherit"
    btn.style.padding = "6px 14px"
    btn.style.fontFamily = "inherit"
    btn.style.fontWeight = "bold"
    p_click = create_proxy(on_name_click)
    p_key = create_proxy(on_name_key)
    p_input = create_proxy(on_name_input)
    p_trim = create_proxy(trim_name)
    name_keep.extend([p_click, p_key, p_input, p_trim])
    btn.addEventListener("click", p_click)
    inp.addEventListener("keydown", p_key)
    inp.addEventListener("input", p_input)
    inp.addEventListener("compositionend", p_trim)
    box.appendChild(inp)
    box.appendChild(btn)
    js.document.body.appendChild(box)
    name_box = box
    name_inp = inp
    return box, inp, btn

def style_name_ui():
    # テーマの色に合わせる
    box = name_box
    inp = name_inp
    btn = box.lastChild
    for el in (inp, btn):
        el.style.background = BG_COLOR
        el.style.color = T_STRONG
        el.style.border = "2px solid " + T_STRONG
        el.style.borderRadius = "0"

def place_name_ui():
    # 盤面の位置に合わせて入力欄を置く（ウィンドウサイズが変わっても追従する）
    if name_box is None:
        return
    T = TILE_SIZE
    rect = canvas.getBoundingClientRect()
    if rect.width == 0 or rect.height == 0:
        return
    sx = rect.width / W
    sy = rect.height / H
    wpx = min(BW * sx * 0.9, 340)
    name_box.style.left = str(rect.left + (BX + BW / 2) * sx - wpx / 2) + "px"
    name_box.style.top = str(rect.top + (BY + T * 5.4) * sy) + "px"
    name_box.style.width = str(wpx) + "px"
    fs = max(16, T * 0.5 * sy)  # 16px未満だと、iPhoneで入力時に画面が拡大される
    name_inp.style.fontSize = str(fs) + "px"
    name_box.lastChild.style.fontSize = str(fs) + "px"

def show_name_ui():
    global name_box
    if name_box is None:
        make_name_ui()
    style_name_ui()
    name_box.style.display = "flex"
    name_inp.value = load_name()
    place_name_ui()
    if input_type != "touch":  # スマホでは、勝手にキーボードを開かない（入力欄をタップしたときに開く）
        try:
            name_inp.focus()
            name_inp.select()
        except Exception:
            pass

def hide_name_ui():
    if name_box is not None:
        name_box.style.display = "none"

def start_name_entry():
    global index
    index = 8
    show_name_ui()

def draw_popup_box():
    # 盤面全体を覆う、半透明の箱
    context.globalAlpha = 0.93
    context.fillStyle = POPUP_BG
    context.fillRect(BX, BY, BW, BH)
    context.globalAlpha = 1.0
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(BX + 1, BY + 1, BW - 2, BH - 2)

def draw_name_entry():
    T = TILE_SIZE
    draw_popup_box()
    draw_txt_c("RANK IN!", BX + BW / 2, BY + T * 2.0, T * 0.95, T_STRONG, BW - T * 0.6)
    draw_txt_c("第" + str(rank_position(score) + 1) + "位  SCORE " + str(score), BX + BW / 2, BY + T * 3.3, T * 0.5, T_STRONG, BW - T * 0.6)
    draw_txt_c("名前を入力してください", BX + BW / 2, BY + T * 4.6, T * 0.4, TEXT_SUB, BW - T * 0.6)
    place_name_ui()

def draw_scoreboard():
    T = TILE_SIZE
    draw_popup_box()
    draw_txt_c("RANKING", BX + BW / 2, BY + T * 1.0, T * 0.75, T_STRONG, BW - T * 0.6)
    top = BY + T * 1.3
    if rank_score >= 0:
        draw_txt_c("YOUR SCORE  " + str(rank_score), BX + BW / 2, BY + T * 1.75, T * 0.42, TEXT_SUB, BW - T * 0.6)
        top = BY + T * 2.0
    foot = BY + BH - T * 0.35
    row_h = min(T * 0.72, (foot - T * 0.55 - top) / RANK_MAX)
    fs = row_h * 0.7
    lst = rank_load()
    left = BX + T * 0.35
    right = BX + BW - T * 0.35
    name_x = BX + T * 1.25
    name_w = (right - name_x) * 0.62
    for i in range(RANK_MAX):
        y = top + row_h * i
        base = y + row_h * 0.72
        hot = (i == rank_last)
        if hot:
            context.strokeStyle = T_STRONG
            context.lineWidth = 2
            context.strokeRect(left - 3, y + 1, right - left + 6, row_h - 2)
        col = T_STRONG if hot else TEXT_MAIN
        context.font = f"bold {fs}px {FONT}"
        context.textAlign = "left"
        context.fillStyle = TEXT_SUB if not hot else T_STRONG
        context.fillText(str(i + 1), left, base)
        if i < len(lst):
            nm, sc = lst[i]
            nsz = fs
            context.font = f"bold {nsz}px {FONT}"
            tw = context.measureText(nm).width
            if tw > name_w:
                nsz = nsz * name_w / tw
                context.font = f"bold {nsz}px {FONT}"
            context.fillStyle = col
            context.fillText(nm, name_x, base)
            context.font = f"bold {fs}px {FONT}"
            context.textAlign = "right"
            context.fillText(str(sc), right, base)
        else:
            context.fillStyle = TEXT_SUB
            context.fillText("---", name_x, base)
    context.textAlign = "left"
    if rank_net == "loading" or rank_net == "offline":
        context.font = f"{T * 0.3}px {FONT}"
        context.textAlign = "right"
        context.fillStyle = TEXT_SUB
        context.fillText("更新中…" if rank_net == "loading" else "オフライン", BX + BW - T * 0.25, BY + T * 0.5)
        context.textAlign = "left"
    if rank_state == "sending":
        msg = "送信中…"
    elif rank_state == "failed":
        msg = "送信に失敗しました（タップで再送信）"
    elif rank_state == "local":
        msg = "オフラインのため、この端末に保存しました"
    else:
        msg = "Tap to Continue" if input_type == "touch" else "Click to Continue"
    draw_txt_c(msg, BX + BW / 2, foot, T * 0.38, TEXT_SUB, BW - T * 0.6)

def draw_rank_button():
    # タイトル画面のRANKINGボタン
    global RBTN
    T = TILE_SIZE
    bw = min(T * 4.4, BW - T * 0.6)
    bh = T * 0.95
    bx = BX + (BW - bw) / 2
    by = BY + T * 7.4
    RBTN = (bx, by, bw, bh)
    context.fillStyle = POPUP_BG
    context.fillRect(bx, by, bw, bh)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(bx + 1, by + 1, bw - 2, bh - 2)
    context.font = f"bold {T * 0.5}px {FONT}"
    context.textAlign = "center"
    context.fillStyle = T_STRONG
    context.fillText("RANKING", bx + bw / 2, by + bh / 2 + T * 0.18)
    context.textAlign = "left"

# ---------- メインループ ----------
def game_main():
    global index, timer, tsugi, score, high_score, lasers
    global cursor_x, cursor_y, mouse_c, combo, combo_timer, RBTN

    T = TILE_SIZE
    context.setTransform(DPR, 0, 0, DPR, 0, 0)  # 以降の描画はCSSピクセル基準
    draw_bg()
    draw_block()

    RBTN = None
    if index == 0 or index == 1:
        start_txt = "Tap to Start" if input_type == "touch" else "Click to Start"
        draw_txt_c("Color Puzzle", BX + BW / 2, BY + T * 3, T * 0.95, T_STRONG, BW - T * 0.6)
        draw_txt_c(start_txt, BX + BW / 2, BY + T * 6, T * 0.5, T_STRONG, BW - T * 0.6)
        draw_rank_button()
        index = 1

        if mouse_c == 1:
            mouse_c = 0
            for y in range(ROW):
                for x in range(COL):
                    masu[y][x] = EMPTY
            score = 0
            combo = 0
            combo_timer = 0
            tsugi = random.choice(PRIMARY)
            set_block(START_NUM)
            index = 2
            refresh_ranking()

    elif index == 2:
        # ブロックの落下処理
        if not drop_block():
            index = 4

    elif index == 3:
        # 白になったブロックの消去とスコア加算
        sc = sweep_block()
        if sc > 0:
            add_score(sc * SCORE_PER_WHITE)
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
            play_beam(combo)  # 複数のレーザーが同時に出ても、鳴らすのは1回
            index = 7
        elif not over_block():
            tsugi = random.choice(PRIMARY)
            mouse_c = 0
            index = 5
        else:
            index = 6
            timer = 0
            refresh_ranking()  # ゲームオーバーの表示中に、最新のランキングを読み込んでおく

    elif index == 5:
        # 操作フェーズ：クリックした位置を中心に3x3へ照射
        if 0 <= cursor_x < COL and 0 <= cursor_y < ROW:
            if tsugi in COLOR and show_cursor:
                draw_area_preview()

            if mouse_c == 1:
                mouse_c = 0
                combo = 0  # 新しい手番の開始でコンボをリセット
                irradiate(cursor_x, cursor_y, tsugi)
                set_block(SPAWN_NUM)
                index = 3
        mouse_c = 0

    elif index == 6:
        # ゲームオーバー表示
        timer += 1
        mouse_c = 0
        draw_txt_c("GAME OVER", BX + BW / 2, BY + T * 5, T * 0.95, "red", BW - T * 0.6)
        if timer >= 50:
            if score > 0 and rank_qualifies(score):
                start_name_entry()   # 上位10位に入るので、名前を入力する
            elif score > 0:
                reset_rank_state()
                open_scoreboard(-1, score)
            else:
                index = 0

    elif index == 8:
        # 名前の入力（HTMLの入力欄で行う）
        mouse_c = 0
        draw_name_entry()

    elif index == 9:
        # スコアボード表示 → 画面を押すとタイトルへ
        timer += 1
        draw_scoreboard()
        if mouse_c == 1 and timer >= 3:
            if rank_state == "sending":
                pass  # 送信中は、画面を押しても進まない
            elif rank_state == "failed":
                post_ranking()  # 再送信
            else:
                index = 0
        mouse_c = 0

    elif index == 7:
        # レーザー表示 → 発射（混色）
        draw_laser()
        timer += 1
        if timer >= LASER_FRAMES:
            # 同色がそろって消えるブロックの数（重なったマスは1個として数える）
            erased = set()
            for cells, run, color, dy, dx in lasers:
                erased.update(run)
            fire_lasers()
            lasers = []
            combo += 1  # 先にコンボを増やしてから、その倍率で加点する
            add_score(len(erased) * SCORE_PER_LINE_BLOCK)
            if combo >= 2:
                combo_timer = COMBO_POPUP_FRAMES
            index = 3  # 白になったブロックの消去へ

    # コンボ表示（2コンボ以上）
    if combo_timer > 0:
        combo_timer -= 1
        draw_combo_popup()

    js.setTimeout(game_main, 100)

apply_mode(load_mode())
refresh_ranking()
game_main()
