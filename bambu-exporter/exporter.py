import os
import json
import ssl
import paho.mqtt.client as mqtt
from prometheus_client import start_http_server, Gauge

# Define Metrics
temp_nozzle = Gauge('bambu_nozzle_temp', 'Nozzle Temperature')
temp_chamber = Gauge('bambu_chamber_temp', 'Chamber Temperature')

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        # Bambu printer sends a 'print' status update
        if 'print' in data:
            print_data = data['print']
            temp_nozzle.set(print_data.get('nozzle_temper', 0))
            temp_chamber.set(print_data.get('chamber_temper', 0))
    except Exception as e:
        print(f"Error parsing message: {e}")

# Connection Setup
client = mqtt.Client()
client.tls_set(cert_reqs=ssl.CERT_NONE) # Ignore self-signed certs
client.username_pw_set("bblp", os.environ['BBL_ACCESS_CODE'])
client.on_message = on_message

client.connect(os.environ['BBL_HOST'], 8883)
client.subscribe(f"device/{os.environ['BBL_SERIAL']}/report")
client.loop_start()

# Start Prometheus Server
start_http_server(9723)
print("Exporter running on port 9723...")
import time
while True: time.sleep(1)