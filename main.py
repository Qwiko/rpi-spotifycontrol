#!/usr/bin/python3
import time
import json
import logging
import spotipy

from gpiozero import Button

logger = logging.getLogger(__name__)

def import_config():
    with open('config.json', 'r') as f:
        return(json.load(f))

class Spotify():
    def __init__(self, client_id, client_secret, redirect_uri, *args, **kwargs) -> None:
        logger.debug("Creating spotify class")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = "user-read-playback-state streaming"

    def authenticate(self):
        logger.debug("Authenticating to Spotify")
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope=self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

    def refresh_token(self):
        token_info = self.auth_manager.cache_handler.get_cached_token()
        if self.auth_manager.is_token_expired(token_info):
            logger.debug("Token expired, recreating session")
            self.authenticate()

    def get_devices(self):
        return self.spotify.devices()

    def select_device(self, device_name):
        devices = self.get_devices()
        selected_devices = [device for device in devices.get("devices") if device.get("name") == device_name]
        if not selected_devices:
            logger.error(f"No device found with name: {device_name}")
            self.selected_device = None
            self.selected_device_id = None
            return

        self.selected_device = selected_devices[0]
        self.selected_device_id = self.selected_device.get("id")

    def get_status(self):
        return self.spotify.current_playback()

    def start(self, uri):
        if not self.selected_device_id:
            return
        # Enable shuffle
        self.spotify.shuffle(True, self.selected_device_id)
        # Play URI
        self.spotify.start_playback(self.selected_device_id, uri)

    def pause(self):
        self.spotify.pause_playback()

def main():
    config = import_config()
    spotify = Spotify(**config)
    spotify.authenticate()

    buttons = config.get("buttons")
    debug = config.get("debug")
    selected_device_name = config.get("selected_device_name")

    spotify.select_device(selected_device_name)

    # If we debug, use MockFactory
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        from gpiozero import Device
        from gpiozero.pins.mock import MockFactory
        Device.pin_factory = MockFactory()

    # Setting up buttons
    for button in buttons:
        button_pin = button.get("pin")
        spotify_uri = button.get("spotify_uri")
        gpio_button = Button(button_pin)
        def callback():
            logger.debug(button_pin)
            handle_click(spotify, spotify_uri)
        gpio_button.when_pressed = callback

    # Main loop
    while True:
        time.sleep(0.01)

def handle_click(spotify, uri):
    #Refresh token
    spotify.refresh_token()

    status = spotify.get_status()
    playing_device = status.get("device")
    is_playing = status.get("is_playing")
    current_context_uri = status.get("context").get("uri")

    # If we are playing the same uri context on the selected device. We pause
    if is_playing and playing_device.get("id") == spotify.selected_device.get("id") and current_context_uri == uri:
        # Pause
        logger.info("Pausing playback")
        spotify.pause()
    else:
        # Play
        logger.info("Starting playback")
        spotify.start(uri)


if __name__ == "__main__":
    main()
