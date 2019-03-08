DROP TABLE black_nodes;

CREATE TABLE black_nodes
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
);
DROP TABLE white_nodes;

CREATE TABLE white_nodes
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
);