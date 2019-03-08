from chess.match import Match


def get_moves_pieces(board, color, wcks, wcqs, bcks, bcqs):
    # TODO: only set moves for color given, not for both.
    """
    Returns a dict for legal moves and piece locations with the keys being the pieces owned by given color.
    :param board: board state to get legal moves for.
    :param color: color whose moves and piece locations are returned
    :param wcks: white can castle king's side
    :param wcqs: white can castle queen's side
    :param bcks: black can castle king's side
    :param bcqs: black can castle queen's side
    :type board: tuple, Board
    :type color: str
    :type wcks: bool
    :type wcqs: bool
    :type bcks: bool
    :type bcqs: bool
    :return: legal moves, piece locations
    :rtype: tuple
    """
    a = Match(state=board, turn=color, wcks=wcks, wcqs=wcqs, bcks=bcks, bcqs=bcqs)
    if color == 'white':
        for key in a.white_moves:
            moves = []
            if 'Q' in key or 'R' in key or 'B' in key:
                for direction in a.white_moves[key]:
                    moves.extend(a.white_moves[key][direction])
                a.white_moves[key] = moves
        return a.white_moves, a.white_pieces_locations
    else:
        for key in a.black_moves:
            moves = []
            if 'Q' in key or 'R' in key or 'B' in key:
                for direction in a.black_moves[key]:
                    moves.extend(a.black_moves[key][direction])
                a.black_moves[key] = moves
        return a.black_moves, a.black_pieces_locations


def get_branch(c_pos, t_pos, state, color):

    c_row, c_column = c_pos[0], c_pos[1]
    t_row, t_column = t_pos[0], t_pos[1]

    piece = state[c_row][c_column]
    state[c_row][c_column] = 1

    if color == 'black' and 'bP' in piece and t_row == 7:
        num = piece[2:]
        piece = 'bQ' + num

    if color == 'white' and 'wP' in piece and t_row == 0:
        num = piece[2:]
        piece = 'wQ' + num

    state[t_row][t_column] = piece

    if 'K' in str(piece) and t_column == c_column - 3:
        rook = state[c_row][0]
        state[c_row][2] = rook
        state[c_row][0] = 1

    if 'K' in str(piece) and t_column == c_column + 2:
        rook = state[c_row][7]
        state[c_row][5] = rook
        state[c_row][7] = 1

    return state


def checkmate(board, color, wcks, wcqs, bcks, bcqs):
    """
    Checks if given state is checkmate for given color.
    :param board: tuple of 8 x 8 lists
    :param color: possible loser, either 'black' or 'white'
    :param wcks: white can castle king's side
    :param wcqs: white can castle queen's side
    :param bcks: black can castle king's side
    :param bcqs: black can castle queen's side
    :type board: tuple, Board
    :type color: str
    :type wcks: bool
    :type wcqs: bool
    :type bcks: bool
    :type bcqs: bool
    :return: True if given color lost else False
    :rtype: bool
    """

    a = Match(state=board, turn=color, wcks=wcks, wcqs=wcqs, bcks=bcks, bcqs=bcqs)

    if a.check_mate:
        return True
    return False
