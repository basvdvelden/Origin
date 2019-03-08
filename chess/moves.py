

def top_moves(loc):
    """
    Returns pseudo legal moves, vertical in top direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in top direction
    :rtype: list
    """
    u_moves = []
    if loc[0] < 7:
        for rank in range(loc[0] + 1, 8):
            u_moves.append((rank, loc[1]))
    return u_moves


def bottom_moves(loc):
    """
    Returns pseudo legal moves, vertical in bottom direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in left direction
    :rtype: list
    """
    d_moves = []
    if loc[0] > 0:
        for rank in range(loc[0] - 1, -1, -1):
            d_moves.append((rank, loc[1]))
    return d_moves


def right_moves(loc):
    """
    Returns pseudo legal moves, horizontal in right direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in right direction
    :rtype: list
    """
    r_moves = []
    if loc[1] < 7:
        for file in range(loc[1] + 1, 8):
            r_moves.append((loc[0], file))
    return r_moves


def left_moves(loc):
    """
    Returns pseudo legal moves, horizontal in left direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in left direction
    :rtype: list
    """
    l_moves = []
    if loc[1] > 0:
        for file in range(loc[1] - 1, -1, -1):
            l_moves.append((loc[0], file))
    return l_moves


def top_left_moves(loc):
    """
    Returns pseudo legal moves, diagonal in top left direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in top left direction
    :rtype: list
    """
    tl_moves = []
    if loc[0] > 0 and loc[1] > 0:
        for dist in range(1, min((loc[0], loc[1])) + 1):
            tl_moves.append((loc[0] - dist, loc[1] - dist))
    return tl_moves


def bottom_right_moves(loc):
    """
    Returns pseudo legal moves, diagonal in bottom right direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in bottom right direction
    :rtype: list
    """
    br_moves = []
    if loc[0] < 7 and loc[1] < 7:
        for dist in range(1, 8 - max((loc[0], loc[1]))):
            br_moves.append((loc[0] + dist, loc[1] + dist))
    return br_moves


def bottom_left_moves(loc):
    """
    Returns pseudo legal moves, diagonal in bottom left direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in bottom left direction
    :rtype: list
    """
    bl_moves = []
    if loc[0] < 7 and loc[1] > 0:
        for dist in range(1, min((8 - loc[0], loc[1] + 1))):
            bl_moves.append((loc[0] + dist, loc[1] - dist))
    return bl_moves


def top_right_moves(loc):
    """
    Returns pseudo legal moves, diagonal in top right direction
    :param loc: location of piece to get moves for
    :type loc: tuple
    :return: pseudo legal moves in top right direction
    :rtype: list
    """
    tr_moves = []
    if loc[0] > 0 and loc[1] < 7:
        for dist in range(1, min((loc[0] + 1, 8 - loc[1]))):
            tr_moves.append((loc[0] - dist, loc[1] + dist))
    return tr_moves


def set_2nd_layer_keys_moves(_dict):
    """
    Called by ps_moves_per_loc, sets the moves with corresponding direction in dictionary
    :param _dict: base dictionary from ps_moves_per_loc
    :type _dict: dict
    """
    directions = ('u', 'd', 'r', 'l', 'tl', 'br', 'tr', 'bl')
    move_functions = (top_moves, bottom_moves, right_moves, left_moves,
                      top_left_moves, bottom_right_moves, top_right_moves, bottom_left_moves)
    for key in _dict:
        loc = (int(key[1]), int(key[4]))
        for index, direction in enumerate(directions):
            _dict[key][direction] = move_functions[index](loc)


def ps_moves_per_loc():
    """
    Creates dictionary with all board locations as keys for a dictionary with keys for each direction
    and all pseudo legal moves available for each location and direction. Only moves for queen's bishops and rooks

    :return: returns the dictionary
    :rtype: dict
    """
    _dict = {}
    for i in range(8):
        for j in range(8):
            _dict[str((i, j))] = {}
    set_2nd_layer_keys_moves(_dict)
    return _dict


def ps_king_moves(loc, color):
    """
    Returns king's pseudo legal moves
    :param loc: king's location
    :param color: king's color
    :type loc: tuple
    :type color: str
    :return: pseudo legal moves
    :rtype: list
    """
    king_moves = ((1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0))
    moves = []
    if color == 'white':
        for move in king_moves:
            if loc[0] + move[0] in range(8) and loc[1] + move[1] in range(8):
                moves.append((loc[0] + move[0], loc[1] + move[1]))
    else:
        for move in king_moves:
            if loc[0] + move[0] in range(8) and loc[1] + move[1] in range(8):
                moves.append((loc[0] + move[0], loc[1] + move[1]))
    return moves


