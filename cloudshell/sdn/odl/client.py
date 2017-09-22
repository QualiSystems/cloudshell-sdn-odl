import httplib

import networkx as nx
import requests
from requests.auth import HTTPBasicAuth


class ODLClient(object):
    VTN_NAME_PREFIX = "CS_VLAN_"
    VTN_TRUNKS_NAME = "CS_TRUNKS"
    VBRIDGE_NAME = "CS_VBRIDGE"
    TRUNK_FLOW_PRIORITY = 9
    DEFAULT_FLOW_TABLE = 0

    def __init__(self, address, username, password, scheme="http", port=8181):
        """

        :param str address: controller address (Example: https://10.10.0.11 or 10.10.0.11)
        :param str username: controller username
        :param str password: controller password
        :param str scheme: protocol (http|https)
        :param int port: controller port
        """
        self._base_url = "{}://{}:{}".format(scheme, address, port)
        self._auth = HTTPBasicAuth(username=username, password=password)
        self._headers = {"Content-Type": "application/json"}

    def _do_get(self, path, raise_for_status=True, **kwargs):
        """Basic GET request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        resp = requests.get(url=url, auth=self._auth, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_post(self, path, raise_for_status=True, **kwargs):
        """Basic POST request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        resp = requests.post(url=url, auth=self._auth, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_put(self, path, raise_for_status=True, **kwargs):
        """Basic PUT request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        resp = requests.put(url=url, auth=self._auth, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_delete(self, path, raise_for_status=True, **kwargs):
        """Basic DELETE request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        resp = requests.delete(url=url, auth=self._auth, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def get_topology(self):
        """Get network topology data

        :rtype: dict
        """
        response = self._do_get(path="restconf/operational/network-topology:network-topology")
        data = response.json()
        return data["network-topology"]["topology"][0]

    def _get_graph(self):
        """Get bidirectional graph representation of the network topology

        :rtype: nx.DiGraph
        """
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
        """Get leaf switches IDs

        :rtype: list[str]
        """
        graph = self._get_graph()
        # leaf switches will have only one outgoing link or will haven't links at all
        return [node for node, out_links_count in graph.out_degree().items() if out_links_count <= 1]

    def get_switches(self):
        """Get all switches names

        :rtype: list[str]
        """
        graph = self._get_graph()
        return graph.nodes()

    def get_switch(self, switch_id):
        """Get switch data by its ID

        :param str switch_id:
        :rtype: dict
        """
        response = self._do_get(path="restconf/operational/opendaylight-inventory:nodes/node/{}".format(switch_id))
        data = response.json()
        return data["node"][0]

    def create_ctrl_flow(self, node_id, flow_id, in_port, priority, table_id=DEFAULT_FLOW_TABLE):
        """Create output CONTROLLER action flow

        :param str node_id:
        :param int table_id:
        :param str flow_id:
        :param str in_port:
        :param int priority:
        :return:
        """
        data = {
            "flow": {
                "id": flow_id,
                "instructions": {
                    "instruction": {
                        "order": "0",
                        "apply-actions": {
                            "action": [
                                {
                                    "order": 0,
                                    "output-action": {
                                        "max-length": 65535,
                                        "output-node-connector": "CONTROLLER"
                                    }
                                }
                            ]
                        }
                    }
                },
                "match": {
                    "in-port": in_port
                },
                "priority": priority,
                "table_id": table_id
            }
        }
        self._do_put(path="restconf/config/opendaylight-inventory:nodes/node/{}/table/{}/flow/{}"
                     .format(node_id, table_id, flow_id),
                     json=data)

    def delete_ctrl_flow(self, node_id, flow_id, table_id=DEFAULT_FLOW_TABLE, raise_for_status=True):
        """Delete Openflow entry from the controller by its id

        :param str node_id:
        :param str flow_id:
        :param int table_id:
        :param bool raise_for_status:
        :return:
        """
        self._do_delete(path="restconf/config/opendaylight-inventory:nodes/node/{}/table/{}/flow/{}".format(
            node_id, table_id, flow_id),
            raise_for_status=raise_for_status)

    def create_vtn(self, tenant_name):
        """Create VTN object on the controller

        :param str tenant_name:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name
            }
        }
        self._do_post(path="restconf/operations/vtn:update-vtn", json=data)

    def delete_vtn(self, tenant_name):
        """Delete VTN object from the controller

        :param str tenant_name:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name
            }
        }
        self._do_post(path="restconf/operations/vtn:remove-vtn", json=data)

    def create_vbridge(self, tenant_name, bridge_name):
        """Create vBridge object under the given VTN on the controller

        :param str tenant_name:
        :param str bridge_name:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name
            }
        }
        self._do_post(path="restconf/operations/vtn-vbridge:update-vbridge", json=data)

    def create_interface(self, tenant_name, bridge_name, if_name):
        """Create interface object under the given VTN and vBridge on the controller

        :param str tenant_name:
        :param str bridge_name:
        :param str if_name:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
                "interface-name": if_name
            }
        }
        self._do_post(path="restconf/operations/vtn-vinterface:update-vinterface", json=data)

    def delete_interface(self, tenant_name, bridge_name, if_name, raise_for_status=True):
        """Delete interface object from the given VTN and vBridge

        :param str tenant_name:
        :param str bridge_name:
        :param str if_name:
        :param bool raise_for_status:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
                "interface-name": if_name
            }
        }

        self._do_post(path="restconf/operations/vtn-vinterface:remove-vinterface",
                      json=data,
                      raise_for_status=raise_for_status)

    def map_port_to_interface(self, tenant_name, bridge_name, if_name, node_id, phys_port_name, vlan_id=0):
        """Map VTN interface to the physical port on the Open vSwitch

        :param str tenant_name:
        :param str bridge_name:
        :param str if_name:
        :param str node_id:
        :param str phys_port_name:
        :param int vlan_id:
        :return:
        """
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

    def get_interface(self, tenant_name, bridge_name, if_name, raise_for_status=True):
        """Get VTN interface data

        :param str tenant_name:
        :param str bridge_name:
        :param str if_name:
        :param bool raise_for_status:
        :rtype: dict
        """
        response = self._do_get(path="restconf/operational/vtn:vtns/vtn/{}/vbridge/{}/vinterface/{}"
                                .format(tenant_name, bridge_name, if_name),
                                raise_for_status=raise_for_status)

        if not raise_for_status and response.status_code == httplib.NOT_FOUND:
            return

        response.raise_for_status()
        data = response.json()
        return data["vinterface"][0]

    def get_vtn_vbridge(self, tenant_name, bridge_name, raise_for_status=True):
        """Get VTN vBridge data

        :param str tenant_name:
        :param str bridge_name:
        :param bool raise_for_status:
        :return:
        """
        response = self._do_get(path="restconf/operational/vtn:vtns/vtn/{}/vbridge/{}".format(tenant_name, bridge_name),
                                raise_for_status=raise_for_status)

        if not raise_for_status and response.status_code == httplib.NOT_FOUND:
            return

        response.raise_for_status()
        data = response.json()
        return data.get("vbridge")[0]

    def vtn_access_interfaces_exists(self, tenant_name, bridge_name):
        """Check whether given vBridge contains access interfaces or not

        :param str tenant_name:
        :param str bridge_name:
        :rtype: bool
        """
        vbridge = self.get_vtn_vbridge(tenant_name=tenant_name, bridge_name=bridge_name)

        for interface in vbridge.get("vinterface", []):
            if interface.get("port-map-config", {}).get("vlan-id") == 0:
                return True

        return False

    def get_trunk_ports(self):
        """Get configured trunk ports

        :rtype: list[tuple[str, str]]
        """
        trunk_ports = []
        vbridge = self.get_vtn_vbridge(tenant_name=self.VTN_TRUNKS_NAME,
                                       bridge_name=self.VBRIDGE_NAME,
                                       raise_for_status=False)
        if vbridge is not None:
            for interface in vbridge.get("vinterface", []):
                trunk_ports.append((interface["port-map-config"]["node"], interface["port-map-config"]["port-name"]))

        return trunk_ports

    def delete_vbridge(self, tenant_name, bridge_name, raise_for_status=True):
        """Delete vBridge object from the given VTN

        :param str tenant_name:
        :param str bridge_name:
        :param bool raise_for_status:
        :return:
        """
        data = {
            "input": {
                "tenant-name": tenant_name,
                "bridge-name": bridge_name,
            }
        }
        self._do_post(path="restconf/operations/vtn-vbridge:remove-vbridge",
                      json=data,
                      raise_for_status=raise_for_status)

    def get_vtn(self, tenant_name, raise_for_status=True):
        """Get VTN by its name

        :param str tenant_name:
        :param bool raise_for_status:
        :return:
        """
        response = self._do_get(path="restconf/operational/vtn:vtns/vtn/{}".format(tenant_name),
                                raise_for_status=raise_for_status)

        if not raise_for_status and response.status_code == httplib.NOT_FOUND:
            return

        response.raise_for_status()
        data = response.json()
        return data.get("vtn")[0]

    def delete_interface_from_all_vbridges(self, tenant_name, if_name):
        """Delete interface from all vBridges in given VTN

        :param str tenant_name:
        :param str if_name:
        :return:
        """
        vtn = self.get_vtn(tenant_name=tenant_name, raise_for_status=False)

        if vtn is not None:
            for vbridge in vtn.get("vbridge", []):
                for interface in vbridge.get("vinterface", []):
                    if interface["name"] == if_name:
                        self.delete_interface(tenant_name=tenant_name,
                                              bridge_name=vbridge["name"],
                                              if_name=interface["name"])
                        break
