# 加法混色パズル
# 同じ種類のブロックが3つ以上揃うと、RGBの場合は周囲に光を照射し混色させ、CMYの場合は光を照射せずお邪魔ブロックとなりRGBの光を待つ。
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
if UI_mode == tate:
	TILE_SIZE = min((win_w-30)//COL, (win_h-30)//(ROW+2))
	UI_height = int(TILE_SIZE * 2)
else:
	TILE_SIZE = min((win_w-30)//(COL+3), (win_h-30)//ROW)
	UI_width = int(TILE_SIZE * 3)

# Canvasサイズ変更
if UI_mode == tate:
	canvas.width = TILE_SIZE * COL
	canvas.height = TILE_SIZE * ROW + UI_height
else:
	canvas.width = TILE_SIZE * COL + UI_width
	canvas.height = TILE_SIZE * ROW

# UI領域の始点
UI_x = COL*TILE_SIZE
UI_y = ROW*TILE_SIZE

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

COLOR = {
	0b100: "#ff0000",
	0b010: "#00ff00",
	0b001: "#0000ff",
	0b110: "#ffff00",
	0b101: "#ff00ff",
	0b011: "#00ffff",
	0b111: "#ffffff"
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

# その他変数
index = 0
score = 0
high_score = 0
timer = 0
tsugi = 0
mark_data = []  # 揃ったブロックの位置と色を記録するための変数

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

# 描画関連
def draw_bg():
	context.clearRect(0, 0, canvas.width, canvas.height)
	
	#背景全体を黒で塗りつぶす
	context.fillStyle = "#000000"
	context.fillRect(0, 0, canvas.width, canvas.height)

	# UI領域に境界線を追加したい
	# 縦or横で条件分岐が必要かも
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
		draw_txt(f"SCORE {score}", TILE_SIZE*0.5, (ROW+0.5)*TILE_SIZE, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt(f"HISC {high_score}", TILE_SIZE*0.5, (ROW+1.5)*TILE_SIZE, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt("NEXT", TILE_SIZE*4.5, (ROW+0.5)*TILE_SIZE, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt("スマホ用UI", TILE_SIZE*4.5, (ROW+1.5)*TILE_SIZE, TILE_SIZE*0.4, "#ffffff", "")
		if tsugi in COLOR:
			context.fillStyle = COLOR[tsugi]
			context.fillRect(TILE_SIZE*6, (ROW+0.2)*TILE_SIZE, TILE_SIZE*0.5, TILE_SIZE*0.5)
	else:
		draw_txt(f"SCORE {score}", (COL+0.5)*TILE_SIZE, TILE_SIZE*1.5, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt(f"HISC {high_score}", (COL+0.5)*TILE_SIZE, TILE_SIZE*2.5, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt("NEXT", (COL+0.5)*TILE_SIZE, TILE_SIZE*3.5, TILE_SIZE*0.4, "#ffffff", "")
		draw_txt("PC用UI", (COL+0.5)*TILE_SIZE, TILE_SIZE*4.5, TILE_SIZE*0.4, "#ffffff", "")
		if tsugi in COLOR:
			context.fillStyle = COLOR[tsugi]
			context.fillRect((COL+2)*TILE_SIZE, TILE_SIZE*3, TILE_SIZE*0.5, TILE_SIZE*0.5)

def draw_block():
	for y in range(ROW):
		for x in range(COL):
			if masu[y][x] != BLACK and masu[y][x] in COLOR:
				context.fillStyle = COLOR[masu[y][x]]
				context.fillRect(x * TILE_SIZE + 1, y * TILE_SIZE + 1,
								 TILE_SIZE - 2, TILE_SIZE - 2)

def draw_txt(txt, x, y, siz, col, tg):
	context.fillStyle = "black"
	context.font = f"bold {siz}px Noto Sans"
	context.fillText(txt, x+1, y+1)

	context.fillStyle = col
	context.fillText(txt, x, y)

# 判定・処理関数
# 判定処理：揃ったブロックの位置と「その揃った色」を記録する
def check_block():
	# mark配列には、揃った場合その「色」が入る（0は揃っていない）
	mark = [[BLACK for _ in range(COL)] for _ in range(ROW)]
	
	# 縦3つチェック
	for y in range(1, ROW - 1):
		for x in range(COL):
			n = masu[y][x]
			if n != BLACK and n != WHITE: # BLACKやWHITE以外で揃った場合
				if masu[y-1][x] == n and masu[y+1][x] == n:
					mark[y-1][x] = n
					mark[y][x] = n
					mark[y+1][x] = n
	
	# 横3つチェック
	for y in range(ROW):
		for x in range(1, COL - 1):
			n = masu[y][x]
			if n != BLACK and n != WHITE:
				if masu[y][x-1] == n and masu[y][x+1] == n:
					mark[y][x-1] = n
					mark[y][x] = n
					mark[y][x+1] = n
	
	# 斜め3つチェック
	for y in range(1, ROW - 1):
		for x in range(1, COL - 1):
			n = masu[y][x]
			if n != BLACK and n != WHITE:
				# 左上・右下
				if masu[y-1][x-1] == n and masu[y+1][x+1] == n:
					mark[y-1][x-1] = n
					mark[y][x] = n
					mark[y+1][x+1] = n
				# 左下・右上
				if masu[y+1][x-1] == n and masu[y-1][x+1] == n:
					mark[y+1][x-1] = n
					mark[y][x] = n
					mark[y-1][x+1] = n
	return mark

# 加法混色＆消去処理
def apply_light_and_sweep(mark):
	num_cleared = 0
	next_masu = [row[:] for row in masu]

	for y in range(ROW):
		for x in range(COL):
			color = mark[y][x]
			
			# BLACKでもWHITEでもない場合
			if color != BLACK and color != WHITE:
				
				# 【ポイント】発光・照射できるのは RGB (単色: ビットが1つだけ立っている) のみ！
				# RED(4), GREEN(2), BLUE(1) のいずれかの判定
				if color in (RED, GREEN, BLUE):
					# 周囲（上下左右）に光を当てる
					for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
						ny, nx = y + dy, x + dx
						if 0 <= ny < ROW and 0 <= nx < COL:
							if masu[ny][nx] != BLACK:
								next_masu[ny][nx] |= color # 混色
				
				elif color in (CYAN, MAGENTA, YELLOW):
					# 周囲（上下左右）に光を当てる
					for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
						ny, nx = y + dy, x + dx
						if 0 <= ny < ROW and 0 <= nx < COL:
							if masu[ny][nx] != BLACK and masu[ny][nx] in (CYAN, MAGENTA, YELLOW):
								next_masu[ny][nx] |= color # 混色
				
				# CMY(イエロー・マゼンタ・シアン)が揃った場合は、
				# 周囲に変色を広げず、自分たちが次の光を待つか、あるいはそのまま消滅/発光する

	# 全マスチェック：WHITE に到達したブロックだけが消滅（BLACKに）する！
	for y in range(ROW):
		for x in range(COL):
			if next_masu[y][x] == WHITE:
				next_masu[y][x] = BLACK
				num_cleared += 1

	# 盤面更新
	for y in range(ROW):
		for x in range(COL):
			masu[y][x] = next_masu[y][x]

	return num_cleared
# def check_block():
# 	mark = []
# 	for y in range(ROW):
# 		row = []
# 		for x in range(COL):
# 			check[y][x] = masu[y][x]
# 			row.append(False)
# 		mark.append(row)
	
# 	# 縦3つチェック
# 	for y in range(1, ROW-1):
# 		for x in range(COL):
# 			n = check[y][x]
# 			if n > 0:
# 				if check[y-1][x] == n and check[y+1][x] == n:
# 					mark[y-1][x] = True
# 					mark[y][x] = True
# 					mark[y+1][x] = True
	
# 	# 横3つチェック
# 	for y in range(ROW):
# 		for x in range(1, COL-1):
# 			n = check[y][x]
# 			if n > 0:
# 				if check[y][x-1] == n and check[y][x+1] == n:
# 					mark[y][x-1] = True
# 					mark[y][x] = True
# 					mark[y][x+1] = True
	
# 	# 斜め3つチェック
# 	for y in range(1, ROW-1):
# 		for x in range(1, COL-1):
# 			n = check[y][x]
# 			if n > 0:
# 				if check[y-1][x-1] == n and check[y+1][x+1] == n:
# 					mark[y-1][x-1] = True
# 					mark[y][x] = True
# 					mark[y+1][x+1] = True
# 				if check[y+1][x-1] == n and check[y-1][x+1] == n:
# 					mark[y+1][x-1] = True
# 					mark[y][x] = True
# 					mark[y-1][x+1] = True
	
# 	for y in range(ROW):
# 		for x in range(COL):
# 			if mark[y][x]:
# 				masu[y][x] = WHITE

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
		if masu[0][x] == BLACK:
			masu[0][x] = random.choice([RED, GREEN, BLUE])

def game_main():
	global index, timer, tsugi, score, high_score, mark_data
	global cursor_x, cursor_y, mouse_c

	draw_bg()
	draw_UI()
	draw_block()

	if index == 0 or index == 1:
		draw_txt("Color Puzzle", TILE_SIZE, TILE_SIZE*3, TILE_SIZE, "#ffffff", "TITLE")
		draw_txt("Click to Start", TILE_SIZE, TILE_SIZE*6, TILE_SIZE*0.5, "#ffffff", "TITLE")
		index = 1

		if mouse_c == 1:
			mouse_c = 0
			for y in range(ROW):
				for x in range(COL):
					masu[y][x] = BLACK
			score = 0
			tsugi = random.choice([RED, GREEN, BLUE])
			set_block()
			index = 2

	elif index == 2:
		# ブロックの落下処理
		if not drop_block():
			index = 3

	elif index == 3:
		# 揃い判定
		# check_block()

		# 揃い判定（mark配列を受け取る）
		mark_data = check_block()
		index = 4

	elif index == 4:
		# 消去とスコア加算
		# sc = sweep_block()

		# 周囲へ加法混色を適用＆WHITE（白色）の消去処理
		sc = apply_light_and_sweep(mark_data)
		score += sc * 10
		if score > high_score:
			high_score = score
		
		if sc > 0:
			index = 2 # 消えたら再度落下チェック
		else:
			if not over_block():
				tsugi = random.choice([RED, GREEN, BLUE])
				index = 5
			else:
				index = 6
				timer = 0
	
	elif index == 5:
		# 操作・配置フェーズ
		if 0 <= cursor_x < COL and 0 <= cursor_y < ROW:
			if tsugi in COLOR:
				context.fillStyle = COLOR[tsugi]
				context.globalAlpha = 0.6
				context.fillRect(cursor_x * TILE_SIZE, cursor_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
				context.globalAlpha = 1.0

			if mouse_c == 1:
				mouse_c = 0
				# クリック位置に光・ブロックを配置（または混色）
				if masu[cursor_y][cursor_x] == BLACK:
					masu[cursor_y][cursor_x] = tsugi
				else:
					masu[cursor_y][cursor_x] |= tsugi # 混色
				
				set_block()
				index = 2

	elif index == 6:
		# ゲームオーバー表示
		timer += 1
		draw_txt("GAME OVER", TILE_SIZE, TILE_SIZE*5, TILE_SIZE, "red", "")
		if timer >= 50:
			index = 0

	js.setTimeout(game_main, 100)

game_main()