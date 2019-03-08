import database.database as database
import settings
from origin.node import Node
from chess.board import Board
from math import sqrt, log
from chess import chess_functions as cf
import copy


class Origin:
    """
    Root of chess game tree.
    """

    C = settings.C

    def __init__(self):
        """
        First calls settings.init_path_value(), then creates a starting board.
        Attributes:
             database = None
             state = Board().board
             nodes = []
             color = 'white'
             opp = 'black'
        """
        settings.init_path_value()
        self.database = None
        self.state = Board().board
        self.nodes = []
        self.color = 'white'
        self.opp = 'black'

    def get_best_move(self, state, user_color):
        """
        Searches node of given state and returns highest value move with it's piece. State can be given as FEN.
        :param state: current state of chess board
        :param user_color: user's side, either 'black' or 'white'
        :type state: str, tuple, list
        :type user_color: str
        :return: returns the move with highest value and its piece respectively
        :rtype: str, tuple
        """
        if type(state) == str:
            from chess.moves import load_fen
            state, turn = load_fen(state)
        num_pieces = 0
        for row in state:
            for sq in row:
                num_pieces += 1 if sq != 1 else 0
        if user_color != 'black' and user_color != 'white':
            raise ValueError("user_color must be 'black' or 'white'")
        if state == self.state:
            values = []
            for node in self.nodes:
                values.append(node.value / node.visits)
            for i, v in enumerate(values):
                if v == max(values):
                    return self.nodes[i].piece, self.nodes[i].move
        else:
            for node in self.nodes:
                move_piece = node.get_best_move(state, num_pieces, user_color)
                if move_piece:
                    return move_piece

    def load(self, fn=r'C:\pythonprojects\chess_prod\database\nodes.db'):
        """
        Load database to self
        :param fn: path to database file
        :return:
        """
        self.database = database.Database(self, fn=fn) if self.database is None else self.database
        self.database.load(self)

    def save_walk(self, walked_nodes=settings.walked_nodes, fn=r'C:\pythonprojects\chess_prod\database\nodes.db'):
        """
        First assigns save.Database(self, fn=fn) to self.database if database is not yet initialized.
        Saves last walk of tree to db: self.database.save_one_walk(walked_nodes).

        :param walked_nodes: list of nodes walked last training round, default is settings.walked_nodes
        :param fn: path to sqlite database file
        :type walked_nodes: list
        :type fn: str
        """
        self.database = database.Database(self, fn=fn) if self.database is None else self.database
        self.database.save_one_walk(walked_nodes)

    def expand(self):
        """
        Generates children nodes for each move available.
        """
        settings.init_tot_n()
        moves, pieces = cf.get_moves_pieces(self.state, self.color, True, True, True, True)
        index = 0
        for key in moves:

            piece = pieces[key]

            for move in moves[key]:
                white_castle = {'ks': True,
                                'qs': True}
                black_castle = {'ks': True,
                                'qs': True}
                sim_board = copy.deepcopy(self.state)
                branch = cf.get_branch(piece, move, sim_board, self.color)
                self.nodes.append(Node(branch, self.color, move, key,
                                       index, 'i' + str(index),
                                       white_castle, black_castle))
                index += 1

    def update(self):
        """
        Adds value of previous training round to this node's children node's value and calls update at that node.
        """
        layer = 0
        points = settings.white_points if self.color == 'white' else settings.black_points
        ind = settings.path[layer]
        self.nodes[ind].value += points
        if len(settings.path) - 1 > layer:
            layer += 1
            self.nodes[ind].update(layer)
        else:
            return

    def train(self):
        """
        Chooses child to train. Calls self.update first if self trained previous round and calls self.expand if we don't
        have child nodes yet. If all child nodes have been visited at least once, we compute the priority of node with:
        UCB1(node) = (node.value / node.visits) + (self.C * sqrt(ln(settings.tot_n) / node.visits)
        Then train the node which maximizes the UCB1 function and add settings.VISITS to settings.tot_n
        """
        settings.walked_nodes = []
        settings.init_path_value()
        if not self.nodes:
            self.expand()
            self.nodes[0].roll_out()
            settings.tot_n += settings.VISITS
            self.update()
            return
        values = []
        for node in self.nodes:
            if node.visits == 0:
                node.roll_out()
                settings.tot_n += settings.VISITS
                self.update()
                return
            val_1 = node.value / node.visits
            val_2 = self.C * sqrt(log(settings.tot_n) / node.visits)
            values.append(val_1 + val_2)
        hi_value = max(values)
        for i, v in enumerate(values):
            if v == hi_value:
                self.nodes[i].train()
                settings.tot_n += settings.VISITS
                self.update()
                return
