#from pyfiglet import Figlet
import os
import warnings
from pathlib import Path
import util.driversetup as ds

import flurryflake
from . import host

warnings.filterwarnings("ignore", category=DeprecationWarning)

#config options
SAVE_TO_DISK = True

#prov levels
#provenance_levels = {
#    1 : 'whole system',
#    2 : 'HTTP server',
#    3 : 'MySQL database',
#    4 : 'Chrome browser',
#}

## Start menu coding
attack_menu_options = {
    'xssstored': 'Execute XSS Stored Attack',
    'xssreflected': 'Execute XSS Reflected Attack',
    'xssdom': 'Execute XSS DOM Attack',
    'commandinjection': 'Execute Command Injection Attack',
    'sqlinjection': 'Execute SQL Injection Attack',
    'bruteforce': 'Execute Brute Force Attack',
    'customattack': 'Use My Own Attack'
}

benign_menu_options = {
    'message': 'Message Board Post (Benign version of XSS stored)',
    'submit': 'Complete a Questionnaire (Benign version of XSS reflected)',
    'query': 'Query a Webpage (Benign version of XSS DOM)',
    'ping': 'Ping Local Host (Benign version of command injection)',
    'databaseentry': 'Create a User ID (Benign version of SQL injection)',
    'login': 'Enter Username and Password (Benign version of brute force)',
    'custombehavior': 'Use My Own Custom Behavior'
}

class FlurryWeb(host.Host):
    def __init__(self, filter, cfg_path=None):
        host.Host.__init__(self, attack_menu_options, benign_menu_options, filter)
        cfg_txt = host.read_input_file(cfg_path)
        cfg_lines = cfg_txt.split("\n")
        cfg_custom_count = 0

        try:
            if cfg_txt == "":
                self.print_attacks()
                self.print_benigns()
                action_str = input('Select one or more attacks to run in a comma-separated list: ')
            else:
                action_str = cfg_lines[0]
                print(action_str)
            self.actions = action_str.split(",")
            scripts = []
            term_customs = [] # For writing config files
            for action in self.actions:
                script = Path("")
                if action == "xssstored":
                    script = Path(os.getcwd() + "/scripts/xssstored.py")
                elif action == "xssreflected":
                    script = Path(os.getcwd() + "/scripts/xssreflected.py")
                elif action == "xssdom":
                    script = Path(os.getcwd() + "/scripts/xssdom.py")
                elif action == "commandinjection":
                    script = Path(os.getcwd() + "/scripts/commandinjection.py")
                elif action == "sqlinjection":
                    script = Path(os.getcwd() + "/scripts/sqlinjection.py")
                elif action == "bruteforce":
                    script = Path(os.getcwd() + "/scripts/bruteforce.py")
                elif action == "message":
                    script = Path(os.getcwd() + "/scripts/messageboard.py")
                elif action == "submit":
                    script = Path(os.getcwd() + "/scripts/questionnaire.py")
                elif action == "query":
                    script = Path(os.getcwd() + "/scripts/pagequery.py")
                elif action == "ping":
                    script = Path(os.getcwd() + "/scripts/commandlineping.py")
                elif action == "databaseentry":
                    script = Path(os.getcwd() + "/scripts/databaseentry.py")
                elif action == "login":
                    script = Path(os.getcwd() + "/scripts/singlelogin.py")
                elif action == "customattack" or action == "custombehavior":
                    if cfg_txt == "":
                        local_path = ""
                        while (not script.is_file()):
                            local_path = input('Provide the local path to your custom script: ')
                            script = Path(os.getcwd() + "/" + local_path)
                            if (not script.is_file()):
                                print('Invalid file path provided. Try again.')
                        term_customs.append(local_path)
                    else:
                        cfg_custom_count += 1
                        script = Path(os.getcwd() + "/" + cfg_lines[cfg_custom_count])
                else:
                    print('Invalid option ' + action + ' provided.')
                if script.is_file():
                    scripts.append(script)
        except Exception as e:
            print(e)

        # Other options
        #host.print_provenance_menu(provenance_levels)
        #prov_level = host.get_level(cfg_txt, cfg_lines, cfg_custom_count)
        num_loops = host.get_loops(cfg_txt, cfg_lines, cfg_custom_count)
        DRIVER = ds.setupDriver()
        self.run(scripts, num_loops)
        DRIVER.close()
        if cfg_txt == "":
            self.save(action_str, term_customs, num_loops)
