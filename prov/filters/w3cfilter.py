import orjson
import os
import sys
import time

import prov.graph

class W3CFilter():
    """
    Initialize the filter.
    """
    def __init__(self, edge_gran, node_gran):
        self.edge_granularity = edge_gran
        self.node_granularity = node_gran

    def load_data(self, data, G):
        object = orjson.loads(data)
        features = {}
        type = ""

        for prov_type in object:

            if prov_type == "activity":
                for node in object[prov_type]:
                    features = object[prov_type][node]
                    if self.node_granularity == "f":
                        type = object[prov_type][node]["prov:type"]
                    else:
                        type = prov_type
                    self.load_node(node, type, features, G)

            elif prov_type == "entity":
                for node in object[prov_type]:
                    if "cf:camflow" in object[prov_type][node]:
                        continue
                    features = object[prov_type][node]
                    if self.node_granularity == "f":
                        type = object[prov_type][node]["prov:type"]
                    else:
                        type = prov_type
                    self.load_node(node, type, features, G)

            elif prov_type == "agent":
                for node in object[prov_type]:
                    features = object[prov_type][node]
                    if self.node_granularity == "f":
                        type = object[prov_type][node]["prov:type"]
                    else:
                        type = prov_type
                    self.load_node(node, type, features, G)

            elif prov_type == "prefix":
                continue
            else:
                for edge in object[prov_type]:
                    features = object[prov_type][edge]
                    jiffies = int(object[prov_type][edge]["cf:jiffies"])
                    if self.edge_granularity == "f":
                        type = object[prov_type][edge]["prov:type"]
                    else:
                        type = prov_type
                    self.load_edge(edge, type, prov_type, object[prov_type][edge], jiffies, features, G)

    """
    Load the specified graph from file, using the filter to parse the data.
    params: input_path, the full file path to the camflow data.
    params: G, the cf2g graph object we are loading to
    """
    def load_data_from_file(self, data, G):
        print("Loading data now...")
        logcount = 0
        start = time.time()
        for line in data:
            load_data(line[0], G)
            logcount +=1
            if logcount % 5000 == 0:
                end = time.time()
                hours, rem = divmod(end-start, 3600)
                minutes, seconds = divmod(rem, 60)
                print("loaded " + str(round(((logcount/len(json_data))*100), 2)) + "% of data in " +
                    ("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)) + " seconds.")
                start = time.time()
        print("Data loaded! Added " + str(logcount) + " logs.")

    """
    This is a helper function to load the node found in a w3c file.
    params: node, the cf2g given serial name.
    params: node_type, the cf node type (file, process_memory, etc.)
    params: G, the cf2g graph object that the node will be loaded to.
    """
    def load_node(self, node, node_type, features, G):
        G.add_node(node, node_type, features)

    """
    This is a helper function to load the edge found in a w3cprov file.
    params: edge, the JSON object to parse the edge from.
    params: prov_type, indicates the w3cprov relation type.
    params: values, JSON object to parse the src and dst node from.
    params: G, the cf2g graph object that the edge will be loaded to.
    """
    def load_edge(self, edge, type, prov_type, values, jiffies, features, G):
        src_node = ""
        dst_node = ""

        if prov_type == "wasGeneratedBy":
            src_node = values["prov:entity"]
            dst_node = values["prov:activity"]
        elif prov_type == "used":
            src_node = values["prov:activity"]
            dst_node = values["prov:entity"]
        elif prov_type == "wasInformedBy":
            src_node = values["prov:informant"]
            dst_node = values["prov:informed"]
        elif prov_type == "wasInfluencedBy":
            src_node = values["prov:influencee"]
            dst_node = values["prov:influencer"]
        elif prov_type == "wasAssociatedWith":
            src_node = values["prov:agent"]
            dst_node = values["prov:activity"]
        elif prov_type == "wasDerivedFrom":
            src_node = values["prov:generatedEntity"]
            dst_node = values["prov:usedEntity"]
        # not currently supported by CamFlow
        elif prov_type == "wasStartedBy" or prov_type == "wasEndedBy":
            src_node = values["prov:trigger"]
            dst_node = values["prov:activity"]
        elif prov_type == "wasInvalidatedBy":
            src_node = values["prov:activity"]
            dst_node = values["prov:entity"]
        elif prov_type == "wasAttributedTo":
            src_node = values["prov:entity"]
            dst_node = values["prov:agent"]
        elif prov_type == "actedOnBehalfOf":
            src_node = values["prov:delegate"]
            dst_node = values["prov:responsible"]
        elif prov_type == "specializationOf":
            src_node = values["prov:specificEntity"]
            dst_node = values["prov:generalEntity"]
        else:
            cf2gerror.relation_error()
            sys.exit()

        if src_node in G.nodes and dst_node in G.nodes:
            G.add_edge(edge, type, src_node, G.nodes[src_node].getType(), dst_node, G.nodes[dst_node].getType(), features, jiffies)
