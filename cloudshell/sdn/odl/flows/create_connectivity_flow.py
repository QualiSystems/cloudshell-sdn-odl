class ODLCreateConnectivityFlow(object):
    def __init__(self, odl_client, logger):
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, vlan_id, access_ports, trunk_ports):
        """

        :param vlan_id:
        :param access_ports:
        :param trunk_ports:
        :return:
        """
        tenant_name = "{}{}".format(self._odl_client.VTN_NAME_PREFIX, vlan_id)
        bridge_name = "{}{}".format(self._odl_client.VBRIDGE_NAME_PREFIX, vlan_id)

        self._odl_client.create_vtn(tenant_name=tenant_name)
        self._odl_client.create_vbridge(tenant_name=tenant_name, bridge_name=bridge_name)

        for node_id, interface in access_ports:
            phys_port_name = interface
            interface = interface.replace("-", "_")
            self._odl_client.create_interface(tenant_name=tenant_name, bridge_name=bridge_name, if_name=interface)

            self._odl_client.map_port_to_interface(tenant_name=tenant_name,
                                                   bridge_name=bridge_name,
                                                   if_name=interface,
                                                   node_id=node_id,
                                                   phys_port_name=phys_port_name,
                                                   vlan_id=0)

        for node_id, interface in trunk_ports:
            phys_port_name = interface
            interface = interface.replace("-", "_")
            self._odl_client.create_interface(tenant_name=tenant_name, bridge_name=bridge_name, if_name=interface)

            self._odl_client.map_port_to_interface(tenant_name=tenant_name,
                                                   bridge_name=bridge_name,
                                                   if_name=interface,
                                                   node_id=node_id,
                                                   phys_port_name=phys_port_name,
                                                   vlan_id=vlan_id)
