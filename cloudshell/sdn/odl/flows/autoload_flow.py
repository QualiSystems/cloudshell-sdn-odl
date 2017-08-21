from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.networking.autoload_structure import GenericResource, GenericChassis
from cloudshell.devices.standards.networking.autoload_structure import GenericPort


class SDNODLController(GenericResource):
    RESOURCE_MODEL = "SDN ODL Controller"


class OpenVSwitchChassis(GenericChassis):
    RESOURCE_MODEL = "OpenVSwitch"


class ODLAutoloadFlow(object):
    def __init__(self, odl_client, logger, api, resource_config):
        self._odl_client = odl_client
        self._logger = logger
        self._api = api
        self._resource_config = resource_config
        self._resources = []
        self._attributes = []

        self._resource = SDNODLController(shell_name="",
                                          shell_type="CS_Controller",
                                          name="ODL Controller",
                                          unique_id="ODL Controller")

    def _set_controller_details(self):
        """ Get root element attributes """
        self._resource.contact_name = ""
        self._resource.system_name = ""
        self._resource.location = ""
        self._resource.os_version = ""
        self._resource.model = ""
        self._resource.vendor = "Opendaylight"

    def execute_flow(self):
        self._set_controller_details()
        # ports used in connections between switches
        used_ports = []
        topo = self._odl_client.get_topology()
        switch_ids = self._odl_client.get_switches()

        for link in topo.get("link", []):
            tp = link["destination"]["dest-node"]
            op = link["source"]["source-node"]
            if tp in switch_ids and op in switch_ids:
                used_ports.append(link["source"]["source-tp"])
                used_ports.append(link["destination"]["dest-tp"])

        for switch_id in self._odl_client.get_leaf_switches():
            sw_resource = OpenVSwitchChassis(shell_name="",
                                             name=switch_id.replace(":", "_"),
                                             unique_id=switch_id.split(":")[-1])

            switch = self._odl_client.get_switch(switch_id)
            sw_ = switch_id.split(":")[-1]

            self._resource.add_sub_resource(sw_, sw_resource)

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
                unique_id = "{}.{}".format(sw_, port_no)

                port_object = GenericPort(shell_name="",
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
                # 'module_model': '',
                # 'version': '',
                # 'serial_number': switch_index

                # switch_name = 'SDN Switch {0}'.format(switch)
                # model = 'OpenVSwitch'
                # todo: check if we can create some specific classes for the SDN resources
                # switch_object = Module(name=switch_name,
                #                        model=model,
                #                        relative_path=switch)
                # self._add_resource(switch_object)

        result = AutoloadDetailsBuilder(self._resource).autoload_details()
        self._log_autoload_details(result)
        return result

    def _log_autoload_details(self, autoload_details):
        """
        Logging autoload details
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
