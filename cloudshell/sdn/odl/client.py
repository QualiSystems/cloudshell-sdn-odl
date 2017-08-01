from collections import defaultdict
import json

import networkx as nx
import requests
from requests.auth import HTTPBasicAuth


class ODLClient(object):
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

    # def calculate_route(self, src_sw, dst_sw):
        # route = []
        # graph = self.get_graph()
        # shortest_path = nx.dijkstra_path(graph, src_sw, dst_sw)
        #
        # # nx.shortest_path(graph)["openflow:1"]["openflow:3"]
        # # [u'openflow:1', u'openflow:2', u'openflow:3']
        #
        # for sw_name in shortest_path:
        #     pass
        #
        # # [{"port_in": 1", "port_out": 2, "switch": 2} ]

    def get_switch(self, switch_id):
        response = self._do_get(path="restconf/operational/opendaylight-inventory:nodes/node/{}".format(switch_id))
        data = response.json()
        return data["node"][0]

    def calculate_routes(self, src_switch, src_port, dst_switch, dst_port):
        # todo: rework it ... make ports as nodes???
        rules = defaultdict(dict)
        graph = self.get_graph()

        rules[src_switch]["port_in"] = int(src_port)
        rules[dst_switch]["port_out"] = int(dst_port)

        shortest_path = nx.dijkstra_path(graph, src_switch, dst_switch)

        for x in xrange(len(shortest_path) - 1):
            src_sw = shortest_path[x]
            dst_sw = shortest_path[x + 1]
            data = graph.get_edge_data(src_sw, dst_sw)
            rules[src_sw]["port_out"] = int(data["src_tp"].split(":")[-1])
            rules[dst_sw]["port_in"] = int(data["dst_tp"].split(":")[-1])

        src_route = []
        dst_route = []

        for key, items in rules.iteritems():
            items["switch"] = key
            src_route.append(items)
            dst_items = items.copy()
            dst_items["port_in"], dst_items["port_out"] = dst_items["port_out"], dst_items["port_in"]
            dst_route.append(dst_items)

        return src_route, dst_route

    def create_route(self, src_switch, src_port, dst_switch, dst_port):
        """Create route
            {
                "cloudshell:input": {
                    "src_mac": "src_mac",
                    "dst_mac": "dst_mac",
                    "allow": "true",
                    "src_rules": [
                        {
                            "port_in": "1",
                            "port_out": "2",
                            "switch": "openflow:1"
                        }
                    ]
                }
            }

        :param src_switch:
        :param src_port:
        :param dst_switch:
        :param dst_port:
        :return:
        """
        src_rules, dst_rules = self.calculate_routes(src_switch, src_port, dst_switch, dst_port)

        data = {
            "cloudshell:input": {
                "src_switch": src_switch,
                "src_port": src_port,
                "dst_switch": dst_switch,
                "dst_port": dst_port,
                "src_rules": json.dumps(src_rules),
                "dst_rules": json.dumps(dst_rules),
                "allow": True,
            }
        }
        print data
        self._do_post(path="restconf/operations/cloudshell:create-route", json=data)

    def delete_route(self, src_switch, src_port, dst_switch, dst_port):
        """Delete route
            {
                "cloudshell:input": {
                    "src_mac": "src_mac",
                    "dst_mac": "dst_mac",
                    "allow": "false",
                    "route": [
                        {
                            "port_in": "1",
                            "port_out": "2",
                            "switch": "openflow:1"
                        }
                    ]
                }
            }

        :param src_switch:
        :param src_port:
        :param dst_switch:
        :param dst_port:
        :return:
        """
        data = {
            "cloudshell:input": {
                "src_switch": src_switch,
                "src_port": src_port,
                "dst_switch": dst_switch,
                "dst_port": dst_port,
                "src_rules": "",
                "dst_rules": "",
                "allow": False,
            }
        }
        # todo: add another API
        self._do_post(path="restconf/operations/cloudshell:create-route", json=data)


if __name__ == "__main__":
    cli = ODLClient(address="localhost", username="admin", password="admin")

    # print cli.get_leaf_switches()

    # print cli.create_route(src_switch="openflow:2",
    #                        src_port="1",
    #                        dst_switch="openflow:2",
    #                        dst_port="2")

    # print cli.delete_route(src_switch="openflow:3",
    #                        src_port="1",
    #                        dst_switch="openflow:3",
    #                        dst_port="2")


    # print cli.create_route(src_switch="openflow:3",
    #                        src_port="1",
    #                        dst_switch="openflow:3",
    #                        dst_port="2")

    print cli.create_route(src_switch="openflow:2",
                           src_port="1",
                           dst_switch="openflow:3",
                           dst_port="2")