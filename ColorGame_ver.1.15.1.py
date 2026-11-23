# 加法混色パズル ver.1.15.1（配色の名前の表示に半透明の背景を付ける。色覚配慮テーマのNEXTの印を大きくする）
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
MULTI_BEAM_STEP = 0.5      # 同時に発射したビームが1本増えるごとに加わる倍率（1本=×1.0、2本=×1.5、3本=×2.0 ...）。コンボの倍率と掛け合わされる
MULTI_BEAM_WHITE = True    # Trueなら、そのビームで白くなって消えたブロックの得点にも、同時発射の倍率をかける（Falseなら、ビームで消えた分だけ）
TEXT_OUTLINE = 0.05        # 盤面上の文字の縁取りの太さ（文字サイズに対する比。0で縁取りなし）
SE_ENABLED = True          # Falseにすると効果音を鳴らさない
SE_DIR = "SE/"             # 音声ファイルを入れたフォルダ（index.htmlと同じ場所。末尾は/）
SE_URL = SE_DIR + "beam_se.wav"     # 予備の1ファイル
SE_VOLUME = 1.0            # 音量（0〜1。ユーザーが聞いて調整した値）
SE_FILES = [SE_DIR + "beam_se_1.wav", SE_DIR + "beam_se_2.wav", SE_DIR + "beam_se_3.wav"]  # コンボ1発目〜の音声ファイル。最後のファイルが以降も続く
SE_STEPS = [0, 2, 4, 6, 8]  # 予備：SE_FILESのファイルが無い番号は、SE_URLの1ファイルをこの半音数だけ上げて鳴らす
BGM_ENABLED = True         # Falseにすると、BGMを鳴らさない
BGM_URL = "BGM/bgm_2.wav"    # BGMの音声ファイル（index.htmlと同じ場所のBGMフォルダ）。ループ再生する
BGM_VOLUME = 0.5           # BGMの音量（0〜1）。効果音より小さめにしておく
BGM_LOOP_START = 0.0       # ループの開始位置（秒）。イントロを1回だけ流したいときに指定する
BGM_LOOP_END = 0.0         # ループの終了位置（秒）。0なら、ファイルの最後まで
SE_TEST = True  # Trueにすると確認用キーが有効：1〜9=その発数目の音を鳴らす／0=順に鳴らす（PCのキーボード用）
TOUCH_OFFSET_TILES = 1.5  # タッチ操作時、照射範囲を指より上にずらすマス数（指で隠れないように）。0でずらさない

# レイアウト関連
MARGIN = 10          # 画面端・パネル間の余白(px)
PANEL_MIN_W = 150    # SIDEレイアウトで、左右のパネルに最低限確保する幅(px)
PANEL_MIN_H = 180    # BOTTOMレイアウトで、下のパネルに最低限確保する高さ(px)（切替ボタンの分を含む）
DEMO_ENABLED = True        # Trueなら、タイトル画面の背景で、デモプレイ（自動で遊ぶ様子）を流す
DEMO_AIM_FRAMES = 6        # デモプレイで、照射の範囲を見せてから撃つまでの時間（1フレーム=0.1秒）
DEMO_THINK_ROWS = 3        # デモプレイが、1フレームに調べる行の数（小さいほど動きが滑らかだが、手を決めるのが遅くなる。盤面は10行）
DEMO_RESTART_FRAMES = 10   # デモプレイでゲームオーバーになってから、盤面をリセットするまでの時間（フレーム）
DEMO_DIM = 0.55            # デモプレイの盤面を暗くする濃さ（0〜1。タイトルの文字を読みやすくする）
DEMO_SOUND = False         # Trueなら、デモプレイ中もビームの効果音を鳴らす
TUTORIAL_ENABLED = True    # Falseにすると、タイトル画面の「あそびかた」ボタン（チュートリアル）を出さない
RULES_DEFAULT_OPEN = None   # ルール説明を、最初から表示するか。None＝横画面（幅≧高さ）のときだけ表示／True＝常に表示／False＝常に隠す（虫眼鏡ボタンで切り替え）
BADGE_AVOID = True   # Netlify無料プランの「Powered by Netlify」バッジ（画面の右下に固定表示）を避ける。バッジが出ない環境ではFalse
BADGE_W = 194        # 画面の右端から、バッジの左端までの距離(px)（閉じた状態のバッジ。実測値）
BADGE_H = 61         # 画面の下端から、バッジの上端までの距離(px)（同上）
BADGE_GAP = 4        # バッジとの間に空ける余白(px)
RANK_MAX = 10      # ランキングに載せる人数
NAME_MAX = 8       # 名前の最大文字数
RANK_API = "/api/ranking"        # ランキングAPIの場所（""にすると端末内だけで動く）
RANK_KEY = "colorgame_ranking"   # localStorageのキー（最後に読み込んだランキング）
NAME_KEY = "colorgame_name"      # localStorageのキー（最後に入力した名前）
MUTE_KEY = "colorgame_mute"      # localStorageのキー（ミュートの状態。"1"ならミュート）
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

# 配色テーマ（モードごとに3種類。ボタンで 標準 → やさしい → 色覚配慮 の順に切り替える）
#  ・標準　　：これまでの配色
#  ・やさしい：まぶしさをおさえる（純粋な白・黒を避け、色の彩度と明るさを少し下げる）
#  ・色覚配慮：色覚の多様性に配慮した、見分けやすい配色（Okabe-Itoの配色をもとにする）。さらに、ブロックに「どの色が混ざっているか」を示す印（●■▲）を付ける
PALETTE_NAMES = ["標準", "やさしい", "色覚配慮"]
PALETTE_KEY = "colorgame_palette"   # localStorageのキー（最後に選んだ配色テーマの番号）
PAL_TOAST_FRAMES = 15               # 配色を切り替えたときに、名前を表示する時間（フレーム）
MARK_COLOR = "#111111"              # 色覚配慮テーマの印の色
MARK_EDGE = "#ffffff"               # 印の縁取りの色

# 色覚配慮：値ごとの色（Okabe-Ito）。ダークとライトで、色の値が同じなら同じ色にする（白と黒だけモードで変える）
CVD = {
    0b100: "#d55e00",   # 赤（朱色）
    0b010: "#009e73",   # 緑（青緑）
    0b001: "#0072b2",   # 青
    0b110: "#f0e442",   # 黄
    0b101: "#cc79a7",   # マゼンタ（赤紫）
    0b011: "#56b4e9",   # シアン（空色）
}
COLOR_DARK_SOFT = {
    0b000: "#2c2f36",
    0b100: "#e5645f",
    0b010: "#5cc07a",
    0b001: "#5b86e6",
    0b110: "#e8cf6a",
    0b101: "#d577d0",
    0b011: "#5fcfd6",
    0b111: "#e9e9e9"
}
COLOR_LIGHT_SOFT = {
    0b111: "#fbf8f1",
    0b011: "#4fb3d9",
    0b101: "#d96aa7",
    0b110: "#f0d264",
    0b001: "#4a5aa8",
    0b100: "#d2504f",
    0b010: "#4aa46a",
    0b000: "#2b2b2b"
}
COLOR_DARK_CVD = {0b000: "#2a2a2a", 0b111: "#ffffff"}
COLOR_LIGHT_CVD = {0b111: "#ffffff", 0b000: "#111111"}
for _k in CVD:
    COLOR_DARK_CVD[_k] = CVD[_k]
    COLOR_LIGHT_CVD[_k] = CVD[_k]
