#!/bin/bash

echo "APT Update"
sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq -y
echo "Installing python3, python3-pip and git"
sudo DEBIAN_FRONTEND=noninteractive apt-get -qq --assume-yes --allow install python3-pip git

# Clone repo
echo "Cloning rpi-spotifycontrol repo"
git clone https://github.com/Qwiko/rpi-spotifycontrol.git

cd rpi-spotifycontrol

# Update git
git pull

echo "Install rpi-spotifycontrol dependencies"
sudo python3 setup.py install

echo "Copying template to systemd"
cat rpi-spotifycontrol.service.template | envsubst > /etc/systemd/system/rpi-spotifycontrol.service

# Reload daemon
sudo systemctl daemon-reload

echo "Enabling and starting rpi-spotifycontrol.service"
sudo systemctl enable rpi-spotifycontrol.service

echo """
Create config.json in your $HOME/rpi-spotifycontrol folder.

Initialize the service and login to spotify with:
cd rpi-spotifycontrol && python3 main.py

After the cache have been created successfully, start the service with:
sudo systemctl start rpi-spotifycontrol.service

See logs with:
sudo journalctl -u rpi-spotifycontrol.service
"""