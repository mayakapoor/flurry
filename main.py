from src.flurry.host import Host
import flurryflake.filters.camflow as camflow
from src.flurry.testclient import TestClient
import time

test1 = Host()
client1 = TestClient()
client1.connect_client()
test1.start_recording("command injection")
test1.commandinjection()
test1.stop_recording()
test1.publish_to_file("json")
test1.publish_to_mqtt("json")
time.sleep(3)
client1.disconnect_client()
