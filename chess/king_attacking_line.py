
class DangerLines(list):
    def __init__(self, inverse_dict, opp_inverse_dict, k_loc):
        self.keys = set()
        self.inv_pieces = inverse_dict
        self.opp_inv_pieces = opp_inverse_dict
        self.king_loc = k_loc
        self.king_attacker = None

    def delete_line(self, key):
        """
        Deletes self[key], and removes key from self.keys.
        :param key: piece to delete moves of.
        :type key: str
        """
        for i, line in enumerate(self):
            if line.key == key:
                self.keys.discard(self[i].key)
                del self[i]

    def delete_lines(self):
        """
        King's location changed so we delete the lines no longer attacking the king.
        """
        for i, line in enumerate(self):
            if self.king_loc not in line:
                self.keys.discard(self[i].key)
                del self[i]
                self.delete_lines()

    def king_moved(self, new_loc):
        """
        Sets self.king_loc to given location.
        :param new_loc: new location of king
        :type new_loc: tuple
        """
        self.king_loc = new_loc
        self.delete_lines()

    def is_targeted(self, loc):
        """
        Checks if given location is targeted by pseudo legal moves contained in self.

        :param loc: location to check
        :type loc: tuple
        :return: True if targeted else False
        :rtype: bool
        """
        for line in self:
            if line.is_targeted(loc):
                return True
        return False

    def would_be_check(self, loc, move, already_check=False):
        """
        Simulates the scenario of given move played, checks if it would result in check.

        :param loc: location of piece
        :param move: move to check if it would result in check
        :param already_check: is it already check?
        :type loc: tuple
        :type move: tuple
        :type already_check: bool
        :return: True if would be check else false
        :rtype: bool
        """
        lines = self.get_targeting_lines(loc)
        if not already_check:
            for line in lines:
                if move == line.loc:
                    return False

        self.inv_pieces[str(move)] = self.inv_pieces[str(loc)]
        del self.inv_pieces[str(loc)]
        result = self.will_be_check(loc, lines=lines)
        self.king_attacker = None
        self.inv_pieces[str(loc)] = self.inv_pieces[str(move)]
        del self.inv_pieces[str(move)]
        return result

    def get_attacker(self):
        """
        Returns loc, direction of piece having king checked.
        :return: location of piece which has king in check, direction of line checking king
        :rtype: tuple
        """
        result = self.king_attacker
        self.king_attacker = None
        return result

    def will_be_check(self, move, lines=False):
        """
        Checks if given move results in check.
        :param move: move to be checked
        :param lines: False if not called by self, otherwise lines targeting given move.
        :type move: tuple
        :type lines: bool, KingTargetingPseudoLine
        :return: True if move results in check else False
        :rtype: bool
        """
        lines = self.get_targeting_lines(move) if not lines else lines

        if len(lines) == 1:
            for target in lines[0]:
                if target == self.king_loc:
                    self.king_attacker = (lines[0].loc, lines[0].direction)
                    return True
                if str(target) in self.inv_pieces.keys() or str(target) in self.opp_inv_pieces.keys():
                    return False

        for ind, line in enumerate(lines):
            for target in line:
                if target == self.king_loc:
                    self.king_attacker = (line.loc, line.direction)
                    return True
                if str(target) in self.inv_pieces.keys() or str(target) in self.opp_inv_pieces.keys():
                    if ind == len(lines) - 1:
                        return False
                    break

    def get_targeting_lines(self, loc):
        """
        Return KingTargetingPseudoLine targeting given loc.

        :param loc: location to get targeting KingTargetingPseudoLine(s) for
        :type loc: tuple
        :return: list of KingTargetingPseudoLine objects targeting given location
        :rtype: KingTargetingPseudoLine
        """
        danger_lines = []
        for line in self:
            if line.is_targeted(loc):
                danger_lines.append(line)
        return danger_lines

    def is_king_attacker(self, key):
        """
        Checks if given piece is pseudo targeting it's opponent's king.

        :param key: piece who might be targeting it's opponent's king
        :type key: str
        :return: True if key in self.keys else False
        :rtype: bool
        """
        if key in self.keys:
            return True
        return False

    def append_x(self, king_targ_ps_line):
        """
        Adds king_targ_ps_line.key to self.keys, then appends king_targ_ps_line to self.

        :param king_targ_ps_line: list of pseudo legal moves targeting the opponent's king,
                                  always moves belonging to a queen, bishop or rook
        :type king_targ_ps_line: KingTargetingPseudoLine
        """
        self.keys.add(king_targ_ps_line.key)
        self.append(king_targ_ps_line)


class KingTargetingPseudoLine(list):
    """
    List subclass, a pseudo legal list of moves which target the opponent's king.
    """
    def __init__(self, key, loc, direction, moves):
        """
        Calls super().__init__(moves), sets self._set to None.
        :param key: the targeting piece
        :param loc: loc of targeting piece
        :param direction: direction aimed at by targeting piece
        :param moves: moves which target the targeting piece's opponent's king
        """
        super().__init__(moves)
        self.key = key
        self.loc = loc
        self.direction = direction
        self._set = None

    def is_targeted(self, loc):
        """
        Checks if loc is in self. initializes self._set if not already initialized.
        :param loc: location that might be targeted
        :type loc: tuple
        :return: True if targeted else False
        :rtype: bool
        """
        if not self._set:
            self._set = set(self)
        if loc in self._set:
            return True
        return False


class SquaresTargeted(dict):
    def __init__(self):
        self.move_set = set()

    def assign(self, key, moves):
        """
        Assigns given moves to self[key] and updates self.move_set
        :param key: piece whose moves to assign
        :param moves: moves to assign to self[key] as a set given as a list of tuples
        :type key: str
        :type moves: list
        :return:
        """
        self[key] = set(moves)
        self.move_set = set()
        for key in self:
            self.move_set.update(self[key])

    def piece_died(self, key):
        """
        Deletes self[key] and updates self.move_set
        :param key: piece that died
        :type key: str
        """
        del self[key]
        self.move_set = set()
        for key in self:
            self.move_set.update(self[key])