# モードごとの、配色テーマの差分（THEMESの上に重ねる。COLORは、値→色の表）
PALETTES = {
    "dark": [
        dict(MARKS=False),
        dict(MARKS=False, COLOR=COLOR_DARK_SOFT, BG_COLOR="#15171b", PANEL_BG="#1d2025", PANEL_BORDER="#5d636b",
             TEXT_SUB="#a3a8ae", TEXT_MAIN="#e6e8ea", T_STRONG="#f0f0f0", BOARD_BG="#15171b", SHADOW="#15171b",
             POPUP_BG="#15171b", SWATCH_EDGE="#555a61", NUISANCE_EDGE="#6f757c", LASER_CORE="#f0f0f0"),
        dict(MARKS=True, COLOR=COLOR_DARK_CVD),
    ],
    "light": [
        dict(MARKS=False),
        dict(MARKS=False, COLOR=COLOR_LIGHT_SOFT, BG_COLOR="#f4f0e8", PANEL_BG="#e9e4da", PANEL_BORDER="#a39d90",
             TEXT_SUB="#69645b", TEXT_MAIN="#2b2b2b", T_STRONG="#1c1c1c", BOARD_BG="#f4f0e8", SHADOW="#f4f0e8",
             POPUP_BG="#f4f0e8", SWATCH_EDGE="#8c877b", NUISANCE_EDGE="#8c877b", LASER_CORE="#3a3a3a", BLOCK_EDGE="#8c877b"),
        dict(MARKS=True, COLOR=COLOR_LIGHT_CVD),
    ],
}
palette = 0     # 今の配色テーマの番号（0=標準, 1=やさしい, 2=色覚配慮）。起動時にlocalStorageから読み込む
MARKS = False   # Trueなら、ブロックに印（どの色が混ざっているか）を描く
pal_toast = 0   # 配色の名前を表示する残りフレーム数

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
PBTN = None       # 配色切替ボタン（3つの丸のアイコン）の位置 (x, y, w, h)。描画のたびに更新される
HBTN = None       # ルール表示ボタン（虫眼鏡のアイコン）の位置 (x, y, w, h)。描画のたびに更新される
show_rules = False   # ルール説明を表示中か（最初の状態は、relayout()のあとで決める）
MBTN = None       # ミュートボタン（スピーカーのアイコン）の位置 (x, y, w, h)。描画のたびに更新される
RBTN = None       # タイトル画面のRANKINGボタンの位置 (x, y, w, h)。タイトル画面のときだけ値が入る
TBTN = None       # タイトル画面の「あそびかた」ボタンの位置 (x, y, w, h)。タイトル画面のときだけ値が入る

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
beam_count = 1    # 直前に同時に発射したビームの数（得点の倍率に使う。白の消去が終わると1に戻る）
popup_beams = 1   # ポップアップに表示する、同時に発射したビームの数
demo = False      # デモプレイ中か（タイトル画面の背景で、盤面が自動で動いている間）
demo_target = None  # デモプレイが、次に照射するマス (x, y)。まだ決めていなければNone
demo_wait = 0     # 照射までの残りフレーム数
demo_row = 0      # 手を考えている途中の、次に調べる行
demo_best = -1    # これまでに調べた中で、いちばんよかった手の評価値
demo_cands = []   # いちばんよかった手の候補 [(x, y), ...]
tut = False       # チュートリアル中か
tut_step = 0      # チュートリアルの何番目の手順か（0始まり）
tut_phase = "aim" # 手順の進み具合："aim"（照射待ち）/ "sweep" / "drop" / "line" / "laser" / "done"
tut_target = (3, 9)   # チュートリアルで、タップしてほしいマス (x, y)
tut_hint = 0      # 「光っているマスを…」の案内を出す残りフレーム数
tut_tick = 0      # 点滅用のカウンタ
tut_base = 0      # 手順を始めたときのスコア（やりなおしで戻す）
TCLOSE = None     # チュートリアルの「とじる」ボタンの位置 (x, y, w, h)
TNEXT = None      # 「つぎへ」ボタン（手順を終えたときだけ値が入る）
TRETRY = None     # 「もう一度」ボタン（同上）
popup_gain = 0    # ポップアップに表示する、獲得した得点（ビームで消えた分＋続けて白になって消えた分）
pop_open = False  # ビームの発射から、続く白の消去までの間か（この間の得点は、同じポップアップにまとめる）

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
show_rules = (W >= H) if RULES_DEFAULT_OPEN is None else bool(RULES_DEFAULT_OPEN)

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

def stop_demo():
    # デモプレイをやめる（盤面はそのまま。次にタイトルへ戻ったとき、また最初から流す）
    global demo, demo_target, demo_row, lasers, combo_timer, beam_count, pop_open
    demo = False
    demo_target = None
    demo_row = 0
    lasers = []
    combo_timer = 0
    beam_count = 1
    pop_open = False

def toggle_rules():
    global show_rules
    show_rules = not show_rules

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
    if hit_rect(e, MBTN):
        toggle_mute()
        return
    if hit_rect(e, HBTN):
        toggle_rules()
        return
    if hit_rect(e, PBTN):
        if index != 8:  # 名前の入力中は、切り替えない
            cycle_palette()
        return
    if hit_button(e):
        if index != 8:  # 名前の入力中は、モードを切り替えない
            switch_mode()
        return
    if tut:
        # チュートリアル中のボタン（とじる・やりなおす・つぎへ）
        if hit_rect(e, TCLOSE):
            tut_close()
            return
        if hit_rect(e, TNEXT):
            tut_next()
            return
        if hit_rect(e, TRETRY):
            tut_setup(tut_step, True)
            return
    if TUTORIAL_ENABLED and (index == 0 or index == 1 or demo) and hit_rect(e, TBTN):
        tut_start()
        return
    if (index == 0 or index == 1 or demo) and hit_rect(e, RBTN):
        stop_demo()
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

def beam_mult(n=None):
    # 同時に発射したビームの数に応じた得点倍率（nを省略すると、直前の発射の本数）
    if n is None:
        n = beam_count
    return 1.0 + MULTI_BEAM_STEP * (max(n, 1) - 1)

def add_score(points, with_beams=True):
    # コンボと同時発射の倍率をかけて得点を加算する。加算した得点を返す
    global score, high_score
    m = combo_mult()
    if with_beams:
        m = m * beam_mult()
    gained = int(round(points * m))
    score += gained
    if score > high_score and not demo and not tut:   # デモプレイ・チュートリアルの得点は、ハイスコアにしない
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
    # 盤面中央のポップアップ：半透明の黒い箱に白文字と白枠。下の盤面が透けて見える
    # 1行目＝獲得した得点「+N」（いちばん大きく）、続けて、小さめに「N COMBO! ×倍率」「N BEAMS! ×倍率」（該当するものだけ）
    T = TILE_SIZE
    subs = []
    if combo >= 2:
        subs.append(f"{combo} COMBO!  ×{combo_mult():.1f}")
    if popup_beams >= 2:
        subs.append(f"{popup_beams} BEAMS!  ×{beam_mult(popup_beams):.1f}")
    main = f"+{popup_gain}"
    big = max(combo, popup_beams)
    k = max(1.0, min(1.0 + 0.08 * (big - 2), 1.4))   # 倍率が大きいほど少し大きく（上限あり）
    s_main = T * 0.9 * k
    s_sub = T * 0.5 * k
    max_w = BW - T * 0.4    # 箱（文字＋左右の余白）の最大の幅
    context.font = f"bold {s_main}px {FONT}"
    tw = context.measureText(main).width
    context.font = f"bold {s_sub}px {FONT}"
    for ln in subs:
        tw = max(tw, context.measureText(ln).width)
    if tw + 0.9 * s_main > max_w:    # 余白（左右で s_main の0.9倍）を含めて、幅に収まらなければ縮める
        f = max_w / (tw + 0.9 * s_main)
        s_main = s_main * f
        s_sub = s_sub * f
        tw = tw * f
    pad = s_main * 0.45
    content_h = s_main * 1.15
    if len(subs) > 0:
        content_h += s_sub * 1.3 * len(subs) - s_sub * 0.3
    bw = tw + 2 * pad
    bh = content_h + 2 * pad
    cx = BX + BW / 2
    cy = BY + BH / 2
    bx = cx - bw / 2
    by = cy - bh / 2

    context.globalAlpha = COMBO_POPUP_ALPHA
    context.fillStyle = POPUP_BG
    context.fillRect(bx, by, bw, bh)
    context.globalAlpha = 1.0

    context.strokeStyle = T_STRONG
    context.lineWidth = max(2, min(5, big))
    context.strokeRect(bx, by, bw, bh)

    context.textAlign = "center"
    context.fillStyle = T_STRONG
    y = by + pad
    context.font = f"bold {s_main}px {FONT}"
    context.fillText(main, cx, y + s_main * 0.85)
    y += s_main * 1.15
    context.font = f"bold {s_sub}px {FONT}"
    for ln in subs:
        context.fillText(ln, cx, y + s_sub * 0.85)
        y += s_sub * 1.3
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
    for para in txt.split("\n"):   # 文中の改行（\n）は、そのまま改行する
        cur = ""
        for ch in para:
            if cur != "" and context.measureText(cur + ch).width > max_w:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        if cur != "":
            lines.append(cur)
    wrap_cache[key] = lines
    return lines

