import pygame
import matplotlib.pyplot as plt
import numpy as np
from train import train_dqn
import time
import sys
from pygame.locals import QUIT
from pygame.locals import KEYDOWN, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_ESCAPE
from human_move import Game
from AI_gluttonous_snake import get_move as search_move

black = pygame.Color(0, 0, 0)
bright_black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
bright_white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 200, 0)
bright_green = pygame.Color(0, 255, 0)
red = pygame.Color(200, 0, 0)
bright_red = pygame.Color(255, 0, 0)
purple = pygame.Color(128, 0, 128)
bright_purple = pygame.Color(255, 0, 255)
orange = pygame.Color(255, 165, 0)
bright_orange = pygame.Color(255, 140, 0)
blue = pygame.Color(32, 178, 170)
bright_blue = pygame.Color(32, 200, 200)
yellow = pygame.Color(255, 205, 0)
bright_yellow = pygame.Color(255, 255, 0)

block_height = 60
block_width = 120

game = Game()
rect_len = game.settings.rect_len
snake = game.snake
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((game.settings.width * rect_len, game.settings.height * rect_len))
pygame.display.set_caption('Gluttonous Snake')

pygame.font.init()
pygame.mixer.init()
# 加载背景音乐
pygame.mixer.music.load("music/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

def text_objects(text, font, color=black):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def message_display(text, x, y, color, size):
    large_text = pygame.font.SysFont('Arial', size)
    text_surf, text_rect = text_objects(text, large_text, color)
    text_rect.center = (x, y)
    screen.blit(text_surf, text_rect)
    pygame.display.update()


def button(msg, x, y, w, h, inactive_color, active_color, action=None, parameter=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            if parameter is not None:
                action(parameter)
            else:
                action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    small_text = pygame.font.SysFont('Arial', 20)
    text_surf, text_rect = text_objects(msg, small_text)
    text_rect.center = (x + (w / 2), y + (h / 2))
    screen.blit(text_surf, text_rect)


def quit_game():
    pygame.quit()
    sys.exit()


def crash():
    message_display('crashed', game.settings.width / 2 * rect_len,
                    game.settings.height / 4 * rect_len, white, size=50)
    time.sleep(1)


def format_time(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


def display_record():
    record_data = []
    with open("record.txt", "r") as file:
        lines = file.readlines()  # 读取文件内容
        if lines:  # 如果 lines 不为空列表
            for line in lines:
                try:
                    t, s = line.strip().split(",")
                    record_data.append((float(t), int(s)))
                except ValueError:
                    print("Error: Invalid record format:", line)
    display = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        button('Quit', game.settings.width / 2 * rect_len - 0.5 * block_width, 360, block_width,
               block_height, white, bright_white, initial_interface)
        # 显示记录
        if not display:
            screen.fill(black)
            message_display('Record', game.settings.width / 2 * rect_len,
                            game.settings.height / 6 * rect_len, white, size=50)
            # 更新屏幕
            x = game.settings.width / 2 * rect_len
            y = game.settings.height / 4 * rect_len
            for i, (t, s) in enumerate(record_data):
                text = f"{format_time(t)} | {s}"
                message_display(text, x, y, white, size=18)
                y += 20  # 调整显示位置
                if i == len(record_data) - 1:
                    display = True
            if not lines:
                display = True
        pygame.display.update()


def clear_record():
    with open("record.txt", "w") as file:
        file.truncate(0)


def initial_interface():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        screen.fill(white)
        message_display('Gluttonous Snake', game.settings.width / 2 * rect_len,
                        game.settings.height / 6 * rect_len, black, size=50)

        button('Start!', game.settings.width / 2 * rect_len - 1.5 * block_width, 150, block_width,
               block_height, green, bright_green, game_loop, 'human')
        button('Quit', game.settings.width / 2 * rect_len + 0.5 * block_width, 150, block_width,
               block_height, red, bright_red, quit_game)
        button('Record', game.settings.width / 2 * rect_len - 1.5 * block_width, 230, block_width,
               block_height, purple, bright_purple, display_record)
        button('Clear Record', game.settings.width / 2 * rect_len + 0.5 * block_width, 230, block_width,
               block_height, orange, bright_orange, clear_record)
        button('AI', game.settings.width / 2 * rect_len - 1.5 * block_width, 310, block_width,
               block_height, blue, bright_blue, game_loop, 'search_ai')
        button('DQN', game.settings.width / 2 * rect_len + 0.5 * block_width, 310, block_width,
               block_height, yellow, bright_yellow, train)

        pygame.display.update()
        pygame.time.Clock().tick(15)


def game_loop(player, fps=30):
    game.restart_game()
    t = time.time()
    while not game.game_end(t):
        pygame.event.pump()
        if player == 'search_ai':
            move = search_move(game, t)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
        else:
            move = human_move()
            fps = 10

        game.do_move(move, t)

        screen.fill(black)
        button('Quit', game.settings.width * rect_len - block_width, 0, block_width,
               block_height, white, bright_white, initial_interface)
        game.snake.blit(rect_len, screen)
        game.strawberry.blit(screen)
        game.blit_score(white, screen)

        pygame.display.flip()
        fpsClock.tick(fps)
    crash()


def human_move():
    direction = snake.facing
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        elif event.type == KEYDOWN:
            if event.key == K_RIGHT or event.key == ord('d'):
                direction = 'right'
            if event.key == K_LEFT or event.key == ord('a'):
                direction = 'left'
            if event.key == K_UP or event.key == ord('w'):
                direction = 'up'
            if event.key == K_DOWN or event.key == ord('s'):
                direction = 'down'
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))

    move = game.direction_to_int(direction)
    return move


def train():
    scores, avg_scores, avg_len_of_snake, max_len_of_snake, running = train_dqn(screen)
    if not running:
        initial_interface()
    plt.figure()
    plt.plot(np.arange(1, len(scores) + 1), scores, label="Score")
    plt.plot(np.arange(1, len(avg_scores) + 1), avg_scores, label="Avg score on 100 episodes")
    plt.legend(bbox_to_anchor=(1.05, 1))
    plt.ylabel('Score')
    plt.xlabel('Episodes #')
    plt.savefig('images/score_plot.png')
    plt.close()

    plt.figure()
    plt.plot(np.arange(1, len(avg_len_of_snake) + 1), avg_len_of_snake, label="Avg Len of Snake")
    plt.plot(np.arange(1, len(max_len_of_snake) + 1), max_len_of_snake, label="Max Len of Snake")
    plt.legend(bbox_to_anchor=(1.05, 1))
    plt.ylabel('Length of Snake')
    plt.xlabel('Episodes #')
    plt.savefig('images/length_plot.png')
    plt.close()

    plt.figure()
    n, bins, patches = plt.hist(max_len_of_snake, 45, density=1, facecolor='green', alpha=0.75)
    plt.plot(np.arange(1, len(bins) + 1), 'r--', linewidth=1)
    mu = round(np.mean(max_len_of_snake), 2)
    sigma = round(np.std(max_len_of_snake), 2)
    median = round(np.median(max_len_of_snake), 2)
    plt.xlabel('Max.Lengths, mu = {:.2f}, sigma={:.2f},  median: {:.2f}'.format(mu, sigma, median))
    plt.ylabel('Probability')
    plt.title('Histogram of Max.Lengths')
    plt.axis([4, 44, 0, 0.15])
    plt.grid(True)
    plt.savefig('images/histogram.png')
    plt.close()


if __name__ == "__main__":
    initial_interface()
