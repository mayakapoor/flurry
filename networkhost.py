#from pyfiglet import Figlet
import os
import warnings
from termcolor import colored
from pathlib import Path
from prov.database import ProvDB
import prov.database as prov
import util.scriptrunner as sr

warnings.filterwarnings("ignore", category=DeprecationWarning)

#config options
REQUIRES_DRIVER = False
SAVE_TO_DISK = True
GENERATE_TYPE_GRAPH = True

## Start menu coding
attack_menu_options = {
    'synflood': 'Execute SYN Flood Attack',
    'dataexfil': 'Execute Data Exfiltration Attack',
    'backdoor': 'Execute Remote Code Execution Attack',
    'customattack': 'Use My Own Attack'
}

benign_menu_options = {
    'ping': 'Ping Local Host',
    'fileread': 'read file',
    'localexecution': 'Execute script locally',
    'custombehavior': 'Use My Own Custom Behavior'
}

def print_attack_menu():
    for key in attack_menu_options.keys():
        print(colored(str(key + '--' + attack_menu_options[key]), 'red'))

def print_benign_menu():
    for key in benign_menu_options.keys():
        print(colored(str(key + '--' + benign_menu_options[key]), 'green'))

def main():
    #welcome()
    print_attack_menu()
    print_benign_menu()
    try:
        action_str = input('Select one or more attacks to run in a comma-separated list: ')
        actions = action_str.split(",")
        scripts = []
        for action in actions:
            script = Path("")
            if action == "synflood":
                script = Path(os.getcwd() + "/scripts/synflood.py")
            elif action == "dataexfil":
                script = Path(os.getcwd() + "/scripts/dataexfil.py")
            elif action == "backdoor":
                script = Path(os.getcwd() + "/scripts/backdoor.py")
            elif action == "ping":
                script = Path(os.getcwd() + "/scripts/ping.py")
            elif action == "fileread":
                script = Path(os.getcwd() + "/scripts/fileread.py")
            elif action == "localexecution":
                script = Path(os.getcwd() + "/scripts/localexec.py")
            elif action == "customattack" or action == "custombehavior":
                while (not script.is_file()):
                    script = Path(input('Provide the full path to your custom script: '))
                    if (not script.is_file()):
                        print('Invalid file path provided. Try again.')
                action = str(input("Provide a single word identifier for this custom execution (i.e. \'bruteforce\')")).split(" ")[0]
            else:
                print('Invalid option ' + action + ' provided.')
            if script.is_file():
                scripts.append(script)
    except Exception as e:
        print(e)

    num_loops = int(input("Execution loop is constructed. How many iterations would you like to make? "))
    prov.print_menu()
    prov_level = int(input("Select provenance capture granularity: "))
    while prov_level < 1 or prov_level > 4:
        prov_level = int(input("Invalid option selected. Try again."))
    i = 0

    print("FINE = CamFlow-provided node and edge types, COARSE = W3C-PROV model types")
    edge_gran = str(input("Select FINE (f) or COARSE (c) granularity for edge types: " )).lower()
    while edge_gran != 'c' and edge_gran != 'f':
        edge_gran = str(input("Invalid option selected. Try again.")).lower()
    node_gran = str(input("Select FINE (f) or COARSE (c) granularity for node types: " )).lower()
    while node_gran != 'c' and node_gran != 'f':
        node_gran = str(input("Invalid option selected. Try again.")).lower()

    database = ProvDB("data/camflow.db", prov_level, edge_gran, node_gran)
    while i < num_loops:
        sr.runList(database, scripts, REQUIRES_DRIVER, SAVE_TO_DISK)
        i += 1

main()
