import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--num_episodes', type=int, default=6000, help='Number of episodes')
parser.add_argument('--num_updates', type=int, default=500, help='Number of updates')
parser.add_argument('--print_every', type=int, default=10, help='Print results every x episodes')
parser.add_argument('--games_in_episode', type=int, default=30, help='Number of games in each episode')
parser.add_argument('--batch_size', type=int, default=20, help='Batch size')
parser.add_argument('--epsilon', type=float, default=0.1, help='Epsilon for exploration')
parser.add_argument('--grid_size', type=int, default=20, help='Grid size')
parser.add_argument('--explore', type=int, default=4000000, help='Explore parameter')
parser.add_argument('--n_actions', type=int, default=4, help='Number of actions')
parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate')
parser.add_argument('--gamma', type=float, default=0.9, help='Gamma')
parser.add_argument('--replace_target_iter', type=int, default=2000, help='Replace target network iteration')
parser.add_argument('--memory_size', type=int, default=10000, help='Memory size')
parser.add_argument('--final_epsilon', type=float, default=0.001, help='Final epsilon')
parser.add_argument('--initial_epsilon', type=float, default=0.001, help='Initial epsilon')
parser.add_argument('--observe', type=int, default=1000, help='Observation steps')
parser.add_argument('--model_file', type=str, default='./model/snake', help='Model file path')

args = parser.parse_args()

