import paho.mqtt.client as mqtt
import sys
import subprocess
import base64
import zlib
import sqlite3
from time import time
from graph import Graph
from colored_print import ColoredPrint
from filters.w3cfilter import W3CFilter

log = ColoredPrint()

provenance_levels = {
    1 : 'Chrome browser',
    2 : 'HTTP server',
    3 : 'MySQL database',
    4 : 'whole system',
}

def print_menu():
    for key in provenance_levels.keys():
        log.info(key, '--', provenance_levels[key] )

class ProvDB():
    def __init__(self, db_file, capture_level):
        self.db_file = db_file
        self.level = capture_level
        db_conn = sqlite3.connect(self.db_file)
        cursor = db_conn.cursor()
        cursor.execute(prov.queries.create_type_table())
        cursor.execute(prov.queries.create_node_table())
        cursor.execute(prov.queries.create_edge_table())
        db_conn.commit()
        cursor.close()
        self.filter = W3CFilter()

    def generate_graph_id():
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

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("camflow/provenance/#", qos=0)

    def on_message(client, userdata, msg):
        decoded_msg = zlib.decompress(base64.b64decode(msg.payload.decode('latin-1'))).decode('latin-1')
        self.filter.load_data(decoded_msg, userdata['graph'])

    def on_disconnect(client, userdata, rc=0):
        print("disconnected with result code "+ str(rc))
        client.loop_stop()

    def start_capture(self):
        graph = Graph()
        id = generate_graph_id()
        print("Connecting MQTT subscriber...")
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.user_data_set({'g_id': id, 'graph': graph})
        time.sleep(3)
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

    def stop_capture(self):
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
