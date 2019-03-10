WIN = 2
DRAW = 0.25
NUM_SIMULATIONS = 1
C = 2
VISITS = NUM_SIMULATIONS
walked_nodes = []
path = []
tot_n = 0
white_points = 0
black_points = 0


def init_tot_n(n=0):
    """
    Initializes total visits = n = tot_n. If save was loaded, the sum of Origin.nodes.visits should be passed.
    :param n: total visits of game tree
    :type n: int
    """
    global tot_n
    tot_n = n


def init_path_value():
    """
    Resets path of traversal, points earned by white and points earned by black.

    global path, white_points, black_points

    white_points, black_points = 0, 0
    path = []
    """
    global path, white_points, black_points
    white_points, black_points = 0, 0
    path = []
