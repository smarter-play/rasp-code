# rasp-code
## Installation
1. `python -m venv .venv`

2. `source .venv/bin/activate`

3. `pip install -r requirements.txt`

## Configuration
Located inside `mqtt->conf` folder
- `bridge_info.py` TCP Server configuration data
- `broker_params.py` : MQTT BROKER configuration data
- `packet_structures.py`: CUSTOM TCP packet structure

## Running 
Simply run `python mqtt/process/rasp_process.py`. 

## Running (using Docker)

This repository comes with an already setup Access Point and Python environment ready to run both
the Access Point and the Bridge server on your Raspberry PI. You just have to run:

```
docker compose up
```

## Testing
You can send simulated packets to the server by running `python simulate.py`.
