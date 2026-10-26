# プロトタイプ。落ち物パズルゲームの仕組みだけ。
import js
import random

# Canvas取得
canvas = js.document.querySelector("#canvas")
context = canvas.getContext("2d")

# サイズ定義
COL = 8
ROW = 10

TILE_SIZE = 70
canvas.width = TILE_SIZE * COL
canvas.height = TILE_SIZE * ROW

# マウス変数
cursor_x = 0
cursor_y = 0
# mouse_x = 0
# mouse_y = 0
mouse_c = 0

# 色定数
BLACK = 0b000
RED = 0b100
GREEN = 0b010
BLUE = 0b001
YELLOW = RED | GREEN
MAGENTA = RED | BLUE
CYAN = GREEN | BLUE
WHITE = RED | GREEN | BLUE

COLOR = {
	0b100:"#ff0000",
	0b010:"#00ff00",
	0b001:"#0000ff",
	0b110:"#ffff00",
	0b101:"#ff00ff",
	0b011:"#00ffff",
	0b111:"#ffffff"
}

# 配列作成
masu = []
check = []
for y in range(ROW):
	row = []
	for x in range(COL):
		row.append(0)
	masu.append(row)
	check.append(row)

masu[7] = [BLACK,RED,BLACK,GREEN,BLACK,BLUE,BLACK,BLACK]
masu[9] = [BLACK,YELLOW,BLACK,MAGENTA,BLACK,CYAN,BLACK,WHITE]

# その他変数
index = 0
score = 0
high_score = 0
timer = 0
tsugi = random.choice([RED, GREEN, BLUE])

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


# 関数

def draw_bg():
	context.clearRect(0, 0, canvas.width, canvas.height)
	context.fillStyle = "#000000"
	context.fillRect(0, 0, canvas.width, canvas.height)

def draw_block():
	for y in range(ROW):
		for x in range(COL):
			if masu[y][x] != BLACK:
				context.fillStyle = COLOR[masu[y][x]]
				context.fillRect(x * TILE_SIZE, y * TILE_SIZE,
								 TILE_SIZE - 2, TILE_SIZE - 2)

def draw_txt(txt, x, y, siz, col, tg):
	context.fillStyle = "black"
	context.font = f"bold {siz}px Noto Sans"
	context.fillText(txt, x+1, y+1)

	context.fillStyle = col
	context.fillText(txt, x, y)

# 判定
def check_block():
	mark = []
	for y in range(ROW):
		row = []
		for x in range(COL):
			check[y][x] = masu[y][x]
			row.append(False)
		mark.append(row)
	
	# 縦3つチェック
	for y in range(1, ROW-1):
		for x in range(COL):
			n = check[y][x]
			if n > 0:
				if check[y-1][x] == n and check[y+1][x] == n:
					mark[y-1][x] = True
					mark[y][x] = True
					mark[y+1][x] = True
	
	# 横3つチェック
	for y in range(ROW):
		for x in range(1, COL-1):
			n = check[y][x]
			if n > 0:
				if check[y][x-1] == n and check[y][x+1] == n:
					mark[y][x-1] = True
					mark[y][x] = True
					mark[y][x+1] = True
	
	# 斜め3つチェック
	for y in range(1, ROW-1):
		for x in range(1, COL-1):
			n = check[y][x]
			if n > 0:
				# 左上、右下が同じ
				if check[y-1][x-1] == n and check[y+1][x+1] == n:
					mark[y-1][x-1] = True
					mark[y][x] = True
					mark[y+1][x+1] = True
				# 左下、右上が同じ
				if check[y+1][x-1] == n and check[y-1][x+1] == n:
					mark[y+1][x-1] = True
					mark[y][x] = True
					mark[y-1][x+1] = True
	
	for y in range(ROW):
		for x in range(COL):
			if mark[y][x]:
				masu[y][x] = WHITE

def sweep_block():
	num = 0
	for y in range(ROW):
		for x in range(COL):
			if masu[y][x] == WHITE:
				masu[y][x] = BLACK
				num += 1
	return num

def drop_block():
	flg = False
	for y in range(ROW-2, -1, -1):
		for x in range(COL):
			if masu[y][x] != 0 and masu[y+1][x] == 0:
				masu[y+1][x] = masu[y][x]
				masu[y][x] = 0
				flg = True
	return flg

def over_block():
	for x in range(COL):
		if masu[0][x] > 0:
			return True
	return False

def set_block():
	for x in range(COL):
		masu[0][x] = random.choice([RED, GREEN, BLUE])

def game_main():
	global index, timer, tsugi, score, high_score
	global cursor_x, cursor_y, mouse_c
	draw_bg()
	draw_block()

	if index == 0 or index == 1:
		draw_txt("Puzzle_Game", TILE_SIZE, TILE_SIZE*3, TILE_SIZE, "#222222", "TITLE")
		draw_txt("Easy", TILE_SIZE, TILE_SIZE*5, TILE_SIZE, "#ffffff", "TITLE")
		draw_txt("Normal", TILE_SIZE, TILE_SIZE*7, TILE_SIZE, "#ffffff", "TITLE")
		draw_txt("Hard", TILE_SIZE, TILE_SIZE*9, TILE_SIZE, "#ffffff", "TITLE")
		index = 1

		if mouse_c == 1:
			mouse_c = 0
			for y in range(ROW):
				for x in range(COL):
					masu[y][x] = BLACK
			mouse_c = 0
			score = 0
			tsugi = random.choice([RED, GREEN, BLUE])
			set_block()
			index = 2

	elif index == 2:
		if not drop_block():
			index = 3

	elif index == 3:
		check_block()
		index = 4

	elif index == 4:
		sc = sweep_block()
		score += sc * 10
		if score > high_score:
			high_score = score
		
		if sc > 0:
			index = 2
		else:
			if not over_block():
				tsugi = random.choice([RED, GREEN, BLUE])
				index = 5
			else:
				index = 6
				timer = 0
	
	elif index == 5:
		if 0 <= cursor_x < COL and 0<= cursor_y < ROW:
			if mouse_c == 1:
				mouse_c = 0
				set_block()
				masu[cursor_y][cursor_x] = tsugi
				index = 2
		
			# カーソル描画
			# if UI_mode == yoko:
				# context.drawImage(
				# 	img_cursor,
				# 	cursor_x*TILE_SIZE + 4,
				# 	cursor_y*TILE_SIZE + 4,
				# 	TILE_SIZE - 8,
				# 	TILE_SIZE - 8
				# )
			context.fillStyle = COLOR[tsugi]
			context.fillRect(cursor_x * TILE_SIZE, cursor_y * TILE_SIZE,TILE_SIZE - 2, TILE_SIZE - 2)

	elif index == 6:
			timer += 1
			if timer < 50:
				# 要確認
				draw_txt("GAME OVER", TILE_SIZE, TILE_SIZE*5, TILE_SIZE, "red", "")
			if timer == 50:
				# difficulty = 0
				index = 0

	js.setTimeout(game_main, 100)

game_main()
