"""
F2 Stack Bridge Script

This script acts as the "glue" between a Bambu Lab 3D printer and the InvenTree
inventory management system. It connects to the printer's MQTT broker to receive
real-time status updates.

When a "print finished" event is detected, it will eventually be responsible for
parsing the filament usage and making an API call to InvenTree to automatically
deduct the used material from the inventory.
"""

import os
import paho.mqtt.client as mqtt
import json
import requests

# --- Environment Variables ---
# Load connection details and credentials from environment variables
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USER = os.getenv("MQTT_USER", "bblp")
MQTT_PASS = os.getenv("MQTT_PASS")
MQTT_SERIAL = os.getenv("MQTT_SERIAL")

INVENTREE_URL = os.getenv("INVENTREE_URL")
INVENTREE_API_USER = os.getenv("INVENTREE_API_USER")
INVENTREE_API_PASSWORD = os.getenv("INVENTREE_API_PASSWORD")

# --- Main Logic ---
def on_connect(client, userdata, flags, rc):
    """Callback function executed when the MQTT client successfully connects to the broker."""
    print(f"Connected to MQTT Broker with result code {rc}")
    # Upon successful connection, subscribe to the printer's main "report" topic.
    # All status updates (temperatures, print progress, events) are published here.
    client.subscribe(f"device/{MQTT_SERIAL}/report")

def on_message(client, userdata, msg):
    """
    Callback function executed when a message is received on a subscribed topic.

    Callback for when a message is received.
    This is where you'll implement the logic to parse print completion
    events and trigger the InvenTree stock deduction.
    """
    print(f"Received message on topic {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode())
        print(json.dumps(payload, indent=2)) # Pretty-print the JSON for debugging
        
        # TODO: Implement the logic to detect a "print finished" event.
        # The payload structure needs to be analyzed to find the correct event.
        # Example: if payload.get("print", {}).get("gcode_state") == "FINISH":
        
        # TODO: Extract filament usage data from the payload.
        # This will likely be in grams or meters.
        # filament_used_grams = ...

        # TODO: Identify which AMS slot was used.
        # ams_slot = ...

        # TODO: Call a function to update InvenTree.
        # update_inventree_stock(ams_slot, filament_used_grams)

    except json.JSONDecodeError:
        print("Could not decode JSON payload")
    except Exception as e:
        print(f"An error occurred: {e}")

def update_inventree_stock(ams_slot, grams_used):
    """
    Placeholder function for updating stock in InvenTree.

    This function will connect to the InvenTree API and deduct stock.
    """
    print(f"Deducting {grams_used}g from spool in AMS slot {ams_slot}")
    # 1. Authenticate with InvenTree to get a token (best practice).
    # 2. Find the stock item associated with the AMS slot (e.g., via a custom location in InvenTree).
    # 3. Use the InvenTree API to "consume" or "remove" stock.
    # See InvenTree API documentation for details.
    print("InvenTree update logic not yet implemented.")


# --- MQTT Client Setup ---
# Validate that all necessary environment variables are set before proceeding.
if not all([MQTT_HOST, MQTT_PASS, MQTT_SERIAL, INVENTREE_URL]):
    print("One or more critical environment variables are not set. Exiting.")
    exit(1)

# Create a new MQTT client instance. The client_id should be unique.
client = mqtt.Client(client_id="f2-stack-bridge")

# Assign the callback functions.
client.on_connect = on_connect
client.on_message = on_message

# Set username and password for authentication.
client.username_pw_set(MQTT_USER, MQTT_PASS)
# Bambu printers use MQTT over TLS, so encryption must be enabled.
client.tls_set() # Bambu printers use TLS for MQTT

# Attempt to connect to the broker.
print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
client.connect(MQTT_HOST, MQTT_PORT, 60)

# loop_forever() is a blocking call that processes network traffic, dispatches
# callbacks, and handles reconnecting automatically.
client.loop_forever()