def draw_mark(kind, cx, cy, r):
    # 印を1つ描く（0=●, 1=■, 2=▲）。黒い図形を白で縁取る
    for k in range(2):
        if k == 0:
            context.strokeStyle = MARK_EDGE
            context.lineWidth = max(2.0, r * 0.7)
        else:
            context.fillStyle = MARK_COLOR
        context.beginPath()
        if kind == 0:
            context.arc(cx, cy, r, 0, TAU)
        elif kind == 1:
            context.rect(cx - r * 0.9, cy - r * 0.9, r * 1.8, r * 1.8)
        else:
            context.moveTo(cx, cy - r * 1.1)
            context.lineTo(cx + r * 1.05, cy + r * 0.8)
            context.lineTo(cx - r * 1.05, cy + r * 0.8)
            context.closePath()
        if k == 0:
            context.stroke()
        else:
            context.fill()

def draw_marks(c, x, y, s, big=False):
    # ブロック（左上x,y・一辺s）に、含まれる三原色の印を並べる（色覚配慮テーマ用）。お邪魔ブロックには何も描かない
    if not MARKS or c == NUISANCE or c not in COLOR:
        return
    present = []
    for i in range(3):
        if mix(c, PRIMARY[i]) == c:
            present.append(i)
    n = len(present)
    r = s * (0.16 if big else 0.11)       # NEXTの欄など、小さい見本では、印を大きくする
    step = s * (0.31 if big else 0.28)
    cx0 = x + s / 2 - step * (n - 1) / 2
    cy = y + s / 2
    for j in range(n):
        draw_mark(present[j], cx0 + step * j, cy, r)

def draw_swatch(x, y, s, c):
    context.fillStyle = COLOR[c]
    context.fillRect(x, y, s, s)
    context.strokeStyle = SWATCH_EDGE
    context.lineWidth = 1
    context.strokeRect(x + 0.5, y + 0.5, s - 1, s - 1)
    draw_marks(c, x, y, s, True)

def ui_font():
    # パネルの基準フォントサイズ。画面の短辺に比例させる（大画面でも文字が大きくなりすぎないよう上限あり）
    return max(12, min(20, int(min(W, H) * 0.03)))

# ---------- 描画：背景とパネル ----------
def draw_bg():
    global BTN, MBTN, HBTN, PBTN
    BTN = None
    MBTN = None
    HBTN = None
    PBTN = None
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

def draw_status_c(p, y, pad, F=None):
    # 4行に詰めたスコア表示（高さが足りないとき用）。Fは文字の大きさ（Noneなら基準フォント）
    if F is None:
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
    # 空き高さに合わせて、スコア表示の形式を切り替える。3行形式でも入らないときは、文字を小さくして収める（ボタンと重ならないように）
    F = ui_font()
    if y + F * 10.4 <= bottom:
        return draw_status_v(p, y, pad)
    need = F * 5.3
    if y + need <= bottom:
        return draw_status_c(p, y, pad)
    F2 = max(8.0, (bottom - y) / 5.3)
    return draw_status_c(p, y, pad, F2)

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

def section_gap(tight=False):
    # 区切り線の前後を含めた、コンテンツどうしの間隔（空きが足りないときは、狭いほうを使う）
    return ui_font() * (0.4 if tight else 1.5)

def draw_divider(p, y, pad):
    # コンテンツを分ける区切り線。パネルの枠線と同じ色で、パネルの幅より少し短く、中央に描く
    inset = pad * 1.5
    ly = int(y) + 0.5
    context.strokeStyle = PANEL_BORDER
    context.lineWidth = 1
    context.beginPath()
    context.moveTo(p["x"] + inset, ly)
    context.lineTo(p["x"] + p["w"] - inset, ly)
    context.stroke()

def draw_rules(p, y, bottom, pad, divider=True):
    # ルール説明。空き領域に収まる項目だけを、上から順に表示する
    F = ui_font()
    y0 = y
    fr = max(11, int(F * 0.9))
    lh = fr * 1.5
    x = p["x"] + pad
    indent = fr * 1.0
    max_w = p["w"] - 2 * pad - indent
    if max_w < fr * 4:
        return y0
    heading_h = F * 1.3
    items = [wrap_text(t, max_w, fr) for t in rule_texts()]
    if divider:
        gap = section_gap()
        total = heading_h
        for lines in items:
            total += len(lines) * lh + fr * 0.4
        if y + gap + total > bottom:
            gap = section_gap(True)       # 全項目が入らないときは、間隔を狭くして項目を優先する
        y = y + gap
    if y + heading_h + len(items[0]) * lh > bottom:
        return y0
    if divider:
        draw_divider(p, y0 + gap * 0.5, pad)
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

def draw_rules_hint(p, y, pad):
    # ルール説明を隠しているとき、右パネルが空にならないよう、見方を1行だけ表示する
    F = ui_font()
    fr = max(11, int(F * 0.9))
    max_w = p["w"] - 2 * pad
    if max_w < fr * 4:
        return
    put("ルール", p["x"] + pad, y, F * 0.8, TEXT_SUB)
    y += F * 1.3
    for ln in wrap_text("下の虫眼鏡ボタンを押すと、ルールが表示されます", max_w, fr):
        put(ln, p["x"] + pad, y, fr, TEXT_SUB, False)
        y += fr * 1.5

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

TAU = 6.283185307

def venn_circle(x, y, r):
    context.beginPath()
    context.arc(x, y, r, 0, TAU)

def draw_legend(p, y, bottom, pad, divider=True):
    # 混色の凡例。3つの円を重ねて、重なった部分に混色の結果を表示する（色はゲームのブロックと同じ）
    # ダークモード＝上・左下・右下の順にR・G・B、ライトモード＝同じ順にC・M・Y。中央（3色の重なり）は消える色
    F = ui_font()
    y0 = y
    title_h = F * 1.3
    avail_w = p["w"] - 2 * pad
    gap = section_gap() if divider else 0
    y = y0 + gap
    r = min(avail_w / 3.0, (bottom - y - title_h) / 2.87, F * 2.4)   # 円の半径。全体の幅は3r、高さは約2.87r
    if r < F * 1.1 and divider:
        gap = section_gap(True)           # 入らないときは、間隔を狭くして凡例を優先する
        y = y0 + gap
        r = min(avail_w / 3.0, (bottom - y - title_h) / 2.87, F * 2.4)
    if r < F * 1.1:
        return y0
    if divider:
        draw_divider(p, y0 + gap * 0.5, pad)
    put("混色", p["x"] + pad, y, F * 0.8, TEXT_SUB)
    y += title_h
    L = r                                            # 円の中心どうしの距離
    cx = p["x"] + p["w"] / 2
    ax = cx                                          # 1つ目（上）
    ay = y + r
    bx = cx - L / 2                                  # 2つ目（左下）
    by = ay + L * 0.866
    cxx = cx + L / 2                                 # 3つ目（右下）
    cyy = by
    A = PRIMARY[0]
    B = PRIMARY[1]
    C = PRIMARY[2]
    # 1) 3つの円を、それぞれの色で塗る
    for (x0, y0_, c) in ((ax, ay, A), (bx, by, B), (cxx, cyy, C)):
        context.fillStyle = COLOR[c]
        venn_circle(x0, y0_, r)
        context.fill()
    # 2) 2つの円が重なる部分を、混色の結果の色で塗る（円の内側にクリップして、もう1つの円を塗る）
    for (x1, y1, x2, y2, c) in ((ax, ay, bx, by, mix(A, B)), (bx, by, cxx, cyy, mix(B, C)), (cxx, cyy, ax, ay, mix(C, A))):
        context.save()
        venn_circle(x1, y1, r)
        context.clip()
        context.fillStyle = COLOR[c]
        venn_circle(x2, y2, r)
        context.fill()
        context.restore()
    # 3) 3つの円が重なる中央を塗る
    context.save()
    venn_circle(ax, ay, r)
    context.clip()
    venn_circle(bx, by, r)
    context.clip()
    context.fillStyle = COLOR[mix(mix(A, B), C)]
    venn_circle(cxx, cyy, r)
    context.fill()
    context.restore()
    # 4) 円の輪郭
    context.strokeStyle = SWATCH_EDGE
    context.lineWidth = 1
    for (x0, y0_) in ((ax, ay), (bx, by), (cxx, cyy)):
        venn_circle(x0, y0_, r)
        context.stroke()
    return cyy + r

