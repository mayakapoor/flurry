import util.driversetup as ds
from prov.graph import Graph

def runList(database, scriptList, saveToDisk):
    '''
        Runs a list of scripts and gathers provenance on each one
    '''
    graph = Graph(database.generate_graph_id())
    database.start_capture(graph)
    for script in scriptList:
        run(database, script, saveToDisk)
    database.stop_capture(graph, saveToDisk)


def run(database, script, saveToDisk):
    try:
        print("running " + str(script))
        fileRead = open(script).read()
        exec(fileRead)
    except FileNotFoundError as e:
        print(e)
        print("Can't open " + str(script))
