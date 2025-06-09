# Pixhawk GUI Interface

This application provides a real-time ground control station (GCS) interface for monitoring and visualizing flight telemetry from a Pixhawk-based drone system.

## Features

- 📡 **Pixhawk MAVLink Connection:** Connect via COM port and baud rate selection to read real-time flight data.
- 📹 **Live Video Streaming:** View an IP camera stream integrated into the UI.
- 📊 **Custom Widgets:**
  - Vertical speed indicator
  - Airspeed gauge
  - Attitude indicator (roll/pitch)
  - Battery level visualization
  - Lidar sensor plot (polar)
- 🛰 **Flight Data Display:**
  - Altitude
  - Flight time
  - Battery percentage
- 🔧 **IP Configurable:** Easily switch between multiple IP camera addresses.

## Requirements

- Python 3.7+
- PyQt5
- OpenCV
- NumPy
- Requests
- pymavlink
- matplotlib

Make sure your Pixhawk is connected and your IP camera and lidar endpoints are accessible.

## Notes
Camera feed is expected to be available at http://<IP>:5000/video_feed

Lidar data should be served as JSON at http://<IP>:5001/lidar
