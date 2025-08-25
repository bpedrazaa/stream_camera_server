# RTSP Websocket Bridge

A containerized WebSocket server that streams video from RTSP cameras to clients.

## Setup

Create a .env file and add your camera streams:

```env
CAMERA_STREAMS=rtsp://username:password@camera1-ip,rtsp://username:password@camera2-ip
RESTART_POLICY=unless-stopped
```

## Usage

Run with Docker Compose:

```bash
docker-compose up
```

The server will start and provide WebSocket streams at:
`ws://localhost:6001/stream1 for the first camer`
`ws://localhost:6001/stream2 for the second camera`

(Add more paths as needed for additional cameras)

> [!NOTE]
> All dependencies are containerized - no local Python installation required.
