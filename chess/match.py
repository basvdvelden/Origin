from chess.board import Board
from copy import deepcopy
from chess.moves import *
from random import choice
from chess.king_attacking_line import KingTargetingPseudoLine, DangerLines, SquaresTargeted
import logging
import json
from multiprocessing import Process

all_ps_moves = ps_moves_per_loc()
complied = False


class Match:
    def __init__(self, state=Board().board, turn='white', wcks=True, wcqs=True, bcks=True, bcqs=True):
        self.white_can_castle = {'ks': wcks, 'qs': wcqs}
        self.black_can_castle = {'ks': bcks, 'qs': bcqs}
        self.state = state
        self.fen = convert_to_fen(self.state, turn, wcks, wcqs, bcks, bcqs)
        self.black_pieces_locations = {}
        self.white_pieces_locations = {}
        self.board_locations_occupied_by_black = {}
        self.board_locations_occupied_by_white = {}
        self.ps_black_moves = {}
        self.ps_white_moves = {}
        self.black_moves = {}
        self.white_moves = {}
        self.set_piece_locations()
        self.continuous_non_capped_turns = 0
        try:
            self.black_king_targeting_ps_lines = DangerLines(self.board_locations_occupied_by_black,
                                                             self.board_locations_occupied_by_white,
                                                             self.black_pieces_locations['K'])

            self.white_king_targeting_ps_lines = DangerLines(self.board_locations_occupied_by_white,
                                                             self.board_locations_occupied_by_black,
                                                             self.white_pieces_locations['K'])
        except KeyError:
            for row in self.state:
                print(row)
            raise KeyError('King is not in board!')
        self.king_attacking_line = []
        self.white_non_iterative = SquaresTargeted()
        self.black_non_iterative = SquaresTargeted()
        self.b_check = False
        self.w_check = False
        self.turn = turn
        self.king_attackers_locations = []
        self.check_mate = False
        self.winner = None
        self.draw = False
        self.moves_keys_history = {'wcc': deepcopy(self.white_can_castle), 'bcc': deepcopy(self.black_can_castle),
                                   'keys': [], 'moves': [], 'state': self.state, 'fen': self.fen}
        self.key = None
        self.trace = []
        global DEBUG, complied
        if DEBUG and not complied:
            inp = input('Debug is on, logs will be overwritten. Continue with debug on? y/n: ')
            if inp != 'y':
                DEBUG = False
            complied = True
        if DEBUG:
            logging.basicConfig(filename='game_data{}.log'.format(count), level=logging.DEBUG, filemode='w')
            self.logger = logging.getLogger()
        self.set_all_ps_moves()

    def is_in_black_ps_moves(self, move):
        """
        Goes through black's pseudo moves and checks if given move is in the black's pseudo moves.
        :param move: see if it is in black pseudo moves
        :type move: tuple
        :return: True if move is in black pseudo moves else False
        :rtype: bool
        """
        for key in self.ps_black_moves:
            if 'Q' in key or 'B' in key or 'R' in key:
                for direction in self.ps_black_moves[key]:
                    if move in self.ps_black_moves[key][direction]:
                        return True
        return False

    def is_in_white_ps_moves(self, move):
        """
        Goes through white's pseudo moves and checks if given move is in the white's pseudo moves.
        :param move: see if it is in white pseudo moves
        :type move: tuple
        :return: True if move is in white pseudo moves else False
        :rtype: bool
        """
        for key in self.ps_white_moves:
            if 'Q' in key or 'B' in key or 'R' in key:
                for direction in self.ps_white_moves[key]:
                    if move in self.ps_white_moves[key][direction]:
                        return True
        return False

    def legal_line(self, moves, color, per_mov=False, board=False):
        """
        Returns legal moves.
        :param moves: pseudo moves
        :param color: side of pseudo moves given, must be 'black' or 'white'
        :param per_mov: set to True if moves given are of a pawn king or knight
        :param board: board to use check the moves given, default is self.state
        :type moves: list
        :type color: str
        :type per_mov: bool
        :type board: tuple
        :return: legal moves
        :rtype: list
        """
        board = self.state if not board else board
        new_moves = []
        if color == 'white':
            me, opp = 'w', 'b'
        else:
            me, opp = 'b', 'w'
        if not per_mov:
            for move in moves:
                if me in str(board[move[0]][move[1]]):
                    moves = new_moves
                    return moves
                elif opp in str(board[move[0]][move[1]]):
                    new_moves.append(move)
                    return new_moves
                elif me not in str(board[move[0]][move[1]]):
                    new_moves.append(move)
        else:
            for move in moves:
                if me not in str(board[move[0]][move[1]]):
                    new_moves.append(move)
        return new_moves

    def set_piece_locations(self):
        """
        Called one time at initialisation, sets locations for pieces of both sides.
        :return:
        """
        for num in range(2):
            pieces = {}
            locations_occupied = {}
            me = 'w' if num == 0 else 'b'
            for i, row in enumerate(self.state):
                for j, sq in enumerate(row):
                    if me in str(sq):
                        key = sq.replace(me, '')
                        pieces[key] = (i, j)
                        locations_occupied['({}, {})'.format(i, j)] = key
            if num == 0:
                self.white_pieces_locations = pieces
                self.board_locations_occupied_by_white = locations_occupied
            else:
                self.black_pieces_locations = pieces
                self.board_locations_occupied_by_black = locations_occupied

    def get_king_targeting_lines(self, color, loc=False, get_direction=False):
        """
        Returns the pieces and their lines that target the given location, also returns their direction at index 1*
        if get_direction is set to True.
        :param color: side who needs the targeting lines, must be 'white' or 'black'
        :param loc: location to use as the target
        :param get_direction: True if the direction key is also needed
        :type color: str
        :type loc: tuple
        :type get_direction: bool
        :return: a tuple of keys, directions*, lines that target the given location
        :rtype: tuple
        """
        if color == 'white':
            ps_move_dict = self.ps_black_moves
            if not loc:
                king = self.white_pieces_locations['K']
            else:
                king = loc
        else:
            ps_move_dict = self.ps_white_moves
            if not loc:
                king = self.black_pieces_locations['K']
            else:
                king = loc

        keys = []
        directions = []
        lines = []

        for key in ps_move_dict:
            if 'Q' in key or 'B' in key or 'R' in key:
                for direction in ps_move_dict[key]:
                    if king in ps_move_dict[key][direction]:
                        if get_direction:
                            directions.append(direction)

                        keys.append(key)
                        lines.append(ps_move_dict[key][direction])

        if get_direction:
            return keys, directions, lines
        else:
            return keys, lines

    def moves_safety_check(self, color):
        """
        Checks if legal moves will cause check in which case the move is removed from legal moves.
        :param color: side to have moves checked, either 'black' or 'white'
        :type color: str
        """
        def kings_move_is_dangerous():
            """Is called if the move is in the opponent's pseudo moves."""
            attackers, lines = self.get_king_targeting_lines(color, loc=move)
            row = piece_locations[key][0]
            col = piece_locations[key][1]
            safe = True
            for attacker, line in zip(attackers, lines):

                sim_board = deepcopy(self.state)
                sim_board[row][col] = 1
                sim_board[move[0]][move[1]] = me + key

                if move[1] == col - 3:
                    sim_board[row][0] = 1
                    sim_board[row][2] = me + 'R1'
                elif move[1] == col + 2:
                    sim_board[row][7] = 1
                    sim_board[row][5] = me + 'R2'

                if move in self.legal_line(line, opp_color, board=sim_board):
                    safe = False
                    break
            if safe:
                safe_moves.append(move)

        if color == 'white':
            move_dict = self.white_moves
            k_targeting_ps_lines = self.white_king_targeting_ps_lines
            opp_non_iter_moves = self.black_non_iterative
            is_in_opp_moves = self.is_in_black_ps_moves
            opp, me = 'b', 'w'
            opp_color = 'black'
            check = self.w_check
            piece_locations = self.white_pieces_locations
            pawn_one_step_two_steps, start_row = (-1, -2), 6
        else:
            move_dict = self.black_moves
            k_targeting_ps_lines = self.black_king_targeting_ps_lines
            opp_non_iter_moves = self.white_non_iterative
            is_in_opp_moves = self.is_in_white_ps_moves
            opp, me = 'w', 'b'
            opp_color = 'white'
            check = self.b_check
            piece_locations = self.black_pieces_locations
            pawn_one_step_two_steps, start_row = (1, 2), 1

        for key in move_dict:
            if 'Q' in key or 'R' in key or 'B' in key:
                if check:
                    if len(self.king_attackers_locations) > 1:
                        move_dict[key] = None
                        continue
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        for direction in move_dict[key]:
                            safe_moves = []
                            for move in move_dict[key][direction]:
                                if k_targeting_ps_lines.would_be_check(piece_locations[key], move, already_check=check):
                                    break
                                elif move in self.king_attacking_line or move in self.king_attackers_locations:
                                    safe_moves.append(move)
                            move_dict[key][direction] = safe_moves
                    else:
                        for direction in move_dict[key]:
                            safe_moves = []
                            for move in move_dict[key][direction]:
                                if move in self.king_attacking_line or move in self.king_attackers_locations:
                                    safe_moves.append(move)

                            move_dict[key][direction] = safe_moves
                elif k_targeting_ps_lines:
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        for direction in move_dict[key]:
                            safe_moves = []
                            for move in move_dict[key][direction]:
                                if k_targeting_ps_lines.would_be_check(piece_locations[key], move):
                                    break
                                safe_moves.append(move)
                            move_dict[key][direction] = safe_moves
                bad_directions = []
                for direction in move_dict[key]:
                    if not move_dict[key][direction]:
                        bad_directions.append(direction)
                for direction in bad_directions:
                    del move_dict[key][direction]
            elif 'N' in key:
                if not move_dict[key]:
                    continue
                if check:
                    if len(self.king_attackers_locations) > 1:
                        move_dict[key] = None
                        continue
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        if k_targeting_ps_lines.would_be_check(piece_locations[key],
                                                               move_dict[key][0],
                                                               already_check=check):

                            move_dict[key] = None
                            continue

                        safe_moves = []
                        for move in move_dict[key]:
                            if move in self.king_attacking_line or move in self.king_attackers_locations:
                                safe_moves.append(move)
                        move_dict[key] = safe_moves if safe_moves else None
                        continue
                    else:
                        safe_moves = []
                        for move in move_dict[key]:
                            if move in self.king_attacking_line or move in self.king_attackers_locations:
                                safe_moves.append(move)
                        move_dict[key] = safe_moves if safe_moves else None
                        continue
                elif k_targeting_ps_lines:
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        if k_targeting_ps_lines.would_be_check(piece_locations[key], move_dict[key][0]):
                            move_dict[key] = None
                            continue
            elif 'P' in key:
                if piece_locations[key][0] + pawn_one_step_two_steps[0] not in range(8):
                    move_dict[key] = None
                    continue
                one_step = (piece_locations[key][0] + pawn_one_step_two_steps[0], piece_locations[key][1])
                safe_moves = []
                if check:
                    if len(self.king_attackers_locations) > 1:
                        move_dict[key] = None
                        continue
                    danger = False
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        danger = True
                        for move in move_dict[key]:
                            if k_targeting_ps_lines.would_be_check(piece_locations[key], move, already_check=check):
                                continue
                            if move in self.king_attackers_locations:
                                safe_moves.append(move)
                    else:
                        for move in move_dict[key]:
                            if move in self.king_attackers_locations:
                                safe_moves.append(move)
                    if danger:
                        if str(self.state[one_step[0]][one_step[1]]) == '1':
                            if k_targeting_ps_lines.would_be_check(piece_locations[key], one_step):
                                move_dict[key] = safe_moves if safe_moves else None
                                continue
                            if one_step in self.king_attacking_line:
                                safe_moves.append(one_step)
                            if piece_locations[key][0] == start_row:
                                two_steps = (piece_locations[key][0] + pawn_one_step_two_steps[1], piece_locations[key][1])
                                if str(self.state[two_steps[0]][two_steps[1]]) == '1':
                                    if two_steps in self.king_attacking_line:
                                        safe_moves.append(two_steps)
                    else:
                        if str(self.state[one_step[0]][one_step[1]]) == '1':
                            if one_step in self.king_attacking_line:
                                safe_moves.append(one_step)
                            if piece_locations[key][0] == start_row:
                                two_steps = (piece_locations[key][0] + pawn_one_step_two_steps[1],
                                             piece_locations[key][1])

                                if str(self.state[two_steps[0]][two_steps[1]]) == '1':
                                    if two_steps in self.king_attacking_line:
                                        safe_moves.append(two_steps)
                elif k_targeting_ps_lines:
                    danger = False
                    if k_targeting_ps_lines.is_targeted(piece_locations[key]):
                        danger = True
                        for move in move_dict[key]:
                            if k_targeting_ps_lines.would_be_check(piece_locations[key], move):
                                continue
                            else:
                                if opp in str(self.state[move[0]][move[1]]):
                                    safe_moves.append(move)
                    else:
                        for move in move_dict[key]:
                            if opp in str(self.state[move[0]][move[1]]):
                                safe_moves.append(move)
                    if str(self.state[one_step[0]][one_step[1]]) == '1':
                        if danger:
                            if k_targeting_ps_lines.would_be_check(piece_locations[key], one_step):
                                move_dict[key] = safe_moves if safe_moves else None
                                continue
                            else:
                                safe_moves.append(one_step)
                                if piece_locations[key][0] == start_row:
                                    two_steps = (piece_locations[key][0] + pawn_one_step_two_steps[1],
                                                 piece_locations[key][1])

                                    if str(self.state[two_steps[0]][two_steps[1]]) == '1':
                                        safe_moves.append(two_steps)
                        else:
                            safe_moves.append(one_step)
                            if piece_locations[key][0] == start_row:
                                two_steps = (piece_locations[key][0] + pawn_one_step_two_steps[1],
                                             piece_locations[key][1])

                                if str(self.state[two_steps[0]][two_steps[1]]) == '1':
                                    safe_moves.append(two_steps)
                else:
                    for move in move_dict[key]:
                        if opp in str(self.state[move[0]][move[1]]):
                            safe_moves.append(move)

                    if str(self.state[one_step[0]][one_step[1]]) == '1':
                        safe_moves.append(one_step)
                        if piece_locations[key][0] == start_row:
                            two_steps = (piece_locations[key][0] + pawn_one_step_two_steps[1], piece_locations[key][1])
                            if str(self.state[two_steps[0]][two_steps[1]]) == '1':
                                safe_moves.append(two_steps)

                move_dict[key] = safe_moves if safe_moves else None

            else:
                safe_moves = []
                if check:
                    for move in move_dict[key]:
                        if move in self.king_attacking_line or move in opp_non_iter_moves.move_set:
                            continue
                        elif is_in_opp_moves(move):
                            kings_move_is_dangerous()
                        else:
                            safe_moves.append(move)
                    move_dict[key] = safe_moves if safe_moves else None
                else:
                    for move in move_dict[key]:
                        if move in opp_non_iter_moves.move_set:
                            continue
                        elif is_in_opp_moves(move):
                            kings_move_is_dangerous()
                        else:
                            safe_moves.append(move)
                    move_dict[key] = safe_moves

        keys_to_del = []
        for key in move_dict:
            if not move_dict[key]:
                keys_to_del.append(key)

        for key in keys_to_del:
            del move_dict[key]

        if not move_dict:
            self.check_mate = True
            self.winner = 'black' if color == 'white' else 'white'

    def set_all_ps_moves(self):
        """
        Is called one time at initialisation, sets all the pseudo-legal moves for both sides.
        """
        for key in self.white_pieces_locations:
            if 'Q' in key or 'R' in key or 'B' in key:
                self.ps_white_moves[key] = {}
                self.update_ps_iterative_moves(key, 'white')
            elif 'P' in key or 'N' in key:
                self.update_ps_non_iterative_moves(key, 'white')
            else:
                self.update_king_moves('white')

        for key in self.black_pieces_locations:
            if 'Q' in key or 'R' in key or 'B' in key:
                self.ps_black_moves[key] = {}
                self.update_ps_iterative_moves(key, 'black')
            elif 'P' in key or 'N' in key:
                self.update_ps_non_iterative_moves(key, 'black')
            else:
                self.update_king_moves('black')

        if self.turn == 'white':
            self.moves_safety_check(color='black')
            self.moves_safety_check(color='white')
        else:
            self.moves_safety_check(color='white')
            self.moves_safety_check(color='black')

    def random_move(self):
        """
        Selects a random move and the. makes the move.
        """
        moves = self.white_moves if self.turn == 'white' else self.black_moves
        random_key = choice(list(moves.keys()))

        if random_key != 'K' and 'P' not in random_key and 'N' not in random_key:
            random_direction = choice(list(moves[random_key].keys()))
            random_move = choice(moves[random_key][random_direction])
        else:
            random_move = choice(moves[random_key])

        self.make_move(random_move, random_key)

    def simulate(self):
        """
        plays a random game
        :return: returns the winner unless it was a draw in which case it will return None
        """
        for n in range(1000000):
            self.random_move()
            if self.draw or self.check_mate:
                return self.winner

    def check_or_king_ps_targeted(self, key, loc, color):
        """
        Checks if it is check or if the opponent's king is targeted by the pseudo moves of the given piece.
        :param key: piece, cannot be a pawn, knight or king
        :param loc: location of given key
        :param color: side of given key must be 'black' or 'white'
        :type key: str
        :type loc: tuple
        :type color: str
        """
        if color == 'white':
            try:
                king_loc = self.black_pieces_locations['K']
            except KeyError:
                self.save_game(fn='king_loc_key_error.json')
                raise

            opp_k_targeting_ps_lines = self.black_king_targeting_ps_lines
            move_dict = self.white_moves
            ps_move_dict = self.ps_white_moves
        else:
            try:
                king_loc = self.white_pieces_locations['K']
            except KeyError:
                self.save_game(fn='king_loc_key_error.json')
                raise

            opp_k_targeting_ps_lines = self.white_king_targeting_ps_lines
            move_dict = self.black_moves
            ps_move_dict = self.ps_black_moves

        ps_moves = []
        for direction in ps_move_dict[key]:
            ps_moves.append(ps_move_dict[key][direction])

        if 'Q' in key:
            directions = ('tr', 'tl', 'br', 'bl', 'u', 'd', 'r', 'l')
        elif 'R' in key:
            directions = ('u', 'd', 'r', 'l')
        else:
            directions = ('tr', 'tl', 'br', 'bl')

        if len(ps_moves) == 4:
            leg_moves = (self.legal_line(ps_moves[0], color), self.legal_line(ps_moves[1], color),
                         self.legal_line(ps_moves[2], color), self.legal_line(ps_moves[3], color))
        else:
            leg_moves = (self.legal_line(ps_moves[0], color), self.legal_line(ps_moves[1], color),
                         self.legal_line(ps_moves[2], color), self.legal_line(ps_moves[3], color),
                         self.legal_line(ps_moves[4], color), self.legal_line(ps_moves[5], color),
                         self.legal_line(ps_moves[6], color), self.legal_line(ps_moves[7], color))

        move_dict[key] = {}
        for index, direction in enumerate(directions):
            if leg_moves[index]:
                move_dict[key][direction] = leg_moves[index]
        i = 0
        for ps_line, leg_line in zip(ps_moves, leg_moves):
            if king_loc in ps_line:
                opp_k_targeting_ps_lines.append_x(KingTargetingPseudoLine(key, loc, directions[i], ps_line))
                if king_loc in leg_line:
                    self.king_attackers_locations.append(loc)
                    self.king_attacking_line.extend(leg_line)
                    self.w_check = True if color == 'black' else self.w_check
                    self.b_check = True if color == 'white' else self.b_check
            i += 1

    def update_legal_iterative_moves(self, key, color):
        """
        This sets the reachable squares a.k.a legal moves. ps_moves must already be set!
        :param key: piece to have legal moves updated, cannot be a pawn, knight or king
        :param color: side of the piece, must be 'black' or 'white'
        :type key: str
        :type color: str
        """
        ps_move_dict = self.ps_white_moves if color == 'white' else self.ps_black_moves
        leg_move_dict = self.white_moves if color == 'white' else self.black_moves
        leg_move_dict[key] = {}

        if 'Q' in key:
            tr, tl = ps_move_dict[key]['tr'], ps_move_dict[key]['tl']
            br, bl = ps_move_dict[key]['br'], ps_move_dict[key]['bl']
            u, d = ps_move_dict[key]['u'], ps_move_dict[key]['d']
            r, l = ps_move_dict[key]['r'], ps_move_dict[key]['l']

            leg_move_dict[key]['tr'], leg_move_dict[key]['tl'] = self.legal_line(tr, color), self.legal_line(tl, color)
            leg_move_dict[key]['br'], leg_move_dict[key]['bl'] = self.legal_line(br, color), self.legal_line(bl, color)
            leg_move_dict[key]['u'], leg_move_dict[key]['d'] = self.legal_line(u, color), self.legal_line(d, color)
            leg_move_dict[key]['r'], leg_move_dict[key]['l'] = self.legal_line(r, color), self.legal_line(l, color)
        elif 'B' in key:
            tr, tl = ps_move_dict[key]['tr'], ps_move_dict[key]['tl']
            br, bl = ps_move_dict[key]['br'], ps_move_dict[key]['bl']

            leg_move_dict[key]['tr'], leg_move_dict[key]['tl'] = self.legal_line(tr, color), self.legal_line(tl, color)
            leg_move_dict[key]['br'], leg_move_dict[key]['bl'] = self.legal_line(br, color), self.legal_line(bl, color)
        else:
            u, d = ps_move_dict[key]['u'], ps_move_dict[key]['d']
            r, l = ps_move_dict[key]['r'], ps_move_dict[key]['l']

            leg_move_dict[key]['u'], leg_move_dict[key]['d'] = self.legal_line(u, color), self.legal_line(d, color)
            leg_move_dict[key]['r'], leg_move_dict[key]['l'] = self.legal_line(r, color), self.legal_line(l, color)

    def update_ps_iterative_moves(self, key, color):
        """
        This sets the pseudo legal lines.
        :param key: piece to have pseudo legal moves updated, cannot be a pawn, knight or king
        :param color: side of the piece, must be 'black' or 'white'
        :type key: str
        :type color: str
        """
        loc = self.white_pieces_locations[key] if color == 'white' else self.black_pieces_locations[key]
        ps_move_dict = self.ps_white_moves if color == 'white' else self.ps_black_moves
        ps_move_dict[key] = {}
        pmk = str(loc)
        if 'Q' in key:

            ps_move_dict[key]['tr'], ps_move_dict[key]['tl'] = all_ps_moves[pmk]['tr'], all_ps_moves[pmk]['tl']
            ps_move_dict[key]['br'], ps_move_dict[key]['bl'] = all_ps_moves[pmk]['br'], all_ps_moves[pmk]['bl']
            ps_move_dict[key]['u'], ps_move_dict[key]['d'] = all_ps_moves[pmk]['u'], all_ps_moves[pmk]['d']
            ps_move_dict[key]['r'], ps_move_dict[key]['l'] = all_ps_moves[pmk]['r'], all_ps_moves[pmk]['l']

        elif 'B' in key:

            ps_move_dict[key]['tr'], ps_move_dict[key]['tl'] = all_ps_moves[pmk]['tr'], all_ps_moves[pmk]['tl']
            ps_move_dict[key]['br'], ps_move_dict[key]['bl'] = all_ps_moves[pmk]['br'], all_ps_moves[pmk]['bl']

        else:

            ps_move_dict[key]['u'], ps_move_dict[key]['d'] = all_ps_moves[pmk]['u'], all_ps_moves[pmk]['d']
            ps_move_dict[key]['r'], ps_move_dict[key]['l'] = all_ps_moves[pmk]['r'], all_ps_moves[pmk]['l']

        self.check_or_king_ps_targeted(key, loc, color)

    def update_legal_non_iterative_moves(self, key, color):
        """
        This sets the legal moves. ps_moves must already be set!
        :param key: piece to have legal moves updated, must be a pawn, knight or king
        :param color: side of the piece, must be 'black' or 'white'
        :type key: str
        :type color: str
        """
        if key == 'K':
            self.update_king_moves(color)
            return
        moves = self.ps_white_moves[key] if color == 'white' else self.ps_black_moves[key]
        leg_move_dict = self.white_moves if color == 'white' else self.black_moves
        leg_move_dict[key] = self.legal_line(moves, color, per_mov=True)

    def update_ps_non_iterative_moves(self, key, color):
        """
        This sets pseudo legal moves.
        :param key: piece to have legal moves updated, must be a pawn, knight or king
        :param color: side of the piece, must be 'black' or 'white'
        :type key: str
        :type color: str
        """
        if color == 'white':
            loc = self.white_pieces_locations[key]
            try:
                king_loc = self.black_pieces_locations['K']
            except KeyError:
                self.save_game(fn='king_loc_non_it.json')
                raise
            ps_moves = self.ps_white_moves
            move_dict = self.white_moves
            non_it_moves = self.white_non_iterative
        else:
            loc = self.black_pieces_locations[key]
            try:
                king_loc = self.white_pieces_locations['K']
            except KeyError:
                self.save_game(fn='king_loc_non_it.json')
                raise
            ps_moves = self.ps_black_moves
            move_dict = self.black_moves
            non_it_moves = self.black_non_iterative

        if 'P' in key:
            moves = ps_pawn_cap_moves(loc, color)
        else:
            moves = ps_knight_moves(loc)

        non_it_moves.assign(key, moves)
        ps_moves[key] = moves

        leg_moves = self.legal_line(moves, color, per_mov=True)
        move_dict[key] = leg_moves

        if king_loc in moves:
            if color == 'white':
                self.b_check = True
            else:
                self.w_check = True
            self.king_attackers_locations.append(loc)

    def king_moved(self, color):
        """
        Updates king_targeting_ps_lines of the side whose king moved.
        :param color: side whose king moved, must be 'black' or 'white'
        :type color: str
        """
        if color == 'white':
            loc = self.white_pieces_locations['K']
            is_in_opp_moves = self.is_in_black_ps_moves
            danger_lines = self.white_king_targeting_ps_lines
            opp_pieces = self.black_pieces_locations
        else:
            loc = self.black_pieces_locations['K']
            is_in_opp_moves = self.is_in_white_ps_moves
            danger_lines = self.black_king_targeting_ps_lines
            opp_pieces = self.white_pieces_locations

        danger_lines.king_moved(loc)
        if is_in_opp_moves(loc):
            keys, dirs, lines = self.get_king_targeting_lines(color, loc=loc, get_direction=True)
            for key, direction, line in zip(keys, dirs, lines):
                if key in danger_lines.keys:
                    continue
                attacker_loc = opp_pieces[key]
                danger_lines.append_x(KingTargetingPseudoLine(key, attacker_loc, direction, line))

    def update_king_moves(self, color):
        """
        Updates moves for given color's king, checks if can castle.
        :param color: side of king to have moves updated
        """
        if color == 'white':
            loc = self.white_pieces_locations['K']
            can_castle = self.white_can_castle
            ps_moves = self.ps_white_moves
            move_dict, pieces = self.white_moves, self.white_pieces_locations
            non_it_moves = self.white_non_iterative
        else:
            loc = self.black_pieces_locations['K']
            can_castle = self.black_can_castle
            ps_moves = self.ps_black_moves
            move_dict, pieces = self.black_moves, self.black_pieces_locations
            non_it_moves = self.black_non_iterative

        moves = ps_king_moves(loc, color)
        ps_moves['K'] = moves
        non_it_moves.assign('K', moves)
        leg_moves = self.legal_line(moves, color, per_mov=True)
        if can_castle['ks']:
            ps_moves['K'].append((pieces['K'][0], 6))
            for col in range(5, 7):
                if self.state[pieces['K'][0]][col] != 1:
                    break
                if col == 6:
                    leg_moves.append((pieces['K'][0], 6))

        if can_castle['qs']:
            ps_moves['K'].append((pieces['K'][0], 1))
            for col in range(3, 0, -1):
                if self.state[pieces['K'][0]][col] != 1:
                    break
                if col == 1:
                    leg_moves.append((pieces['K'][0], 1))
        move_dict['K'] = None
        if leg_moves:
            move_dict['K'] = leg_moves

        else:
            del move_dict['K']

    def update_logs(self, key, move, old_loc, castled):
        """
        Updates classes whose definitions are located in king_attacking_line.py.
        These check if certain moves are allowed and won't cause check.
        Also checks if pawns reached the final rank.
        :param key: last moved piece
        :param move: last move made
        :param old_loc: old location of last moved piece
        :param castled: did a king castle, only True if piece is king
        """
        if self.turn == 'white':
            opp_k_targeting_ps_lines, opp_non_iter_moves = self.black_king_targeting_ps_lines, self.black_non_iterative
            pieces_locations, inv_pieces = self.white_pieces_locations, self.board_locations_occupied_by_white
            ps_moves, moves = self.ps_white_moves, self.white_moves
            pawn_edge_row = 0
            can_castle = self.white_can_castle
        else:
            opp_k_targeting_ps_lines, opp_non_iter_moves = self.white_king_targeting_ps_lines, self.white_non_iterative
            pieces_locations, inv_pieces = self.black_pieces_locations, self.board_locations_occupied_by_black
            ps_moves, moves = self.ps_black_moves, self.black_moves
            pawn_edge_row = 7
            can_castle = self.black_can_castle

        if key == 'R1':
            can_castle['qs'] = False
        elif key == 'R2':
            can_castle['ks'] = False
        elif key == 'K':
            can_castle['ks'], can_castle['qs'] = False, False
            if castled:
                if move[1] == 1:
                    pieces_locations['R1'] = (move[0], 2)
                    inv_pieces[str((move[0], 2))] = 'R1'
                    try:
                        del inv_pieces[str((move[0], 0))]
                    except KeyError:
                        self.save_game(fn='castled_r1_.json')
                        raise KeyError("couldn't delete old location of R1")

                    opp_k_targeting_ps_lines.delete_line('R1')
                    self.update_ps_iterative_moves('R1', self.turn)

                elif move[1] == 6:
                    pieces_locations['R2'] = (move[0], 5)
                    inv_pieces[str((move[0], 5))] = 'R2'
                    try:
                        del inv_pieces[str((move[0], 7))]
                    except KeyError:
                        self.save_game(fn='castled_r2_.json')
                        raise KeyError("couldn't delete old location of R2")

                    opp_k_targeting_ps_lines.delete_line('R2')
                    self.update_ps_iterative_moves('R2', self.turn)
                else:
                    raise ValueError('Castled was passed as true but the move is not a legal castle move.')

        elif 'P' in key and move[0] == pawn_edge_row:
            non_it_moves = self.white_non_iterative if self.turn == 'white' else self.black_non_iterative
            non_it_moves.piece_died(key)
            del pieces_locations[key], ps_moves[key], moves[key]
            self.key = 'Q' + key[1]
            key = self.key
            ps_moves[key] = {}
            self.state[move[0]][move[1]] = self.turn[0] + key

        pieces_locations[key] = move
        inv_pieces[str(move)] = key
        try:
            del inv_pieces[str(old_loc)]
        except KeyError:
            self.save_game(fn='del_inv_pieces.json')
            raise

        if opp_k_targeting_ps_lines.is_king_attacker(key):
            opp_k_targeting_ps_lines.delete_line(key)

        if opp_k_targeting_ps_lines.is_targeted(old_loc):
            def is_check():
                attacker = opp_k_targeting_ps_lines.get_attacker()
                self.king_attackers_locations.append(attacker[0])
                try:
                    att_key = inv_pieces[str(attacker[0])]
                except KeyError:
                    print(opp_k_targeting_ps_lines.keys)
                    self.save_game(fn='att_key_error.json')
                    raise KeyError('Something went wrong!')
                ps_line = ps_moves[att_key][attacker[1]]
                self.king_attacking_line.extend(self.legal_line(ps_line, self.turn))

            if self.turn == 'white':
                self.b_check = opp_k_targeting_ps_lines.will_be_check(old_loc)
                if self.b_check:
                    is_check()
            else:
                self.w_check = opp_k_targeting_ps_lines.will_be_check(old_loc)
                if self.w_check:
                    is_check()

    def is_piece_capped(self, move):
        """
        Checks if a piece was captured, and updates data in response.
        :param move: last move made
        """
        if self.turn == 'white':
            danger_lines = self.white_king_targeting_ps_lines
            opp_ps_moves, opp_moves, opp_non_it_moves = self.ps_black_moves, self.black_moves, self.black_non_iterative
            opp_pieces, opp_inv_pieces = self.black_pieces_locations, self.board_locations_occupied_by_black
            opp_can_castle = self.black_can_castle
        else:
            danger_lines = self.black_king_targeting_ps_lines
            opp_ps_moves, opp_moves, opp_non_it_moves = self.ps_white_moves, self.white_moves, self.white_non_iterative
            opp_pieces, opp_inv_pieces = self.white_pieces_locations, self.board_locations_occupied_by_white
            opp_can_castle = self.white_can_castle

        if self.state[move[0]][move[1]] != 1:
            self.continuous_non_capped_turns = 0
            capped = self.state[move[0]][move[1]][1:]
            if 'P' not in capped and 'N' not in capped:
                if 'R1' in capped:
                    opp_can_castle['qs'] = False
                elif 'R2' in capped:
                    opp_can_castle['ks'] = False
                if danger_lines.is_king_attacker(capped):
                    danger_lines.delete_line(capped)
            else:
                opp_non_it_moves.piece_died(capped)
            try:
                del opp_pieces[capped], opp_ps_moves[capped], opp_inv_pieces[str(move)], opp_moves[capped]
            except KeyError:
                if capped not in opp_moves.keys() or capped not in opp_ps_moves.keys():
                    pass
                else:
                    self.save_game(fn='del_key_error_301.json')
                    raise
        else:
            self.continuous_non_capped_turns += 1

    def save_game(self, fn='match.json'):
        """
        Saves full match in match.json with starting board, all moves made including the pieces and
        whether black and white could castle.
        loading a file with data for a match can be played using rerun_game(fn=fn).
        :param fn: default is match.json, file to have match stored in
        :type fn: str
        """
        with open(fn, 'w') as f:
            json.dump(self.moves_keys_history, f, indent=1)

    def make_move(self, move, key):
        """
        Places piece in new location and updates data:
        self.is_piece_capped(...),
        self.update_logs(...)
        and updates moves for pieces needing it.
        :param move: move to be made
        :param key: piece to move
        """

        self.key = key
        self.moves_keys_history['keys'].append(key)
        self.moves_keys_history['moves'].append(move)

        if self.turn == 'white':
            ps_moves, pieces_locations = self.ps_white_moves, self.white_pieces_locations
            opp_ps_moves = self.ps_black_moves
            old_loc = pieces_locations[self.key]
            opp = 'black'
        else:
            ps_moves, pieces_locations = self.ps_black_moves, self.black_pieces_locations
            opp_ps_moves = self.ps_white_moves
            old_loc = pieces_locations[self.key]
            opp = 'white'

        self.is_piece_capped(move)
        if self.continuous_non_capped_turns == 50:
            self.draw, self.winner = True, None
            return

        piece = self.state[old_loc[0]][old_loc[1]]
        self.state[old_loc[0]][old_loc[1]] = 1
        self.state[move[0]][move[1]] = piece

        castled = False
        if self.key == 'K':
            if move[1] == pieces_locations[self.key][1] - 3:
                castled = True
                rook1, self.state[move[0]][0] = self.state[move[0]][0], 1
                self.state[move[0]][2] = rook1

            elif move[1] == pieces_locations[self.key][1] + 2:
                castled = True
                rook2, self.state[move[0]][7] = self.state[move[0]][7], 1
                self.state[move[0]][5] = rook2

        self.update_logs(self.key, move, old_loc, castled)

        def update_moves(_key, _color):
            if 'P' not in _key and 'N' not in _key and 'K' not in _key:
                self.update_ps_iterative_moves(_key, _color)
            elif 'K' not in _key:
                self.update_ps_non_iterative_moves(_key, _color)
            else:
                if self.key == 'K':
                    self.king_moved(_color)
                self.update_king_moves(_color)

        def update_legal_moves(_key, _color):
            if 'P' not in _key and 'N' not in _key and 'K' not in _key:
                self.update_legal_iterative_moves(_key, _color)
            else:
                self.update_legal_non_iterative_moves(_key, _color)
        for key_2 in ps_moves:
            if key_2 == self.key:
                update_moves(key_2, self.turn)
                continue
            update_legal_moves(key_2, self.turn)
        for key_2 in opp_ps_moves:
            update_legal_moves(key_2, opp)

        self.moves_safety_check(opp)

        if len(self.black_pieces_locations) == 1 and len(self.white_pieces_locations) == 1:
            self.draw = True
            self.winner = None

        self.turn = 'black' if self.turn == 'white' else 'white'
        self.w_check = False
        self.b_check = False
        self.king_attackers_locations = []
        self.king_attacking_line = []


