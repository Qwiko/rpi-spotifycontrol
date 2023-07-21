#!/usr/bin/python3
import logging
from main import Spotify, import_config


def main():
    spotify = Spotify(logger=logging.getLogger(__name__), **import_config())

    devices = spotify.spotify.devices()
    print("NAME: ID")
    for device in devices.get("devices"):
        print(f"{device.get('name')}: {device.get('id')}")
if __name__ == "__main__":
    main()
