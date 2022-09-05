To build the vm image on a linux host, install packer and virtualbox and run the following command in the packer directory:

packer build -var-file=fedora35.pkrvars.hcl -var 'vm_name=flurry-fedora' -var 'provider_name=virtualbox' fedora-server.pkr.hcl

The process is completely automated and may take a while. Red text does not necessarily mean an error.

During the build process, the VM will open up as it's being created; DO NOT touch anything!

After the build is completed, the VM will delete itself and the output files will be written to buid/packer-fedora-35-x86_64-virtualbox

To use the newly created VM image, import the OVF file in buid/packer-fedora-35-x86_64-virtualbox into virtualbox. 
The default settings are recommended, but you may adjust them to fit the needs of your host machine.

Unless you changed it in the script files, the password for the user "cyber" is ITIS6010
