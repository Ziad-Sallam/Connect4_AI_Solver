import copy
import math
import time

from Connect4 import Connect4


class Connect4AI:
    def __init__(self, game, max_depth=4):
        """
        game: instance of Connect4 class
        max_depth: how deep minimax will search
        """
        self.game = game
        self.max_depth = max_depth

    # ------------------------------
    # Generate valid moves
    # ------------------------------
    def get_valid_moves(self, board):
        moves = []
        for c in range(self.game.width):
            if board[c][self.game.length - 1] == 0:  # column not full
                moves.append(c)
        return moves

    # ------------------------------
    # Apply move on a copied board
    # ------------------------------
    def simulate_move(self, board, col, player):
        new_board = copy.deepcopy(board)
        # find first empty row
        row = 0
        while row < self.game.length and new_board[col][row] != 0:
            row += 1
        if row < self.game.length:
            new_board[col][row] = player
        return new_board

    # ------------------------------
    # Terminal state detection
    # ------------------------------
    def is_terminal(self, board):
        g = self.game

        # check win by scanning windows of 4
        dirs = [(1,0),(0,1),(1,1),(1,-1)]
        for x in range(g.width):
            for y in range(g.length):
                p = board[x][y]
                if p == 0: continue

                for dx, dy in dirs:
                    count = 1
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < g.width and 0 <= ny < g.length and board[nx][ny] == p:
                        count += 1
                        nx += dx
                        ny += dy
                    if count >= 4:
                        return True, p  # terminal & winner

        # draw?
        full = all(board[c][g.length - 1] != 0 for c in range(g.width))
        if full:
            return True, 0

        return False, None

    # ------------------------------
    # Minimax + Alpha Beta
    # ------------------------------
    def minimax(self, board, depth, alpha, beta, maximizing):
        terminal, winner = self.is_terminal(board)

        # terminal outcome
        if terminal:
            if winner == 1:
                return None, 10**9   # huge positive
            elif winner == 2:
                return None, -10**9  # huge negative
            else:
                return None, 0       # draw

        if depth == 0:
            # evaluate using game’s heuristic
            old_board = self.game.board
            self.game.board = board
            v = self.game.advanced_dynamic_heuristic()
            self.game.board = old_board
            return None, v

        valid_moves = self.get_valid_moves(board)

        if maximizing:
            best_val = -math.inf
            best_move = None

            for move in valid_moves:
                new_b = self.simulate_move(board, move, 1)
                _, eval = self.minimax(new_b, depth - 1, alpha, beta, False)

                if eval > best_val:
                    best_val = eval
                    best_move = move

                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break

            return best_move, best_val

        else:
            best_val = math.inf
            best_move = None

            for move in valid_moves:
                new_b = self.simulate_move(board, move, 2)
                _, eval = self.minimax(new_b, depth - 1, alpha, beta, True)

                if eval < best_val:
                    best_val = eval
                    best_move = move

                beta = min(beta, best_val)
                if beta <= alpha:
                    break

            return best_move, best_val

    # ------------------------------
    # Public method to get best move
    # ------------------------------
    def best_move(self):
        move, _ = self.minimax(
            board=self.game.board,
            depth=self.max_depth,
            alpha=-math.inf,
            beta=math.inf,
            maximizing=(self.game.turn == 1)
        )

        # If minimax fails to find a move (terminal node), pick a safe fallback
        if move is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]  # pick first available
            return 0  # emergency default

        return move




x = Connect4()
ai = Connect4AI(x, max_depth=6)

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
