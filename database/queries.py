class Queries:
    def __init__(self, connection):
        """
        Initializes cursor for given connection.
        Calls self.setup()
        :param connection: sqlite connection to db file
        :type connection: sqlite3.Connection
        """
        self.conn = connection
        self.c = self.conn.cursor()
        self.setup()

    def setup(self):
        self.create_nodes_table('white_nodes')
        self.create_nodes_table('black_nodes')
        self.c.execute("PRAGMA synchronous = OFF")
        self.c.execute("PRAGMA journal_mode = OFF")
        self.conn.isolation_level = None
        self.conn.commit()

    def create_nodes_table(self, tbn):
        """
        Creates table if not exists with columns:

        node_id         INTEGER not null
                            primary key autoincrement,
        board           VARCHAR [350],
        move            VARCHAR [6],
        piece           VARCHAR [3],
        ind             INT,
        this_can_castle VARCHAR[27],
        next_can_castle VARCHAR[27],
        value           INT,
        visits          INT,
        branch_path     VARCHAR[200] UNIQUE,
        parent_id       INTEGER

        This does not set parent_id to foreign key! To do this call self.set_foreign_keys(color)
        :param tbn: table name
        :type tbn: str
        """
        self.c.execute("""CREATE TABLE IF NOT EXISTS {tbn}
                          (
                            node_id         INTEGER not null
                              primary key autoincrement,
                            board           VARCHAR [350],
                            move            VARCHAR [6],
                            piece           VARCHAR [3],
                            ind             INT,
                            this_can_castle VARCHAR[27],
                            next_can_castle VARCHAR[27],
                            value           INT,
                            visits          INT,
                            branch_path     VARCHAR[200] UNIQUE,
                            parent_id       INTEGER
                          )""".format(tbn=tbn))

    def set_foreign_keys(self, color):
        other_color = 'black' if color == 'white' else 'white'
        create_temp = """CREATE TABLE {color}_nodes_dg_tmp
                            (
                            node_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            board VARCHAR[350],
                            move VARCHAR[6],
                            piece VARCHAR[3],
                            ind INT,
                            this_can_castle VARCHAR[27],
                            next_can_castle VARCHAR[27],
                            value INT,
                            visits INT,
                            branch_path VARCHAR[200] UNIQUE,
                            parent_id INTEGER
                            CONSTRAINT {color}_nodes_{other}_nodes__fk 
                            REFERENCES {other}_nodes ("node_id") ON UPDATE CASCADE
                            )""".format(color=color, other=other_color)

        migrate_temp = """INSERT INTO {color}_nodes_dg_tmp
                    (node_id, board, move, piece, ind, this_can_castle, next_can_castle, value, visits, parent_id) 
                    
                    SELECT node_id, board, move, piece, ind, this_can_castle, next_can_castle, value, visits, parent_id
                    FROM {color}_nodes""".format(color=color)

        drop = """DROP TABLE {color}_nodes""".format(color=color)

        rename = """ALTER TABLE {color}_nodes_dg_tmp RENAME TO {color}_nodes""".format(color=color)
        queries = (create_temp, migrate_temp, drop, rename)
        for q in queries:
            self.c.execute(q)

    def insert_node(self, data, tbn, mult=False):
        """
        Insert node in given tbn.

        :param data: rows to be inserted
        :param tbn: name of table, 'white_nodes' or 'black_nodes'
        :param mult: True if inserting multiple rows in one call
        :type data: list, tuple
        :type tbn: str
        :type mult: bool
        """
        query_mode = self.c.execute if not mult else self.c.executemany
        query_mode("""INSERT INTO {tbn} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(tbn=tbn), data)

    def update_value_visits(self, data, tbn, mult=False):
        """
        Update the value and visits of given nodes as:

                    UPDATE {tbn}
                    SET value = node.value, visits = node.visits
                    WHERE branch_path = node.branch_path;

        :param data: rows to be updated
        :param tbn: name of table, 'white_nodes' or 'black_nodes'
        :param mult: True if updating multiple rows in one call
        :type data: list, tuple
        :type tbn: str
        :type mult: bool
        """

        query_mode = self.c.execute if not mult else self.c.executemany
        query = """UPDATE {tbn}
                   SET value = value + ?, visits = visits + ?
                   WHERE branch_path = ?""".format(tbn=tbn)
        query_mode(query, data)

    def get_nodes(self, tbn, parent_id):
        """
        Returns a list of rows containing data for .origin.node
        :param tbn: table name to get nodes from
        :param parent_id: node_id of parent node, if root node parent_id should be None
        :type parent_id: int, None
        :type tbn: str
        :return: list of dictionaries with node data
        :rtype: list
        """
        if parent_id is None:
            self.c.execute("""SELECT * FROM {tbn} 
                              WHERE parent_id ISNULL
                              ORDER BY ind ASC""".format(tbn=tbn))
        else:
            self.c.execute("""SELECT * FROM {tbn} 
                              WHERE parent_id = ?
                              ORDER BY ind ASC""".format(tbn=tbn), (parent_id, ))

        nodes = self.c.fetchall()
        if not nodes:
            return None

        keys = ('node_id', 'board', 'move', 'piece', 'ind', 'tcc', 'ncc', 'val', 'visits', 'branch_path')
        new_nodes = []

        for row in nodes:
            nodes_dict = {}
            for col, key in zip(row, keys):
                nodes_dict[key] = col
            new_nodes.append(nodes_dict)

        return new_nodes

    def get_node_id(self, node):
        """
        Get primary key for given node.
        :param node: tree node
        :type node: Node
        :return: node_id
        :rtype: int
        """
        table = '{}_nodes'.format(node.color)
        self.c.execute("""SELECT node_id FROM {tbn}
                          WHERE branch_path = ? LIMIT 1"""
                       .format(tbn=table), (node.branch_path, ))

        parent_id = self.c.fetchone()

        if parent_id is None:
            return parent_id
        else:
            return parent_id[0]
