# Parker-Hub

Welcome to Parker-Hub, my personal central hub for managing 3D printing workflows and other integrated services. This project leverages Docker to create a seamless, synchronized environment for 3D printing, accessible from anywhere on my personal Tailnet.

## Overview

The core idea behind Parker-Hub is to solve the challenge of keeping 3D models and slicer profiles synchronized between different computers. I primarily use a Windows PC for designing and slicing, but I want a centralized, always-on server (running on Ubuntu) to manage the printer and store files.

This setup allows me to:

- **Sync OrcaSlicer Settings:** Keep my user profiles, filament settings, and printer configurations consistent between my Windows machine and the server.
- **Centralize 3D Models:** Have a single source of truth for all my `.stl` and `.3mf` files.
- **Remote Access:** Access the OrcaSlicer web interface from any device on my Tailnet (phone, laptop, etc.) to monitor and manage prints on my Bambu Lab H2D printer.
- **Extensibility:** Easily add new services to monitor and enhance my 3D printing experience.

## Core Services

This project is orchestrated using `docker-compose` and currently includes two main services:

### 1. OrcaSlicer

The `linuxserver/orcaslicer` image provides a full-featured OrcaSlicer instance running in a Docker container. It's configured with GPU passthrough to my NVIDIA GPU for better performance, especially with the graphical user interface.

- **Web UI:** Accessible at `http://<server-ip>:3000`.
- **Configuration Volume:** The `./data/orcaslicer-data` directory is mapped to `/config` inside the container. This is where all slicer settings, profiles, and user data are stored.
- **Projects Volume:** The `./data/3d-files` directory is mapped to `/projects`, making all my 3D models available directly within the OrcaSlicer interface.

### 2. Syncthing

Syncthing is the backbone of the synchronization process. It keeps files and profiles consistent between my Windows PC and the Ubuntu server.

- **Web UI:** Accessible at `http://<server-ip>:8384`.
- **Sync Folders:**
  - **OrcaSlicer Profiles:** The `./data/orcaslicer-data/user` directory on the server is shared via Syncthing. On my Windows machine, I sync my local `%APPDATA%\OrcaSlicer\user` directory to this share. This ensures any change to a filament profile, printer setting, or process is immediately reflected on the server's OrcaSlicer instance.
  - **3D Models:** The `./data/3d-files` directory is also shared, keeping my entire library of models in sync.

## How It Works

The workflow is designed to be simple and automated:

1.  I work on my Windows PC, using my local OrcaSlicer application to tweak profiles or exported from my CAD tool.
2.  The Syncthing client on my Windows PC detects changes in the `user` profile directory and the 3D models folder.
3.  These changes are automatically pushed to the Syncthing container running on the server.
4.  The Syncthing container writes the updated files to the volumes shared with the OrcaSlicer container (`./data/orcaslicer-data/user` and `./data/3d-files`).
5.  The Dockerized OrcaSlicer instance now has the exact same profiles and files as my local machine.
6.  I can then connect to my Tailnet from any device, open a browser to the OrcaSlicer web UI, and start a print without having to manually transfer files or worry about outdated settings.

## Getting Started

1.  Clone the repository.
2.  Ensure Docker and `docker-compose` are installed on the server.
3.  If you have an NVIDIA GPU, ensure the NVIDIA Container Toolkit is installed for GPU passthrough.
4.  Run `docker-compose up -d` to start the services.
5.  **Initial Syncthing Setup:**
    - Access the Syncthing UI at `http://<server-ip>:8384`.
    - Add your desired PC as a remote device.
    - On the desired PC, share your OrcaSlicer user profile directory (e.g., `C:\Users\<YourUser>\AppData\Roaming\OrcaSlicer\user`) and your 3D models directory with the server.
    - On the server's Syncthing UI, accept the incoming shares and point them to the `/orca-sync` and `/projects-sync` folders respectively.
6.  **OrcaSlicer Access:**
    - Access the OrcaSlicer UI at `http://<server-ip>:3000`.
    - Your profiles and models should appear automatically once Syncthing completes its initial sync.

## Future Plans

The vision for Parker-Hub is to evolve from a 3D printing utility into a full-stack **Autonomy R&D and Manufacturing Hub**. The goal is to create an industrial-grade engineering environment for personal projects, such as the development of a 2-meter VTOL tailsitter.

Planned service integrations are categorized as follows:

### 1. Manufacturing & Project Management
- **InvenTree:** An open-source inventory management system to track filament spools, PCB components, and the lifecycle of printed parts.
- **Plane:** A self-hosted project management tool (like Jira) to manage design cycles, sprints, and development tickets.

### 2. Autonomy Simulation (SITL/HITL)
- **ArduPilot/JSBSIM Sandbox:** A containerized environment for software-in-the-loop (SITL) simulation to test ArduPilot firmware without risking the physical airframe.
- **MAVProxy/MAVLink Router:** A central hub for routing MAVLink messages between the simulation/aircraft, a Ground Control Station, and the telemetry database.

### 3. Flight Telemetry & Analysis
- **InfluxDB & Telegraf:** A time-series database to ingest and store MAVLink flight logs for detailed post-flight analysis.
- **Grafana:** For creating dashboards that visualize flight data, compare simulated vs. actual flight paths, and monitor aircraft health metrics.

### 4. DevOps & Companion Compute
- **Gitea:** A self-hosted Git service for version control of all firmware, software, and design files.
- **ROS2 Development Container:** An environment that mirrors the on-board companion computer (e.g., Jetson Orin Nano) to develop and test computer vision or obstacle avoidance nodes before deployment.