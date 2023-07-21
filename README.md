# Spotify controller on Raspberry PI

## Install on host

Place the script in your home directory
```bash
curl https://raw.githubusercontent.com/Qwiko/rpi-spotifycontrol/master/initialize.sh -O

sh ./initialize.sh
```

## config.json
```json
{
    "allowed_time": {
        "start": 6,
        "end": 20
    },
    "debug": false,
    "buttons": [
        {
            "spotify_uri": "",
            "pin": 17
        }
    ],
    "selected_device_name": "", // Exact name of the device to be controlled
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "" // http://localhost:9000
}
```

## Update
```bash
cd ~/rpi-spotifycontrol
git pull
sudo systemctl restart rpi-spotifycontrol.service
```