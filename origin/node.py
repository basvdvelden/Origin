import settings
from math import sqrt, log
from chess import match as mch, chess_functions as cf
import copy
from chess.moves import convert_to_fen, load_fen


class Node:
    """
    Node in chess game tree.
    """
    C = settings.C

    def __init__(self, state, color, move, piece, index, branch_path, this_can_castle, next_can_castle, v=0, n=0):
        """
        If given state is a fen converts fen to list of lists, checks if this is a leaf node (checkmate or draw)
        :param state (str, list, tuple): either a fen or tuple/list of 8 lists
        :param color (str): side of this node, either 'white' or 'black'
        :param move (tuple): coordinates
        :param piece (str): string of piece belonging to move
        :param index (int): index of this node in parent node.nodes
        :param branch_path (str): a string specifying the path to this node
        :param this_can_castle (dict): castling availability for this node
        :param next_can_castle (dict): castling availability for next node
        :param v (int): value of this node, if created while expanding in parent node v=0
        :param n (int): visits to this node, if created while expanding in parent node n=0
        """

        self.branch_path = branch_path
        self.index = index
        self.move = copy.deepcopy(move)
        self.piece = copy.deepcopy(piece)
        self.value = v
        self.visits = n
        self.nodes = []
        self.color = color
        self.next_can_castle = copy.deepcopy(next_can_castle)
        self.this_can_castle = copy.deepcopy(this_can_castle)

        if self.color == 'white':
            self.white_can_castle = copy.deepcopy(self.this_can_castle)
            self.black_can_castle = copy.deepcopy(self.next_can_castle)
        else:
            self.white_can_castle = copy.deepcopy(self.next_can_castle)
            self.black_can_castle = copy.deepcopy(self.this_can_castle)

        if type(state) == str:
            self.state, self.opp = load_fen(state)
            self.fen = state
        else:
            self.state = state
            self.opp = 'black' if self.color == 'white' else 'white'
            self.fen = convert_to_fen(state, self.opp,
                                      self.white_can_castle['ks'],
                                      self.white_can_castle['qs'],
                                      self.black_can_castle['ks'],
                                      self.black_can_castle['qs'], )

        self.win = cf.checkmate(self.state, self.opp,
                                self.white_can_castle['ks'], self.white_can_castle['qs'],
                                self.black_can_castle['ks'], self.black_can_castle['qs'])
        if not self.win:
            moves, pieces = cf.get_moves_pieces(self.state, self.opp,
                                                self.white_can_castle['ks'], self.white_can_castle['qs'],
                                                self.black_can_castle['ks'], self.black_can_castle['qs'])

            self.draw = True if not moves else False
        else:
            self.draw = False

    def expand(self):
        """
        Generates children nodes for each move available of this node. Checks if a king or rook moved.
        """
        moves, pieces = cf.get_moves_pieces(self.state, self.opp,
                                            self.white_can_castle['ks'], self.white_can_castle['qs'],
                                            self.black_can_castle['ks'], self.black_can_castle['qs'])

        opp_can_castle, i_can_castle = {}, {}
        i_can_castle['ks'], i_can_castle['qs'] = self.this_can_castle['ks'], self.this_can_castle['qs']

        index = 0
        for key in moves:

            piece = pieces[key]
            opp_can_castle['ks'], opp_can_castle['qs'] = self.next_can_castle['ks'], self.next_can_castle['qs']

            if key == 'K':
                opp_can_castle['ks'], opp_can_castle['qs'] = False, False
            elif key == 'R1':
                opp_can_castle['qs'] = False
            elif key == 'R2':
                opp_can_castle['ks'] = False

            for move in moves[key]:
                branch_path = self.branch_path + 's' + str(index)
                sim_board = copy.deepcopy(self.state)
                board_state = cf.get_branch(piece, move, sim_board, self.opp)

                self.nodes.append(Node(board_state, self.opp, move, key,
                                       index, branch_path,
                                       opp_can_castle, i_can_castle))
                index += 1

    def update(self, layer):
        """
        Adds value of previous training round to this node's children node's value and calls update at that node.
        :param layer: index for settings.path to get node to be updated
        :type layer: int
        """

        points = settings.white_points if self.opp == 'white' else settings.black_points
        ind = settings.path[layer]
        self.nodes[ind].value += points
        self.value += settings.white_points if layer == 0 else 0

        if len(settings.path) - 1 > layer:
            layer += 1
            self.nodes[ind].update(layer)
        else:
            return

    def train(self):
        """
        We begin by adding a visit to self.visits or more if otherwise specified in settings.
        Then add our index to settings.path,
        And add self to settings.walked_nodes.

        Decides child to walk in 3 possible actions:

        if this has no nodes we expand and call the self.nodes[0].roll_out(),
        if we have a node still unvisited we call that node's roll_out(),
        otherwise we roll_out() the node which maximizes the UCB1 function.

        if this is a leaf node we return after updating settings.black_points and settings.white_points
        """
        self.visits += settings.VISITS
        settings.path.append(self.index)
        settings.walked_nodes.append(self)
        if not self.nodes:

            this_points = settings.black_points if self.color == 'black' else settings.white_points
            opp_points = settings.white_points if this_points == settings.black_points else settings.black_points

            if self.draw:
                this_points += (settings.DRAW * settings.VISITS) / 2
                opp_points += (settings.DRAW * settings.VISITS) / 2
                return
            elif self.win:
                this_points += (settings.WIN * settings.VISITS)
                opp_points -= 2
                return
            else:
                self.expand()
                self.nodes[0].roll_out()
                return

        values = []

        for node in self.nodes:
            if node.visits == 0:
                node.roll_out()
                return

            val_1 = node.value / node.visits
            val_2 = self.C * sqrt(log(settings.tot_n) / node.visits)
            values.append(val_1 + val_2)

        hi_value = max(values)

        for i, v in enumerate(values):
            if v == hi_value:
                self.nodes[i].train()
                return

    def simulate(self):
        """
        Simulates a random game and adds earned points to settings.white_points and settings.black_points
        """
        if self.win:
            if self.color == 'white':
                settings.white_points += settings.WIN
            else:
                settings.black_points += settings.WIN
            return
        if self.draw:
            settings.white_points += settings.DRAW
            settings.black_points += settings.DRAW
            return
        white_can_castle, black_can_castle = copy.deepcopy(self.white_can_castle), copy.deepcopy(self.black_can_castle)
        state = copy.deepcopy(self.state)
        winner = mch.random_game(state, self.opp, white_can_castle, black_can_castle)
        if not winner:
            settings.black_points += settings.DRAW
            settings.white_points += settings.DRAW
        if winner == 'white':
            settings.white_points += settings.WIN
        if winner == 'black':
            settings.black_points += settings.WIN

    def roll_out(self):
        """
        Appends self to settings.walked_nodes and self.index to settings.path,
        then calls self.simulate()
        """
        settings.walked_nodes.append(self)
        settings.path.append(self.index)
        self.visits += settings.VISITS
        self.simulate()

    def __str__(self):
        return self.branch_path
