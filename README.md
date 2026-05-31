# Filament-to-Flight Stack (F2 Stack)

Welcome to the Filament-to-Flight Stack (F2 Stack), my personal central hub for managing digital fabrication, from 3D printing workflows to automated inventory and future autonomy R&D. This project leverages Docker to create a seamless, integrated environment accessible from anywhere on my personal Tailnet.

## Overview

The core idea behind the F2 Stack is to create a cohesive, server-based ecosystem for my personal engineering projects. It solves the challenge of synchronizing files across computers, monitoring machines in real-time, and automating tedious tasks like inventory management.

## System Architecture

The stack is composed of several services orchestrated by `docker-compose`.

### File Sync & Remote Slicing

This is the foundational layer for keeping designs and slicer profiles consistent across machines.

#### OrcaSlicer

The `linuxserver/orcaslicer` image provides a full-featured OrcaSlicer instance running in a Docker container. It's configured with GPU passthrough to my NVIDIA GPU for better performance, especially with the graphical user interface.

- **Web UI:** Accessible at `http://<server-ip>:3000`.
- **Configuration Volume:** The `./data/orcaslicer-data` directory is mapped to `/config` inside the container. This is where all slicer settings, profiles, and user data are stored.
- **Projects Volume:** The `./data/3d-files` directory is mapped to `/projects`, making all my 3D models available directly within the OrcaSlicer interface.

#### Syncthing

Syncthing is the backbone of the synchronization process. It keeps files and profiles consistent between my Windows PC and the Ubuntu server.

- **Web UI:** Accessible at `http://<server-ip>:8384`.
- **Sync Folders:**
  - **OrcaSlicer Profiles:** The `./data/orcaslicer-data/user` directory on the server is shared. On my Windows machine, I sync my local `%APPDATA%\OrcaSlicer\user` directory to this share.
  - **3D Models:** The `./data/3d-files` directory is also shared, keeping my entire library of models in sync.

### Printer Monitoring & Inventory

This layer provides real-time telemetry, data visualization, and inventory tracking for the Bambu Lab printer. It consists of the following services:

- **`bambu-exporter`**: A custom service (built from the `./bambu-exporter` directory) that connects to the printer's MQTT stream and exposes its data as Prometheus-compatible metrics. Using a custom build allows for easy modification and adaptation.
- **`prometheus`**: A time-series database that collects and stores the metrics from `bambu-exporter`. Accessible at `http://<server-ip>:9090`.
- **`grafana`**: Visualizes the data stored in Prometheus. This is where the real-time system dashboard is built. Accessible at `http://<server-ip>:3002`.
- **`inventree-db`**: A PostgreSQL database that provides persistent storage for the InvenTree service.
- **`inventree`**: An open-source inventory management system used to track filament spools, material usage, and costs. It provides a REST API, which is key for automation. Accessible at `http://<server-ip>:8000`.

### Automation (Optional)

#### `bridge-script`

A custom Python script that acts as the "glue" between the printer and the inventory system. It listens for "print finished" events on the MQTT stream, extracts the filament usage, and automatically deducts that amount from the correct spool in InvenTree via its API.

*Note: This service is commented out by default in `docker-compose.yml` and can be enabled to complete the automation loop.*

## How It Works

The workflow is designed to be simple and automated:

1.  I work on my Windows PC, using my local OrcaSlicer application to tweak profiles or exported from my CAD tool.
2.  The Syncthing client on my Windows PC detects changes in the `user` profile directory and the 3D models folder.
3.  These changes are automatically pushed to the Syncthing container running on the server.
4.  The Syncthing container writes the updated files to the volumes shared with the OrcaSlicer container (`./data/orcaslicer-data/user` and `./data/3d-files`).
5.  The Dockerized OrcaSlicer instance now has the exact same profiles and files as my local machine.
6.  I can then connect to my Tailnet from any device, open a browser to the OrcaSlicer web UI, and start a print without having to manually transfer files or worry about outdated settings.

**When a print finishes on the Bambu Lab printer:**

1.  The printer publishes a "print finished" message to its MQTT topic.
2.  If enabled, the `bridge-script` container receives the message.
3.  The script parses the payload to determine how much filament was used.
4.  It then makes an API call to InvenTree to subtract the used amount from the stock of the filament spool assigned to that print.

## Getting Started

1.  Clone the repository.
2.  Ensure Docker and `docker-compose` are installed on the server.
3.  Create the necessary directories for configs and data: `mkdir -p data bambu-exporter prometheus`.
4.  Create a `.env` file by copying the example template: `cp .env.example .env`.
5.  Edit the `.env` file. At a minimum, you must set:
    - Your user/group IDs (`PUID`/`PGID`).
    - Your printer's network details (`BAMBU_PRINTER_IP`, `BAMBU_ACCESS_CODE`, `BAMBU_SERIAL_NUMBER`).
    - The external URL for InvenTree (`INVENTREE_SITE_URL`). For a simple local setup, `http://<server-ip>:8000` is sufficient.
6.  If you have an NVIDIA GPU, ensure the NVIDIA Container Toolkit is installed for GPU passthrough.
7.  Run `docker-compose up -d` to start all services.
8.  **Initial Syncthing Setup:**
    - Access the Syncthing UI at `http://<server-ip>:8384`.
    - Add your desired PC as a remote device.
    - On the desired PC, share your OrcaSlicer user profile directory (e.g., `C:\Users\<YourUser>\AppData\Roaming\OrcaSlicer\user`) and your 3D models directory with the server.
    - On the server's Syncthing UI, accept the incoming shares and point them to the `/orca-sync` and `/projects-sync` folders.
9.  **Grafana Setup:**
    - Access Grafana at `http://<server-ip>:3002`.
    - Log in with the credentials from your `.env` file.
    - Add Prometheus (`http://prometheus:9090`) as a data source and start building your dashboard!
10. **InvenTree Setup:**
    - Access InvenTree at `http://<server-ip>:8000`.
    - Log in with the admin credentials from your `.env` file.

## Future Plans

The vision for the F2 Stack is to evolve from a 3D printing utility into a full-stack **Autonomy R&D and Manufacturing Hub**. The goal is to create a comprehensive engineering environment for personal projects, such as the development of my 2-meter wingspan VTOL tailsitter running Ardupilot.

Planned service integrations are categorized as follows:

### 1. Manufacturing & Project Management (In Progress)
- **InvenTree:** Track filament spools, PCB components, and the lifecycle of printed parts.
- **Plane:** A self-hosted project management tool (like Jira) to manage design cycles, sprints, and development tickets.

### 2. Autonomy Simulation
- **ArduPilot/JSBSIM Sandbox:** A containerized environment for software-in-the-loop (SITL) simulation to test ArduPilot firmware without risking the physical airframe.
- **MAVProxy/MAVLink Router:** A central hub for routing MAVLink messages between the simulation/aircraft, a Ground Control Station, and the telemetry database.

### 3. Flight Telemetry & Analysis
- **InfluxDB & Telegraf:** A time-series database to ingest and store MAVLink flight logs for detailed post-flight analysis.
- **Grafana:** For creating dashboards that visualize flight data, compare simulated vs. actual flight paths, and monitor aircraft health metrics.

### 4. DevOps & Companion Compute
- **Gitea:** A self-hosted Git service for version control of all firmware, software, and design files.
- **ROS2 Development Container:** An environment that mirrors the on-board companion computer (e.g., Jetson Orin Nano) to develop and test computer vision or obstacle avoidance nodes before deployment.