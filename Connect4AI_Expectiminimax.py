import math
import copy
import time
from Connect4 import Connect4


class Connect4AI_Expectiminimax:
    def __init__(self, game, max_depth=4, show_tree=True):
        self.game = game
        self.max_depth = max_depth
        self.show_tree = show_tree
        self.node_count = 0

    def get_valid_moves(self, board):
        valid = []
        for col in range(self.game.width):
            if board[col][self.game.length - 1] == 0:
                valid.append(col)
        return valid

    def simulate(self, board, col, player):
        new = copy.deepcopy(board)
        for r in range(self.game.length):
            if new[col][r] == 0:
                new[col][r] = player
                break
        return new

    def is_terminal(self, board):
        if len(self.get_valid_moves(board)) == 0:
            return True

        temp = copy.deepcopy(self.game)
        temp.board = board
        temp.calculate_score()

        if temp.score_1 > 0 or temp.score_2 > 0:
            return True

        return False

    def print_node(self, depth, move, value, node_type, probability=None):
        """Print a node in the search tree"""
        if not self.show_tree:
            return
        
        indent = "  " * (self.max_depth - depth)
        self.node_count += 1
        
        # Node type indicator
        if node_type == "MAX":
            type_symbol = "▲"
        elif node_type == "MIN":
            type_symbol = "▼"
        elif node_type == "CHANCE":
            type_symbol = "◆"
        else:
            type_symbol = "●"
        
        # Format the move
        if move is not None:
            move_str = f"Col {move}"
        else:
            move_str = "ROOT"
        
        # Format the value
        if value == math.inf:
            value_str = "+∞"
        elif value == -math.inf:
            value_str = "-∞"
        else:
            value_str = f"{value:+.1f}"
        
        # Build the output string
        output = f"{indent}{type_symbol} [{move_str}]"
        
        # Add probability for chance nodes
        if probability is not None:
            output += f" P={probability:.1%}"
        
        output += f" Value: {value_str}"
        
        print(output)

    def expectation_value(self, board, chosen_col, depth, maximizing, parent_move=None):
        """
        Chance node: disc may fall left or right with given probabilities
        """
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

        # Redistribute probability if needed
        if total == 0:
            tmp = copy.deepcopy(self.game)
            tmp.board = board
            value = tmp.advanced_dynamic_heuristic()
            self.print_node(depth, parent_move, value, "CHANCE (no valid)")
            return None, value

        for c in normalized:
            normalized[c] /= total

        # Print chance node
        self.print_node(depth, parent_move, 0, "CHANCE")

        expected_value = 0

        for move, prob in normalized.items():
            new_board = self.simulate(board, move, player)
            _, value = self.expectiminimax(new_board, depth - 1, not maximizing, move)
            
            # Print each outcome with its probability
            indent = "  " * (self.max_depth - depth + 1)
            print(f"{indent}  → Outcome Col {move}: P={prob:.1%}, V={value:+.1f}, Contrib={prob*value:+.1f}")
            
            expected_value += prob * value

        # Print final expected value
        indent = "  " * (self.max_depth - depth)
        print(f"{indent}  Expected Value: {expected_value:+.1f}")

        return None, expected_value

    def expectiminimax(self, board, depth, maximizing, move=None):
        """
        Expectiminimax core with tree visualization
        """
        valid = self.get_valid_moves(board)

        if depth == 0 or self.is_terminal(board):
            tmp = copy.deepcopy(self.game)
            tmp.board = board
            value = tmp.advanced_dynamic_heuristic()
            
            node_label = "LEAF" if depth == 0 else "TERMINAL"
            self.print_node(depth, move, value, node_label)
            return None, value

        node_type = "MAX" if maximizing else "MIN"

        if maximizing:
            best_value = -math.inf
            best_move = None
            
            self.print_node(depth, move, best_value, node_type)

            for child_move in valid:
                _, value = self.expectation_value(board, child_move, depth, True, child_move)
                if value > best_value:
                    best_value = value
                    best_move = child_move

            return best_move, best_value

        else:
            # Minimizing player (opponent)
            best_value = math.inf
            best_move = None
            
            self.print_node(depth, move, best_value, node_type)

            for child_move in valid:
                _, value = self.expectation_value(board, child_move, depth, False, child_move)
                if value < best_value:
                    best_value = value
                    best_move = child_move

            return best_move, best_value

    def best_move(self):
        """Get the best move and print the search tree"""
        self.node_count = 0
        
        if self.show_tree:
            print("\n" + "="*70)
            print("EXPECTIMINIMAX SEARCH TREE (with Chance Nodes)")
            print("="*70)
            print("Legend: ▲=MAX  ▼=MIN  ◆=CHANCE  ●=LEAF/TERMINAL")
            print("="*70)
        
        start_time = time.time()
        
        move, value = self.expectiminimax(
            self.game.board,
            self.max_depth,
            maximizing=(self.game.turn == 1),
            move=None
        )
        
        elapsed = time.time() - start_time
        
        if self.show_tree:
            print("="*70)
            print(f"Best Move: Column {move} | Expected Value: {value:.1f}")
            print(f"Nodes Explored: {self.node_count}")
            print(f"Time: {elapsed:.3f} seconds")
            print("="*70 + "\n")

        if move is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]
            return 0

        return move


if __name__ == "__main__":
    x = Connect4()
    ai = Connect4AI_Expectiminimax(x, max_depth=3, show_tree=True)

    while True:
        print(x)

        if x.turn == 1:
            col = int(input("Player 1 column: "))
        else:
            print("\nAI thinking...")
            col = ai.best_move()

        x.play(col)