def badge_rect():
    # バッジを避けるための領域 (x, y)。この点から画面の右下端までが、使えない領域
    if not BADGE_AVOID:
        return None
    return (W - BADGE_W - BADGE_GAP, H - BADGE_H - BADGE_GAP)

def avoid_badge(p, bottom):
    # パネルの右下がバッジと重なるとき、内容の下端を、バッジの上端より上に制限する
    r = badge_rect()
    if r is not None and p["x"] + p["w"] > r[0] and p["y"] + p["h"] > r[1]:
        return min(bottom, r[1] - 2)
    return bottom

def button_metrics():
    # ボタンの高さ、ボタン間の隙間、アイコンのボタン全体の幅、モード切替ボタンの最小の幅
    F = ui_font()
    bh = max(28, int(F * 2.0))
    gap = max(6, int(F * 0.5))
    has_sound = SE_ENABLED or BGM_ENABLED
    icons_w = (bh + gap) * (3 if has_sound else 2)   # アイコンのボタン：ミュート・ルール・配色
    min_w = F * 6.8 + 12
    return bh, gap, icons_w, min_w

def rules_min_h(p, pad):
    # ルール説明の見出しと、最初の1項目が入るのに必要な高さ
    F = ui_font()
    fr = max(11, int(F * 0.9))
    lh = fr * 1.5
    indent = fr * 1.0
    max_w = p["w"] - 2 * pad - indent
    if max_w < fr * 4:
        return 0
    first = wrap_text(rule_texts()[0], max_w, fr)
    return section_gap(True) + F * 1.3 + len(first) * lh + fr * 0.4

def draw_legend_rules(p, y, bottom, pad, divider_first):
    # 混色の凡例 → ルール説明の順に描く（優先度は、凡例のほうが上）。
    # ルールを開いているときは、最初の1項目が入る高さだけ、ルールのために残す（開いたのに何も出ない、を防ぐ）
    lb = bottom
    if show_rules:
        lb = bottom - rules_min_h(p, pad)
    y2 = draw_legend(p, y, lb, pad, divider_first)
    if show_rules:
        draw_rules(p, y2, bottom, pad, divider_first or y2 > y)

def draw_mode_button(p, pad, bottom):
    # パネル下部に、モード切替ボタンと、アイコンのボタン（ミュート・ルール表示）を描く。いちばん上のボタンの上端より上を、内容の表示領域として返す
    # ボタンが1行に並ばないほど狭いときは、アイコンのボタンを、モード切替ボタンの上の段に置く
    global BTN
    F = ui_font()
    bh, gap, icons_w, min_w = button_metrics()
    has_sound = SE_ENABLED or BGM_ENABLED
    r = badge_rect()
    bx = p["x"] + pad
    by = p["y"] + p["h"] - pad - bh
    full = p["w"] - 2 * pad

    def hits(x_right, y_top):
        # その横幅・高さのボタンが、バッジの領域と重なるか
        return r is not None and x_right > r[0] and y_top + bh > r[1]

    # 1行に並べる場合
    bw = min(full - icons_w, int(F * 14))
    one_row = bw >= min_w
    if one_row and hits(bx + bw + icons_w, by):
        bw = min(bw, int(r[0] - bx - icons_w))        # バッジを避けて、モード切替ボタンを細くする
        one_row = bw >= min_w
    if one_row:
        iy = by
        ix = bx + bw + gap
        top = by
    else:
        # 2段に並べる場合（下の段：モード切替ボタン、上の段：アイコンのボタン）
        bw = min(full, int(F * 14))
        if hits(bx + bw, by):
            room = int(r[0] - bx)
            if room >= min_w:
                bw = room
            else:
                by = r[1] - bh                         # 細くできないときは、バッジの上に持ち上げる
        iy = by - bh - gap
        if hits(bx + icons_w - gap, iy):
            iy = min(iy, r[1] - bh)
        ix = bx
        top = iy
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
    if has_sound:
        draw_mute_button(ix, iy, bh)
        ix += bh + gap
    draw_help_button(ix, iy, bh)
    ix += bh + gap
    draw_palette_button(ix, iy, bh)
    return top - pad * 0.5

def draw_help_button(x, y, s):
    # 虫眼鏡のアイコン。ルール説明の表示・非表示を切り替える。表示中は、白黒を反転する
    global HBTN
    HBTN = (x, y, s, s)
    fg = T_STRONG
    bg = BG_COLOR
    if show_rules:
        fg, bg = BG_COLOR, T_STRONG
    context.fillStyle = bg
    context.fillRect(x, y, s, s)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(x + 1, y + 1, s - 2, s - 2)
    u = s * 0.5 * 0.85
    lw = max(2, u * 0.2)
    # レンズ（左上）と持ち手（右下）。図形全体の中心が、ボタンの中心に来るようにずらす
    cx = x + s / 2 + 0.04 * u
    cy = y + s / 2 + 0.04 * u
    lx = cx - 0.2 * u
    ly = cy - 0.2 * u
    context.strokeStyle = fg
    context.lineWidth = lw
    context.lineCap = "round"
    context.beginPath()
    context.arc(lx, ly, 0.5 * u, 0, TAU)
    context.stroke()
    context.beginPath()
    context.moveTo(lx + 0.5 * u * 0.7071 + lw * 0.2, ly + 0.5 * u * 0.7071 + lw * 0.2)
    context.lineTo(cx + 0.62 * u, cy + 0.62 * u)
    context.stroke()
    context.lineCap = "butt"

def draw_palette_button(x, y, s):
    # 配色切替のアイコン。今の配色の三原色を、3つの丸で見せる。押すたびに 標準 → やさしい → 色覚配慮 の順に切り替わる
    global PBTN
    PBTN = (x, y, s, s)
    context.fillStyle = BG_COLOR
    context.fillRect(x, y, s, s)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(x + 1, y + 1, s - 2, s - 2)
    r = s * 0.17
    cx = x + s / 2
    cy = y + s / 2
    pts = [(cx, cy - r * 0.95), (cx - r * 1.05, cy + r * 0.85), (cx + r * 1.05, cy + r * 0.85)]
    for i in range(3):
        context.fillStyle = COLOR[PRIMARY[i]]
        context.beginPath()
        context.arc(pts[i][0], pts[i][1], r, 0, TAU)
        context.fill()
        context.strokeStyle = SWATCH_EDGE
        context.lineWidth = 1
        context.stroke()

