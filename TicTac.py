import json
import random
from collections import defaultdict
from tqdm import tqdm  # For progress bar

class QLearningBot:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay  # Exploration rate decay
        self.min_epsilon = 0.1  # Minimum exploration rate

    def choose_action(self, state):
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return None  # No action possible

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
            state = None
            for move in game:
                board = move['board']
                action = move['action']
                reward = move['reward']
                next_state = board  # Keep board as a list of lists
                if state is not None:
                    self.update_q_value(state, action, reward, next_state)
                state = next_state
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

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

    def save_q_table(self, filename='q_table.json'):
        with open(filename, 'w') as file:
            json.dump(self.q_table, file)

    def load_q_table(self, filename='q_table.json'):
        try:
            with open(filename, 'r') as file:
                self.q_table = json.load(file)
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

class TicTacToeGame:
    def __init__(self, num_games=1000):
        self.num_games = num_games
        self.q_learning_bot = QLearningBot()
        self.random_bot = RandomBot()
        self.saved_games = []

    def play_game(self, training_mode=True):
        board = [[' ' for _ in range(3)] for _ in range(3)]
        current_player = 'X'  # Assume Q-learning bot is 'X', random bot is 'O'
        game_over = False
        game_history = []

        while not game_over:
            if current_player == 'X':
                action = self.q_learning_bot.choose_action(board)
            else:
                action = self.random_bot.choose_action(board)

            if action not in self.get_possible_actions(board):
                continue

            board[action[0]][action[1]] = current_player

            winner = self.q_learning_bot.check_winner(board)
            reward = 0
            if winner:
                if winner == 'X':
                    reward = 1
                elif winner == 'O':
                    reward = -1
                game_over = True
            elif self.q_learning_bot.is_draw(board):
                reward = 0.5
                game_over = True

            if training_mode:
                game_history.append({
                    'board': [row[:] for row in board],
                    'action': action,
                    'reward': reward
                })

            current_player = 'O' if current_player == 'X' else 'X'

        if training_mode:
            self.saved_games.append(game_history)

    def get_possible_actions(self, board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

    def train(self):
        print("Training started...")
        for _ in tqdm(range(self.num_games)):
            self.play_game(training_mode=True)
        self.q_learning_bot.train_from_games(self.saved_games)
        self.q_learning_bot.save_q_table()

    def play_against_human(self):
        board = [[' ' for _ in range(3)] for _ in range(3)]
        current_player = 'X'  # Q-learning bot starts
        game_over = False

        while not game_over:
            self.print_board(board)
            if current_player == 'X':
                print("\nBot's turn:")
                action = self.q_learning_bot.choose_action(board)
            else:
                print("\nYour turn:")
                action = self.get_human_action(board)

            if action and action in self.get_possible_actions(board):
                board[action[0]][action[1]] = current_player

                winner = self.q_learning_bot.check_winner(board)
                if winner:
                    self.print_board(board)
                    print(f"\n{winner} wins!")
                    game_over = True
                elif self.q_learning_bot.is_draw(board):
                    self.print_board(board)
                    print("\nIt's a draw!")
                    game_over = True
                else:
                    current_player = 'O' if current_player == 'X' else 'X'

    def get_human_action(self, board):
        while True:
            try:
                move = input("Enter your move (row and column numbers separated by space, e.g., '0 1'): ")
                row, col = map(int, move.split())
                if (row, col) in self.get_possible_actions(board):
                    return (row, col)
                else:
                    print("Invalid move! Please enter a valid move.")
            except ValueError:
                print("Invalid input! Please enter numbers separated by a space.")

    def print_board(self, board):
        print("\nCurrent board:")
        for row in board:
            print(' | '.join(row))
            print('-' * 5)

if __name__ == "__main__":
    choice = input("Enter 'train' to train the bot or 'play' to play against the bot: ").strip().lower()

    if choice == 'train':
        num_games = int(input("Enter the number of games to train the Q-Learning Bot against the Random Bot: "))
        game = TicTacToeGame(num_games)
        game.train()
    elif choice == 'play':
        game = TicTacToeGame()
        game.q_learning_bot.load_q_table()
        game.play_against_human()
    else:
        print("Invalid choice! Please enter either 'train' or 'play'.")
