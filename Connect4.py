
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


x = Connect4()
while True:
    print(f"Player 1 score: {x.score_1}")
    print(f"Player 2 score: {x.score_2}")
    print(x)
    text=""
    if x.turn == 1:
        text = "\033[1;34mSelect a column:\033[0m"
    else:
        text = "\033[1;31mSelect a column:\033[0m"
    col = int(input(text))
    x.play(col)





