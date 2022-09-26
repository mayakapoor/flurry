from src.flurry.host import Host
import flurryflake.filters.camflow as camflow

test1 = Host()
test1.start_recording("command injection")
test1.commandinjection()
test1.stop_recording()
