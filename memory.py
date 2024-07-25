# memory.py

class Memory:
    def __init__(self):
        self.memory = {}

    def store_game(self, board_state, result):
        """
        Store the game board state and its result.
        
        :param board_state: A list of lists representing the 3x3 Tic-Tac-Toe board.
        :param result: The outcome of the game ('X wins', 'O wins', 'Draw', etc.).
        """
        state_tuple = tuple(tuple(row) for row in board_state)
        self.memory[state_tuple] = result

    def retrieve_game(self, board_state):
        """
        Retrieve the result for a given board state.
        
        :param board_state: A list of lists representing the 3x3 Tic-Tac-Toe board.
        :return: The game result if found, otherwise None.
        """
        state_tuple = tuple(tuple(row) for row in board_state)
        return self.memory.get(state_tuple, None)

    def print_board(self, board_state):
        """
        Print the board in a grid format.
        
        :param board_state: A list of lists representing the 3x3 Tic-Tac-Toe board.
        """
        for row in board_state:
            print(' | '.join(cell if cell != ' ' else ' ' for cell in row))
            print('-' * 5)
