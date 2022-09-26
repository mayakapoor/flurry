if [ $USER = "root" ]
then
    echo "Don't run this script as root. Run it as a normal user, and it'll use sudo for all the elevated privileges stuff"
    echo "(if all the git clone commands were run as root, the folders they download would be owned by root, making them unwritable by normal users)"
    exit
fi
echo "Adding NOPASSWD property to sudoers for ${USER}"
sudo echo "${USER}   ALL = NOPASSWD: ALL" | sudo EDITOR='tee -a' visudo
echo "installing camflow..."
sudo apt install -y libpaho-mqtt1.3
sudo dpkg -i /tmp/camconfd_0.5.2-1_amd64.deb
sudo dpkg -i /tmp/camflow-cli_0.2.2-1_amd64.deb
sudo dpkg -i /tmp/camflowd_0.3.3-1_amd64.deb
sudo dpkg -i /tmp/libprovenance_0.5.4-1_amd64.deb
sudo dpkg -i /tmp/linux-headers-5.15.5-200.camflow.fc35_5.15.5-200.camflow.fc35-1_amd64.deb
sudo dpkg -i /tmp/linux-image-5.15.5-200.camflow.fc35_5.15.5-200.camflow.fc35-1_amd64.deb
sudo dpkg -i /tmp/linux-libc-dev_5.15.5-200.camflow.fc35-1_amd64.deb
sudo dpkg -i /tmp/linux-image-5.15.5-200.camflow.fc35-dbg_5.15.5-200.camflow.fc35-1_amd64.deb

echo "Enabling camflow services..."
sudo systemctl enable camconfd.service
sudo systemctl enable camflowd.service

echo "setting up camflow config files..."

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

sudo apt update
echo "installing wget if it wasn't already installed..."
sudo apt install -y wget

echo "downloading xampp installer..."
wget -O xampp-installer "https://downloadsapachefriends.global.ssl.fastly.net/8.1.6/xampp-linux-x64-8.1.6-0-installer.run?from_af=true"
chmod +x xampp-installer
echo "installing xampp (this part has no output)..."
sudo ./xampp-installer --mode unattended
#read continue
echo "adding xampp to path..."
sudo sed -i "s/Defaults    secure_path = \/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/var\/lib\/snapd\/snap\/bin/Defaults    secure_path = \/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/var\/lib\/snapd\/snap\/bin:\/opt\/lampp/" /etc/sudoers
echo "export PATH=\${PATH}:/opt/lampp" >> ~/.bashrc

echo "setting up cron jobs..."

crontab -l > new_cron
echo "@reboot sudo /opt/lampp/xampp start" >> new_cron
echo "@reboot sleep 10s && cd ~ && source /opt/lampp/setupdb.sh; crontab -l | grep -v 'source /opt/lampp/setupdb.sh' | crontab -" >> new_cron
touch setupdb.sh
echo "line=\$(curl -s -c cookies.txt -b cookies.txt http://127.0.0.1/setup.php | grep \"<input\" | grep \"name='user_token'\")
line=\$(echo \$line | grep -oP \"(?<=value=')[a-z0-9A-Z]*(?=')\")
curl -X POST -c cookies.txt -b cookies.txt -F \"create_db='Create / Reset Databse'\" -F \"user_token=$line\" http://127.0.0.1/setup.php
rm cookies.txt" > setupdb.sh
sudo mv setupdb.sh /opt/lampp
crontab new_cron
rm new_cron


echo "Setting up the DVWA..."
cd /opt/lampp/htdocs
sudo git clone https://github.com/digininja/DVWA.git

sudo cp /opt/lampp/htdocs/DVWA/config/config.inc.php.dist /opt/lampp/htdocs/DVWA/config/config.inc.php
sudo cp -r /opt/lampp/htdocs/DVWA/* /opt/lampp/htdocs

sudo sh -c "sed \"s/\[ 'db_user' \]     = 'dvwa'/\[ 'db_user' \]     = 'root'/;s/\[ 'db_password' \] = 'p@ssw0rd'/\[ 'db_password' \]     = ''/\" /opt/lampp/htdocs/config/config.inc.php.dist > /opt/lampp/htdocs/config/config.inc.php"


echo "Cloning Flurry Repo..."

cd ~

git clone https://sfrett:glpat-Y5ehixY4aaWByVMtzsFx@gitlab.com/crest-lab/provenance/prov-grl/flurry.git

echo "installing chrome and chrome driver..."

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

GC_VERSION=$(google-chrome --version)
GC_VERSION_NUM=$(echo "$GC_VERSION" | cut -b 15- | cut -d "." -f 1)
GCD_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${GC_VERSION_NUM})
wget -O chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/${GCD_VERSION}/chromedriver_linux64.zip"

unzip chromedriver_linux64.zip
sudo mv chromedriver /bin

sudo sed -i "s/dashboard/login.php/" /opt/lampp/htdocs/index.php
echo "installing curl..."
sudo apt install -y curl
# Install conda and copy environment
echo "Installing Conda..."

cd /tmp
curl -O "https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh"
chmod +x Anaconda3-2022.05-Linux-x86_64.sh
./Anaconda3-2022.05-Linux-x86_64.sh -b
cd ~
export PATH=$PATH:/home/$USER/anaconda3/condabin
conda init bash
touch condasetup.sh
cd ~/flurry
conda env create -f environment.yml
sed -i "s/from collections import Mapping/from collections.abc import Mapping/" ~/anaconda3/envs/flurryenv/lib/python3.10/site-packages/dgl/dataloading/base.py

echo "installing mosquitto..."
sudo apt install -y mosquitto
sudo systemctl enable mosquitto.service

echo "installing hydra..."
sudo apt install -y hydra
echo "installing hping3..."
sudo apt install -y hping3

echo "installing sysdig..."
sudo apt install -y sysdig

echo "Setting camflow kernel as default... (This might fail as it assumes the camflow kernel is the first option under \"Advanced options for Ubuntu\")"

sudo sed -i "s/GRUB_DEFAULT=0/GRUB_DEFAULT=1>0/" /etc/default/grub

sudo update-grub

echo "IMPORTANT: The system will now reboot. Please choose the camflow kernel on the GRUB boot menu, if it's not already the default In VirtualBox, you may need to hold shift during the virtualbox splash screen to access it"
echo "Ready? [y/N] "

read answer

if [ "${answer^^}" = "Y" ]
then
    sudo reboot now
else
    echo "Reboot as soon as possible"
fi
