import paho.mqtt.client as mqtt
import sys
import subprocess
import base64
import zlib
import sqlite3
import time
from prov.graph import Graph
from termcolor import colored
from prov.filters.w3cfilter import W3CFilter
import prov.queries
from prov.output import GraphTransformer, GraphSerializer

provenance_levels = {
    1 : 'whole system',
    2 : 'HTTP server',
    3 : 'MySQL database',
    4 : 'Chrome browser',
}

# MQTT settings
MQTT_USERNAME = "camflow"
MQTT_PASSWORD = "camflow"
MQTT_HOST = "localhost"
MQTT_PORT = 1883

def print_menu():
    for key in provenance_levels.keys():
        print(colored(str(str(key) + '--' + provenance_levels[key]), 'magenta'))

class ProvDB():
    def __init__(self, db_file, capture_level, edge_gran, node_gran):
        self.db_file = db_file
        self.level = capture_level
        self.client = mqtt.Client()
        db_conn = sqlite3.connect(self.db_file)
        cursor = db_conn.cursor()
        cursor.execute(prov.queries.create_type_table())
        cursor.execute(prov.queries.create_node_table())
        cursor.execute(prov.queries.create_edge_table())
        db_conn.commit()
        cursor.close()
        self.filter = W3CFilter(edge_gran, node_gran)

    def generate_graph_id(self):
        sql = """
            SELECT MAX(graph_id) AS g_id FROM Nodes
            """
        db_conn = sqlite3.connect(self.db_file)
        cursor = db_conn.cursor()
        max_id = cursor.execute(sql).fetchall()
        db_conn.commit()
        cursor.close()
        if max_id[0][0] is None:
            g_id = 1
        else:
            g_id = max_id[0][0]
            g_id += 1
        return g_id

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("camflow/provenance/#", qos=0)

    def on_message(self, client, userdata, msg):
        decoded_msg = zlib.decompress(base64.b64decode(msg.payload.decode('latin-1'))).decode('latin-1')
        self.filter.load_data(decoded_msg, userdata['graph'])

    def on_disconnect(self, client, userdata, rc=0):
        print("disconnected with result code "+ str(rc))
        self.client.loop_stop()

    def start_capture(self, graph):
        print("Connecting MQTT subscriber...")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        self.client.user_data_set({'graph': graph})
        self.client.loop_start()
        time.sleep(1)
        if self.level == 1:
            subprocess.run(["sudo", "camflow", "-a", "true"])
        elif self.level == 2:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/bin/httpd", "true"])
        elif self.level == 3:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/google/chrome/chrome", "true"])
            subprocess.run(["sudo", "camflow", "--track-file", "/usr/bin/chromedriver", "true"])
        elif self.level == 4:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/sbin/mysqld", "true"])
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/bin/mysqld_safe", "true"])

    def stop_capture(self, graph, saveToDisk):
        self.client.loop_stop()
        if self.level == 1:
            subprocess.run(["sudo", "camflow", "-a", "false"])
        elif self.level == 2:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/bin/httpd", "false"])
        elif self.level == 3:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/google/chrome/chrome", "false"])
            subprocess.run(["sudo", "camflow", "--track-file", "/usr/bin/chromedriver", "false"])
        elif self.level == 4:
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/sbin/mysqld", "false"])
            subprocess.run(["sudo", "camflow", "--track-file", "/opt/lampp/bin/mysqld_safe", "false"])
        db_conn = sqlite3.connect(self.db_file)
        if saveToDisk:
            graph.save_to_disk(db_conn)
        outputter = GraphTransformer("output", graph.getIndex())
        outputter.graph_to_png(graph)
        outputter.graph_to_pickle(graph)
        serializer = GraphSerializer("output", graph.getIndex())
        serializer.graph_info_to_file(graph)
        serializer.node_types_to_json(graph)
        serializer.edge_types_to_json(graph)
        serializer.graph_to_json(graph)
