import math
import copy
import time
import json
from Connect4 import Connect4


class Connect4AI_Expectiminimax_TreeSaver:
    def __init__(self, game, max_depth=4):
        self.game = game
        self.max_depth = max_depth
        self.tree_data = None
        self.node_id_counter = 0

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

    def board_to_string(self, board):
        """Convert board to string representation"""
        result = []
        for r in range(self.game.length - 1, -1, -1):
            row = []
            for c in range(self.game.width):
                row.append(str(board[c][r]))
            result.append(''.join(row))
        return '\n'.join(result)

    def expectation_value(self, board, chosen_col, depth, maximizing, parent_move=None, parent_id=None):
        """
        Chance node: disc may fall left or right with given probabilities
        """
        # Create chance node
        chance_node_id = self.node_id_counter
        self.node_id_counter += 1
        
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

        # Create chance node structure
        chance_node = {
            'id': chance_node_id,
            'parent_id': parent_id,
            'depth': depth,
            'move': parent_move,
            'node_type': 'CHANCE',
            'chosen_col': chosen_col,
            'board_state': self.board_to_string(board),
            'probability_distribution': {},
            'outcomes': [],
            'expected_value': 0,
            'valid_moves': valid
        }

        # Redistribute probability if needed
        if total == 0:
            tmp = copy.deepcopy(self.game)
            tmp.board = board
            value = tmp.advanced_dynamic_heuristic()
            chance_node['expected_value'] = value
            chance_node['note'] = 'No valid outcomes'
            return chance_node, value

        for c in normalized:
            normalized[c] /= total

        chance_node['probability_distribution'] = {str(k): v for k, v in normalized.items()}

        expected_value = 0

        for move, prob in normalized.items():
            new_board = self.simulate(board, move, player)
            child_node, value = self.expectiminimax(new_board, depth - 1, not maximizing, move, chance_node_id)
            
            outcome = {
                'actual_column': move,
                'probability': prob,
                'value': value,
                'contribution': prob * value,
                'child_node': child_node
            }
            
            chance_node['outcomes'].append(outcome)
            expected_value += prob * value

        chance_node['expected_value'] = expected_value

        return chance_node, expected_value

    def expectiminimax(self, board, depth, maximizing, move=None, parent_id=None):
        """
        Expectiminimax core with tree structure capture
        """
        # Create node
        node_id = self.node_id_counter
        self.node_id_counter += 1
        
        valid = self.get_valid_moves(board)

        node = {
            'id': node_id,
            'parent_id': parent_id,
            'depth': depth,
            'move': move,
            'node_type': 'MAX' if maximizing else 'MIN',
            'board_state': self.board_to_string(board),
            'children': [],
            'value': None,
            'best_move': None,
            'terminal': False,
            'valid_moves': valid
        }

        if depth == 0 or self.is_terminal(board):
            tmp = copy.deepcopy(self.game)
            tmp.board = board
            value = tmp.advanced_dynamic_heuristic()
            
            node['terminal'] = True
            node['terminal_type'] = 'LEAF' if depth == 0 else 'TERMINAL'
            node['value'] = value
            return node, value

        if maximizing:
            best_value = -math.inf
            best_move = None

            for child_move in valid:
                chance_node, value = self.expectation_value(board, child_move, depth, True, child_move, node_id)
                
                node['children'].append(chance_node)
                
                if value > best_value:
                    best_value = value
                    best_move = child_move

            node['value'] = best_value
            node['best_move'] = best_move
            return node, best_value

        else:
            # Minimizing player (opponent)
            best_value = math.inf
            best_move = None

            for child_move in valid:
                chance_node, value = self.expectation_value(board, child_move, depth, False, child_move, node_id)
                
                node['children'].append(chance_node)
                
                if value < best_value:
                    best_value = value
                    best_move = child_move

            node['value'] = best_value
            node['best_move'] = best_move
            return node, best_value

    def best_move(self):
        """Get the best move and save the tree"""
        self.node_id_counter = 0
        
        print("\n" + "="*70)
        print("Running Expectiminimax and saving tree...")
        print("="*70)
        
        start_time = time.time()
        
        tree_root, value = self.expectiminimax(
            self.game.board,
            self.max_depth,
            maximizing=(self.game.turn == 1),
            move=None,
            parent_id=None
        )
        
        elapsed = time.time() - start_time
        
        # Save tree data
        self.tree_data = {
            'root': tree_root,
            'metadata': {
                'algorithm': 'expectiminimax',
                'max_depth': self.max_depth,
                'total_nodes': self.node_id_counter,
                'best_move': tree_root['best_move'],
                'expected_value': value,
                'computation_time': elapsed,
                'current_turn': self.game.turn,
                'board_width': self.game.width,
                'board_height': self.game.length,
                'note': 'Includes CHANCE nodes for probabilistic outcomes'
            }
        }
        
        print(f"Best Move: Column {tree_root['best_move']} | Expected Value: {value:.1f}")
        print(f"Nodes Explored: {self.node_id_counter} (includes chance nodes)")
        print(f"Time: {elapsed:.3f} seconds")
        print("="*70 + "\n")

        if tree_root['best_move'] is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]
            return 0

        return tree_root['best_move']

    def save_tree_to_json(self, filename='expectiminimax_tree.json'):
        """Save the tree to a JSON file"""
        if self.tree_data is None:
            print("No tree data available. Run best_move() first.")
            return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.tree_data, f, indent=2)
            print(f"✓ Tree saved to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error saving tree: {e}")
            return False

    def save_tree_to_python(self, filename='expectiminimax_tree.py'):
        """Save the tree as a Python dictionary"""
        if self.tree_data is None:
            print("No tree data available. Run best_move() first.")
            return False
        
        try:
            with open(filename, 'w') as f:
                f.write("# Auto-generated expectiminimax tree data\n")
                f.write("# Import this in your GUI: from expectiminimax_tree import tree_data\n\n")
                f.write(f"tree_data = {repr(self.tree_data)}")
            print(f"✓ Tree saved to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error saving tree: {e}")
            return False

    def get_tree_stats(self):
        """Get statistics about the tree"""
        if self.tree_data is None:
            return None
        
        def count_nodes(node, stats):
            stats['total'] += 1
            
            node_type = node.get('node_type', 'UNKNOWN')
            
            if node_type == 'MAX':
                stats['max_nodes'] += 1
            elif node_type == 'MIN':
                stats['min_nodes'] += 1
            elif node_type == 'CHANCE':
                stats['chance_nodes'] += 1
            
            if node.get('terminal', False):
                stats['terminal'] += 1
            
            # For chance nodes, count outcomes
            for outcome in node.get('outcomes', []):
                count_nodes(outcome['child_node'], stats)
            
            # For regular nodes, count children
            for child in node.get('children', []):
                count_nodes(child, stats)
        
        stats = {
            'total': 0,
            'max_nodes': 0,
            'min_nodes': 0,
            'chance_nodes': 0,
            'terminal': 0
        }
        
        count_nodes(self.tree_data['root'], stats)
        
        return stats


if __name__ == "__main__":
    x = Connect4()
    
    # Make some moves
    x.play(3)
    x.play(3)
    x.play(2)
    
    print("Current board:")
    print(x)
    
    ai = Connect4AI_Expectiminimax_TreeSaver(x, max_depth=3)  # Lower depth for expectiminimax
    
    # Get best move (this builds the tree)
    col = ai.best_move()
    
    # Save tree in both formats
    ai.save_tree_to_json('expectiminimax_tree.json')
    ai.save_tree_to_python('expectiminimax_tree.py')
    
    # Print statistics
    stats = ai.get_tree_stats()
    print("\nTree Statistics:")
    print(f"  Total nodes explored: {stats['total']}")
    print(f"  MAX nodes: {stats['max_nodes']}")
    print(f"  MIN nodes: {stats['min_nodes']}")
    print(f"  CHANCE nodes: {stats['chance_nodes']}")
    print(f"  Terminal nodes: {stats['terminal']}")
    
    print("\n" + "="*70)
    print("Expectiminimax tree saved!")
    print("="*70)
    print("\nNote: Expectiminimax trees include CHANCE nodes with probability")
    print("      distributions for each possible outcome.")