def draw_mute_button(x, y, s):
    # スピーカーのアイコン。音が出る状態は音波つき、ミュート中は×印つき
    # 左の余白（スピーカーの左端〜枠）と右の余白（音波・×印の右端〜枠）が同じ幅になるよう、図形全体を横に中央寄せする
    global MBTN
    MBTN = (x, y, s, s)
    context.fillStyle = BG_COLOR
    context.fillRect(x, y, s, s)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(x + 1, y + 1, s - 2, s - 2)
    u = s * 0.5 * 0.85           # 図形の大きさの単位（枠から少し離すため、枠の半分より小さくする）
    lw = max(2, u * 0.16)        # 線の太さ
    left = -0.55 * u             # スピーカーの左端（中心cxからの距離）
    right = 0.88 * u + lw / 2    # 音波・×印の右端（どちらの状態でも同じ位置にして、スピーカーが動かないようにする）
    cx = x + (s - (right - left)) / 2 - left
    cy = y + s / 2
    context.fillStyle = T_STRONG
    context.beginPath()
    context.moveTo(cx - 0.55 * u, cy - 0.22 * u)
    context.lineTo(cx - 0.25 * u, cy - 0.22 * u)
    context.lineTo(cx + 0.1 * u, cy - 0.5 * u)
    context.lineTo(cx + 0.1 * u, cy + 0.5 * u)
    context.lineTo(cx - 0.25 * u, cy + 0.22 * u)
    context.lineTo(cx - 0.55 * u, cy + 0.22 * u)
    context.closePath()
    context.fill()
    context.lineWidth = lw
    context.lineCap = "round"
    if muted:
        context.beginPath()
        context.moveTo(cx + 0.40 * u, cy - 0.24 * u)
        context.lineTo(cx + 0.88 * u, cy + 0.24 * u)
        context.moveTo(cx + 0.88 * u, cy - 0.24 * u)
        context.lineTo(cx + 0.40 * u, cy + 0.24 * u)
        context.stroke()
    else:
        context.beginPath()
        context.arc(cx + 0.1 * u, cy, 0.42 * u, -0.7, 0.7)
        context.stroke()
        context.beginPath()
        context.arc(cx + 0.1 * u, cy, 0.78 * u, -0.7, 0.7)
        context.stroke()
    context.lineCap = "butt"

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
    if kind != "all" or w < 520:
        bottom = avoid_badge(p, bottom)
    if kind == "status":
        cy = draw_status(p, cy, bottom, pad)
        draw_legend(p, cy, bottom, pad)
    elif kind == "rules":
        if show_rules:
            draw_rules(p, cy, bottom, pad, False)
        else:
            draw_rules_hint(p, cy, pad)
    elif w >= 520:
        # パネルが横に広いときは2列にする（左：スコアとボタン、右：凡例とルール）
        left_w = int(w * 0.36)
        # ボタンが1行に並ぶ幅まで、左列を広げる（右列が狭くなりすぎない範囲で）
        need_w = int(2 * pad + button_metrics()[3] + button_metrics()[2]) + 3
        if need_w > left_w and w - need_w >= w * 0.4:
            left_w = need_w
        pl = {"x": x, "y": y, "w": left_w, "h": h}
        pr = {"x": x + left_w, "y": y, "w": w - left_w, "h": h}
        # 2列のときは、ボタンを左列（スコア側）に置き、ルール側の高さを減らさない
        bottom_l = draw_mode_button(pl, pad, bottom)
        draw_status(pl, cy, bottom_l, pad)
        bottom_r = avoid_badge(pr, bottom)
        draw_legend_rules(pr, cy, bottom_r, pad, False)
    else:
        cy = draw_status_h(p, cy, pad)
        draw_legend_rules(p, cy, bottom, pad, True)

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
                else:
                    draw_marks(masu[y][x], BX + x * T, BY + y * T, T)

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
se_keep = []         # JSから呼ばれる関数は保持しておく
master = None        # 全体の音量を調整するGainNode（BGMも効果音も、ここを通す。ミュートで0にする）
muted = False        # Trueなら、ミュート中
bgm_src = None       # 再生中のBGM（AudioBufferSourceNode）。Noneなら、まだ鳴らしていない（保持しないと呼ばれる前に消えることがある）

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
        if key == "bgm":
            start_bgm()
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
    if BGM_ENABLED:
        se_pending += 1
    for i in range(len(SE_FILES)):
        load_one(i, SE_FILES[i])
    load_one("base", SE_URL)
    if BGM_ENABLED:
        load_one("bgm", BGM_URL)

def load_mute():
    try:
        return js.localStorage.getItem(MUTE_KEY) == "1"
    except Exception:
        return False

def apply_mute():
    # ミュート中は全体の音量を0にする（BGMは止めずに無音にするので、解除すると続きから聞こえる）
    if master is not None:
        master.gain.value = 0.0 if muted else 1.0

def toggle_mute():
    global muted
    muted = not muted
    apply_mute()
    try:
        js.localStorage.setItem(MUTE_KEY, "1" if muted else "0")
    except Exception:
        pass

muted = load_mute()

def start_bgm():
    # BGMをループ再生で鳴らし始める（すでに鳴っているときは何もしない）
    global bgm_src
    if not BGM_ENABLED or bgm_src is not None or audio_ctx is None:
        return
    buf = se_buffers.get("bgm")
    if buf is None:
        return
    try:
        src = audio_ctx.createBufferSource()
        src.buffer = buf
        src.loop = True  # 途切れずに繰り返す
        if BGM_LOOP_END > 0:
            src.loopStart = BGM_LOOP_START
            src.loopEnd = BGM_LOOP_END
        elif BGM_LOOP_START > 0:
            src.loopStart = BGM_LOOP_START
        gain = audio_ctx.createGain()
        gain.gain.value = BGM_VOLUME
        src.connect(gain)
        gain.connect(master)
        src.start()
        bgm_src = src
    except Exception as e:
        se_log("BGMの再生に失敗: " + str(e))

def on_visibility(e):
    # 別のタブやアプリに切り替えている間は、BGMも効果音も止める（戻ると再開）
    if audio_ctx is None:
        return
    try:
        if js.document.hidden:
            audio_ctx.suspend()
        else:
            audio_ctx.resume()
    except Exception:
        pass

js.document.addEventListener("visibilitychange", create_proxy(on_visibility))

def init_audio():
    # ユーザー操作の中で呼ぶ（スマホなどは、操作の中で初期化しないと音が出ない）
    global audio_ctx, se_loading, master
    if not SE_ENABLED and not BGM_ENABLED:
        return
    try:
        if audio_ctx is None:
            audio_ctx = js.AudioContext.new()
            master = audio_ctx.createGain()
            master.connect(audio_ctx.destination)
            apply_mute()
        if audio_ctx.state == "suspended":
            audio_ctx.resume()
        if not se_loading:
            se_loading = True
            load_se()
        start_bgm()  # 読み込み済みなら、ここで鳴らし始める（読み込み中なら、完了時に鳴らす）
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
        gain.connect(master)
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
    globals().update(PALETTES[mode][palette])    # 配色テーマの差分を重ねる（色の表・背景・文字の色・印の有無）
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

def load_palette():
    try:
        v = int(js.localStorage.getItem(PALETTE_KEY))
        if 0 <= v < len(PALETTE_NAMES):
            return v
    except Exception:
        pass
    return 0

def save_palette():
    try:
        js.localStorage.setItem(PALETTE_KEY, str(palette))
    except Exception:
        pass

def cycle_palette():
    # 配色テーマを切り替える（ゲームは、そのまま続ける。盤面もスコアも変えない）
    global palette, pal_toast
    hi_scores[MODE] = high_score      # apply_modeはハイスコアを読み直すので、先に保存しておく
    palette = (palette + 1) % len(PALETTE_NAMES)
    apply_mode(MODE)
    save_palette()
    if name_box is not None and index == 8:
        style_name_ui()
    pal_toast = PAL_TOAST_FRAMES

