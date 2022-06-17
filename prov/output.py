import os
import json

import prov.graph
import dgl
import networkx as nx
from collections import defaultdict

#######################
#        helpers      #
#######################
def one_hot_encode(idx, len):
    ret = [0] * len
    ret[idx] = 1
    return ret

def reverse_dict(dictionary):
    revdict = {}
    for key in dictionary:
        revdict[dictionary[key]] = key
    return revdict

#######################
#    output funcs     #
#######################

def print_graph_info(G, id):
    print("Statistics for graph: " + str(id))
    #print("Binary type: " + str(bin))
    #print("Multiclass type: " + str(multi))
    print("number of nodes: " + str(G.num_nodes()))
    print("number of node types: " + str(G.num_node_types()))
    for type in G.nodetypes:
        print(type + " - " + str(len(G.nodetypes[type])))
    print("number of edges: " + str(G.num_edges()))
    print("number of edge types: " + str(G.num_edge_types()))
    for type in G.edgetypes:
        print(type + " - " + str(len(G.edgetypes[type])))
    print("number of distinct edge schemas: " + str(G.num_schemas()))
    for schema in G.get_schemas():
        print(schema)

class GraphTransformer():
    def __init__(self, output_path, id):
        self.output_path = output_path
        self.id = id

        def set_output_path(self, new_path):
            self.output_path = new_path

        def set_id(self, new_id):
            self.id = new_id

    # make a graph with whatever has been loaded into our storage.
    def create_networkx_graph_with_attributes(self, G):
        print("Making NetworkX Graph...")
        nxG = nx.MultiDiGraph()
        nxG.add_nodes_from(G.get_nodes_with_attributes())
        nxG.add_edges_from(G.get_edges_with_attributes())
        print("Graph constructed.")
        return nxG

    def create_networkx_graph(self, G):
        print("Making NetworkX Graph...")
        nxG = nx.MultiDiGraph()
        nxG.add_nodes_from(G.get_nodes_for_networkx())
        nxG.add_edges_from(G.get_edges_for_networkx())
        print("Graph constructed.")
        return nxG

    def create_dgl_graph(self, G):
        print("Making DGL Graph...")
        DG = dgl.graph(G.get_graph_dictionary(), idtype=int)
        print("Graph constructed.")
        return DG

    def create_labeled_graph(self, G):
        print("Making NetworkX Graph...")
        nxG = nx.DiGraph()
        nxG.add_nodes_from(G.get_nodes_for_networkx())
        nxG.add_edges_from(G.get_edges_for_networkx())
        nx.draw_networkx_labels(nxG, pos=nx.spring_layout(nxG), labels=G.get_nodes_with_types())
        nx.draw_networkx_edge_labels(nxG, pos=nx.spring_layout(nxG), edge_labels=G.get_edges_with_types())
        print("Graph constructed.")
        return nxG

    # serialize the graph with a default path name.
    def graph_to_pickle(self, G):
        print("converting graph to pickle...")
        out = self.output_path
        out += "/graph{}/graph{}.gpickle".format(str(self.id), str(self.id))
        NG = self.create_networkx_graph(G)
        nx.write_gpickle(NG, out)
        print("Graph pickle outputted to " + out + ".")

    def graph_to_png(self, G):
        NG = nx.DiGraph()
        NG.add_nodes_from(G.get_nodes_for_networkx())
        reNG = nx.relabel_nodes(NG, G.get_nodes_with_types())
        for edge in G.get_edges():
            reNG.add_edge(edge.getSrcNode().getType(), edge.getDstNode().getType(), label=edge.getType(), data=edge.getType())
        print("Drawing graph...")
        out = self.output_path + "/graph{}".format(str(self.id))
        if not os.path.exists(out):
            os.makedirs(out)
        out += "/graph{}.png".format(str(self.id), str(self.id))

        A = nx.nx_agraph.to_agraph(reNG)
        A.draw(out, format="png", prog="dot", args="-Goverlap=scale -Efont_size=8")
        print("Graph drawn to " + out + ".")


class GraphSerializer():
    def __init__(self, output_path, id):
        self.output_path = output_path
        self.id = id

    def set_output_path(self, new_path):
        self.output_path = new_path

    def set_id(self, new_id):
        self.id = new_id

    #output a JSON-formatted dictionary where key = node type, value = list of nodes
    def node_types_to_json(self, G):
        print("outputting node types to JSON format...")
        type_dict = {}
        types = list(G.nodetypes.keys())
        for node in G.nodes:
            type_dict[G.nodes[node].id()] = one_hot_encode(types.index(G.nodes[node].getType()), len(types))
        out = self.output_path + "/graph{}".format(str(self.id))
        if not os.path.exists(out):
            os.makedirs(out)
        out += "/nodetypes{}.json".format(str(self.id), str(self.id))
        with open(f'{out}', 'w') as f:
            f.write(str(types))
            json.dump(type_dict, f, indent=2)
        print("Node types outputted to " + out + ".")


    #output a JSON-formatted dictionary where key = edge type, value = list of nodes
    def edge_types_to_json(self, G):
        print("outputting edge types to JSON format...")
        type_dict = {}
        types = list(G.edgetypes.keys())
        for edge in G.edges:
            type_dict[G.edges[edge].id()] = one_hot_encode(types.index(G.edges[edge].getType()), len(types))

        out = self.output_path + "/graph{}".format(str(self.id))
        if not os.path.exists(out):
            os.makedirs(out)
        out += "/edgetypes{}.json".format(str(self.id), str(self.id))
        with open(f'{out}', 'w') as f:
            f.write(str(types))
            json.dump(type_dict, f, indent=2)
        print("Edge types outputted to " + out + ".")

    # output a JSON-formatted dictionary where key = edge_schema, value = src node list and dest node list where src[i]-edge-dest[i]
    def graph_to_json(self, G):
        print("outputting graph to JSON format...")
        output_dict = G.get_graph_dictionary()

        out = self.output_path + "/graph{}".format(str(self.id))
        if not os.path.exists(out):
            os.makedirs(out)
        out += "/graph{}.json".format(str(self.id), str(self.id))
        with open(f'{out}', 'w') as f:
            json.dump(output_dict, f)
        print("Graph outputted to " + out + ".")

    def graph_info_to_file(self, G):
        out = self.output_path + "/graph{}".format(str(self.id))
        if not os.path.exists(out):
            os.makedirs(out)
        out += "/stats{}.txt".format(str(self.id), str(self.id))
        with open(f'{out}', 'w') as f:
            f.write("Statistics for graph: " + str(self.id) + "\n")
            #f.write("Class Selections: " + str(self.bin_type) + "\n")
            f.write("number of nodes: " + str(G.num_nodes()) + "\n")
            f.write("number of node types: " + str(G.num_node_types()) + "\n")
            for type in G.nodetypes:
                f.write(type + " - " + str(len(G.nodetypes[type])) + "\n")
            f.write("number of edges: " + str(G.num_edges()) + "\n")
            f.write("number of edge types: " + str(G.num_edge_types()) + "\n")
            for type in G.edgetypes:
                f.write(type + " - " + str(len(G.edgetypes[type])) + "\n")
            f.write("number of distinct edge schemas: " + str(G.num_schemas()) + "\n")
            for schema in G.get_schemas():
                str_schema = '-'.join(schema)
                f.write(str(str_schema) + " - " + str(len(G.schemas[schema])) + "\n")
