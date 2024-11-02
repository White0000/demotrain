import pygame
import random
import sys
import json
from operator import itemgetter

# 初始化颜色
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
TEXT_COLOR = (119, 110, 101)
FONT = None
SCORE_FILE = "scoreboard.json"

# 设置窗口大小和格子大小
GRID_SIZE = 4
TILE_SIZE = 100
TILE_PADDING = 10
WINDOW_SIZE = GRID_SIZE * (TILE_SIZE + TILE_PADDING) + TILE_PADDING

# 初始化pygame
pygame.init()
FONT = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))
pygame.display.set_caption("2048 Game")

# 初始化棋盘
def init_board():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    add_random_tile(board)
    add_random_tile(board)
    return board

# 添加随机 2 或 4
def add_random_tile(board):
    empty_tiles = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if board[i][j] == 0]
    if not empty_tiles:
        return
    i, j = random.choice(empty_tiles)
    board[i][j] = 4 if random.random() > 0.9 else 2

# 绘制棋盘和每个格子
def draw_board(board, score):
    screen.fill(BACKGROUND_COLOR)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            tile_value = board[i][j]
            tile_color = TILE_COLORS.get(tile_value, TILE_COLORS[2048])
            rect = pygame.Rect(
                j * (TILE_SIZE + TILE_PADDING) + TILE_PADDING,
                i * (TILE_SIZE + TILE_PADDING) + TILE_PADDING,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(screen, tile_color, rect)
            if tile_value > 0:
                text = FONT.render(str(tile_value), True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
    # 显示得分
    score_text = FONT.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, WINDOW_SIZE + 20))
    pygame.display.flip()

# 判断游戏是否结束
def is_game_over(board):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == 0:
                return False
            if i < GRID_SIZE - 1 and board[i][j] == board[i + 1][j]:
                return False
            if j < GRID_SIZE - 1 and board[i][j] == board[i][j + 1]:
                return False
    return True

# 移动和合并操作
def move_and_merge(row):
    new_row = [num for num in row if num != 0]
    merged_row = []
    skip = False
    score_gain = 0
    for i in range(len(new_row)):
        if skip:
            skip = False
            continue
        if i + 1 < len(new_row) and new_row[i] == new_row[i + 1]:
            merged_row.append(new_row[i] * 2)
            score_gain += new_row[i] * 2
            skip = True
        else:
            merged_row.append(new_row[i])
    return merged_row + [0] * (GRID_SIZE - len(merged_row)), score_gain

# 处理棋盘移动
def move(board, direction):
    moved = False
    score_gain = 0
    if direction == "up":
        for j in range(GRID_SIZE):
            col = [board[i][j] for i in range(GRID_SIZE)]
            new_col, col_score = move_and_merge(col)
            score_gain += col_score
            for i in range(GRID_SIZE):
                if board[i][j] != new_col[i]:
                    moved = True
                board[i][j] = new_col[i]
    elif direction == "down":
        for j in range(GRID_SIZE):
            col = [board[i][j] for i in range(GRID_SIZE)][::-1]
            new_col, col_score = move_and_merge(col)
            score_gain += col_score
            for i in range(GRID_SIZE):
                if board[i][j] != new_col[GRID_SIZE - 1 - i]:
                    moved = True
                board[i][j] = new_col[GRID_SIZE - 1 - i]
    elif direction == "left":
        for i in range(GRID_SIZE):
            new_row, row_score = move_and_merge(board[i])
            score_gain += row_score
            if board[i] != new_row:
                moved = True
            board[i] = new_row
    elif direction == "right":
        for i in range(GRID_SIZE):
            new_row, row_score = move_and_merge(board[i][::-1])
            new_row.reverse()
            score_gain += row_score
            if board[i] != new_row:
                moved = True
            board[i] = new_row
    return moved, score_gain

# 保存得分到排行榜
def save_score(score):
    try:
        with open(SCORE_FILE, "r") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []
    scores.append({"score": score})
    scores = sorted(scores, key=itemgetter("score"), reverse=True)[:5]  # 仅保留前5名
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

# 显示排行榜
def show_scoreboard():
    try:
        with open(SCORE_FILE, "r") as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []
    screen.fill(BACKGROUND_COLOR)
    title = FONT.render("Top Scores", True, TEXT_COLOR)
    screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 50))
    for i, entry in enumerate(scores[:5], start=1):
        score_text = FONT.render(f"{i}. {entry['score']}", True, TEXT_COLOR)
        screen.blit(score_text, (WINDOW_SIZE // 2 - score_text.get_width() // 2, 100 + i * 40))
    pygame.display.flip()
    pygame.time.wait(10000)  # 暂停3秒显示排行榜

# 主游戏循环
def main():
    board = init_board()
    score = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        draw_board(board, score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    moved, score_gain = move(board, "up")
                elif event.key == pygame.K_DOWN:
                    moved, score_gain = move(board, "down")
                elif event.key == pygame.K_LEFT:
                    moved, score_gain = move(board, "left")
                elif event.key == pygame.K_RIGHT:
                    moved, score_gain = move(board, "right")
                else:
                    moved, score_gain = False, 0

                if moved:
                    score += score_gain
                    add_random_tile(board)
                    draw_board(board, score)
                    if is_game_over(board):
                        print("Game Over!")
                        save_score(score)
                        show_scoreboard()
                        running = False
        clock.tick(60)

if __name__ == "__main__":
    main()