def draw_pal_toast():
    # 配色を切り替えた直後に、テーマの名前を盤面の下のほうに表示する
    global pal_toast
    if pal_toast > 0:
        pal_toast -= 1
        T = TILE_SIZE
        txt = "配色：" + PALETTE_NAMES[palette]
        fs = T * 0.45
        context.font = f"bold {fs}px {FONT}"
        tw = context.measureText(txt).width
        if tw > BW - T * 1.2:
            fs = fs * (BW - T * 1.2) / tw
            tw = BW - T * 1.2
        pad = fs * 0.5
        bw = tw + 2 * pad
        bh = fs + 2 * pad
        bx = BX + (BW - bw) / 2
        by = BY + BH - T * 0.35 - fs - pad * 0.7
        context.globalAlpha = COMBO_POPUP_ALPHA     # 盤面のブロックが透けて見える、半透明の背景
        context.fillStyle = POPUP_BG
        context.fillRect(bx, by, bw, bh)
        context.globalAlpha = 1.0
        context.strokeStyle = T_STRONG
        context.lineWidth = 2
        context.strokeRect(bx, by, bw, bh)
        draw_txt_c(txt, BX + BW / 2, by + pad + fs * 0.85, fs, T_STRONG, BW - T * 1.2)

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
    # プレイ中（ゲームオーバーの表示中を含む）に切り替えたときは、そこまでのスコアがランキングに入るか判定し、
    # 入るなら、スコアを残したまま名前の入力へ進む（ランキングはモードを区別しないので、そのまま登録できる）
    global index, score, combo, combo_timer, lasers, timer, tsugi, mouse_c, pressed, show_cursor, beam_count, pop_open, tut
    tut = False   # チュートリアル中なら終える（得点は記録しない）
    entry = (not demo) and index in (2, 3, 4, 5, 6, 7) and score > 0 and rank_qualifies(score)
    hi_scores[MODE] = high_score
    apply_mode("light" if MODE == "dark" else "dark")
    save_mode()
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = EMPTY
    stop_demo()   # デモプレイ中なら終える（タイトルに戻ると、また最初から流す）
    index = 0
    if not entry:
        score = 0
    combo = 0
    combo_timer = 0
    beam_count = 1
    pop_open = False
    lasers = []
    timer = 0
    tsugi = 0
    mouse_c = 0
    pressed = False
    show_cursor = False
    hide_name_ui()
    if entry:
        start_name_entry()

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

def draw_menu_button(label, top):
    # タイトル画面のボタン（RANKING・あそびかた）。top は盤面の上端からの位置（マス単位）。戻り値は (x, y, w, h)
    T = TILE_SIZE
    bw = min(T * 4.4, BW - T * 0.6)
    bh = T * 0.95
    bx = BX + (BW - bw) / 2
    by = BY + T * top
    context.fillStyle = POPUP_BG
    context.fillRect(bx, by, bw, bh)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(bx + 1, by + 1, bw - 2, bh - 2)
    fs = T * 0.5
    context.font = f"bold {fs}px {FONT}"
    tw = context.measureText(label).width
    if tw > bw - T * 0.3:
        fs = fs * (bw - T * 0.3) / tw
        context.font = f"bold {fs}px {FONT}"
    context.textAlign = "center"
    context.fillStyle = T_STRONG
    context.fillText(label, bx + bw / 2, by + bh / 2 + fs * 0.36)
    context.textAlign = "left"
    return (bx, by, bw, bh)

def draw_rank_button():
    # タイトル画面のRANKINGボタンと、その下の「あそびかた」ボタン
    global RBTN, TBTN
    if TUTORIAL_ENABLED:
        RBTN = draw_menu_button("RANKING", 6.9)
        TBTN = draw_menu_button("あそびかた", 8.1)
    else:
        RBTN = draw_menu_button("RANKING", 7.4)
        TBTN = None

# ---------- デモプレイ（タイトル画面の背景で、自動で遊ぶ） ----------
def draw_title_overlay():
    # タイトルの文字とRANKINGボタン
    T = TILE_SIZE
    start_txt = "Tap to Start" if input_type == "touch" else "Click to Start"
    draw_txt_c("Color Puzzle", BX + BW / 2, BY + T * 3, T * 0.95, T_STRONG, BW - T * 0.6)
    draw_txt_c(start_txt, BX + BW / 2, BY + T * 6, T * 0.5, T_STRONG, BW - T * 0.6)
    draw_rank_button()

def draw_demo_dim():
    # デモプレイの盤面を暗くして、タイトルの文字を読みやすくする
    context.globalAlpha = DEMO_DIM
    context.fillStyle = POPUP_BG
    context.fillRect(BX, BY, BW, BH)
    context.globalAlpha = 1.0

def demo_init():
    # デモプレイを最初から始める（盤面をまっさらにして、ゲーム開始と同じ状態にする）
    global demo, demo_target, demo_row, index, score, combo, combo_timer, beam_count, pop_open, lasers, tsugi, timer, mouse_c
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = EMPTY
    demo = True
    demo_target = None
    demo_row = 0
    score = 0
    combo = 0
    combo_timer = 0
    beam_count = 1
    pop_open = False
    lasers = []
    timer = 0
    mouse_c = 0
    tsugi = random.choice(PRIMARY)
    set_block(START_NUM)
    index = 2

def demo_eval_row(cy):
    # デモプレイの手の候補を調べる（1行分）：ブロックのある場所に3x3の照射を試して、同じ色の3つ並びがいちばん多くできるマスを探す
    global demo_best, demo_cands
    for cx in range(COL):
        near = False
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                y = cy + dy
                x = cx + dx
                if 0 <= y < ROW and 0 <= x < COL and masu[y][x] != EMPTY:
                    near = True
        if not near:
            continue
        # 照射する範囲だけ保存して、試したあとに戻す
        saved = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                y = cy + dy
                x = cx + dx
                if 0 <= y < ROW and 0 <= x < COL:
                    saved.append((y, x, masu[y][x]))
        irradiate(cx, cy, tsugi)
        cells = set()
        for run, ldy, ldx, n in find_lines():
            for c in run:
                cells.add(c)
        white = 0
        pairs = 0
        for y in range(ROW):
            for x in range(COL):
                v = masu[y][x]
                if v == CLEAR:
                    white += 1
                if v != EMPTY and v != NUISANCE and v != CLEAR:
                    if x + 1 < COL and masu[y][x + 1] == v:
                        pairs += 1
                    if y + 1 < ROW and masu[y + 1][x] == v:
                        pairs += 1
        for (y, x, v) in saved:
            masu[y][x] = v
        val = len(cells) * 10 + white * 4 + pairs
        if val > demo_best:
            demo_best = val
            demo_cands = [(cx, cy)]
        elif val == demo_best:
            demo_cands.append((cx, cy))

def demo_step():
    # デモプレイの操作フェーズ：数フレームかけて手を考え（重い計算を分けて、動きが止まらないようにする）、照射する範囲を少し見せてから撃つ
    global index, combo, demo_target, demo_wait, cursor_x, cursor_y, demo_row, demo_best, demo_cands
    if demo_target is None:
        if demo_row == 0:
            demo_best = -1
            demo_cands = []
        end = min(ROW, demo_row + DEMO_THINK_ROWS)
        for cy in range(demo_row, end):
            demo_eval_row(cy)
        demo_row = end
        if demo_row < ROW:
            return
        demo_row = 0
        if len(demo_cands) == 0:
            demo_target = (random.choice(range(COL)), random.choice(range(ROW)))
        else:
            demo_target = random.choice(demo_cands)
        demo_wait = DEMO_AIM_FRAMES
    tx = demo_target[0]
    ty = demo_target[1]
    if tsugi in COLOR:
        sx = cursor_x
        sy = cursor_y
        cursor_x = tx          # 予告表示は、実際のカーソル位置を使うので、いったん差し替えて戻す
        cursor_y = ty
        draw_area_preview()
        cursor_x = sx
        cursor_y = sy
    demo_wait -= 1
    if demo_wait <= 0:
        combo = 0
        irradiate(tx, ty, tsugi)
        set_block(SPAWN_NUM)
        demo_target = None
        index = 3

def demo_to_game():
    # デモプレイ中にクリックされたとき：デモを終えて、ゲームを始める
    global index, score, combo, combo_timer, beam_count, pop_open, tsugi, mouse_c
    stop_demo()
    mouse_c = 0
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = EMPTY
    score = 0
    combo = 0
    combo_timer = 0
    beam_count = 1
    pop_open = False
    tsugi = random.choice(PRIMARY)
    set_block(START_NUM)
    index = 2
    refresh_ranking()

# ---------- チュートリアル（タイトル画面の「あそびかた」から。決まった盤面を、案内に沿って操作する） ----------
TUT_STEPS = 5
TUT_TITLES = ["① 色を混ぜる", "② ビームを出す", "③ 白にして消す", "④ お邪魔ブロック", "⑤ 倍率でスコアUP"]
CNAME = {0b100: "赤", 0b010: "緑", 0b001: "青", 0b110: "黄", 0b101: "マゼンタ", 0b011: "シアン", 0b111: "白", 0b000: "黒"}

