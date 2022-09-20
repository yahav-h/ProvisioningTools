import os
import time
import json
import requests
from helpers import readCfg, callInThread, ProcessExecutor, Commands, AGENT


cfg = readCfg(AGENT)
schema = "http"
SERVER_URL = f"{schema}://{cfg.get('peer')}:{cfg.get('port')}"
headers = {"content-type": "application/json"}
service_path = os.path.join(os.path.expanduser("~"),"TokenService")
response = requests.request(
    method="POST",
    url=f"{SERVER_URL}/status",
    data=json.dumps({"action": "stopped", "source": "10.10.29.142", "req-time": time.time()}),
    headers=headers
)
data = response.json()
track_id = data.get('track-id')
time.sleep(10)
while data.get('status') == 'pending':
    response = requests.request(
        method="GET",
        url=f"{SERVER_URL}/track?id={track_id}",
        headers=headers
    )
    data = response.json()
    time.sleep(3)
print("\t\t**starting service**")
t = callInThread(target=ProcessExecutor.execute, args=(Commands.SERVICE_START.value % service_path,), daemon=True)
time.sleep(3)
