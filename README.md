# HandTracking-Websockets

A real-time hand tracking system that streams landmark data through WebSocket connections for hand motion capture in Unreal Engine 5.

## Features

- Real-time hand tracking using MediaPipe
- WebSocket server for data streaming to Unreal Engine 5
- Normalized hand coordinate system for mocap integration
- Support for tracking both hands simultaneously
- Rest state detection when hands are not visible
- Live hand motion capture data streaming

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- WebSockets
- AsyncIO
- Unreal Engine 5 project with WebSocket client capability

Install dependencies:
```pip install -r requirements.txt```

## Usage

1. Start the Python WebSocket server:
```python main.py```

2. In Unreal Engine 5, connect to the WebSocket server at `ws://localhost:8765` to receive motion capture data for hand tracking

## Data Format

The server streams JSON data in the following format:

```json
{
    "HandLeft": {
        "landmarks": [
            {
                "id": 0,
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            ...
        ],
        "depth": 0.123,
        "rest": false
    },
    "HandRight": {
        "rest": true
    }
}