def tut_board(step):
    # 手順ごとの盤面。色は「役割」（PRIMARYの何番目か）で決めるので、ダークモードでもライトモードでも同じ流れになる
    # 戻り値: (NEXTの色, [(x, y, 色), ...], タップしてほしいマス(x, y))
    p0 = PRIMARY[0]
    p1 = PRIMARY[1]
    p2 = PRIMARY[2]
    s01 = mix(p0, p1)
    n = NUISANCE
    if step == 0:
        return p0, [(2, 9, p1), (3, 9, p2), (4, 9, p1), (3, 8, p1), (5, 9, p1)], (3, 9)
    if step == 1:
        return p0, [(2, 9, p1), (3, 9, p1), (4, 9, s01), (6, 9, p0)], (3, 9)
    if step == 2:
        return p2, [(2, 9, p0), (3, 9, s01), (4, 9, s01)], (3, 9)
    if step == 3:
        return p0, [(2, 9, n), (3, 9, n), (4, 9, n), (6, 9, n)], (3, 9)
    # 1回のタップで、3本同時のビームが3回続けて出て（3コンボ×同時3本）、最後に全部のブロックが消える盤面（探索で見つけた配置）
    # 文字は色の役割：N=お邪魔ブロック、A/B/C=三原色の1・2・3番目、D=A+B、E=A+C、F=B+C の混色
    # ブロックは5段目より下に置く（上の説明の箱と重ならないように）
    role = {"N": n, "A": p0, "B": p1, "C": p2, "D": s01, "E": mix(p0, p2), "F": mix(p1, p2)}
    rows = {
        5: "....NB..",
        6: "....AB..",
        7: ".DD.NDD.",
        8: ".DBANDB.",
        9: "BNANNANB",
    }
    blocks = []
    for y in rows:
        for x in range(COL):
            ch = rows[y][x]
            if ch != ".":
                blocks.append((x, y, role[ch]))
    return p0, blocks, (5, 8)

def tut_text(step, done):
    # 手順ごとの説明文（モードと操作方法に合わせて、色の名前や言い回しを変える）
    light = (MODE == "light")
    src = "インク" if light else "光"
    vte = "吹き付けて" if light else "照射して"          # 「〜を照射して、」の形
    vyo = "吹き付けよう" if light else "照射しよう"      # 「〜を照射しよう」の形
    vmi = "吹き付けてみよう" if light else "照射してみよう"
    p0 = CNAME[PRIMARY[0]]
    p1 = CNAME[PRIMARY[1]]
    p2 = CNAME[PRIMARY[2]]
    s01 = CNAME[mix(PRIMARY[0], PRIMARY[1])]
    y01 = "黄色" if s01 == "黄" else s01       # 「黄色のビーム」のように色の名前だけで言うとき用
    nu = CNAME[NUISANCE]
    clr = CNAME[CLEAR]
    tri = "シアン・マゼンタ・黄" if light else "赤・緑・青"
    act = "タップ" if input_type == "touch" else "クリック"
    ADJ = {"赤": "赤い", "青": "青い", "黄": "黄色い"}
    a0 = ADJ.get(p0, p0 + "の")     # 「赤い光」「シアンの光」のような言い方
    a2 = ADJ.get(p2, p2 + "の")
    if step == 0:
        if done:
            return f"{p1}ブロックに{p0}が混ざって、{s01}になった！\n3x3の範囲外のブロックは変わらない。"
        t = f"点滅しているマスを{act}して、まわりの3x3マスに{src}を{vyo}。\n{src}の色はNEXTで確認できる。"
        if input_type == "touch":
            t += "\n（長押しで照射範囲を確認できる）"
        return t
    if step == 1:
        if done:
            return f"3つ並んで{y01}のビームが発射！\n並んだブロックは消えて、軌道上の{p0}ブロックは{s01}に変色した。"
        return f"同じ色が3つ並ぶとビームが出る。\n{a0}{src}を{vte}、{s01}を3つ並べよう。"
    if step == 2:
        if done:
            return f"{s01}に{p2}が混ざったことで、{tri}がそろい、{clr}になって消えた！\n消えるとスコアが入る。"
        return f"{tri}の3色が混ざると{clr}になって消える。\n{a2}{src}を{vte}、{s01}を{clr}にしよう。"
    if step == 3:
        if done:
            return f"{nu}ブロックは{src}が当たるとその色になる。\nビームを当てることでも変色するため、うまく使おう。"
        return f"{nu}ブロックは3つ並んでもビームを出さない。\n{a0}{src}を{vmi}。"
    if done:
        b = 1.0 + MULTI_BEAM_STEP * 2
        c = 1.0 + COMBO_BONUS_STEP * 2
        return f"3コンボで×{c:.1f}、\n同時に3本で×{b:.1f}。\nそれぞれの倍率は重なるため、スコアが大きく増える！"
    return "高いスコアを目指すには倍率が重要だ。\n「コンボ」と「同時消し」を狙ってみよう。"

def tut_clear_board():
    global lasers, combo, combo_timer, beam_count, pop_open, timer, mouse_c, pressed, show_cursor
    for y in range(ROW):
        for x in range(COL):
            masu[y][x] = EMPTY
    lasers = []
    combo = 0
    combo_timer = 0
    beam_count = 1
    pop_open = False
    timer = 0
    mouse_c = 0

def tut_setup(step, retry=False):
    # 手順の盤面を用意する（retry=Trueなら、スコアも手順の開始時に戻す）
    global tut_step, tut_phase, tut_target, tut_hint, tsugi, score, tut_base
    tut_step = step
    tut_clear_board()
    if retry:
        score = tut_base
    else:
        tut_base = score
    col, blocks, tgt = tut_board(step)
    for (x, y, c) in blocks:
        masu[y][x] = c
    tsugi = col
    tut_target = tgt
    tut_phase = "aim"
    tut_hint = 0

def tut_start():
    # チュートリアルを始める（デモプレイは止める）
    global tut, score, tut_base, index, pressed, show_cursor
    stop_demo()
    tut = True
    score = 0
    tut_base = 0
    index = 0
    pressed = False
    show_cursor = False
    tut_setup(0)

def tut_close():
    # チュートリアルを終えて、タイトル画面に戻る（また、デモプレイが始まる）
    global tut, score, index, tsugi, pressed, show_cursor
    tut = False
    tut_clear_board()
    score = 0
    tsugi = 0
    index = 0
    pressed = False
    show_cursor = False

def tut_next():
    if tut_step >= TUT_STEPS - 1:
        tut_close()
    else:
        tut_setup(tut_step + 1)

def draw_tut_button(label, x, y, w, h):
    context.fillStyle = POPUP_BG
    context.fillRect(x, y, w, h)
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(x + 1, y + 1, w - 2, h - 2)
    fs = h * 0.5
    context.font = f"bold {fs}px {FONT}"
    tw = context.measureText(label).width
    if tw > w - 6:
        fs = fs * (w - 6) / tw
        context.font = f"bold {fs}px {FONT}"
    context.textAlign = "center"
    context.fillStyle = T_STRONG
    context.fillText(label, x + w / 2, y + h / 2 + fs * 0.36)
    context.textAlign = "left"
    return (x, y, w, h)

