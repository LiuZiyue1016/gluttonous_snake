import numpy as np

# 定义贪吃蛇的动作，
# R表示向右边运动，就在在positon坐标的X轴加1,Y轴坐标不变，可以实现贪吃蛇头部坐标更新。
player_moves = {
    'L': np.array([-1., 0.]),
    'R': np.array([1., 0.]),
    'U': np.array([0., -1.]),
    'D': np.array([0., 1.])
}
initial_playersize = 4


class SnakeClass(object):
    def __init__(self, grid_size):
        self.pos = np.array([grid_size // 2, grid_size // 2]).astype('float')  # 初始化贪吃蛇头部position坐标，位于显示区域的中心
        self.dir = np.array([1., 0.])  # 初始化贪吃蛇的运动
        self.len = initial_playersize  # 初始化贪吃蛇的长度
        # 建立一个position数据用于存贮贪吃蛇历史轨迹，这些轨迹也是贪吃蛇的身子
        self.prev_pos = [np.array([grid_size // 2, grid_size // 2]).astype('float')]
        self.grid_size = grid_size

    def move(self):
        self.pos += self.dir
        self.prev_pos.append(self.pos.copy())
        self.prev_pos = self.prev_pos[-self.len - 1:]

    def check_dead(self, pos):  # 判断贪吃蛇的头部是否到达边界或则碰到自己的身体。
        if pos[0] <= -1 or pos[0] >= self.grid_size:
            return True
        elif pos[1] <= -1 or pos[1] >= self.grid_size:
            return True
        # 判断贪吃蛇头是否碰到了身体
        elif list(pos) in [list(item) for item in self.prev_pos[:-1]]:
            return True
        else:
            return False

    def get_proximity(self):  # 该函数定义了贪吃蛇头部的位置更新
        L = self.pos - np.array([1, 0])
        R = self.pos + np.array([1, 0])
        U = self.pos - np.array([0, 1])
        D = self.pos + np.array([0, 1])
        poss_directions = [L, R, U, D]
        proximity = [int(self.check_dead(x)) for x in poss_directions]
        return proximity

    def __len__(self):
        return self.len + 1


class AppleClass(object):  # 定义苹果出现的地方
    def __init__(self, grid_size):
        self.pos = np.random.randint(1, grid_size, 2)
        self.score = 0
        self.grid_size = grid_size

    def eaten(self):
        # generate new apple every time the previous one is eaten
        self.pos = np.random.randint(1, self.grid_size, 2)
        self.score += 1


class GameEnvironment(object):
    def __init__(self, grid_size, nothing, dead, apple):
        self.snake = SnakeClass(grid_size)
        self.apple = AppleClass(grid_size)
        self.game_over = False
        self.grid_size = grid_size
        self.reward_nothing = nothing
        self.reward_dead = dead
        self.reward_apple = apple
        self.time_since_apple = 0
        self.width = 32
        self.height = 24

    def reset_game(self):
        self.apple.pos = np.random.randint(1, self.grid_size, 2).astype('float')  # 随机初始化苹果的位置
        self.apple.score = 0  # 初始化score
        self.snake.pos = np.random.randint(1, self.grid_size, 2).astype('float')  # 初始化贪吃蛇出现的位置
        self.snake.prev_pos = [self.snake.pos.copy().astype('float')]
        self.snake.len = initial_playersize
        self.game_over = False

    def get_board_state(self):
        return [self.snake.pos, self.snake.dir, self.snake.prev_pos, self.apple.pos, self.apple.score, self.game_over]

    def update_board_state(self, move):
        reward = self.reward_nothing
        done = False
        # python 中的all函数用于判断可迭代iterable中所有元素是否都是True，如果是返回Treu，否则False
        if move == 0:
            if not (self.snake.dir == player_moves['R']).all():
                self.snake.dir = player_moves['L']
        if move == 1:
            if not (self.snake.dir == player_moves['L']).all():
                self.snake.dir = player_moves['R']
        if move == 2:
            if not (self.snake.dir == player_moves['D']).all():
                self.snake.dir = player_moves['U']
        if move == 3:
            if not (self.snake.dir == player_moves['U']).all():
                self.snake.dir = player_moves['D']
        self.snake.move()
        self.time_since_apple += 1

        if self.time_since_apple == 100:  # episode为100时候结束游戏
            self.game_over = True
            reward = self.reward_dead
            self.time_since_apple = 0
            done = True
        # --
        if self.snake.check_dead(self.snake.pos) == True:  # 碰到边缘和身子，结束游戏
            self.game_over = True
            reward = self.reward_dead
            self.time_since_apple = 0
            done = True
        elif (self.snake.pos == self.apple.pos).all():  # 判断是否吃到苹果
            self.apple.eaten()
            self.snake.len += 1
            self.time_since_apple = 0
            reward = self.reward_apple
        len_of_snake = len(self.snake)
        return reward, done, len_of_snake