def rerun_game(fn='del_inv_pieces.json'):
    with open(fn, 'r') as f:
        data = json.load(f)
        board, turn = load_fen(data['fen'])
        a = Match(state=board, turn=turn, bcqs=data['bcc']['qs'])
        i = 0
        for piece_key, move in zip(data['keys'], data['moves']):
            if piece_key == 'R1':
                breakpoint()
            a.make_move(tuple(move), piece_key)
            # if i > 25:
            #     breakpoint()
            i += 1


def run_simulation_test():
    b = Board()
    a = Match(state=b.board)
    a.simulate()
    del a


def random_game(board, turn, white_can_castle, black_can_castle):
    wcks, wcqs = white_can_castle['ks'], white_can_castle['qs']
    bcks, bcqs = black_can_castle['ks'], black_can_castle['qs']
    match = Match(state=board, turn=turn, wcks=wcks, wcqs=wcqs, bcks=bcks, bcqs=bcqs)
    return match.simulate()


def check_board(state):
    board = state
    a = Match(state=board, turn='black')


def chess_sim_multiprocess(num_procs=5):
    procs = []
    for p in range(num_procs):
        proc = Process(target=run_simulation_test)
        procs.append(proc)
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()


DEBUG = False


if __name__ == '__main__':
    rerun_game(fn='..\del_inv_pieces.json')