def ps_knight_moves(loc):
    """
    Returns pseudo legal knight move.
    :param loc: knight's location
    :type loc: tuple
    :return: pseudo legal moves
    :rtype: list
    """
    knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
    moves = []
    for move in knight_moves:
        if loc[0] + move[0] in range(8) and loc[1] + move[1] in range(8):
            moves.append((loc[0] + move[0], loc[1] + move[1]))
    return moves


def ps_pawn_cap_moves(loc, color):
    """
    Returns pseudo legal capture moves for given location and color for a pawn.
    :param loc: pawn's location
    :param color: pawn's color, either 'black' or 'white'
    :type loc: tuple
    :type color: str
    :return: pawn's pseudo legal capture moves
    """
    moves = []
    if color == 'white':
        if loc[0] - 1 > -1 and loc[1] - 1 > -1:
            moves.append((loc[0] - 1, loc[1] - 1))
        if loc[0] - 1 > -1 and loc[1] + 1 < 8:
            moves.append((loc[0] - 1, loc[1] + 1))
    else:
        if loc[0] + 1 < 8 and loc[1] - 1 > -1:
            moves.append((loc[0] + 1, loc[1] - 1))
        if loc[0] + 1 < 8 and loc[1] + 1 < 8:
            moves.append((loc[0] + 1, loc[1] + 1))
    return moves


def convert_to_fen(board, turn, wcks, wcqs, bcks, bcqs):
    """
    Converts given board to fen string.
    :param board: 8 x 8 chess board
    :param turn: color allowed to move next
    :param wcks: white can castle king side
    :param wcqs: white can castle queen side
    :param bcks: black can castle king side
    :param bcqs: black can castle queen side
    :type board: tuple, list
    :type turn: str
    :type wcks: bool
    :type wcqs: bool
    :type bcks: bool
    :type bcqs: bool
    :return: fen string
    :rtype: str
    """
    _dict = {'wQ': 'Q',
             'wK': 'K',
             'wR': 'R',
             'wB': 'B',
             'wP': 'P',
             'wN': 'N',
             'bQ': 'q',
             'bK': 'k',
             'bR': 'r',
             'bB': 'b',
             'bP': 'p',
             'bN': 'n'}
    fen = ''
    for i, row in enumerate(board):
        empty_squares = 0
        for j, col in enumerate(row):
            if col == 1:
                empty_squares += 1
                if j == 7:
                    fen += str(empty_squares)
                    break
                else:
                    continue
            if empty_squares != 0:
                fen += str(empty_squares)
                empty_squares = 0
            if len(col) > 2:
                key = col[:2]
            else:
                key = col
            fen += _dict[key]
        fen += '/' if i < 7 else ''
    fen += ' ' + turn[0] + ' '
    can_castle = False
    if wcks:
        can_castle = True
        fen += 'K'
    if wcqs:
        can_castle = True
        fen += 'Q'
    if bcks:
        can_castle = True
        fen += 'k'
    if bcqs:
        can_castle = True
        fen += 'q'
    if not can_castle:
        fen += '-'
    return fen


class FenDict(dict):
    def __init__(self, _dict):
        super().__init__(_dict)

    def get_piece(self, key):
        result = self[key]
        if len(self[key]) == 3:
            self[key] = str(self[key][:2] + str(int(self[key][2]) + 1))
        else:
            self[key] = self[key] + '1'
        return result


def load_fen(fen):
    """"
    Returns a board as a list of lists and color next to move from given fen.
    :param fen: fen string to be converted
    :type fen: str
    :return: board, turn
    :rtype: tuple
    """
    # TODO: add numbers to pawns when placing them
    _dict = {'Q': 'wQ',
             'K': 'wK',
             'R': 'wR1',
             'B': 'wB1',
             'P': 'wP1',
             'N': 'wN1',
             'q': 'bQ',
             'k': 'bK',
             'r': 'bR1',
             'b': 'bB1',
             'p': 'bP1',
             'n': 'bN1'}
    fen_dict = FenDict(_dict)
    fen_turn = fen.split(' ')
    fen, turn = fen_turn[0], fen_turn[1]
    board = []
    str_nums = {'1', '2', '3', '4', '5', '6', '7', '8'}
    row, col = 0, 0
    for key in fen:
        if key == '/':
            col = 0
            row += 1
            continue
        elif key not in str_nums:
            if col == 0:
                board.insert(row, [])

            board[row].insert(col, fen_dict.get_piece(key))
            col += 1
        else:
            if col == 0:
                board.insert(row, [])
            for n in range(int(key)):
                board[row].insert(col, 1)
                col += 1
    turn = 'white' if turn == 'w' else 'black'
    return board, turn
