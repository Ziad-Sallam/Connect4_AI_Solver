import math
import copy
import time


class Connect4AI_NoPruning:
    def __init__(self, game, max_depth=4):
        self.game = game
        self.max_depth = max_depth

    # -----------------------
    # Get valid moves (columns)
    # -----------------------
    def get_valid_moves(self, board):
        moves = []
        for col in range(self.game.width):
            if board[col][self.game.length - 1] == 0:  # top cell empty
                moves.append(col)
        return moves

    # -----------------------
    # Simulate dropping a piece
    # -----------------------
    def simulate_move(self, board, col, player):
        new_board = copy.deepcopy(board)
        for row in range(self.game.length):
            if new_board[col][row] == 0:
                new_board[col][row] = player
                break
        return new_board

    # -----------------------
    # Terminal check
    # -----------------------
    def is_terminal(self, board):
        # no valid moves OR someone won
        if len(self.get_valid_moves(board)) == 0:
            return True

        # check score function (use your built-in scoring)
        temp_game = copy.deepcopy(self.game)
        temp_game.board = board
        temp_game.calculate_score()

        if temp_game.score_1 > 0 or temp_game.score_2 > 0:
            return True

        return False

    # -----------------------
    # Minimax (NO pruning)
    # -----------------------
    def minimax(self, board, depth, maximizing):
        valid_moves = self.get_valid_moves(board)

        if depth == 0 or self.is_terminal(board):
            temp_game = copy.deepcopy(self.game)
            temp_game.board = board
            return None, temp_game.advanced_dynamic_heuristic()

        if maximizing:
            best_value = -math.inf
            best_move = None

            for move in valid_moves:
                new_board = self.simulate_move(board, move, 1)
                _, value = self.minimax(new_board, depth - 1, False)

                if value > best_value:
                    best_value = value
                    best_move = move

            return best_move, best_value

        else:
            best_value = math.inf
            best_move = None

            for move in valid_moves:
                new_board = self.simulate_move(board, move, 2)
                _, value = self.minimax(new_board, depth - 1, True)

                if value < best_value:
                    best_value = value
                    best_move = move

            return best_move, best_value

    # -----------------------
    # Pick the best move
    # -----------------------
    def best_move(self):
        move, _ = self.minimax(
            board=self.game.board,
            depth=self.max_depth,
            maximizing=(self.game.turn == 1)
        )

        # Fallback if minimax returns None
        if move is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]
            return 0

        return move


from Connect4 import Connect4

x = Connect4()
ai = Connect4AI_NoPruning(x, max_depth=6)

while True:
    print(x)

    if x.turn == 1:
        col = int(input("Player 1 move: "))
    else:
        print("AI thinking...")
        st_time = time.time()
        col = ai.best_move()
        print("AI thinking took {} seconds".format(time.time() - st_time))

    x.play(col)
