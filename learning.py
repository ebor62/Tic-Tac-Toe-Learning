# learning.py

import random
from memory import Memory

class QLearningBot:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.995):
        self.memory = Memory()
        self.q_values = {}  # Q-values storage
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = 0.01

    def get_q_value(self, state, action):
        return self.q_values.get((tuple(tuple(row) for row in state), action), 0.0)

    def update_q_value(self, state, action, reward, next_state):
        possible_actions = self.get_possible_actions(next_state)
        max_next_q_value = max((self.get_q_value(next_state, a) for a in possible_actions), default=0)
        current_q_value = self.get_q_value(state, action)
        new_q_value = current_q_value + self.learning_rate * (reward + self.discount_factor * max_next_q_value - current_q_value)
        self.q_values[(tuple(tuple(row) for row in state), action)] = new_q_value

    def get_possible_actions(self, state):
        return [(i, j) for i in range(3) for j in range(3) if state[i][j] == ' ']

    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.get_possible_actions(state))
        else:
            possible_actions = self.get_possible_actions(state)
            if possible_actions:
                return max(possible_actions, key=lambda action: self.get_q_value(state, action))
            return None

    def analyze_games(self):
        for state, result in self.memory.memory.items():
            reward = self.get_reward(result)
            actions = self.get_possible_actions(state)
            for action in actions:
                next_state = self.apply_action(state, action, 'X')
                self.update_q_value(state, action, reward, next_state)

    def get_reward(self, result):
        if result == 'X wins':
            return 1
        elif result == 'O wins':
            return -1
        else:
            return 0

    def apply_action(self, state, action, player):
        new_state = [row[:] for row in state]
        new_state[action[0]][action[1]] = player
        return new_state

    def train_bot(self):
        self.analyze_games()
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

# Example usage
if __name__ == "__main__":
    bot = QLearningBot()
    bot.train_bot()
    # Save Q-values or use them in your bot's gameplay
    print(f"Number of games saved: {bot.memory.get_num_games()}")
