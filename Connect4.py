
class Connect4:
    def __init__(self, length:int=6 , width:int=7):
        self.length = length
        self.width = width
        self.board = [[0 for i in range(length)] for j in range(width)]
        self.turn=1
        self.score_1=0
        self.score_2=0

    def play(self, row:int):
        j=0
        while j < self.length and self.board[row][j]!=0:
            j+=1
        if j==self.length:
            print("out of bound")
            return 1
        self.board[row][j]=self.turn
        self.turn = (self.turn%2)+1
        self.calculate_score()
        return 0

    def calculate_score(self):
        self.score_1 = 0
        self.score_2 = 0

        # Directions: horiz, vert, diag-down, diag-up
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for c in range(self.width):
            for r in range(self.length):
                player = self.board[c][r]
                if player == 0:
                    continue

                for dc, dr in directions:
                    # Check only if starting a new sequence
                    prev_c, prev_r = c - dc, r - dr
                    if 0 <= prev_c < self.width and 0 <= prev_r < self.length:
                        if self.board[prev_c][prev_r] == player:
                            continue  # sequence already counted

                    # Count consecutive tokens in this direction
                    length = 0
                    x, y = c, r
                    while 0 <= x < self.width and 0 <= y < self.length and self.board[x][y] == player:
                        length += 1
                        x += dc
                        y += dr

                    increment = max(0, length - 3)
                    if player == 1:
                        self.score_1 += increment
                    else:
                        self.score_2 += increment

    def advanced_dynamic_heuristic(self):
        """
        Fully dynamic expert-grade heuristic for Connect-Four
        that adapts to arbitrary board sizes.
        """

        PLAYER = 1
        OPP = 2
        N = 4  # connect N (your game uses 4)

        score = 0

        # ===== Dynamic Weights =====
        MAX_DIM = max(self.width, self.length)

        WIN_SCORE = 200000
        DOUBLE_THREAT = 80000
        ODD_THREAT = 200
        SHAPE = 25
        BLOCK = 15
        CLUSTER_BASE = 30
        CENTER_BASE = 10

        # ================================
        #   DYNAMIC HEATMAP GENERATION
        # ================================
        import math

        cx, cy = self.width / 2, self.length / 2
        heatmap = [[0] * self.length for _ in range(self.width)]

        for c in range(self.width):
            for r in range(self.length):
                # gaussian-like center weighting
                dist = math.sqrt((c - cx) ** 2 + (r - cy) ** 2)
                max_dist = math.sqrt(cx ** 2 + cy ** 2)
                heatmap[c][r] = 1 - (dist / max_dist)

        # normalize to integer-ish scale
        for c in range(self.width):
            for r in range(self.length):
                heatmap[c][r] *= 15  # scale factor

        # ================================
        #   HELPER: CLUSTER SIZE
        # ================================
        def cluster_score(c, r, player):
            dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
            size = 1
            for dc, dr in dirs:
                x, y = c + dc, r + dr
                while 0 <= x < self.width and 0 <= y < self.length:
                    if self.board[x][y] == player:
                        size += 1
                        x += dc
                        y += dr
                    else:
                        break
            # cluster scales dynamically with board size
            return CLUSTER_BASE * (size * size) / math.sqrt(MAX_DIM)

        # =========  POSITIONAL & CLUSTER SCORING ==========
        for c in range(self.width):
            for r in range(self.length):
                cell = self.board[c][r]
                if cell == 0:
                    continue

                sign = 1 if cell == PLAYER else -1

                # center / heatmap score
                score += sign * heatmap[c][r]

                # center control weighting (dynamic)
                dist_center = abs(c - cx) + abs(r - cy)
                max_dist = cx + cy
                center_val = 1 - (dist_center / max_dist)
                score += sign * center_val * CENTER_BASE

                # cluster shape score
                score += sign * cluster_score(c, r, cell)

        # ===========================================
        #   THREAT & PATTERN ANALYSIS (DYNAMIC)
        # ===========================================
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        def analyze_window(window, coords):
            nonlocal score
            p1 = window.count(PLAYER)
            p2 = window.count(OPP)
            empty = window.count(0)

            # Wins
            if p1 == N: score += WIN_SCORE
            if p2 == N: score -= WIN_SCORE

            # Double threats
            if p1 == N - 1 and empty == 1: score += DOUBLE_THREAT
            if p2 == N - 1 and empty == 1: score -= DOUBLE_THREAT

            # Odd/even reachable row threats
            for (cx, cy) in coords:
                if self.board[cx][cy] == 0:
                    if cy % 2 == 1:  # reachable odd row (dynamic parity)
                        if p1 == N - 1: score += ODD_THREAT
                        if p2 == N - 1: score -= ODD_THREAT

            # Shapes (2 + empty)
            if p1 == N - 2 and empty == 2: score += SHAPE
            if p2 == N - 2 and empty == 2: score -= SHAPE

        # Scan board dynamically
        for dc, dr in directions:
            for c in range(self.width):
                for r in range(self.length):
                    window = []
                    coords = []
                    for i in range(N):
                        x, y = c + dc * i, r + dr * i
                        if 0 <= x < self.width and 0 <= y < self.length:
                            window.append(self.board[x][y])
                            coords.append((x, y))
                    if len(window) == N:
                        analyze_window(window, coords)

        return score

    def __str__(self):
        symbols = {0: '.', 1: '\033[1;34m1\033[0m', 2: '\033[31m2\033[0m'}
        lines = []

        # Column numbers
        col_numbers = '   ' + '   '.join(str(c) for c in range(self.width))
        lines.append(col_numbers)

        # Top border
        lines.append('  +' + '---+' * self.width)

        # Rows from top to bottom
        for r in range(self.length - 1, -1, -1):
            row_cells = ' | '.join(symbols[self.board[c][r]] for c in range(self.width))
            lines.append(f"  | {row_cells} |")
            # Add horizontal separator
            lines.append('  +' + '---+' * self.width)

        return '\n'.join(lines)


# x = Connect4()
# while True:
#     print(f"Player 1 score: {x.score_1}")
#     print(f"Player 2 score: {x.score_2}")
#     print(x)
#     text=""
#     if x.turn == 1:
#         text = "\033[1;34mSelect a column:\033[0m"
#     else:
#         text = "\033[1;31mSelect a column:\033[0m"
#     col = int(input(text))
#     x.play(col)





