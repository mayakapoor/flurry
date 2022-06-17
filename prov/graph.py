from collections import defaultdict
import prov.queries as queries
import time

"""
The node class represents a single vertex in the network.
\param[in] serial the unique CamFlow serial id given to the node.
\param[in] type the assigned type to the node.
\param[in] index the node index which will serve to serialize it.
"""
class Node():
    def __init__(self, serial, type, index):
        self.index = index
        # node type
        self.type = type
        # features of the node
        self.features = None
        # cf given name
        self.serial = serial

    def id(self):
        return self.index

    def getType(self):
        return self.type

    def getSerial(self):
        return self.serial

    def hasFeatures(self):
        return self.features != None

    def getFeatures(self):
        return self.features

    def add_features(self, features):
        self.features = features

"""
The edge class represents a single relation in the network.
\param[in] serial the unique CamFlow serial id given to the edge.
\param[in] type the assigned type to the edge.
\param[in] src_node the node serial of the source node of the directed edge.
\param[in] dst_node the node serial of the destination node of the directed edge.
\param[in] index the edge index which will serve to serialize it.
"""
class Edge():
    def __init__(self, serial, type, src_node, dst_node, jiffies, index):
        self.index = index
        # edge type
        self.type = type
        # features of the edge
        self.features = None
        # source node of the edge
        self.src_node = src_node
        # dest node of the edge
        self.dst_node = dst_node
        # cf given name
        self.serial = serial
        #jiffies when captured
        self.jiffies = jiffies

    def id(self):
        return self.index

    def getSerial(self):
        return self.serial

    def getJiffies(self):
        return self.jiffies

    def getType(self):
        return self.type

    def getSrcNode(self):
        return self.src_node

    def getDstNode(self):
        return self.dst_node

    def hasFeatures(self):
        return self.features != None

    def getFeatures(self):
        return self.features

    def add_features(self, features):
        self.features = features

