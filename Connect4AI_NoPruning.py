import math
import copy
import time
import json
from Connect4 import Connect4


class Connect4AI_NoPruning_TreeSaver:
    def __init__(self, game, max_depth=4):
        self.game = game
        self.max_depth = max_depth
        self.tree_data = None
        self.node_id_counter = 0

    def get_valid_moves(self, board):
        moves = []
        for col in range(self.game.width):
            if board[col][self.game.length - 1] == 0:
                moves.append(col)
        return moves

    def simulate_move(self, board, col, player):
        new_board = copy.deepcopy(board)
        for row in range(self.game.length):
            if new_board[col][row] == 0:
                new_board[col][row] = player
                break
        return new_board

    def is_terminal(self, board):
        if len(self.get_valid_moves(board)) == 0:
            return True

        temp_game = copy.deepcopy(self.game)
        temp_game.board = board
        temp_game.calculate_score()

        if temp_game.score_1 > 0 or temp_game.score_2 > 0:
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

    def minimax(self, board, depth, maximizing, move=None, parent_id=None):
        """Minimax WITHOUT pruning - explores entire tree"""
        
        # Create node
        node_id = self.node_id_counter
        self.node_id_counter += 1
        
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
            'terminal': False
        }
        
        valid_moves = self.get_valid_moves(board)

        # Terminal check
        if depth == 0 or self.is_terminal(board):
            temp_game = copy.deepcopy(self.game)
            temp_game.board = board
            value = temp_game.advanced_dynamic_heuristic()
            
            node['terminal'] = True
            node['terminal_type'] = 'LEAF' if depth == 0 else 'TERMINAL'
            node['value'] = value
            node['valid_moves'] = valid_moves
            return node, value

        node['valid_moves'] = valid_moves

        if maximizing:
            best_value = -math.inf
            best_move = None

            # Explore ALL children (no pruning)
            for child_move in valid_moves:
                new_board = self.simulate_move(board, child_move, 1)
                child_node, value = self.minimax(new_board, depth - 1, False, child_move, node_id)
                
                node['children'].append(child_node)

                if value > best_value:
                    best_value = value
                    best_move = child_move

            node['value'] = best_value
            node['best_move'] = best_move
            return node, best_value

        else:
            best_value = math.inf
            best_move = None

            # Explore ALL children (no pruning)
            for child_move in valid_moves:
                new_board = self.simulate_move(board, child_move, 2)
                child_node, value = self.minimax(new_board, depth - 1, True, child_move, node_id)
                
                node['children'].append(child_node)

                if value < best_value:
                    best_value = value
                    best_move = child_move

            node['value'] = best_value
            node['best_move'] = best_move
            return node, best_value

    def best_move(self):
        """Pick the best move and save the tree"""
        self.node_id_counter = 0
        
        print("\n" + "="*60)
        print("Running Minimax (NO PRUNING) and saving tree...")
        print("="*60)
        
        start_time = time.time()
        
        tree_root, value = self.minimax(
            board=self.game.board,
            depth=self.max_depth,
            maximizing=(self.game.turn == 1),
            move=None,
            parent_id=None
        )
        
        elapsed = time.time() - start_time
        
        # Save tree data
        self.tree_data = {
            'root': tree_root,
            'metadata': {
                'algorithm': 'minimax_no_pruning',
                'max_depth': self.max_depth,
                'total_nodes': self.node_id_counter,
                'best_move': tree_root['best_move'],
                'best_value': value,
                'computation_time': elapsed,
                'current_turn': self.game.turn,
                'board_width': self.game.width,
                'board_height': self.game.length
            }
        }
        
        print(f"Best Move: Column {tree_root['best_move']} | Value: {value:.1f}")
        print(f"Nodes Explored: {self.node_id_counter} (FULL TREE - no pruning)")
        print(f"Time: {elapsed:.3f} seconds")
        print("="*60 + "\n")

        if tree_root['best_move'] is None:
            valid = self.get_valid_moves(self.game.board)
            if valid:
                return valid[0]
            return 0

        return tree_root['best_move']

    def save_tree_to_json(self, filename='minimax_no_pruning_tree.json'):
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

    def save_tree_to_python(self, filename='minimax_no_pruning_tree.py'):
        """Save the tree as a Python dictionary"""
        if self.tree_data is None:
            print("No tree data available. Run best_move() first.")
            return False
        
        try:
            with open(filename, 'w') as f:
                f.write("# Auto-generated minimax tree data (NO PRUNING)\n")
                f.write("# Import this in your GUI: from minimax_no_pruning_tree import tree_data\n\n")
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
        
        def count_nodes(node, stats, depth_counts):
            stats['total'] += 1
            
            if node.get('terminal', False):
                stats['terminal'] += 1
            
            current_depth = node['depth']
            if current_depth not in depth_counts:
                depth_counts[current_depth] = 0
            depth_counts[current_depth] += 1
            
            if node['node_type'] == 'MAX':
                stats['max_nodes'] += 1
            else:
                stats['min_nodes'] += 1
            
            for child in node.get('children', []):
                count_nodes(child, stats, depth_counts)
        
        stats = {
            'total': 0,
            'max_nodes': 0,
            'min_nodes': 0,
            'terminal': 0
        }
        
        depth_counts = {}
        
        count_nodes(self.tree_data['root'], stats, depth_counts)
        
        stats['nodes_by_depth'] = depth_counts
        
        return stats


if __name__ == "__main__":
    x = Connect4()
    
    # Make some moves
    x.play(3)
    x.play(3)
    x.play(2)
    
    print("Current board:")
    print(x)
    
    ai = Connect4AI_NoPruning_TreeSaver(x, max_depth=4)
    
    # Get best move (this builds the tree)
    col = ai.best_move()
    
    # Save tree in both formats
    ai.save_tree_to_json('minimax_no_pruning_tree.json')
    ai.save_tree_to_python('minimax_no_pruning_tree.py')
    
    # Print statistics
    stats = ai.get_tree_stats()
    print("\nTree Statistics:")
    print(f"  Total nodes explored: {stats['total']}")
    print(f"  MAX nodes: {stats['max_nodes']}")
    print(f"  MIN nodes: {stats['min_nodes']}")
    print(f"  Terminal nodes: {stats['terminal']}")
    print(f"\n  Nodes by depth:")
    for depth in sorted(stats['nodes_by_depth'].keys(), reverse=True):
        print(f"    Depth {depth}: {stats['nodes_by_depth'][depth]} nodes")
    
    print("\n" + "="*60)
    print("Full tree saved! (No pruning - all nodes explored)")
    print("="*60)