def create_node_table():
    sql = """
        CREATE TABLE IF NOT EXISTS Nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id INTEGER NOT NULL,
        graph_id INTEGER NOT NULL,
        FOREIGN KEY (type_id) REFERENCES Types(id)
        );
        """
    return sql

def create_type_table():
    sql = """
        CREATE TABLE IF NOT EXISTS Types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL UNIQUE
        );
        """
    return sql

def get_type_index(type):
    sql = """
        SELECT id FROM Types
        WHERE type="{}";
        """.format(type)
    return sql

def insert_type(new_type):
    sql = """
        REPLACE INTO Types (type) VALUES ("{}");
        """.format(new_type)
    return sql

def create_edge_table():
    sql = """
        CREATE TABLE IF NOT EXISTS Edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id INTEGER NOT NULL,
        src_node_id INTEGER NOT NULL,
        dst_node_id INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        graph_id INTEGER NOT NULL,
        FOREIGN KEY (type_id) REFERENCES Types(id),
        FOREIGN KEY (src_node_id) REFERENCES Nodes(id),
        FOREIGN KEY (dst_node_id) REFERENCES Nodes(id)
        );
        """
    return sql

def insert_node(type_id, graph_id):
    sql = """
        REPLACE INTO Nodes (type_id, graph_id) VALUES ({}, {});
        """.format(type_id, graph_id)
    return sql

def insert_edge(graph_id, edge_type_id, src_node_id, dst_node_id, created_at):
    sql = """
        REPLACE INTO Edges (type_id, src_node_id, dst_node_id, created_at, graph_id)
        VALUES ({}, {}, {}, {}, {});
        """.format(edge_type_id, src_node_id, dst_node_id,
            created_at, graph_id)
    return sql

def get_last_row_id():
    sql = """
        SELECT last_insert_rowid();
        """
    return sql