"""
This class represents an internal graph of Nodes and Edges
"""
class Graph():
    def __init__(self, id):
        # graph id
        self.id = id
        # node serial to Node object
        self.nodes = defaultdict()
        # edge serial to Edge object
        self.edges = defaultdict()
        # type schema (nt-et-nt), to list of node index tuples (src,dst)
        self.schemas = defaultdict(list)
        self.nodetypes = defaultdict(list)
        self.edgetypes = defaultdict(list)
        #self.nodehashes = set()
        #self.edgehashes = set()

    def getIndex(self):
        return self.id

    def num_nodes(self):
        return len(self.nodes)

    def num_edges(self):
        return len(self.edges)

    def num_node_types(self):
        return len(self.nodetypes)

    def num_edge_types(self):
        return len(self.edgetypes)

    def num_schemas(self):
        return len(self.schemas)

    def num_nodes_of_type(self, type):
        if type in self.nodetypes:
            return len(self.nodetypes[type])
        return 0

    def num_edges_of_type(self, type):
        if type in self.edgetypes:
            return len(self.edgetypes[type])
        return 0

    def num_edges_of_schema(self, schema):
        if schema in self.schemas:
            return len(self.schemas[schema])
        return 0

    #returns list of node ids
    def get_nodes_for_networkx(self):
        node_list = []
        for node in self.nodes:
            node_list.append(int(self.nodes[node].id()))
        return node_list

    def get_node_types(self):
        return self.nodetypes

    def get_nodes_with_types(self):
        node_dict = {}
        for node in self.nodes:
            node_dict[int(self.nodes[node].id())] = self.nodes[node].getType()
        return node_dict

    def get_nodes_with_attributes(self):
        node_list = []
        for node in self.nodes:
            node_list.append((self.nodes[node].id(), self.nodes[node].getFeatures()))
        return node_list

    def get_edges(self):
        edge_list = []
        for edge in self.edges:
            edge_list.append(self.edges[edge])
        return edge_list

    def get_edges_for_networkx(self):
        edge_list = []
        for edge in self.edges:
            edge_list.append((int(self.edges[edge].getSrcNode().id()),
                              int(self.edges[edge].getDstNode().id())))
        return edge_list

    def get_edges_with_types(self):
        edge_dict = {}
        for edge in self.edges:
            edge_dict[(int(self.edges[edge].getSrcNode().id()),
                       int(self.edges[edge].getDstNode().id()))] = self.edges[edge].getType()
        return edge_dict

    def get_edges_with_attributes(self):
        edge_list = []
        for edge in self.edges:
            edge_list.append((int(self.edges[edge].getSrcNode().id()),
                              int(self.edges[edge].getDstNode().id()),
                              self.edges[edge].getFeatures()))
        return edge_list

    def get_schemas(self):
        return list(self.schemas.keys())

    def get_schema_node_lists(self, schema):
        return list(map(list, zip(*self.schemas[schema])))

    def get_graph_dictionary(self):
        output_dict = defaultdict(list)
        for schema in self.get_schemas():
            str_schema = '-'.join(schema)
            src_dst = self.get_schema_node_lists(schema)
            output_dict[str_schema] = (src_dst[0], src_dst[1])
        return output_dict

    def add_node(self, serial, type, ):
        self.nodes[serial] = Node(serial, type, len(self.nodes))
        self.nodetypes[type].append(serial)

    def add_node(self, serial, type, features):
        self.nodes[serial] = Node(serial, type, len(self.nodes))
        self.nodetypes[type].append(serial)
        self.nodes[serial].add_features(features)

    def add_edge(self, serial, type, src_node, src_node_type, dst_node, dst_node_type, jiffies):
        self.edges[serial] = Edge(serial, type, self.nodes[src_node], self.nodes[dst_node], jiffies, len(self.edges))
        self.edgetypes[type].append(serial)

    def add_edge(self, serial, type, src_node, src_node_type, dst_node, dst_node_type, features, jiffies):
        self.edges[serial] = Edge(serial, type, self.nodes[src_node], self.nodes[dst_node], jiffies, len(self.edges))
        self.edgetypes[type].append(serial)
        self.edges[serial].add_features(features)

        # add nodes
        if src_node not in self.nodes:
            self.nodes[serial] = Node(src_node, src_node_type, len(self.nodes))
            self.nodetypes[src_node_type].append(src_node)
        if dst_node not in self.nodes:
            self.nodes[serial] = Node(dst_node, dst_node_type, len(self.nodes))
            self.nodetypes[dst_node_type].append(dst_node)

        # add edge schema
        self.schemas[(src_node_type, type, dst_node_type)].append((self.nodes[src_node].id(), self.nodes[dst_node].id()))

    def save_to_disk(self, db):
        start = time.time()
        print("Saving graph to database...")
        cursor = db.cursor()
        for type in self.nodetypes.keys():
            sql = queries.insert_type(type)
            cursor.execute(sql)
        for type in self.edgetypes.keys():
            sql = queries.insert_type(type)
            cursor.execute(sql)
        db.commit()
        print("type: " + str(time.time() - start))

        start = time.time()
        edgefeatures = []
        #cursor.execute("BEGIN TRANSACTION;")
        for edge in self.edges:
            sql = queries.get_type_index(self.edges[edge].getSrcNode().getType())
            cursor.execute(sql)
            src_node_type_id = cursor.fetchone()[0]
            sql = queries.insert_node(src_node_type_id, self.getIndex())
            cursor.execute(sql)
            cursor.execute(queries.get_last_row_id())
            src_node_id = cursor.fetchone()[0]

            sql = queries.get_type_index(self.edges[edge].getDstNode().getType())
            cursor.execute(sql)
            dst_node_type_id = cursor.fetchone()[0]
            sql = queries.insert_node(dst_node_type_id, self.getIndex())
            cursor.execute(sql)
            cursor.execute(queries.get_last_row_id())
            dst_node_id = cursor.fetchone()[0]
            
            start = time.time()

            sql = queries.get_type_index(self.edges[edge].getType())
            cursor.execute(sql)
            edge_type_id = cursor.fetchone()[0]

            sql = queries.insert_edge(self.getIndex(),
                edge_type_id,
                src_node_id,
                dst_node_id,
                self.edges[edge].getJiffies())
            cursor.execute(sql)
        print("edges: " + str(time.time()-start))
        db.commit()
        cursor.close()
        print("Graph {} saved.".format(self.id))

    def clear(self):
        self.nodes = defaultdict()
        self.edges = defaultdict()
        self.schemas = defaultdict(list)
        self.nodetypes = defaultdict(list)
        self.edgetypes = defaultdict(list)
