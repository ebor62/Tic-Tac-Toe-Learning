# game_play.py

import random
from learning import QLearningBot

class TicTacToeGame:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.bot = QLearningBot()
        self.current_player = 'X'  # X starts the game

    def print_board(self):
        print("\nCurrent board:")
        for row in self.board:
            print(' | '.join(row))
            print('-' * 5)

    def check_winner(self):
        # Check rows, columns, and diagonals for a winner
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                return self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]

        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]

        return None

    def is_draw(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def make_move(self, row, col, player):
        if self.board[row][col] == ' ':
            self.board[row][col] = player
            return True
        return False

    def player_move(self):
        while True:
            try:
                move = input("Enter your move (row and column numbers separated by space, e.g., '0 1'): ")
                row, col = map(int, move.split())
                if row in range(3) and col in range(3):
                    if self.make_move(row, col, 'O'):
                        break
                    else:
                        print("Invalid move! That position is already taken.")
                else:
                    print("Invalid input! Please enter numbers between 0 and 2.")
            except ValueError:
                print("Invalid input! Please enter two numbers separated by space.")

    def bot_move(self):
        action = self.bot.choose_action(self.board)
        if action:
            row, col = action
            self.make_move(row, col, 'X')
        else:
            print("Bot has no possible moves.")

    def play_game(self):
        print("Welcome to Tic-Tac-Toe!")
        self.print_board()

        while True:
            if self.current_player == 'O':
                print("\nYour turn:")
                self.player_move()
            else:
                print("\nBot's turn:")
                self.bot_move()

            self.print_board()

            winner = self.check_winner()
            if winner:
                print(f"\n{winner} wins!")
                break

            if self.is_draw():
                print("\nIt's a draw!")
                break

            # Switch players
            self.current_player = 'O' if self.current_player == 'X' else 'X'

        print("Game over!")

# Example usage
if __name__ == "__main__":
    game = TicTacToeGame()
    game.play_game()
