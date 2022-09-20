# ProvisioningTools

---

Provisioning Tools Repository - simple base HTTP server which 
expect to get updates from agents and act acoring to a basic flow using shell commands.

---

### <i>HOW-TO</i>:
Create a Virtual Environment
```shell
 $ /usr/bin/python3 -m venv myvenv
```
Install dependencies
```shell
$ ./myvenv/bin/python3 -m pip install --upgrade pip
$ ./myvenv/bin/python3 -m pip install -r ./requirements.txt
```
Update SERVER Configuration File
```yaml
# SERVER.YML
host: "0.0.0.0"
port: 8191
secret: "sixteen byte key"
```
Update AGENT Configuration File
```yaml
peer: "IP OF THE MACHINE RUNNING THE SERVER"
port: 8191
secret: "sixteen byte key"
```

