import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from Connect4 import Connect4
from Connect4AI import Connect4AI_TreeSaver
from Connect4AI_NoPruning import Connect4AI_NoPruning_TreeSaver
from Connect4AI_Expectiminimax import Connect4AI_Expectiminimax






class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - Minimax Tree Visualizer")
        self.root.geometry("1600x900")
        self.root.configure(bg="#f0f0f0")
        
        # Game state
        self.game = Connect4()
        self.ai = None
        self.tree_data = None
        self.selected_algorithm = "minimax_pruning"
        self.ai_depth = 4
        
        # Colors
        self.colors = {
            'bg': '#f0f0f0',
            'board': '#2563eb',
            'empty': '#ffffff',
            'player1': '#ef4444',
            'player2': '#fbbf24',
            'btn': '#667eea',
            'btn_hover': '#5568d3'
        }
        
        self.create_widgets()
        self.update_board()
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Game
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), ipadx=20, ipady=20)
        
        # Title
        title = tk.Label(left_frame, text="Connect 4", font=("Arial", 28, "bold"), 
                        bg='white', fg=self.colors['btn'])
        title.pack(pady=10)
        
        # Game info
        self.info_label = tk.Label(left_frame, text="Player 1's Turn (Red)", 
                                   font=("Arial", 14), bg='white', fg=self.colors['player1'])
        self.info_label.pack(pady=10)
        
        # Score display
        self.score_label = tk.Label(left_frame, text="Score - P1: 0 | P2: 0", 
                                    font=("Arial", 12), bg='white')
        self.score_label.pack(pady=5)
        
        # Column buttons
        btn_frame = tk.Frame(left_frame, bg='white')
        btn_frame.pack(pady=10)
        
        self.col_buttons = []
        for i in range(7):
            btn = tk.Button(btn_frame, text=str(i), width=4, height=2,
                          font=("Arial", 12, "bold"),
                          bg=self.colors['btn'], fg='white',
                          command=lambda col=i: self.drop_piece(col))
            btn.grid(row=0, column=i, padx=3)
            self.col_buttons.append(btn)
        
        # Board canvas
        self.canvas = tk.Canvas(left_frame, width=490, height=420, 
                               bg=self.colors['board'], highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Control buttons
        control_frame = tk.Frame(left_frame, bg='white')
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="Reset Game", command=self.reset_game,
                 bg="#10b981", fg='white', font=("Arial", 12, "bold"),
                 padx=10, pady=5).grid(row=0, column=0, padx=5)
        
        tk.Button(control_frame, text="AI Move", command=self.ai_move,
                 bg="#8b5cf6", fg='white', font=("Arial", 12, "bold"),
                 padx=10, pady=5).grid(row=0, column=1, padx=5)
        
        # AI Settings
        settings_frame = tk.LabelFrame(left_frame, text="AI Settings", 
                                       bg='white', font=("Arial", 12, "bold"))
        settings_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(settings_frame, text="Algorithm:", bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.algo_var = tk.StringVar(value="minimax_pruning")
        algos = [
            ("Minimax + Pruning", "minimax_pruning"),
            ("Minimax No Pruning", "minimax_no_pruning"),
            ("Expectiminimax", "expectiminimax")
        ]
        
        for i, (text, value) in enumerate(algos):
            tk.Radiobutton(settings_frame, text=text, variable=self.algo_var,
                          value=value, bg='white',
                          command=self.update_algorithm).grid(row=i+1, column=0, sticky='w', padx=20)
        
        tk.Label(settings_frame, text="Search Depth:", bg='white').grid(row=4, column=0, sticky='w', padx=5, pady=5)
        
        self.depth_var = tk.IntVar(value=4)
        depth_spinner = tk.Spinbox(settings_frame, from_=1, to=6, textvariable=self.depth_var,
                                  width=10, command=self.update_depth)
        depth_spinner.grid(row=4, column=1, padx=5, pady=5)
        
        # Auto-generate tree option
        self.auto_tree_var = tk.BooleanVar(value=True)  # Changed to True by default
        tk.Checkbutton(settings_frame, text="Auto-generate tree after each move", 
                      variable=self.auto_tree_var, bg='white',
                      font=("Arial", 9)).grid(row=5, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Right panel - Tree visualization
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, ipadx=20, ipady=20)
        
        tree_title = tk.Label(right_frame, text="Minimax Tree Visualization", 
                             font=("Arial", 20, "bold"), bg='white', fg=self.colors['btn'])
        tree_title.pack(pady=10)
        
        # Tree controls
        tree_control_frame = tk.Frame(right_frame, bg='white')
        tree_control_frame.pack(pady=5)
        
        tk.Button(tree_control_frame, text="Generate Tree", command=self.generate_tree,
                 bg="#f59e0b", fg='white', font=("Arial", 11, "bold"),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(tree_control_frame, text="Load Tree JSON", command=self.load_tree,
                 bg="#6366f1", fg='white', font=("Arial", 11, "bold"),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(tree_control_frame, text="Clear Tree", command=self.clear_tree,
                 bg="#ef4444", fg='white', font=("Arial", 11, "bold"),
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Tree stats
        self.tree_stats_label = tk.Label(right_frame, text="No tree generated", 
                                         font=("Arial", 10), bg='white', fg='#666')
        self.tree_stats_label.pack(pady=5)
        
        # Tree display with scrollbar
        tree_frame = tk.Frame(right_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas for graphical tree
        self.tree_canvas = tk.Canvas(tree_frame, bg='#f9fafb',
                                     yscrollcommand=tree_scroll_y.set,
                                     xscrollcommand=tree_scroll_x.set)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree_canvas.yview)
        tree_scroll_x.config(command=self.tree_canvas.xview)
        
        # Bind mouse wheel
        self.tree_canvas.bind("<MouseWheel>", lambda e: self.tree_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Node positions cache
        self.node_positions = {}
    
    def update_board(self):
        self.canvas.delete("all")
        
        # Draw board
        for row in range(6):
            for col in range(7):
                x = col * 70 + 35
                y = (5 - row) * 70 + 35
                
                # Draw cell
                cell_value = self.game.board[col][row]
                if cell_value == 0:
                    color = self.colors['empty']
                elif cell_value == 1:
                    color = self.colors['player1']
                else:
                    color = self.colors['player2']
                
                self.canvas.create_oval(x-25, y-25, x+25, y+25, 
                                       fill=color, outline='#1e40af', width=2)
        
        # Update info
        if self.game.turn == 1:
            self.info_label.config(text="Player 1's Turn (Red)", fg=self.colors['player1'])
        else:
            self.info_label.config(text="Player 2's Turn (Yellow)", fg=self.colors['player2'])
        
        self.score_label.config(text=f"Score - P1: {self.game.score_1} | P2: {self.game.score_2}")
    
    def drop_piece(self, col):
        result = self.game.play(col)
        if result == 1:
            messagebox.showwarning("Invalid Move", "Column is full!")
            return
        
        self.update_board()
        
        # Always auto-generate tree after player move
        self.root.after(100, self.generate_tree_silently)
        
        self.check_winner()
    
    def ai_move(self):
        try:
            self.info_label.config(text="AI is thinking...", fg='#8b5cf6')
            self.root.update()
            
            # Create a fresh game instance with copied state
            temp_game = Connect4()
            temp_game.board = [[self.game.board[c][r] for r in range(self.game.length)] 
                              for c in range(self.game.width)]
            temp_game.turn = self.game.turn
            temp_game.score_1 = self.game.score_1
            temp_game.score_2 = self.game.score_2
            
            # Create AI based on selected algorithm
            if self.selected_algorithm == "minimax_pruning":
                ai = Connect4AI_TreeSaver(temp_game, max_depth=self.ai_depth)
            elif self.selected_algorithm == "minimax_no_pruning":
                ai = Connect4AI_NoPruning_TreeSaver(temp_game, max_depth=self.ai_depth)
            else:  # expectiminimax
                ai = Connect4AI_Expectiminimax(temp_game, max_depth=min(self.ai_depth, 3))
            
            col = ai.best_move()
            
            # Save tree data from AI move
            self.tree_data = ai.tree_data
            
            self.game.play(col)
            
            self.update_board()
            
            # Always display tree after AI move
            self.display_tree()
            stats = ai.get_tree_stats()
            stats_text = f"AI Move (Col {col}) | Nodes: {stats['total']} | "
            if 'pruned' in stats:
                stats_text += f"Pruned: {stats['pruned']} | "
            if 'chance_nodes' in stats:
                stats_text += f"Chance: {stats['chance_nodes']} | "
            stats_text += f"Time: {self.tree_data['metadata']['computation_time']:.3f}s"
            self.tree_stats_label.config(text=stats_text, fg='#059669')
            
            self.check_winner()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"AI move failed: {str(e)}")
    
    def generate_tree_silently(self):
        """Generate tree without showing success message"""
        try:
            # Create fresh AI with current game state
            temp_game = Connect4()
            temp_game.board = [[self.game.board[c][r] for r in range(self.game.length)] 
                              for c in range(self.game.width)]
            temp_game.turn = self.game.turn
            temp_game.score_1 = self.game.score_1
            temp_game.score_2 = self.game.score_2
            
            self.tree_stats_label.config(text="Generating tree...", fg='#8b5cf6')
            self.root.update()
            
            if self.selected_algorithm == "minimax_pruning":
                ai = Connect4AI_TreeSaver(temp_game, max_depth=self.ai_depth)
            elif self.selected_algorithm == "minimax_no_pruning":
                ai = Connect4AI_NoPruning_TreeSaver(temp_game, max_depth=self.ai_depth)
            else:  # expectiminimax
                ai = Connect4AI_Expectiminimax(temp_game, max_depth=min(self.ai_depth, 3))
            
            ai.best_move()
            self.tree_data = ai.tree_data
            
            self.display_tree()
            
            # Show stats
            stats = ai.get_tree_stats()
            player_turn = "Player 1" if temp_game.turn == 1 else "Player 2"
            stats_text = f"{player_turn}'s Turn | Nodes: {stats['total']} | "
            if 'pruned' in stats:
                stats_text += f"Pruned: {stats['pruned']} | "
            if 'chance_nodes' in stats:
                stats_text += f"Chance: {stats['chance_nodes']} | "
            stats_text += f"Time: {self.tree_data['metadata']['computation_time']:.3f}s"
            self.tree_stats_label.config(text=stats_text, fg='#059669')
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.tree_stats_label.config(text=f"Tree generation failed: {str(e)}", fg='#ef4444')
    
    def generate_tree(self):
        try:
            # Create fresh AI with current game state
            temp_game = Connect4()
            temp_game.board = [[self.game.board[c][r] for r in range(self.game.length)] 
                              for c in range(self.game.width)]
            temp_game.turn = self.game.turn
            temp_game.score_1 = self.game.score_1
            temp_game.score_2 = self.game.score_2
            
            self.info_label.config(text="Generating tree...", fg='#8b5cf6')
            self.root.update()
            
            if self.selected_algorithm == "minimax_pruning":
                ai = Connect4AI_TreeSaver(temp_game, max_depth=self.ai_depth)
            elif self.selected_algorithm == "minimax_no_pruning":
                ai = Connect4AI_NoPruning_TreeSaver(temp_game, max_depth=self.ai_depth)
            else:  # expectiminimax
                ai = Connect4AI_Expectiminimax(temp_game, max_depth=min(self.ai_depth, 3))
            
            ai.best_move()
            self.tree_data = ai.tree_data
            
            self.display_tree()
            self.update_board()
            
            # Show stats
            stats = ai.get_tree_stats()
            stats_text = f"Nodes: {stats['total']} | "
            if 'pruned' in stats:
                stats_text += f"Pruned: {stats['pruned']} | "
            if 'chance_nodes' in stats:
                stats_text += f"Chance: {stats['chance_nodes']} | "
            stats_text += f"Time: {self.tree_data['metadata']['computation_time']:.3f}s"
            self.tree_stats_label.config(text=stats_text, fg='#059669')
            
            messagebox.showinfo("Success", "Tree generated successfully!")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to generate tree: {str(e)}")
    
    def display_tree(self):
        self.tree_canvas.delete("all")
        self.node_positions = {}
        
        if self.tree_data is None:
            self.tree_canvas.create_text(400, 300, text="No tree data available",
                                        font=("Arial", 14), fill='#666')
            return
        
        # Display metadata
        meta = self.tree_data['metadata']
        header = f"Algorithm: {meta['algorithm'].upper()} | "
        header += f"Depth: {meta['max_depth']} | Nodes: {meta['total_nodes']} | "
        header += f"Best: Col {meta.get('best_move', 'N/A')} | "
        header += f"Value: {meta.get('best_value', meta.get('expected_value', 0)):.2f}"
        
        self.tree_canvas.create_text(10, 10, text=header, anchor='nw',
                                     font=("Arial", 10, "bold"), fill='#667eea')
        
        # Calculate tree layout
        self.calculate_tree_layout(self.tree_data['root'])
        
        # Draw edges first
        self.draw_edges(self.tree_data['root'])
        
        # Draw nodes on top
        self.draw_nodes(self.tree_data['root'])
        
        # Update scroll region
        bbox = self.tree_canvas.bbox("all")
        if bbox:
            self.tree_canvas.configure(scrollregion=bbox)
    
    def calculate_tree_layout(self, node, depth=0, x_offset=0):
        """Calculate positions for all nodes using Reingold-Tilford algorithm"""
        node_width = 100
        node_height = 80
        horizontal_spacing = 120
        vertical_spacing = 100
        
        node_id = node.get('id', 0)
        
        # Get children
        children = []
        if node.get('node_type') == 'CHANCE' and 'outcomes' in node:
            for outcome in node.get('outcomes', []):
                if 'child_node' in outcome:
                    children.append(outcome['child_node'])
        else:
            children = node.get('children', [])
        
        # Filter out pruned children
        children = [c for c in children if not c.get('pruned', False)]
        
        if not children:
            # Leaf node
            x = x_offset
            y = 50 + depth * vertical_spacing
            self.node_positions[node_id] = (x, y, node)
            return x, 1
        
        # Recursively calculate positions for children
        child_x_start = x_offset
        total_width = 0
        
        for i, child in enumerate(children):
            child_x, child_width = self.calculate_tree_layout(child, depth + 1, child_x_start)
            child_x_start += child_width * horizontal_spacing
            total_width += child_width
        
        # Center parent over children
        first_child_id = children[0].get('id', 0)
        last_child_id = children[-1].get('id', 0)
        
        if first_child_id in self.node_positions and last_child_id in self.node_positions:
            first_x = self.node_positions[first_child_id][0]
            last_x = self.node_positions[last_child_id][0]
            x = (first_x + last_x) / 2
        else:
            x = x_offset + (total_width * horizontal_spacing) / 2
        
        y = 50 + depth * vertical_spacing
        self.node_positions[node_id] = (x, y, node)
        
        return x, total_width
    
    def draw_edges(self, node):
        """Draw edges connecting nodes"""
        node_id = node.get('id', 0)
        if node_id not in self.node_positions:
            return
        
        x1, y1, _ = self.node_positions[node_id]
        
        # Get children
        children = []
        if node.get('node_type') == 'CHANCE' and 'outcomes' in node:
            for outcome in node.get('outcomes', []):
                if 'child_node' in outcome:
                    children.append((outcome['child_node'], outcome.get('probability', 0)))
        else:
            children = [(c, None) for c in node.get('children', [])]
        
        for child, prob in children:
            if child.get('pruned', False):
                continue
            
            child_id = child.get('id', 0)
            if child_id in self.node_positions:
                x2, y2, _ = self.node_positions[child_id]
                
                # Draw edge
                if prob is not None:
                    # Dashed line for chance nodes
                    self.tree_canvas.create_line(x1, y1 + 25, x2, y2 - 25,
                                                 fill='#f59e0b', width=2, dash=(4, 2))
                    # Draw probability
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    self.tree_canvas.create_text(mid_x, mid_y, text=f"{prob:.0%}",
                                                font=("Arial", 8), fill='#f59e0b')
                else:
                    # Solid line for regular nodes
                    self.tree_canvas.create_line(x1, y1 + 25, x2, y2 - 25,
                                                 fill='#9ca3af', width=2)
                
                # Recursively draw edges for children
                self.draw_edges(child)
    
    def draw_nodes(self, node):
        """Draw nodes as boxes"""
        node_id = node.get('id', 0)
        if node_id not in self.node_positions:
            return
        
        x, y, _ = self.node_positions[node_id]
        
        # Node colors
        node_type = node.get('node_type', 'UNKNOWN')
        if node_type == 'MAX':
            fill_color = '#fecaca'
            outline_color = '#dc2626'
            symbol = '▲'
        elif node_type == 'MIN':
            fill_color = '#bfdbfe'
            outline_color = '#2563eb'
            symbol = '▼'
        elif node_type == 'CHANCE':
            fill_color = '#fde68a'
            outline_color = '#f59e0b'
            symbol = '◆'
        else:
            fill_color = '#d1fae5'
            outline_color = '#059669'
            symbol = '●'
        
        # Draw node box
        box_width = 90
        box_height = 50
        
        self.tree_canvas.create_rectangle(x - box_width/2, y - box_height/2,
                                         x + box_width/2, y + box_height/2,
                                         fill=fill_color, outline=outline_color, width=2)
        
        # Draw node info
        move_str = f"Col {node.get('move')}" if node.get('move') is not None else "ROOT"
        value = node.get('value', node.get('expected_value', 0))
        
        # Symbol and move
        self.tree_canvas.create_text(x, y - 15, text=f"{symbol} {move_str}",
                                    font=("Arial", 9, "bold"), fill=outline_color)
        
        # Value
        self.tree_canvas.create_text(x, y + 5, text=f"{value:+.1f}",
                                    font=("Arial", 10, "bold"), fill='#059669')
        
        # Terminal indicator
        if node.get('terminal', False):
            term_type = node.get('terminal_type', 'T')
            self.tree_canvas.create_text(x, y + 20, text=f"[{term_type}]",
                                        font=("Arial", 7), fill='#666')
        
        # Draw children
        children = []
        if node.get('node_type') == 'CHANCE' and 'outcomes' in node:
            for outcome in node.get('outcomes', []):
                if 'child_node' in outcome:
                    children.append(outcome['child_node'])
        else:
            children = node.get('children', [])
        
        for child in children:
            if not child.get('pruned', False):
                self.draw_nodes(child)
    
    def display_node(self, node, depth, prefix, is_last=True):
        if node.get('pruned', False):
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}✂ PRUNED [Col {node.get('move', '?')}]\n"
            self.tree_text.insert(tk.END, line, 'pruned')
            return
        
        # Node symbol
        node_type = node.get('node_type', 'UNKNOWN')
        if node_type == 'MAX':
            symbol = '▲'
            tag = 'max'
        elif node_type == 'MIN':
            symbol = '▼'
            tag = 'min'
        elif node_type == 'CHANCE':
            symbol = '◆'
            tag = 'chance'
        else:
            symbol = '●'
            tag = 'value'
        
        # Build line with tree structure
        if depth == 0:
            connector = ""
        else:
            connector = "└── " if is_last else "├── "
        
        move_str = f"Col {node.get('move')}" if node.get('move') is not None else "ROOT"
        value = node.get('value', node.get('expected_value', 0))
        
        line = f"{prefix}{connector}{symbol} [{move_str}] "
        self.tree_text.insert(tk.END, line, tag)
        
        # Add value
        value_str = f"Value: {value:+.2f}"
        if node.get('terminal', False):
            value_str += f" [{node.get('terminal_type', 'TERMINAL')}]"
        
        self.tree_text.insert(tk.END, value_str + "\n", 'value')
        
        # Update prefix for children
        if depth == 0:
            new_prefix = ""
        else:
            new_prefix = prefix + ("    " if is_last else "│   ")
        
        # For chance nodes, show probability distribution
        if node_type == 'CHANCE' and 'outcomes' in node:
            outcomes = node.get('outcomes', [])
            for i, outcome in enumerate(outcomes):
                is_last_outcome = (i == len(outcomes) - 1)
                outcome_connector = "└── " if is_last_outcome else "├── "
                prob_line = f"{new_prefix}{outcome_connector}◇ P={outcome['probability']:.1%} Col {outcome['actual_column']}: "
                self.tree_text.insert(tk.END, prob_line, 'chance')
                contrib_line = f"V={outcome['value']:+.2f}, Contrib={outcome['contribution']:+.2f}\n"
                self.tree_text.insert(tk.END, contrib_line, 'value')
                
                if 'child_node' in outcome:
                    child_prefix = new_prefix + ("    " if is_last_outcome else "│   ")
                    self.display_node(outcome['child_node'], depth + 1, child_prefix, True)
        
        # Display children
        children = node.get('children', [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self.display_node(child, depth + 1, new_prefix, is_last_child)
    
    def load_tree(self):
        filename = filedialog.askopenfilename(
            title="Select Tree JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.tree_data = json.load(f)
                
                self.display_tree()
                messagebox.showinfo("Success", "Tree loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load tree: {str(e)}")
    
    def clear_tree(self):
        self.tree_canvas.delete("all")
        self.tree_data = None
        self.node_positions = {}
        self.tree_stats_label.config(text="Tree cleared", fg='#666')
    
    def reset_game(self):
        self.game = Connect4()
        self.ai = None
        self.tree_data = None
        self.update_board()
        self.clear_tree()
        messagebox.showinfo("Reset", "Game reset!")
    
    def update_algorithm(self):
        self.selected_algorithm = self.algo_var.get()
        self.ai = None  # Reset AI
    
    def update_depth(self):
        self.ai_depth = self.depth_var.get()
        self.ai = None  # Reset AI
    
    def check_winner(self):
        # Check if board is full
        board_full = all(self.game.board[col][self.game.length - 1] != 0 
                        for col in range(self.game.width))
        
        # Game only ends when board is full
        if board_full:
            # Determine winner by score
            if self.game.score_1 > self.game.score_2:
                messagebox.showinfo("Game Over", 
                    f"Board Full!\n\nPlayer 1 (Red) wins!\n\n"
                    f"Connected Fours:\nPlayer 1: {self.game.score_1}\n"
                    f"Player 2: {self.game.score_2}")
            elif self.game.score_2 > self.game.score_1:
                messagebox.showinfo("Game Over", 
                    f"Board Full!\n\nPlayer 2 (Yellow) wins!\n\n"
                    f"Connected Fours:\nPlayer 1: {self.game.score_1}\n"
                    f"Player 2: {self.game.score_2}")
            else:
                messagebox.showinfo("Game Over", 
                    f"Board Full!\n\nIt's a TIE!\n\n"
                    f"Connected Fours:\nPlayer 1: {self.game.score_1}\n"
                    f"Player 2: {self.game.score_2}")
            self.reset_game()


if __name__ == "__main__":
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()