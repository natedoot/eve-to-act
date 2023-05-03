# eve-to-act
## Convert EVE-NG topology to ACT topology
1. Auth to EVE-NG and get topology and node information
2. Process node and topology data
3. Convert to ACT topology
4. Output ACT topology file
## How to use and arguments
### Usage
```
usage: eve-to-act.py [eve url] [lab directory] [lab name] [options]

# Inline arguments example
doot@clab:~/eve-to-act$ /usr/bin/python3 eve-api.py http://192.168.1.219 "arista evpn" "evpn migration.unl" -eve-user admin -eve-pw eve

# Args file example
doot@clab:~/eve-to-act$ /usr/bin/python3 eve-api.py @args.txt

```
### Optional arguments
| Option | Description |
| --- | --- |
| -h, --help | show this help message and exit |
| -eve-user EVE_USER | EVE Username (default: admin) |
| -eve-pw EVE_PW | EVE Password (default: eve) |
| --veos-version VEOS_VERSION | vEOS version (default: 4.28.0F) |
| --act-veos-username ACT_VEOS_USERNAME | vEOS username (default: cvpadmin) |
| --act-veos-password ACT_VEOS_PASSWORD | vEOS password (default: arista123) |
| --mgmt-ip-range MGMT_IP_RANGE | Management IP range (default: 192.168.0.100-192.168.0.250) |
| --act-add-cvp | Enable adding CVP (default: True) |
| --act-cvp-version ACT_CVP_VERSION | CVP version (default: 2022.2.1) |
| --act-cvp-user ACT_CVP_USER | CVP user (default: root) |
| --act-cvp-password ACT_CVP_PASSWORD | CVP password (default: cvproot) |
| --act-cvp-instance-type ACT_CVP_INSTANCE_TYPE | CVP instance type (default: singlenode) |
| --act-cvp-ip ACT_CVP_IP | CVP IP address (default: 192.168.0.5) |
