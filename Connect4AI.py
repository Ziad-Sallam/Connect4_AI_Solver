import copy
import math
import time
import json
from Connect4 import Connect4


class Connect4AI_TreeSaver:
    def __init__(self, game, max_depth=4):
        """
        game: instance of Connect4 class
        max_depth: how deep minimax will search
        """
        self.game = game
        self.max_depth = max_depth
        self.tree_data = None
        self.node_id_counter = 0

    def get_valid_moves(self, board):
        moves = []
        for c in range(self.game.width):
            if board[c][self.game.length - 1] == 0:
                moves.append(c)
        return moves

    def simulate_move(self, board, col, player):
        new_board = copy.deepcopy(board)
        row = 0
        while row < self.game.length and new_board[col][row] != 0:
            row += 1
        if row < self.game.length:
            new_board[col][row] = player
        return new_board

    def is_terminal(self, board):
        g = self.game
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
                        return True, p

        full = all(board[c][g.length - 1] != 0 for c in range(g.width))
        if full:
            return True, 0

        return False, None

    def board_to_string(self, board):
        """Convert board to string representation for storage"""
        result = []
        for r in range(self.game.length - 1, -1, -1):
            row = []
            for c in range(self.game.width):
                row.append(str(board[c][r]))
            result.append(''.join(row))
        return '\n'.join(result)

    def minimax(self, board, depth, alpha, beta, maximizing, move=None, parent_id=None):
        """Minimax with tree structure capture"""
        
        # Create node
        node_id = self.node_id_counter
        self.node_id_counter += 1
        
        node = {
            'id': node_id,
            'parent_id': parent_id,
            'depth': depth,
            'move': move,
            'node_type': 'MAX' if maximizing else 'MIN',
            'alpha': alpha if alpha != -math.inf else None,
            'beta': beta if beta != math.inf else None,
            'board_state': self.board_to_string(board),
            'children': [],
            'value': None,
            'best_move': None,
            'terminal': False,
            'pruned': False
        }
        
        # Check terminal state
        terminal, winner = self.is_terminal(board)
        
        if terminal:
            node['terminal'] = True
            node['terminal_type'] = 'WIN' if winner else 'DRAW'
            if winner == 1:
                node['value'] = 10**9
            elif winner == 2:
                node['value'] = -10**9
            else:
                node['value'] = 0
            return node, node['value']

        # Check depth limit
        if depth == 0:
            old_board = self.game.board
            self.game.board = board
            value = self.game.advanced_dynamic_heuristic()
            self.game.board = old_board
            
            node['terminal'] = True
            node['terminal_type'] = 'LEAF'
            node['value'] = value
            return node, value

        valid_moves = self.get_valid_moves(board)
        node['valid_moves'] = valid_moves

        if maximizing:
            best_val = -math.inf
            best_move = None

            for i, child_move in enumerate(valid_moves):
                new_b = self.simulate_move(board, child_move, 1)
                child_node, eval_val = self.minimax(new_b, depth - 1, alpha, beta, False, child_move, node_id)
                
                node['children'].append(child_node)

                if eval_val > best_val:
                    best_val = eval_val
                    best_move = child_move

                alpha = max(alpha, best_val)
                
                # Mark pruning
                if beta <= alpha:
                    # Mark remaining moves as pruned
                    for pruned_move in valid_moves[i+1:]:
                        pruned_node = {
                            'id': self.node_id_counter,
                            'parent_id': node_id,
                            'depth': depth - 1,
                            'move': pruned_move,
                            'node_type': 'MIN',
                            'pruned': True,
                            'alpha': alpha,
                            'beta': beta,
                            'children': []
                        }
                        self.node_id_counter += 1
                        node['children'].append(pruned_node)
                    break

            node['value'] = best_val
            node['best_move'] = best_move
            return node, best_val

        else:
            best_val = math.inf
            best_move = None

            for i, child_move in enumerate(valid_moves):
                new_b = self.simulate_move(board, child_move, 2)
                child_node, eval_val = self.minimax(new_b, depth - 1, alpha, beta, True, child_move, node_id)
                
                node['children'].append(child_node)

                if eval_val < best_val:
                    best_val = eval_val
                    best_move = child_move

                beta = min(beta, best_val)
                
                # Mark pruning
                if beta <= alpha:
                    # Mark remaining moves as pruned
                    for pruned_move in valid_moves[i+1:]:
                        pruned_node = {
                            'id': self.node_id_counter,
                            'parent_id': node_id,
                            'depth': depth - 1,
                            'move': pruned_move,
                            'node_type': 'MAX',
                            'pruned': True,
                            'alpha': alpha,
                            'beta': beta,
                            'children': []
                        }
                        self.node_id_counter += 1
                        node['children'].append(pruned_node)
                    break

            node['value'] = best_val
            node['best_move'] = best_move
            return node, best_val

    def best_move(self):
        """Get the best move and save the tree"""
        self.node_id_counter = 0
        
        print("\n" + "="*60)
        print("Running Minimax and saving tree...")
        print("="*60)
        
        start_time = time.time()
        
        tree_root, value = self.minimax(
            board=self.game.board,
            depth=self.max_depth,
            alpha=-math.inf,
            beta=math.inf,
            maximizing=(self.game.turn == 1),
            move=None,
            parent_id=None
        )
        
        elapsed = time.time() - start_time
        
        # Save tree data
        self.tree_data = {
            'root': tree_root,
            'metadata': {
                'algorithm': 'minimax_with_pruning',
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
        print(f"Nodes Explored: {self.node_id_counter}")
        print(f"Time: {elapsed:.3f} seconds")
        print("="*60 + "\n")

        return tree_root['best_move']

    def save_tree_to_json(self, filename='minimax_tree.json'):
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

    def save_tree_to_python(self, filename='minimax_tree.py'):
        """Save the tree as a Python dictionary for easy importing"""
        if self.tree_data is None:
            print("No tree data available. Run best_move() first.")
            return False
        
        try:
            with open(filename, 'w') as f:
                f.write("# Auto-generated minimax tree data\n")
                f.write("# Import this in your GUI: from minimax_tree import tree_data\n\n")
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
            if node.get('pruned', False):
                stats['pruned'] += 1
                return
            
            stats['total'] += 1
            
            if node.get('terminal', False):
                stats['terminal'] += 1
            
            if node['node_type'] == 'MAX':
                stats['max_nodes'] += 1
            else:
                stats['min_nodes'] += 1
            
            for child in node.get('children', []):
                count_nodes(child, stats)
        
        stats = {
            'total': 0,
            'max_nodes': 0,
            'min_nodes': 0,
            'terminal': 0,
            'pruned': 0
        }
        
        count_nodes(self.tree_data['root'], stats)
        
        return stats


if __name__ == "__main__":
    x = Connect4()
    
    # Make some moves to create an interesting position
    x.play(3)
    x.play(3)
    x.play(2)
    
    print("Current board:")
    print(x)
    
    ai = Connect4AI_TreeSaver(x, max_depth=4)
    
    # Get best move (this builds the tree)
    col = ai.best_move()
    
    # Save tree in both formats
    ai.save_tree_to_json('minimax_tree.json')
    ai.save_tree_to_python('minimax_tree.py')
    
    # Print statistics
    stats = ai.get_tree_stats()
    print("\nTree Statistics:")
    print(f"  Total nodes explored: {stats['total']}")
    print(f"  MAX nodes: {stats['max_nodes']}")
    print(f"  MIN nodes: {stats['min_nodes']}")
    print(f"  Terminal nodes: {stats['terminal']}")
    print(f"  Pruned branches: {stats['pruned']}")
    
    print("\n" + "="*60)
    print("Tree saved! You can now use it in your GUI.")
    print("="*60)
    print("\nTo load in your GUI:")
    print("  JSON format:   tree = json.load(open('minimax_tree.json'))")
    print("  Python format: from minimax_tree import tree_data")