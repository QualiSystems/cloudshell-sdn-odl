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
            graph.add_node(node["node-id"])

        for link in topo.get("link", []):
            src = link["source"]
            dst = link["destination"]

            graph.add_edge(src["source-node"], dst["dest-node"], attr_dict={
                "src_tp": src["source-tp"],
                "dst_tp": dst["dest-tp"]
            })

        return graph

    def get_leaf_switches(self):
        """Return leaf switches

        :rtype: list[str]
        """
        graph = self.get_graph()
        # leaf switches will have only one outgoing link or will haven't links at all
        return [node for node, out_links_count in graph.out_degree().items() if out_links_count <= 1]

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

    def calculate_route(self, src_switch, src_port, dst_switch, dst_port):
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

        # return rules
        # return rules
        xx = []
        for key, items in rules.iteritems():
            items["switch"] = key
            xx.append(items)
        return xx

    def create_route(self, src_switch, src_port, dst_switch, dst_port):
        route = self.calculate_route(src_switch, src_port, dst_switch, dst_port)
        # data = {
        #     "route": "sffs", #json.dumps(route),
        #     "switch": src_switch,
        #     "port": src_port
        # }
        data = {
            "cloudshell:input": {
                "route": json.dumps(route),
                "switch": src_switch,
                "port": src_port
            }
        }
        self._do_post(path="restconf/operations/cloudshell:create-route", json=data)

    def delete_route(self):
        pass


if __name__ == "__main__":
    cli = ODLClient(address="localhost", username="admin", password="admin")
    cli.get_leaf_switches()
    print cli.create_route(src_switch="openflow:1", src_port="1", dst_switch="openflow:3", dst_port="1")
    # sw = cli.get_switch("openflow:1")