def draw_tut_ui():
    # 盤面の上側に、説明の箱とボタンを描く（ブロックは下の段に置いてあるので、隠れない）
    global TCLOSE, TNEXT, TRETRY
    T = TILE_SIZE
    bh = T * 4.6
    context.globalAlpha = 0.92
    context.fillStyle = POPUP_BG
    context.fillRect(BX, BY, BW, bh)
    context.globalAlpha = 1.0
    context.strokeStyle = T_STRONG
    context.lineWidth = 2
    context.strokeRect(BX + 1, BY + 1, BW - 2, bh - 2)
    x = BX + T * 0.35
    put(f"{tut_step + 1}/{TUT_STEPS}  {TUT_TITLES[tut_step]}", x, BY + T * 0.3, T * 0.42, T_STRONG)
    msg = tut_text(tut_step, tut_phase == "done")
    fs = T * 0.36
    lines = wrap_text(msg, BW - T * 0.7, fs)
    while len(lines) > 4 and fs > 8:
        fs = fs * 0.92
        lines = wrap_text(msg, BW - T * 0.7, fs)
    for i in range(len(lines)):
        put(lines[i], x, BY + T * 0.95 + i * fs * 1.3, fs, TEXT_MAIN, False)
    if tut_hint > 0 and tut_phase == "aim":
        tap = "タップ" if input_type == "touch" else "クリック"
        put(f"光っているマスを{tap}してね", x, BY + bh - T * 1.55, T * 0.36, T_STRONG)
    by = BY + bh - T * 0.95
    h = T * 0.7
    TCLOSE = draw_tut_button("とじる", x, by, T * 1.6, h)
    TNEXT = None
    TRETRY = None
    if tut_phase == "done":
        right = BX + BW - T * 0.35
        last = (tut_step >= TUT_STEPS - 1)
        TNEXT = draw_tut_button("おわり" if last else "つぎへ", right - T * 2.0, by, T * 2.0, h)
        TRETRY = draw_tut_button("もう一度", right - T * 4.2, by, T * 2.0, h)

def draw_tut_target():
    # タップしてほしいマスの枠と、照射される3x3の範囲（薄い色）を、いっしょに点滅させる
    T = TILE_SIZE
    if (tut_tick // 4) % 2 == 1:
        return
    tx = tut_target[0]
    ty = tut_target[1]
    context.fillStyle = COLOR[tsugi]
    context.globalAlpha = 0.3
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            y = ty + dy
            x = tx + dx
            if 0 <= y < ROW and 0 <= x < COL:
                context.fillRect(BX + x * T, BY + y * T, T, T)
    context.globalAlpha = 1.0
    context.strokeStyle = SHADOW
    context.lineWidth = 6
    context.strokeRect(BX + tx * T + 3, BY + ty * T + 3, T - 6, T - 6)
    context.strokeStyle = T_STRONG
    context.lineWidth = 3
    context.strokeRect(BX + tx * T + 3, BY + ty * T + 3, T - 6, T - 6)

def tut_main():
    # チュートリアル1フレーム分の処理（ゲーム本体と同じ流れ：照射→白の消去→落下→判定→ビーム）。ブロックは降ってこない
    global tut_phase, tut_hint, tut_tick, lasers, timer, combo, combo_timer, beam_count, popup_beams, popup_gain, pop_open, mouse_c
    tut_tick += 1
    if tut_hint > 0:
        tut_hint -= 1
    if tut_phase == "aim":
        draw_tut_target()
        if show_cursor and tsugi in COLOR:
            draw_area_preview()
        if mouse_c == 1:
            mouse_c = 0
            if cursor_x == tut_target[0] and cursor_y == tut_target[1]:
                combo = 0
                irradiate(cursor_x, cursor_y, tsugi)
                tut_phase = "sweep"
            else:
                tut_hint = 20
    elif tut_phase == "sweep":
        sc = sweep_block()
        if sc > 0:
            gw = add_score(sc * SCORE_PER_WHITE, MULTI_BEAM_WHITE)
            if pop_open:
                popup_gain += gw
            else:
                popup_gain = gw
                popup_beams = 1
            combo_timer = COMBO_POPUP_FRAMES
        pop_open = False
        beam_count = 1
        tut_phase = "drop"
    elif tut_phase == "drop":
        if not drop_block():
            tut_phase = "line"
    elif tut_phase == "line":
        lines = find_lines()
        if len(lines) > 0:
            lasers = []
            for run, dy, dx, n in lines:
                cells = line_cells(run[0][0], run[0][1], dy, dx)
                lasers.append((cells, run, n, dy, dx))
            timer = 0
            play_beam(combo)
            tut_phase = "laser"
        else:
            tut_phase = "done"
    elif tut_phase == "laser":
        draw_laser()
        timer += 1
        if timer >= LASER_FRAMES:
            erased = set()
            for cells, run, color, dy, dx in lasers:
                erased.update(run)
            beam_count = len(lasers)
            fire_lasers()
            lasers = []
            combo += 1
            popup_gain = add_score(len(erased) * SCORE_PER_LINE_BLOCK)
            popup_beams = beam_count
            combo_timer = COMBO_POPUP_FRAMES
            pop_open = True
            tut_phase = "sweep"
    mouse_c = 0
    draw_tut_ui()
    if combo_timer > 0:
        combo_timer -= 1
        draw_combo_popup()

# ---------- メインループ ----------
def game_main():
    global index, timer, tsugi, score, high_score, lasers
    global cursor_x, cursor_y, mouse_c, combo, combo_timer, RBTN, TBTN, beam_count, popup_beams, popup_gain, pop_open

    T = TILE_SIZE
    context.setTransform(DPR, 0, 0, DPR, 0, 0)  # 以降の描画はCSSピクセル基準
    draw_bg()
    draw_block()

    RBTN = None
    TBTN = None
    if tut:
        tut_main()
        draw_pal_toast()
        js.setTimeout(game_main, 100)
        return
    if demo:
        if mouse_c == 1:
            demo_to_game()    # デモプレイ中にクリックされた → ゲーム開始
        else:
            draw_demo_dim()
    if (index == 0 or index == 1) and DEMO_ENABLED:
        demo_init()           # タイトル画面では、盤面をまっさらにして、デモプレイを流す
    elif index == 0 or index == 1:
        draw_title_overlay()
        index = 1

        if mouse_c == 1:
            mouse_c = 0
            for y in range(ROW):
                for x in range(COL):
                    masu[y][x] = EMPTY
            score = 0
            combo = 0
            combo_timer = 0
            beam_count = 1
            pop_open = False
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
            gw = add_score(sc * SCORE_PER_WHITE, MULTI_BEAM_WHITE)
            if pop_open:
                popup_gain += gw   # ビームの発射に続く白の消去は、同じポップアップにまとめる
            else:
                popup_gain = gw    # 照射だけで白になって消えたとき
                popup_beams = 1
            combo_timer = COMBO_POPUP_FRAMES
        pop_open = False
        beam_count = 1  # 同時発射の倍率は、この発射の分だけ
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
            if not demo or DEMO_SOUND:
                play_beam(combo)  # 複数のレーザーが同時に出ても、鳴らすのは1回
            index = 7
        elif not over_block():
            tsugi = random.choice(PRIMARY)
            mouse_c = 0
            index = 5
        else:
            index = 6
            timer = 0
            if not demo:
                refresh_ranking()  # ゲームオーバーの表示中に、最新のランキングを読み込んでおく

    elif index == 5 and demo:
        demo_step()

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
        if demo:
            # デモプレイでは、GAME OVERを表示せず、少し待って盤面をリセットし、また最初から流す
            if timer >= DEMO_RESTART_FRAMES:
                demo_init()
        else:
            draw_txt_c("GAME OVER", BX + BW / 2, BY + T * 5, T * 0.95, "red", BW - T * 0.6)
        if not demo and timer >= 50:
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
            beam_count = len(lasers)  # 同時に発射したビームの数
            fire_lasers()
            lasers = []
            combo += 1  # 先にコンボを増やしてから、その倍率で加点する（同時発射の倍率も重ねてかかる）
            popup_gain = add_score(len(erased) * SCORE_PER_LINE_BLOCK)
            popup_beams = beam_count
            combo_timer = COMBO_POPUP_FRAMES
            pop_open = True
            index = 3  # 白になったブロックの消去へ

    if demo:
        draw_title_overlay()   # デモプレイの上に、タイトルの文字とRANKINGボタンを重ねる
        combo_timer = 0        # 得点のポップアップは、タイトルの文字と重なるので出さない

    # コンボ表示（2コンボ以上）
    if combo_timer > 0:
        combo_timer -= 1
        draw_combo_popup()
    draw_pal_toast()

    js.setTimeout(game_main, 100)

palette = load_palette()
apply_mode(load_mode())
refresh_ranking()
game_main()
