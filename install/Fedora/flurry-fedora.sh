
if [ $USER == "root" ]
then
    echo "Don't run this script as root. Run it as a normal user, and it'll use sudo internally as needed"
    echo "This is done to stop the permissions from getting messed up on downloaded files"
    exit
fi
echo "Adding NOPASSWD property to sudoers for ${USER}"
sudo echo "${USER}   ALL = NOPASSWD: ALL" | sudo EDITOR='tee -a' visudo

echo "Installing Camflow..."
curl -1sLf 'https://dl.cloudsmith.io/public/camflow/camflow/cfg/setup/bash.rpm.sh' | sudo -E bash
sudo dnf -y install camflow

echo "Enabling camflow services..."
sudo systemctl enable camconfd.service
sudo systemctl enable camflowd.service

sudo sh -c "echo '[provenance]
;unique identifier for the machine, use hostid if set to 0
machine_id=0
;enable provenance capture
enabled=true
;record provenance of all kernel object
;all=true
node_filter=directory
node_filter=inode_unknown
node_filter=char
node_filter=envp
; propagate_node_filter=directory
; relation_filter=sh_read
; relation_filter=sh_write
; propagate_relation_filter=write

[compression]
; enable node compression
node=true
edge=true
duplicate=true

[file]
;set opaque file
opaque=/usr/bin/bash
;set tracked file
;track=/home/thomas/test.o
;propagate=/home/thomas/test.o

[ipv4−egress]
;propagate=0.0.0.0/0:80
;propagate=0.0.0.0/0:404
;record exchanged with local server
;record=127.0.0.1/32:80

[ipv4−ingress]
;propagate=0.0.0.0/0:80
;propagate=0.0.0.0/0:404
;record exchanged with local server
;record=127.0.0.1/32:80


[user]
;track=vagrant
;propagate=vagrant
;opaque=vagrant

[group]
;track=vagrant
;propagate=vagrant
;opaque=vagrant

[secctx]
;track=system_u:object_r:bin_t:s0
;propagate=system_u:object_r:bin_t:s0
;opaque=system_u:object_r:bin_t:s0' > /etc/camflow.ini"

sudo sh -c "echo '[general]
;output=null
output=mqtt
;output=unix_socket
;output=fifo
;output=log

format=w3c
;format=spade_json

[log]
;path=/tmp/audit.log

[mqtt]
address=localhost:1883
username=camflow
password=camflow
; message delivered: 0 at most once, 1 at least once, 2 exactly once
qos=0
; topic, provided prefix + machine_id (e.g. camflow/provenance/1234)
topic=camflow/provenance/

[unix]
address=/tmp/camflowd.sock

[fifo]
path=/tmp/camflowd-pipe' > /etc/camflowd.ini"


sudo dnf -y update
echo "Installing libnsl..."
sudo dnf -y install libnsl
echo "Installing wget..."
sudo dnf -y install wget

# XAMPP needs to be downloaded here, but it's not in a repository
wget -O xampp-installer "https://downloadsapachefriends.global.ssl.fastly.net/8.1.6/xampp-linux-x64-8.1.6-0-installer.run?from_af=true"
chmod +x xampp-installer
sudo ./xampp-installer
#read continue
echo "adding xampp to path..."
sudo sed -i "s/Defaults    secure_path = \/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/var\/lib\/snapd\/snap\/bin/Defaults    secure_path = \/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/var\/lib\/snapd\/snap\/bin:\/opt\/lampp/" /etc/sudoers
echo "export PATH=\${PATH}:/opt/lampp" >> ~/.bashrc
echo "setting up cron job..."
sudo dnf -y install cronie
echo "@reboot sudo /opt/lampp/xampp start" | EDITOR='tee -a' crontab -e



echo "Setting up the DVWA..."
cd /opt/lampp/htdocs
sudo git clone https://github.com/digininja/DVWA.git

sudo cp /opt/lampp/htdocs/DVWA/config/config.inc.php.dist /opt/lampp/htdocs/DVWA/config/config.inc.php
sudo cp -r /opt/lampp/htdocs/DVWA/* /opt/lampp/htdocs

sudo sh -c "sed \"s/\[ 'db_user' \]     = 'dvwa'/\[ 'db_user' \]     = 'root'/;s/\[ 'db_password' \] = 'p@ssw0rd'/\[ 'db_password' \]     = ''/\" /opt/lampp/htdocs/config/config.inc.php.dist > /opt/lampp/htdocs/config/config.inc.php"
#sudo sh -c "sed \"s/\[ 'db_password' \]     = 'p@ssw0rd'/\[ 'db_password' \]     = ''/\" /opt/lampp/htdocs/DVWA/config/config.inc.php > /opt/lampp/htdocs/DVWA/config/config.inc.php"

echo "Cloning Flurry Repo..."

cd ~

git clone https://gitlab.com/crest-lab/provenance/prov-grl/flurry.git

# add /opt/lampp to secure path in sudoers
# Install chrome and chrome driver
#sudo dnf -y install google-chrome-stable

sudo dnf config-manager --set-enabled google-chrome
sudo dnf install google-chrome

GC_VERSION=$(google-chrome --version)
GC_VERSION_NUM=$(echo "$GC_VERSION" | cut -b 15- | cut -d "." -f 1)
GCD_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${GC_VERSION_NUM})
wget -O chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/${GCD_VERSION}/chromedriver_linux64.zip"

unzip chromedriver_linux64.zip
sudo mv chromedriver /bin

# Make xampp point to the DVWA
sudo sed -i "s/dashboard/login.php/" /opt/lampp/htdocs/index.php
# Install conda and copy environment
echo "Installing Conda..."
sudo dnf -y install conda
conda init bash
touch condasetup.sh
echo "cd ~/flurry
conda env create -f environment.yml
sed -i \"s/from collections import Mapping/from collections.abc import Mapping/\" ~/.conda/envs/flurryenv/lib/python3.10/site-packages/dgl/dataloading/base.py
echo \"finished, press enter to exit...\"
read continue" > condasetup.sh
chmod +x condasetup.sh
gnome-terminal -- ./condasetup.sh
echo "installing mosquitto..."
sudo dnf -y install mosquitto
sudo systemctl enable mosquitto.service

echo "installing hydra..."
sudo dnf -y install hydra
echo "installing hping3..."
sudo dnf -y install hping3


echo "setting camflow kernel as default..."
GRUBBY_OUT=$(sudo grubby --info=ALL | grep camflow | grep kernel)
RQUOTE=${GRUBBY_OUT#*\"}
CLEAN_OUT=${RQUOTE%\"*}

sudo grubby --set-default $CLEAN_OUT


echo "IMPORTANT: The system will now reboot. Wait until all other terminal windows have finished before continuing, then choose the Camflow kernel in GRUB"
echo "Ready? [y/N] "

read answer

if [ "${answer^^}" = "Y" ]
then
    sudo reboot now
else
    echo "Reboot as soon as possible"
fi

