
import os
import sys
import argparse
import subprocess
from pathlib import Path
from termcolor import colored
import flurryflake
from flurryflake import FlurryBank

class Host():
    def __init__(self, attacks, benigns, filter):
        self.attack_menu = attacks
        self.benign_menu = benigns
        self.actions = []
        self.filter = filter
        self.bank = FlurryBank(filter)
    #   self.provenance_levels = levels

    #def print_provenance_levels():
    #    for key in self.provenance_levels.keys():
    #        print(colored(str(str(key) + '--' + self.provenance_levels[key]), 'magenta'))

    def print_attacks(self):
        for key in self.attack_menu.keys():
            print(colored(str(key + '--' + self.attack_menu[key]), 'red'))

    def print_benigns(self):
        for key in self.benign_menu.keys():
            print(colored(str(key + '--' + self.benign_menu[key]), 'green'))

    def run(self, scripts, num_loops):
        i = 0
        while i < num_loops:
            '''
                Runs a list of scripts and gathers provenance on each one
            '''
            graph = self.bank.make_flake(self.actions)
            self.bank.connect_client(graph)
            for script in scripts:
                try:
                    print("running " + str(script))
                    fileRead = open(script).read()
                    exec(fileRead)
                except FileNotFoundError as e:
                    print(e)
                    print("Can't open " + str(script))
            self.bank.disconnect_client(graph)
            i += 1

    def save(self, action_str, term_customs, num_loops):
        fn = input("Enter filename to save this configuration (cwd = " + os.getcwd() + "; leave blank to not save config): ")
        if (fn != ""):
            f = open(fn, "w")
            f.write(action_str + "\n")
            for tc in term_customs:
                f.write(tc)
            f.write(str(num_loops) + "\n")
            f.close()

def read_input_file(f):
    cfg_txt = ""
    if f is not None:
        cfg_path = Path(os.getcwd() + "/" + f)
        if not cfg_path.is_file():
            print("Could not find the automation file; try again.")
            sys.exit()
        cfg_txt = open(cfg_path).read()
    return cfg_txt

#def get_level(cfg_txt, cfg_lines, cfg_custom_count):
#    prov_level = 1
#    if cfg_txt == "":
#        prov_level = int(input("Select provenance capture granularity: "))
#        while prov_level < 1 or prov_level > 4:
#            prov_level = int(input("Invalid option selected. Try again."))
#    else:
#        prov_level = int(cfg_lines[2 + cfg_custom_count])
#        print(prov_level)
#    return prov_level

def get_loops(cfg_txt, cfg_lines, cfg_custom_count):
    num_loops = 1
    if cfg_txt == "":
        num_loops = int(input("Execution loop is constructed. How many iterations would you like to make? "))
    else:
        num_loops = int(cfg_lines[1 + cfg_custom_count])
        print(num_loops)
    return num_loops
