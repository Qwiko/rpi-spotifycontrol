#!/usr/bin/python3
import time
import datetime
import json
import logging
import spotipy
import requests
from gpiozero import Button


def import_config():
    with open('config.json', 'r') as f:
        return(json.load(f))

class Spotify():
    def __init__(self, client_id, client_secret, redirect_uri, logger, *args, **kwargs) -> None:
        self.logger = logger
        self.logger.debug("Creating spotify class")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = "user-read-playback-state streaming"
        self.auth_manager, self.spotify = self.authenticate()
        self.logger.info("Spotify initialized")

    def authenticate(self):
        self.logger.debug("Authenticating to Spotify")
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope=self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        self.logger.info("Authenticated to Spotify")
        return auth_manager, spotify

    def refresh_token(self):
        token_info = self.auth_manager.cache_handler.get_cached_token()
        if self.auth_manager.is_token_expired(token_info):
            self.logger.info("Token expired, recreating session")
            self.auth_manager, self.spotify = self.authenticate()

    def get_devices(self):
        return self.spotify.devices()

    def select_device(self, device_name):
        self.logger.info(f"Selecting device with name: {device_name}")
        devices = self.get_devices()
        selected_devices = [device for device in devices.get("devices") if device.get("name") == device_name]
        if not selected_devices:
            self.logger.error(f"No device found with name: {device_name}, sleeping for 5 seconds and exiting.")
            time.sleep(5)
            exit(1)
        self.selected_device = selected_devices[0]
        self.selected_device_id = self.selected_device.get("id")
        self.logger.info(f"Device found with id: {self.selected_device_id}")

    def get_status(self):
        return self.spotify.current_playback()

    def start(self, uri):
        if not self.selected_device_id:
            return
        
        # Play URI
        self.spotify.start_playback(self.selected_device_id, uri)

    def pause(self):
        if not self.selected_device_id:
            return

        self.spotify.pause_playback()

    def shuffle(self, status):
        if not self.selected_device_id:
            return

        if not status:
            status = {}

        if status.get("shuffle_state"):
            return

        self.logger.info("Enabling Shuffle")
        self.spotify.shuffle(True, self.selected_device_id)

def handle_click(button, spotify, uri, allowed_time, logger):
    now = datetime.datetime.now()

    if (now.hour > allowed_time.get("end") or now.hour <= allowed_time.get("start")):
        logger.error(f"Button clicked but not within allowed time {allowed_time}")
        time.sleep(1)
        return

    #Refresh token
    spotify.refresh_token()

    try:
        status = spotify.get_status()
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        logger.info("Error grabbing current status, trying again.")
        status = spotify.get_status()

    #Defaults
    is_playing = False
    current_context_uri = ""
    playing_device_id = ""

    if status:
        playing_device = status.get("device")
        
        if playing_device:
            playing_device_id = playing_device.get("id")
        is_playing = status.get("is_playing")
        current_context_uri = status.get("context").get("uri")

    # If we are playing the same uri context on the selected device. We pause
    if is_playing and playing_device_id == spotify.selected_device.get("id") and current_context_uri == uri:
        # Pause
        logger.info(f"Pausing playback with pin: {button.get('pin')}")
        try:
            spotify.pause()
        except spotipy.exceptions.SpotifyException as e:
            logger.error(e)
            logger.info("Waiting 2 seconds and trying again.")
            time.sleep(2)
            spotify.pause
    else:
        # Play
        logger.info(f"Starting playback with pin: {button.get('pin')}")
        try:
            spotify.shuffle(status)
            spotify.start(uri)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(e)
            logger.info("Waiting 2 seconds and trying again.")
            time.sleep(2)
            spotify.shuffle(status)
            spotify.start(uri)

def main():
    config = import_config()

    debug = config.get("debug")
    
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    spotify = Spotify(logger=logger, **config)

    buttons = config.get("buttons")
    
    selected_device_name = config.get("selected_device_name")
    allowed_time = config.get("allowed_time") if config.get("allowed_time") else {}

    spotify.select_device(selected_device_name)

    # Setting up buttons
    gpio_buttons = []
    for button in buttons:
        button_pin = button.get("pin")
        spotify_uri = button.get("spotify_uri")
        gpio_button = Button(button_pin)
        gpio_button.when_pressed = lambda button=button, button_pin=button_pin, spotify_uri=spotify_uri: handle_click(button, spotify, spotify_uri, allowed_time, logger)
        gpio_buttons.append(gpio_button)

    # Main loop
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
