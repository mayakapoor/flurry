## Flurry
A fully automated framework to simulate host behavior and capture data provenance and system behavior for graph generation and representation learning.

## Description
Flurry is a simulation framework for different types of systems that researchers may want to gather provenance data from. Flurry comes equipped with tools for provenance capture and provenance graph generation. Using Flurry, researchers may run either prewritten attack or benign behavior scripts, capture these system processes and accesses, and generate graphs from them, or run custom scripts. The framework is highly customizable so that nearly any contrivable scenario can be experimented with and tested.


## Installation
To make the Flurry installation process faster and less prone to mistakes, automatic install scripts are now provided. Two options are available: The first requires a premade Fedora or Ubuntu VM, while the second uses Hashicorp Packer to create one automatically.

Option 1: Flurry installer

This option assumes you have a working Fedora 35 or Ubuntu 22.04 Desktop VM in VirtualBox.

Installer scripts are available for Fedora 35 and Ubuntu 22.04. Other version numbers are unlikely to work without modifications, so make sure to create a virtual machine with one of these two operating systems. Currently, the scripts reside in the folder install-scripts/<distro> in this repo. Each distro folder contains the install script and a folder called "Packer". The Packer folder is NOT necessary for this option and can be safely ignored.

```
cd existing_repo
git remote add origin https://github.com/mayakapoor/flurry.git
git branch -M main
git push -uf origin main
```

chmod +x flurry-fedora.sh

- [ ] [Set up project integrations](https://gitlab.com/crest-lab/provenance/prov-grl/flurry/-/settings/integrations)

Then, run it with:

./flurry-fedora.sh


You will need to enter your password once, and the installation should be completely automatic from that point on. This script should NOT be run with sudo.
    After the script finishes, reboot the system. Hold shift during the VirtualBox splash screen to access the GRUB boot menu and make sure that the selected option has the word "camflow" in it. If it's the default option (which it should be), you should be able to let Virtualbox skip the boot menu from now on.

For Ubuntu:
    Download the flurry-ubuntu.sh script and place it in your Ubuntu VM's /home/<user> directory
    Download all 8 of the deb files in install-scripts/Ubuntu and place them in the VM's /tmp directory. The install script will install all of them automatically.
    Open a terminal in the /home/<user> directory and give the script permission to execute with the command:

chmod +x flurry-ubuntu.sh


Then, run it with:

./flurry-ubuntu.sh


    As with the Fedora script, you should only need to enter your password once. This script should NOT be run with sudo.
    	After the script finishes, reboot the system. Hold shift during the Virtualbox splash screen to access the GRUB boot menu and select "Advanced Options for Ubuntu", then the option that has the word "camflow" in it. If these options are the default (they should be), you can let Virtualbox skip the boot menu from now on.

Option 2: Packer

This option is a bit more complex, but is also more customizable and does not require you to make a virtual machine in advance (Packer will make one automatically)

First, install packer: https://www.packer.io/downloads

Currently, the packer templates reside in the folder PROJ-SIS-CCI-CREST/Research/Prov-GRL/install scripts/<distro>/Packer in the shared Google Drive folder. Download the Packer folder for your desired Linux distro.

Open a terminal in the folder you just downloaded. You should be in the same folder as the <distro>-server.pkr.hcl file

Build the template. If you're using a Linux host, the command for the Fedora VM template is:

packer build -var-file=fedora35.pkrvars.hcl -var 'vm_name=flurry-fedora' -var 'provider_name=virtualbox' fedora-server.pkr.hcl

(this is all one line)

and the command for Ubuntu is:

packer build -var-file=ubuntu22.pkrvars.hcl -var 'vm_name=flurry-ubuntu' -var 'provider_name=virtualbox' ubuntu-server.pkr.hcl


The build process should be automatic from there. When the build is finished, all VM windows will be closed and the results will be outputted to the "build" directory

To create the VM, open up virtualbox, choose "Tools" on the left sidebar, then "Import" on the top. Navigate to the build folder and choose the ovf file that Packer created. Choose your import specs. The selected options should be enough to prevent crashes, but you may choose to use more or less cores and RAM depending on the capabilities of your host machine.

Wait for Virtualbox to finish importing, then start the new VM. The password for the user "cyber" is ITIS6010

## Provenance Capture Tools

CamFlow

CamFlow is a Linux security module designed for fine-grained, whole-system provenance capture. The module works by using hooks to monitor security access in the kernel space as well as NetFilter hooks to capture network provenance. These are passed via the CamFlow daemon to user-space, where it may be conveyed to a log file, piped to a storage back-end, or conveyed via message bus to some other interface. There are a number of configuration options both for the application and daemon in order to fine-tune the provenance capture to your liking. The system may also be configured for whole-system capture or target capture for specific files and/or processes.

sysdig (upcoming feature)


## Usage
The FLURRY virtual machine is set up with a user profile and password. The password can be used for sudo/root permissions. If the virtual machine was generated by packer scripts, this is the default login information:

Username: cyber
Password: ITIS6010

The GUI is currently missing from Flurry v5.0. Instead, to start Flurry, open a terminal in /home/cyber/flurry Then, run the following command:

conda activate flurryenv


This will start the conda environment and give Flurry access to the python packages it needs to run. After initializing the conda environment once, you will not need to do so again until the terminal window is closed and reopened.

For browser-based attacks and behaviors, run this command:

python3 webhost.py


For network-based attacks and behaviors, run this command instead:

python3 networkhost.py


From there, select any number of attacks, behaviors, and scripts, then set the iteration count, provenance capture scope, and the convention to use for what constitutes a node and an edge. Once all the inputs have been made, Flurry should proceed automatically.

Note: In the browser-based attacks, the DVWA web page may fail to show up, even if the webserver is running. To fix it, access the page http://127.0.0.1/setup.php in a web browser and click the button at the bottom of the page to set up the DVWA’s SQL database. Then, run Flurry again.

## Advanced Usage
Advanced Execution
Custom Scripts
In addition to the 18 total attack and benign routines, Flurry supports custom scripts. The files in the scripts folder, which handle all the default routines, follow the same format as custom scripts and may be used as templates

Input Configuration
Flurry can be run using input configuration files. To save the input given for a run as a file, answer the prompt after Flurry has finished executing. To rerun the same inputs, simply start Flurry again and enter the local path to the config file. If a valid config file is provided, no further input will be required.

A typical input configuration file looks like this:
xssdom,xssreflected,commandinjection,message,ping
2
1
c
f


Functionally, this is just the set of inputs to use when responding to the prompts. The first line is a comma-separated list of attacks to run, the second is the number of iterations, the third is the provenance capture scope (1 is “whole system”), and lines four and five are the edge and node types, respectively. If the input involves custom scripts, they are added after the list of attacks, one line at a time:

sqlinjection,customattack,customattack,custombehavior
scripts/custom1.py
scripts/custom2.py
scripts/anothercustom.py
1
1
c
f


## Support
For support, please contact: mayakapoor99@gmail.com.

## Roadmap
Upcoming features include:
-- sysdig graph generation support
-- GUI for running Flurry
-- improved documentation

## Contributing
Contributions such as additional host configurations or filters for graph generation are welcome!

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
Licensed with MIT Open License.

## Project status
Continuing to be developed.
