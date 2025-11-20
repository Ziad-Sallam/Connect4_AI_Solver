import math
import copy
import time

from Connect4 import Connect4


class Connect4AI_Expectiminimax:
    def __init__(self, game, max_depth=4):
        self.game = game
        self.max_depth = max_depth

    # --------------------
    # Valid moves
    # --------------------
    def get_valid_moves(self, board):
        valid = []
        for col in range(self.game.width):
            if board[col][self.game.length - 1] == 0:
                valid.append(col)
        return valid

    # --------------------
    # Simulate gravity drop
    # --------------------
    def simulate(self, board, col, player):
        new = copy.deepcopy(board)
        for r in range(self.game.length):
            if new[col][r] == 0:
                new[col][r] = player
                break
        return new

    # --------------------
    # Is terminal?
    # --------------------
    def is_terminal(self, board):
        if len(self.get_valid_moves(board)) == 0:
            return True

        temp = copy.deepcopy(self.game)
        temp.board = board
        temp.calculate_score()

        if temp.score_1 > 0 or temp.score_2 > 0:
            return True

        return False

    # --------------------
    # Expectation node:
    # Disc may fall left or right with given probabilities
    # --------------------
    def expectation_value(self, board, chosen_col, depth, maximizing):
        player = 1 if maximizing else 2
        valid = self.get_valid_moves(board)

        # Base probability model
        probs = {
            chosen_col: 0.6,
            chosen_col - 1: 0.2,
            chosen_col + 1: 0.2
        }

        # Filter out invalid moves
        total = 0
        normalized = {}
        for c, p in probs.items():
            if c in valid:
                normalized[c] = p
                total += p

        # redistribute probability if needed
        if total == 0:
            return None, self.game.advanced_dynamic_heuristic()

        for c in normalized:
            normalized[c] /= total

        expected_value = 0

        for move, prob in normalized.items():
            new_board = self.simulate(board, move, player)
            _, value = self.expectiminimax(new_board, depth - 1, not maximizing)
            expected_value += prob * value

        return None, expected_value

    # --------------------
    # Expectiminimax core
    # --------------------
    def expectiminimax(self, board, depth, maximizing):
        valid = self.get_valid_moves(board)

        if depth == 0 or self.is_terminal(board):
            tmp = copy.deepcopy(self.game)
            tmp.board = board
            return None, tmp.advanced_dynamic_heuristic()

        if maximizing:
            best_value = -math.inf
            best_move = None

            for move in valid:
                _, value = self.expectation_value(board, move, depth, True)
                if value > best_value:
                    best_value = value
                    best_move = move

            return best_move, best_value

        else:
            # Minimizing player (opponent)
            best_value = math.inf
            best_move = None

            for move in valid:
                _, value = self.expectation_value(board, move, depth, False)
                if value < best_value:
                    best_value = value
                    best_move = move

            return best_move, best_value

    # --------------------
    # Best move wrapper
    # --------------------
    def best_move(self):
        move, _ = self.expectiminimax(
            self.game.board,
            self.max_depth,
            maximizing=(self.game.turn == 1)
        )

        if move is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]
            return 0

        return move


x = Connect4()
ai = Connect4AI_Expectiminimax(x, max_depth=4)

while True:
    print(x)

    if x.turn == 1:
        col = int(input("Player 1 column: "))
    else:

        print("AI thinking...")
        st_time = time.time()
        col = ai.best_move()

        print("AI thinking took {} seconds".format(time.time() - st_time))


    x.play(col)