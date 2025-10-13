"""A simple Flask API to simulate Zukun device interactions."""
import io
import logging
import shutil
import threading
import time

from flask import Flask, jsonify, send_file
from PIL import Image
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZukunTestAPI")
app = Flask(__name__)

# Simulated recording state
recording = False
recording_thread = None

def simulate_recording():
    """Simulate a recording process."""
    global recording # noqa: PLW0602
    while recording:
        logger.info("Recording...")
        time.sleep(1)

@app.route("/battery", methods=["GET"])
def get_battery():
    """Return simulated battery status."""
    battery = psutil.sensors_battery()
    if battery is None:
        return jsonify({"battery_percent": 100.0})
    return jsonify({"battery_percent": battery.percent, "charging": battery.power_plugged})

@app.route("/storage", methods=["GET"])
def get_storage():
    """Return simulated storage status."""
    total, used, free = shutil.disk_usage("/")
    return jsonify({
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    })

@app.route("/image", methods=["GET"])
def get_image():
    """Return a simple generated image."""
    # Generate a simple image dynamically
    img = Image.new("RGB", (200, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/record", methods=["POST"])
def start_recording():
    """Start simulated recording."""
    global recording, recording_thread # noqa: PLW0603
    if recording:
        return jsonify({"status": "already recording"}), 400
    recording = True
    recording_thread = threading.Thread(target=simulate_recording)
    recording_thread.start()
    return jsonify({"status": "recording started"})

@app.route("/stop", methods=["POST"])
def stop_recording():
    """Stop simulated recording."""
    global recording # noqa: PLW0603
    if not recording:
        return jsonify({"status": "not recording"}), 400
    recording = False
    return jsonify({"status": "recording stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
