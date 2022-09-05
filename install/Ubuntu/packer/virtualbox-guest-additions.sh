sudo mkdir -p /mnt/vboxadd
sudo mount -o loop VBoxGuestAdditions.iso /mnt/vboxadd/ # The iso file was automatically put in the home directory by packer
cd /mnt/vboxadd/
sudo ./VBoxLinuxAdditions.run
exit 0
