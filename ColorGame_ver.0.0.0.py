# プロトタイプ。混色システムの実装だけ。
import js
import random

# Canvas取得
canvas = js.document.querySelector("#canvas")
context = canvas.getContext("2d")

# # 画像読み込みメソッド
# def load_img(src):
# 	img = js.Image.new()
# 	img.src = src
# 	return img

# サイズ定義
COL = 8
ROW = 10

######################## 後から変更 ########################
TILE_SIZE = 70
canvas.width = TILE_SIZE * COL
canvas.height = TILE_SIZE * ROW

# マウス変数
cursor_x = 0
cursor_y = 0
mouse_x = 0
mouse_y = 0
mouse_c = 0

# 色定数
BLACK = 0b000
RED = 0b001
GREEN = 0b010
BLUE = 0b100
YELLOW = RED | GREEN
MAGENTA = RED | BLUE
CYAN = GREEN | BLUE
WHITE = RED | GREEN | BLUE

LIGHT_R = 0b001
LIGHT_G = 0b010
LIGHT_B = 0b100

COLOR = {
    0b001:"#ff0000",
    0b010:"#00ff00",
    0b100:"#0000ff",
    0b011:"#ffff00",
    0b101:"#ff00ff",
    0b110:"#00ffff",
    0b111:"#ffffff"
}

# 配列作成
masu = [
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,RED,BLACK,GREEN,BLACK,BLUE,BLACK,BLACK],
	[BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK,BLACK],
	[BLACK,YELLOW,BLACK,MAGENTA,BLACK,CYAN,BLACK,WHITE]
]
# check = []

# その他変数
index = 0
tsugi = random.choice([LIGHT_R, LIGHT_G, LIGHT_B])

# 入力
def mouse_move(e):
	global mouse_x, mouse_y
	rect = canvas.getBoundingClientRect()
	mouse_x = int(e.clientX - rect.left)
	mouse_y = int(e.clientY - rect.top)

def mouse_press(e):
	global mouse_c
	mouse_c = 1

canvas.addEventListener("mousemove", mouse_move)
canvas.addEventListener("mousedown", mouse_press)

# 描画
def draw_block():
	for y in range(ROW):
		for x in range(COL):
			if masu[y][x] > 0:
				context.fillStyle = COLOR[masu[y][x]]
				context.fillRect(x*TILE_SIZE, y*TILE_SIZE,
										TILE_SIZE, TILE_SIZE)

def draw_light():
	if tsugi == 0:
		return
	
	context.fillstyle = COLOR[tsugi]

	# NEXTライト
	context.globalAlpha = 1
	context.fillRect(0, 0, TILE_SIZE, TILE_SIZE)


def draw_txt(txt, x, y, siz):
	context.fillStyle = "#ffffff"
	context.font = f"bold {siz}px Noto Sans"
	context.fillText(txt, x, y)

# 色を変える関数
def light_block(color, light):
	# 空マスは変化しない
	if color == BLACK:
		return BLACK
	
	color |= light
	
	if color == WHITE:
		# 白色になったら数秒後に消える
		# 上手く機能しない
		js.setTimeout(game_main, 10000)
		return BLACK
	
	return color

# ブロックを降らせるメソッド
def set_block():
	masu[0][random.randrange(COL)] = random.randint(1, 3)

def game_main():
	global tsugi
	global cursor_x, cursor_y, mouse_c
	context.clearRect(0, 0, COL*TILE_SIZE, ROW*TILE_SIZE)
	# 背景描画
	context.fillStyle = "#000000"
	context.fillRect(0, 0, canvas.width, canvas.height)

	# ブロック描画
	draw_block()

	# ブロック配置（ライトで照らす）
	# ライトの色が未決定なら決める

	cursor_x = mouse_x // TILE_SIZE
	cursor_y = mouse_y // TILE_SIZE

	if 0 <= cursor_x < COL and 0<= cursor_y < ROW:
		# クリックした際の処理
		if mouse_c == 1:
			mouse_c = 0

			for y in range(3):
				for x in range(3):

					ny = cursor_y - 1 + y
					nx = cursor_x - 1 + x

					# 範囲外なら処理しない
					if not(0 <= ny < ROW and 0 <= nx < COL):
						continue
					
					# 色変更
					masu[ny][nx] = light_block(masu[ny][nx], tsugi)

			tsugi = random.choice([LIGHT_R, LIGHT_G, LIGHT_B])

		if tsugi > 0:
			if tsugi == LIGHT_R:
				context.fillStyle = "#ff0000"
			elif tsugi == LIGHT_G:
				context.fillStyle = "#00ff00"
			else:
				context.fillStyle = "#0000ff"
			context.fillRect(0, 0, TILE_SIZE, TILE_SIZE)
			
			
	# ライト範囲描画
	context.globalAlpha = 0.5
	if tsugi == LIGHT_R:
		context.fillStyle = "#ff0000"
	elif tsugi == LIGHT_G:
		context.fillStyle = "#00ff00"
	elif tsugi == LIGHT_B:
		context.fillStyle = "#0000ff"
	context.fillRect(cursor_x*TILE_SIZE-TILE_SIZE, cursor_y*TILE_SIZE-TILE_SIZE,
							TILE_SIZE*3, TILE_SIZE*3)
	context.globalAlpha = 1

	js.setTimeout(game_main, 100)

# 起動
game_main()