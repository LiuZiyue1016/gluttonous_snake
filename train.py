import torch
import torch.nn as nn
import numpy as np
from network import DQNnetwork, get_network_input
from AI_move import GameEnvironment
from collections import deque
from replay_buffer import ReplayMemory
import time
import pygame
from args import args


model = DQNnetwork(input_dim=10, hidden_dim=20, output_dim=5)
board = GameEnvironment(args.grid_size, nothing=0, dead=-1, apple=1)
memory = ReplayMemory(1000)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
MSE = nn.MSELoss()

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)


def text_objects(text, font, color=black):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def message_display(screen, text1, text2, x1, y1, x2, y2, color, size):
    large_text = pygame.font.SysFont('Arial', size)
    text_surf, text_rect = text_objects(text1, large_text, color)
    text_rect.center = (x1, y1)
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(text2, large_text, color)
    text_rect.center = (x2, y2)
    screen.blit(text_surf, text_rect)
    pygame.display.update()


def button(screen, msg, x, y, w, h, inactive_color, active_color):
    running = True
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1:
            running = False
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    small_text = pygame.font.SysFont('Arial', 20)
    text_surf, text_rect = text_objects(msg, small_text)
    text_rect.center = (x + (w / 2), y + (h / 2))
    screen.blit(text_surf, text_rect)
    return running


def run_episode(num_games, screen, i_episode, running):
    run = True
    games_played = 0
    total_reward = 0
    episode_games = 0
    len_array = []

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        screen.fill(black)
        running = button(screen, 'Quit', 520, 0, 120, 60, white, white)
        if not running:
            break
        message_display(screen, 'training...', f'{i_episode} / 6000', 320, 120,
                        320, 200, white, size=50)
        pygame.display.flip()

        state = get_network_input(board.snake, board.apple)
        action_0 = model(state)
        rand = np.random.uniform(0, 1)
        if rand > args.epsilon:
            action = torch.argmax(action_0)
        else:
            action = np.random.randint(0, 5)

        # update_board_state the same snake till
        reward, done, len_of_snake = board.update_board_state(action)
        next_state = get_network_input(board.snake, board.apple)

        memory.push(state, action, reward, next_state, done)

        total_reward += reward

        episode_games += 1

        if board.game_over == True:
            games_played += 1
            len_array.append(len_of_snake)
            board.reset_game()

            if num_games == games_played:
                run = False

    avg_len_of_snake = np.mean(len_array)
    max_len_of_snake = np.max(len_array)
    return total_reward, avg_len_of_snake, max_len_of_snake, running


def learn(num_updates, batch_size):
    total_loss = 0

    for i in range(num_updates):
        optimizer.zero_grad()
        sample = memory.sample(batch_size)

        states, actions, rewards, next_states, dones = sample
        states = torch.cat([x.unsqueeze(0) for x in states], dim=0)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.cat([x.unsqueeze(0) for x in next_states])
        dones = torch.FloatTensor(dones)

        q_local = model.forward(states)
        next_q_value = model.forward(next_states)

        q_expected = q_local.gather(1, actions.unsqueeze(0).transpose(0, 1)).transpose(0, 1).squeeze(0)

        q_targets_next = torch.max(next_q_value, 1)[0] * (torch.ones(dones.size()) - dones)

        q_targets = rewards + args.gamma * q_targets_next

        loss = MSE(q_expected, q_targets)

        total_loss += loss
        loss.backward()
        optimizer.step()

    return total_loss


def train_dqn(screen):
    running = True
    scores_deque = deque(maxlen=100)
    scores_array = []
    avg_scores_array = []

    avg_len_array = []
    avg_max_len_array = []

    time_start = time.time()

    for i_episode in range(args.num_episodes + 1):
        score, avg_len, max_len, running = run_episode(args.games_in_episode, screen, i_episode, running)
        if not running:
            break
        scores_deque.append(score)
        scores_array.append(score)
        avg_len_array.append(avg_len)
        avg_max_len_array.append(max_len)

        avg_score = np.mean(scores_deque)
        avg_scores_array.append(avg_score)

        total_loss = learn(args.num_updates, args.batch_size)

        dt = int(time.time() - time_start)

        if i_episode % args.print_every == 0 and i_episode > 0:
            print('Ep.: {:6}, Loss: {:.3f}, Avg.Score: {:.2f}, Avg.LenOfSnake: {:.2f}, Max.LenOfSnake:  '
                  '{:.2f} Time: {:02}:{:02}:{:02}'.format(i_episode, total_loss, score, avg_len,
                                                          max_len, dt // 3600, dt % 3600 // 60, dt % 60))

        memory.truncate()

        # if i_episode % 250 == 0 and i_episode > 0:
        #     torch.save(model.state_dict(), './dir_chk_len/Snake_{}'.format(i_episode))
    return scores_array, avg_scores_array, avg_len_array, avg_max_len_array, running


