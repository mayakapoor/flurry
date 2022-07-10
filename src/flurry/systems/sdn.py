import os
import warnings
from pathlib import Path

import flurryflake
from . import host

warnings.filterwarnings("ignore", category=DeprecationWarning)

#config options
SAVE_TO_DISK = True

## Start menu coding
attack_menu_options = {
    'customattack': 'Use My Own Attack'
}

benign_menu_options = {
    'custombehavior': 'Use My Own Custom Behavior'
}

class FlurrySDN(host.Host):
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
                if action == "customattack" or action == "custombehavior":
                    if cfg_txt == "":
                        local_path = ""
                        while (not script.is_file()):
                            local_path = input('Provide the local path to your custom script: ')
                            script = Path(os.getcwd() + "/" + local_path)
                            if (not script.is_file()):
                                print('Invalid file path provided. Try again.')
                        term_customs.append(local_path)
                        #action = str(input("Provide a single word identifier for this custom execution (i.e. \'bruteforce\')")).split(" ")[0]
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
        num_loops = host.get_loops(cfg_txt, cfg_lines, cfg_custom_count)
        self.run(scripts, num_loops)
        if cfg_txt == "":
            self.save(action_str, term_customs, num_loops)
