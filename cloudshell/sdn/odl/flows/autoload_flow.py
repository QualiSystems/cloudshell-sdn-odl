from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.sdn.autoload_structure import SDNControllerResource
from cloudshell.devices.standards.sdn.autoload_structure import GenericSDNSwitch
from cloudshell.devices.standards.sdn.autoload_structure import GenericSDNPort


class ODLAutoloadFlow(object):
    def __init__(self, odl_client, logger, api, resource_config):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :param resource_config: cloudshell.sdn.config_attrs_structure.GenericSDNResource
        """
        self._odl_client = odl_client
        self._logger = logger
        self._api = api
        self._resource_config = resource_config
        self._resources = []
        self._attributes = []
        self._resource = SDNControllerResource(shell_name=self._resource_config.shell_name,
                                               name="ODL Controller",
                                               unique_id="ODL Controller")  # todo: use resource_name here !!!

    def _create_trunks_vtn(self):
        """

        :return:
        """
        self._odl_client.create_vtn(tenant_name=self._odl_client.VTN_TRUNKS_NAME)
        self._odl_client.create_vbridge(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                        bridge_name=self._odl_client.VBRIDGE_NAME)

    def _convert_port_name(self, switch_id, port_name):
        """

        :return:
        """
        return "{}_{}".format(switch_id, port_name).replace("-", "_").replace(":", "_")

    def execute_flow(self):
        # ports used in connections between switches
        used_ports = []
        topo = self._odl_client.get_topology()
        switch_ids = self._odl_client.get_switches()

        self._create_trunks_vtn()

        for link in topo.get("link", []):
            tp = link["destination"]["dest-node"]
            op = link["source"]["source-node"]
            if tp in switch_ids and op in switch_ids:
                used_ports.append(link["source"]["source-tp"])
                used_ports.append(link["destination"]["dest-tp"])

        for switch_id in self._odl_client.get_leaf_switches():
            sw_unique_id = switch_id.split(":")[-1]
            sw_resource = GenericSDNSwitch(shell_name=self._resource_config.shell_name,
                                           name=switch_id.replace("openflow:", "openflow_"),
                                           unique_id=sw_unique_id)

            self._resource.add_sub_resource(sw_unique_id, sw_resource)
            switch = self._odl_client.get_switch(switch_id)

            for port in [port for port in switch["node-connector"]
                         if port["id"] not in used_ports
                         # ignore loopback interface
                         and "local" not in port["id"].lower()]:

                try:
                    port_name = port["flow-node-inventory:name"].replace("/", "-")
                except KeyError:
                    port_name = port["id"].replace("/", "-")

                try:
                    port_no = port["flow-node-inventory:port-number"]
                except KeyError:
                    # todo: for some ports the is no flow-node-inventory:port-number attr
                    port_no = port["id"].split(":")[-1]

                mac_addr = port.get("flow-node-inventory:hardware-address")
                unique_id = "{}.{}".format(sw_unique_id, port_no)

                port_object = GenericSDNPort(shell_name=self._resource_config.shell_name,
                                             name=port_name.replace(":", "-"),
                                             unique_id=unique_id)

                port_object.port_description = ""
                port_object.l2_protocol_type = ""
                port_object.mac_address = mac_addr
                port_object.mtu = 0
                port_object.bandwidth = 0
                port_object.ipv4_address = ""
                port_object.ipv6_address = ""
                port_object.duplex = ""
                port_object.auto_negotiation = ""
                port_object.adjacent = ""
                sw_resource.add_sub_resource(port_no, port_object)

                if (switch_id, port_name) in self._resource_config.add_trunk_ports:
                    if_name = self._convert_port_name(switch_id=switch_id, port_name=port_name)

                    self._odl_client.create_interface(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                                      bridge_name=self._odl_client.VBRIDGE_NAME,
                                                      if_name=if_name)

                    self._odl_client.map_port_to_interface(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                                           bridge_name=self._odl_client.VBRIDGE_NAME,
                                                           if_name=if_name,
                                                           node_id=switch_id,
                                                           phys_port_name=port_name)

                    self._odl_client.create_ctrl_flow(node_id=switch_id,
                                                      flow_id=if_name,
                                                      in_port=port["id"],
                                                      priority=self._odl_client.TRUNK_FLOW_PRIORITY)

                elif (switch_id, port_name) in self._resource_config.remove_trunk_ports:
                    if_name = self._convert_port_name(switch_id=switch_id, port_name=port_name)

                    self._odl_client.delete_interface_from_all_vbridges(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                                                        if_name=if_name)

                    self._odl_client.delete_ctrl_flow(node_id=switch_id, flow_id=if_name, raise_for_status=False)

        result = AutoloadDetailsBuilder(self._resource).autoload_details()
        self._log_autoload_details(result)

        return result

    def _log_autoload_details(self, autoload_details):
        """Log autoload details

        :param autoload_details:
        :return:
        """
        self._logger.debug("-------------------- <RESOURCES> ----------------------")
        for resource in autoload_details.resources:
            self._logger.debug(
                "{0:15}, {1:20}, {2}".format(resource.relative_address, resource.name, resource.unique_identifier))
        self._logger.debug("-------------------- </RESOURCES> ----------------------")

        self._logger.debug("-------------------- <ATTRIBUTES> ---------------------")
        for attribute in autoload_details.attributes:
            self._logger.debug("-- {0:15}, {1:60}, {2}".format(attribute.relative_address, attribute.attribute_name,
                                                               attribute.attribute_value))
        self._logger.debug("-------------------- </ATTRIBUTES> ---------------------")
