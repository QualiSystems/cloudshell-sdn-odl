from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.standards.networking.autoload_structure import GenericResource
from cloudshell.devices.standards.networking.autoload_structure import GenericModule
from cloudshell.devices.standards.networking.autoload_structure import GenericPort


class ODLAutoloadFlow(object):
    def __init__(self, odl_client, logger, api, resource_config):
        self._odl_client = odl_client
        self._logger = logger
        self._api = api
        self._resource_config = resource_config
        self._resources = []
        self._attributes = []

        self._resource = GenericResource(shell_name=None,
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

        for switch_id in self._odl_client.get_leaf_switches():
            sw_resource = GenericModule(shell_name=None,
                                        name="Module {}".format(switch_id),
                                        unique_id="{}".format(switch_id.split(":")[-1]))

            switch = self._odl_client.get_switch(switch_id)
            sw_ = switch_id.split(":")[-1]
            self._resource.add_sub_resource(sw_, sw_resource)

            for port in switch["node-connector"]:
                port_name = port["flow-node-inventory:name"]

                # ignore loopback interface
                if "local" in port["id"].lower():
                    continue

                # todo: delete port which is connected to another switch

                port_no = port["flow-node-inventory:port-number"]
                mac_addr = port["flow-node-inventory:hardware-address"]
                unique_id = "{}.{}".format(sw_, port_no)

                port_object = GenericPort(shell_name=None,
                                          name=port_name,
                                          unique_id=unique_id)

                port_object.port_description = ""
                port_object.l2_protocol_type = ""
                port_object.mac_address = mac_addr
                port_object.mtu = ""
                port_object.bandwidth = ""
                port_object.ipv4_address = ""
                port_object.ipv6_address = ""
                port_object.duplex = ""
                port_object.auto_negotiation = ""
                port_object.adjacent = ""

                self._resource.add_sub_resource(port_no, port_object)
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

        return AutoloadDetailsBuilder(self._resource).autoload_details()
