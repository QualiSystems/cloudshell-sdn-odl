import networkx as nx
import requests
from requests.auth import HTTPBasicAuth


class ODLClient(object):
    VTN_NAME_PREFIX = "VTN_VLAN_"
    VBRIDGE_NAME_PREFIX = "VBRINDGE_VLAN_"

    def __init__(self, address, username, password, port=8181):
        if "http" not in address:
            address = "{}://{}".format("http", address)

        self._base_url = "{}:{}".format(address, port)
        self._auth = HTTPBasicAuth(username=username, password=password)
        self._headers = {"Content-Type": "application/json"}

    def _do_get(self, path):
        url = "{}/{}".format(self._base_url, path)
        resp = requests.get(url=url, auth=self._auth, headers=self._headers)
        resp.raise_for_status()
        return resp

    def _do_post(self, path, **kwargs):
        url = "{}/{}".format(self._base_url, path)
        resp = requests.post(url=url, auth=self._auth, headers=self._headers, **kwargs)
        print resp.content
        resp.raise_for_status()
        return resp

    def _do_delete(self, path):
        url = "{}/{}".format(self._base_url, path)
        resp = requests.delete(url=url, auth=self._auth, headers=self._headers)
        resp.raise_for_status()
        return resp

    def get_topology(self):
        response = self._do_get(path="restconf/operational/network-topology:network-topology")
        data = response.json()

        return data["network-topology"]["topology"][0]

    def get_graph(self):
        graph = nx.DiGraph()
        topo = self.get_topology()

        for node in topo.get("node", []):
            if 'opendaylight-topology-inventory:inventory-node-ref' in node:
                graph.add_node(node["node-id"])

        for link in topo.get("link", []):
            src = link["source"]
            dst = link["destination"]

            if src["source-node"] in graph.nodes() and dst["dest-node"] in graph.nodes():
                graph.add_edge(src["source-node"], dst["dest-node"], attr_dict={
                    "src_tp": src["source-tp"],
                    "dst_tp": dst["dest-tp"]
                })
                graph.add_edge(dst["dest-node"], src["source-node"], attr_dict={
                    "src_tp": dst["dest-tp"],
                    "dst_tp": src["source-tp"]
                })

        return graph

    def get_leaf_switches(self):
        """Return leaf switches

        :rtype: list[str]
        """
        graph = self.get_graph()
        # leaf switches will have only one outgoing link or will haven't links at all
        return [node for node, out_links_count in graph.out_degree().items() if out_links_count <= 1]

    def get_switches(self):
        """Return leaf switches

        :rtype: list[str]
        """
        graph = self.get_graph()
        return graph.nodes()

    def get_switch(self, switch_id):
        response = self._do_get(path="restconf/operational/opendaylight-inventory:nodes/node/{}".format(switch_id))
        data = response.json()
        return data["node"][0]

    def create_vtn(self, tenant_name):
        data = {
            "input": {
                "tenant-name": tenant_name
            }
        }
        self._do_post(path="restconf/operations/vtn:update-vtn", json=data)

    def vtn_interfaces_exists(self, tenant_name, bridge_name):
        response = self._do_get(path="restconf/operational/vtn:vtns/vtn/{}/vbridge/{}".format(tenant_name, bridge_name))
        data = response.json()
        vbridge = data.get("vbridge")[0]

        return bool(vbridge.get("vinterface"))

    def delete_vtn(self, tenant_name):
        data = {
            "input": {
                "tenant-name": tenant_name
            }
        }
        self._do_post(path="restconf/operations/vtn:remove-vtn", json=data)

    def create_vbridge(self, tenant_name, bridge_name):
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name
            }
        }
        self._do_post(path="restconf/operations/vtn-vbridge:update-vbridge", json=data)

    def create_interface(self, tenant_name, bridge_name, if_name):
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
                "interface-name": if_name
            }
        }
        self._do_post(path="restconf/operations/vtn-vinterface:update-vinterface", json=data)

    def delete_interface(self, tenant_name, bridge_name, if_name):
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
                "interface-name": if_name
            }
        }
        self._do_post(path="restconf/operations/vtn-vinterface:remove-vinterface", json=data)

    def map_port_to_interface(self, tenant_name, bridge_name, if_name, node_id, phys_port_name, vlan_id):
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
                "interface-name": if_name,
                "node": node_id,
                "port-name": phys_port_name,
                "vlan-id": vlan_id
            }
        }
        self._do_post(path="restconf/operations/vtn-port-map:set-port-map", json=data)
