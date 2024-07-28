import json
import random
from tqdm import tqdm
from collections import defaultdict

class QLearningBot:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.memory = Memory()

    def choose_action(self, state):
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return None
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_actions)
        q_values = {a: self.get_q_value(state, a) for a in possible_actions}
        max_q_value = max(q_values.values(), default=0)
        best_actions = [a for a, q in q_values.items() if q == max_q_value]
        return random.choice(best_actions) if best_actions else None

    def get_possible_actions(self, state):
        return [(i, j) for i in range(3) for j in range(3) if state[i][j] == ' ']

    def get_q_value(self, state, action):
        state_key = str(state)
        action_key = str(action)
        return self.q_table[state_key].get(action_key, 0.0)

    def update_q_value(self, state, action, reward, next_state):
        best_next_action = self.choose_action(next_state)
        best_next_q_value = self.get_q_value(next_state, best_next_action) if best_next_action else 0
        current_q_value = self.get_q_value(state, action)
        new_q_value = (1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * best_next_q_value)
        self.q_table[str(state)][str(action)] = new_q_value

    def train_from_games(self, saved_games):
        for game in saved_games:
            if not isinstance(game, dict):
                print(f"Unexpected game format: {game}")
                continue

            state = None
            for move in game.get('moves', []):
                if not isinstance(move, dict):
                    print(f"Unexpected move format: {move}")
                    continue

                if 'board' not in move or 'action' not in move or 'reward' not in move:
                    print(f"Missing keys in move: {move}")
                    continue

                board = move['board']
                action = move['action']
                reward = move['reward']

                print(f"Training with board: {board}, action: {action}, reward: {reward}")

                if state is not None:
                    self.update_q_value(state, action, reward, board)
                state = board

    def save_q_table(self, filename='q_table.json'):
        with open(filename, 'w') as file:
            json.dump(self.q_table, file)

    def load_q_table(self, filename='q_table.json'):
        try:
            with open(filename, 'r') as file:
                self.q_table = json.load(file)
                self.q_table = defaultdict(lambda: defaultdict(float), self.q_table)
        except FileNotFoundError:
            print("Q-table file not found. Starting with an empty Q-table.")
        except json.JSONDecodeError:
            print("Error decoding JSON. The file may be corrupted or improperly formatted.")
            self.q_table = defaultdict(lambda: defaultdict(float))

class RandomBot:
    def choose_action(self, board):
        possible_actions = self.get_possible_actions(board)
        return random.choice(possible_actions) if possible_actions else None

    def get_possible_actions(self, board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

class Memory:
    def __init__(self):
        self.memory = {}
        self.num_games = 0

    def store_game(self, board_state, result):
        state_tuple = tuple(tuple(row) for row in board_state)
        self.memory[state_tuple] = result
        self.num_games += 1

    def get_num_games(self):
        return self.num_games

class TicTacToeGame:
    def __init__(self):
        self.q_learning_bot = QLearningBot()
        self.random_bot = RandomBot()
        self.saved_games = []
        self.memory = self.q_learning_bot.memory
        self.num_games = 0

    def print_board(self, board):
        print("\nCurrent board:")
        for row in board:
            print(' | '.join(cell if cell != ' ' else ' ' for cell in row))
            print('-' * 5)

    def check_winner(self, board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]
        return None

    def is_draw(self, board):
        return all(cell != ' ' for row in board for cell in row)

    def get_possible_actions(self, board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

    def play_game(self, training_mode=False):
        board = [[' ' for _ in range(3)] for _ in range(3)]
        current_player = 'X'
        game_over = False

        while not game_over:
            if current_player == 'X':
                action = self.q_learning_bot.choose_action(board)
            else:
                if not training_mode:
                    self.print_board(board)
                    move = input(f"Player {current_player}'s turn (row,col): ").strip()
                    try:
                        row, col = map(int, move.split(','))
                    except ValueError:
                        print("Invalid input format. Please enter as row,col (e.g., 1,1).")
                        continue
                    if not (0 <= row < 3 and 0 <= col < 3):
                        print("Move out of bounds. Please enter values between 0 and 2.")
                        continue
                    action = (row, col)
                else:
                    action = self.random_bot.choose_action(board)

            if action not in self.get_possible_actions(board):
                print("Invalid move. Try again.")
                continue

            board[action[0]][action[1]] = current_player
            reward = 0
            winner = self.check_winner(board)
            if winner:
                if winner == 'X':
                    reward = 1
                elif winner == 'O':
                    reward = -1
                game_over = True
            elif self.is_draw(board):
                reward = 0.5
                game_over = True

            if training_mode:
                self.saved_games.append({
                    'moves': [{
                        'board': [row[:] for row in board],
                        'action': action,
                        'reward': reward
                    }]
                })

            current_player = 'O' if current_player == 'X' else 'X'

        self.print_board(board)
        if winner:
            print(f"Game over. Winner: {winner}")
        else:
            print("Game over. It's a draw!")

    def save_games(self, filename='saved_games.json'):
        with open(filename, 'w') as file:
            json.dump(self.saved_games, file)

    def load_games(self, filename='saved_games.json'):
        try:
            with open(filename, 'r') as file:
                self.saved_games = json.load(file)
        except FileNotFoundError:
            print("Saved games file not found. Starting with an empty list of saved games.")
        except json.JSONDecodeError:
            print("Error decoding JSON. The file may be corrupted or improperly formatted.")
            self.saved_games = []

    def train(self):
        self.load_games()  # Load previously saved games
        print(f"Number of games loaded: {len(self.saved_games)}")
        print("Training started...")
        self.saved_games = []  # Reset saved games before starting training
        for _ in tqdm(range(self.num_games)):
            self.play_game(training_mode=True)
        self.save_games()  # Save new games
        self.q_learning_bot.train_from_games(self.saved_games)
        self.q_learning_bot.save_q_table()
        print("Training completed!")

if __name__ == "__main__":
    game = TicTacToeGame()
    while True:
        print(f"\nNumber of games saved: {game.memory.get_num_games()}")
        choice = input("Enter 'train' to train the bot, 'play' to play against the bot, or 'exit' to quit: ").strip().lower()
        if choice == 'train':
            num_games = int(input("Enter the number of games to train the Q-Learning Bot against the Random Bot: "))
            game.num_games = num_games
            game.train()
        elif choice == 'play':
            game.play_game(training_mode=False)
        elif choice == 'exit':
            print("Exiting the game.")
            break
        else:
            print("Invalid choice. Please enter 'train', 'play', or 'exit'.")
