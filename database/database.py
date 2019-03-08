import sqlite3
from database.queries import Queries


class Database(Queries):
    """
    Sqlite3 database, inherits from Queries.
    """
    def __init__(self, root, fn=r'C:\pythonprojects\chess_prod\database\nodes.db'):
        conn = sqlite3.connect(fn)
        self.fn = fn
        super(Database, self).__init__(conn)
        self.root = root
        self.tbn = 'white_nodes'

    def load(self, root):
        """
        Loads database to given root, sets settings.tot_n.
        :param root: root of chess game tree
        :type root: origin.Origin
        """
        from origin.node import Node

        curr = root
        tbn = 'white_nodes'
        parent_id = None
        color = 'white'
        stack = []

        while curr:
            data = self.get_nodes(tbn, parent_id)
            if data is None:
                if stack:
                    new = stack.pop()
                    curr, parent_id = new['node'], new['node_id']
                    tbn = '{}_nodes'.format(curr.opp)
                    color = curr.opp
                else:
                    curr = None
            else:
                for node in data:
                    child = Node(eval(node['board']), color, eval(node['move']), node['piece'],
                                 node['ind'], node['branch_path'],
                                 eval(node['tcc']), eval(node['ncc']), v=node['val'],
                                 n=node['visits'])

                    curr.nodes.append(child)
                    try:
                        stack.append({'node': curr.nodes[node['ind']], 'node_id': node['node_id']})
                    except IndexError:
                        breakpoint()

                new = stack.pop()
                curr, parent_id = new['node'], new['node_id']
                tbn = '{}_nodes'.format(curr.opp)
                color = curr.opp
        import settings
        settings.init_tot_n(n=sum(node.visits for node in root.nodes))

    def save_one_walk(self, nodes):
        """
        Update values in db of last walked nodes, inserts if not yet present.
        :param nodes: nodes walked last training round
        :type nodes: list, tuple
        """
        import settings
        root_node = nodes[0]
        node_id = self.get_node_id(root_node)
        if node_id is not None:
            data = (settings.white_points, settings.VISITS, root_node.branch_path)
            self.update_value_visits(data, 'white_nodes')
        else:
            data = (None,
                    repr(root_node.state),
                    repr(root_node.move),
                    root_node.piece,
                    root_node.index,
                    repr(root_node.this_can_castle),
                    repr(root_node.next_can_castle),
                    root_node.value,
                    root_node.visits,
                    root_node.branch_path,
                    None)
            self.insert_node(data, 'white_nodes')
            node_id = self.get_node_id(root_node)

        nodes = nodes[1:]

        for node in nodes:

            parent_id = node_id
            node_id = self.get_node_id(node)
            tbn = '{}_nodes'.format(node.color)

            if node_id is not None:
                points = settings.white_points if node.color == 'white' else settings.black_points
                data = (points, settings.VISITS, node.branch_path)
                self.update_value_visits(data, tbn)
            else:
                data = (None,
                        repr(node.state),
                        repr(node.move),
                        node.piece,
                        node.index,
                        repr(node.this_can_castle),
                        repr(node.next_can_castle),
                        node.value,
                        node.visits,
                        node.branch_path,
                        parent_id)
                self.insert_node(data, tbn)
        self.conn.commit()
