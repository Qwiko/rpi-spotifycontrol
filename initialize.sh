#!/bin/bash

echo "APT Update"
sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq > /dev/null
echo "Installing python3, python3-pip and git"
sudo DEBIAN_FRONTEND=noninteractive apt-get -qq install python3-pip git > /dev/null

# Clone repo
echo "Cloning rpi-spotifycontrol repo"
git clone https://github.com/Qwiko/rpi-spotifycontrol.git

cd rpi-spotifycontrol

# Update git
git pull

echo "Install rpi-spotifycontrol dependencies"
sudo python3 setup.py install

echo "Copying template to systemd"
cat rpi-spotifycontrol.service.template | envsubst >  rpi-spotifycontrol.service

sudo cp ./rpi-spotifycontrol.service /etc/systemd/system/rpi-spotifycontrol.service

# Reload daemon
sudo systemctl daemon-reload

echo "Enabling and starting rpi-spotifycontrol.service"
sudo systemctl enable rpi-spotifycontrol.service

msg="""
###########################################################
Create config.json in your $HOME/rpi-spotifycontrol folder.

Initialize the service and login to spotify with:
cd rpi-spotifycontrol && python3 main.py

After the cache have been created successfully, start the service with:
sudo systemctl start rpi-spotifycontrol.service

See logs with:
sudo journalctl -u rpi-spotifycontrol.service
############################################################
"""

echo $msg && echo $msg > guide.txt