#!/bin/bash

rpm --import https://download.sysdig.com/DRAIOS-GPG-KEY.public
curl -s -o /etc/yum.repos.d/draios.repo http://download.sysdig.com/stable/rpm/draios.repo

rpm -i http://mirror.us.leaseweb.net/epel/6/i386/epel-release-6-8.noarch.rpm

yum -y install kernel-devel-$(uname -r)

yum -y install draios-agent
echo customerid: ACCESS_KEY >> /opt/draios/etc/dragent.yaml
echo tags: [TAGS] >> /opt/draios/etc/dragent.yaml
sudo systemctl enable dragent
sudo systemctl start dragent
