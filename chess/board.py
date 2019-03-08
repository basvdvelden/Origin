"""
Class Board
Tuple object of starting board for chess as a tuple of 8 lists with length 8.
"""


class Board:
    def __init__(self):
        self.board = [[1] * 8 for i in range(8)]
        self.board = tuple(self.board)
        for c in range(2):
            if c == 0:
                color = 'white'
            else:
                color = 'black'
            for i in range(8):
                self.piece_placement(i, color)

    def piece_placement(self, i, color):
        # TODO: Clean and optimize code.
        """
        Place pieces in starting positions for given color.
        :param i:
        :param color: color to have pieces placed, either 'black' or 'white'
        """
        if i == 0 and color == 'black':
            for p in range(8):
                p_ind = str(p + 1)
                self.board[1][p] = 'bP' + p_ind
        if i == 1 and color == 'black':
            self.board[0][0], self.board[0][7] = 'bR1', 'bR2'
        if i == 2 and color == 'black':
            self.board[0][1], self.board[0][6] = 'bN1', 'bN2'
        if i == 3 and color == 'black':
            self.board[0][2], self.board[0][5] = 'bB1', 'bB2'
        if i == 4 and color == 'black':
            self.board[0][3] = 'bQ'
        if i == 5 and color == 'black':
            self.board[0][4] = 'bK'
        if i == 0 and color == 'white':
            for p in range(8):
                p_ind = str(p + 1)
                self.board[6][p] = 'wP' + p_ind
        if i == 1 and color == 'white':
            self.board[7][0], self.board[7][7] = 'wR1', 'wR2'
        if i == 2 and color == 'white':
            self.board[7][1], self.board[7][6] = 'wN1', 'wN2'
        if i == 3 and color == 'white':
            self.board[7][2], self.board[7][5] = 'wB1', 'wB2'
        if i == 4 and color == 'white':
            self.board[7][3] = 'wQ'
        if i == 5 and color == 'white':
            self.board[7][4] = 'wK'
