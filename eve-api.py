import json
import re
import requests
from urllib.parse import quote
import yaml
from jinja2 import Environment, FileSystemLoader
import argparse

def main(args):
    eveurl = args.eveurl
    eve_user = args.eve_user
    eve_pw = args.eve_pw
    labdir = args.labdir
    labname = args.labname
    veos_version = args.veos_version
    act_veos_username = args.act_veos_username
    act_veos_password = args.act_veos_password
    mgmt_ip_range = args.mgmt_ip_range
    act_add_cvp = args.act_add_cvp
    act_cvp_version = args.act_cvp_version
    act_cvp_user = args.act_cvp_user
    act_cvp_password = args.act_cvp_password
    act_cvp_instance_type = args.act_cvp_instance_type
    act_cvp_ip = args.act_cvp_ip

def assign_unique_ips(mgmt_ip_range, node_list):
    start_ip, end_ip = args.mgmt_ip_range.split("-")
    start_ip_parts = [int(part) for part in start_ip.split(".")]
    end_ip_parts = [int(part) for part in end_ip.split(".")]

    nodes_ip_map = {}
    current_ip_parts = start_ip_parts

    for node in node_list:
        if current_ip_parts <= end_ip_parts:
            nodes_ip_map[node] = ".".join(str(part) for part in current_ip_parts)

            current_ip_parts[3] += 1
            if current_ip_parts[3] > 255:
                current_ip_parts[3] = 0
                current_ip_parts[2] += 1
                if current_ip_parts[2] > 255:
                    current_ip_parts[2] = 0
                    current_ip_parts[1] += 1
                    if current_ip_parts[1] > 255:
                        current_ip_parts[1] = 0
                        current_ip_parts[0] += 1
        else:
            raise Exception("The IP range is too small for the number of nodes.")

    return nodes_ip_map

def process_json_files():
    # Read JSON files
    with open("outputs/eve/eve-nodes-result.json", "r") as f:
        eve_nodes_result = json.load(f)

    with open("outputs/eve/eve-topology-result.json", "r") as f:
        eve_topology_result = json.load(f)

    # Process eve_topology_result and add name value from eve_nodes_result
    updated_topology_result = []
    for item in eve_topology_result:
        print(item["source_type"])
        if item["source_type"] == "node" and item["destination_label"] == "":
            source_id = re.sub("node", "", item["source"])
            source_name = eve_nodes_result.get(source_id, {"name": "unknown"})["name"]
            updated_item = {**item, "source": source_name}
            updated_topology_result.append(updated_item)
        elif item["source_type"] == "node" and item["destination_type"] == "node":
            source_id = re.sub("node", "", item["source"])
            destination_id = re.sub("node", "", item["destination"])
            source_name = eve_nodes_result.get(source_id, {"name": "unknown"})["name"]
            destination_name = eve_nodes_result.get(destination_id, {"name": "unknown"})["name"]
            updated_item = {**item, "source": source_name, "destination": destination_name}
            updated_topology_result.append(updated_item)
        else:
            print("unsupported")
    unique_node_names = set(item["source"] for item in updated_topology_result)
    nodes_ip_map = assign_unique_ips(args.mgmt_ip_range, unique_node_names)

    # Render the Jinja2 template and write the output to act-topology.yaml
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/act_topology_template.j2')
    act_topology_yaml = template.render(
        updated_topology_result=updated_topology_result,
        act_veos_username=args.act_veos_username,
        act_veos_password=args.act_veos_password,
        veos_version=args.veos_version,
        act_cvp_user=args.act_cvp_user,
        act_cvp_password=args.act_cvp_password,
        act_cvp_version=args.act_cvp_version,
        act_add_cvp=args.act_add_cvp,
        act_cvp_ip=args.act_cvp_ip,
        nodes_ip_map=nodes_ip_map
    )

    with open("outputs/act_topology/act-topology.yaml", "w") as f:
        f.write(act_topology_yaml)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,description="EVE-NG to ACT Topology Convert",fromfile_prefix_chars="@",prog='eve-to-act.py')
    parser.add_argument("eveurl", type=str,help="EVE-NG URL")
    parser.add_argument("-eve-user", type=str, default="admin", help="EVE Username")
    parser.add_argument("-eve-pw", type=str, default="eve", help="EVE Password")
    parser.add_argument("labdir", type=str, default="", help="Lab directory")
    parser.add_argument("labname", type=str, default="", help="Lab UNL File Name")
    parser.add_argument("--veos-version", type=str, default="4.28.0F", help="vEOS version")
    parser.add_argument("--act-veos-username", type=str, default="cvpadmin", help="vEOS username")
    parser.add_argument("--act-veos-password", type=str, default="arista123", help="vEOS password")
    parser.add_argument("--mgmt-ip-range", type=str, default="192.168.0.100-192.168.0.250", help="Management IP range")
    parser.add_argument("--act-add-cvp", action="store_false", help="Enable adding CVP")
    parser.add_argument("--act-cvp-version", type=str, default="2022.2.1", help="CVP version")
    parser.add_argument("--act-cvp-user", type=str, default="root", help="CVP user")
    parser.add_argument("--act-cvp-password", type=str, default="cvproot", help="CVP password")
    parser.add_argument("--act-cvp-instance-type", type=str, default="singlenode", help="CVP instance type")
    parser.add_argument("--act-cvp-ip", type=str, default="192.168.0.5", help="CVP IP address")

    args = parser.parse_args()
    main(args)

    # Auth to EVE
    auth_url = f"{args.eveurl}/api/auth/login"
    headers = {"Accept": "application/json"}
    data = {"username": args.eve_user, "password": args.eve_pw}
    response = requests.post(auth_url, headers=headers, data=json.dumps(data), verify=False)
    response.raise_for_status()
    cookies = response.cookies

    # Get EVE topology
    topo_url = f"{args.eveurl}/api/labs/{quote(args.labdir)}/{quote(args.labname)}/topology"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(topo_url, headers=headers, cookies=cookies, verify=False)
    response.raise_for_status()
    topology = response.json()["data"]

    # Write EVE topology to file
    with open("outputs/eve/eve-topology-result.json", "w") as f:
        json.dump(topology, f, indent=2)

    # Get node names
    nodes_url = f"{args.eveurl}/api/labs/{quote(args.labdir)}/{quote(args.labname)}/nodes"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(nodes_url, headers=headers, cookies=cookies, verify=False)
    response.raise_for_status()
    lab_nodes_result = response.json()["data"]

    # Write nodes to file
    with open("outputs/eve/eve-nodes-result.json", "w") as f:
        json.dump(lab_nodes_result, f, indent=2)

    # Process JSON files and create a new YAML file
    process_json_files()
