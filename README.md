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

## Testing
Inside `resource` folder there is a `mcu` class acting as a simple TCP Client by sending 'random' data to the server. Simply uncomment the relevant code fragments in `rasp_process.py` and re-run.