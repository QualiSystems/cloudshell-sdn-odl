class ODLCreateConnectivityFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, vlan_id, access_ports, trunk_ports):
        """

        :param int vlan_id:
        :param list[str] access_ports:
        :param list[str] trunk_ports:
        :return:
        """
        tenant_name = "{}{}".format(self._odl_client.VTN_NAME_PREFIX, vlan_id)
        bridge_name = "{}{}".format(self._odl_client.VBRIDGE_NAME_PREFIX, vlan_id)

        self._odl_client.create_vtn(tenant_name=tenant_name)
        self._odl_client.create_vbridge(tenant_name=tenant_name, bridge_name=bridge_name)

        for node_id, interface in self._odl_client.get_leaf_interfaces():
            phys_port_name = interface
            # todo: replace symbols in interface in one place
            interface = "{}_{}".format(node_id, interface).replace("-", "_").replace(":", "_")

            old_iface = self._odl_client.get_interface(tenant_name=tenant_name,
                                                       bridge_name=bridge_name,
                                                       if_name=interface)

            # we don't need to override existing access ports
            if old_iface is not None and old_iface.get("port-map-config", {}).get("vlan-id") == 0:
                continue

            if (node_id, phys_port_name) in access_ports:
                vlan = 0
            else:
                vlan = vlan_id

            self._odl_client.create_interface(tenant_name=tenant_name, bridge_name=bridge_name, if_name=interface)
            self._odl_client.map_port_to_interface(tenant_name=tenant_name,
                                                   bridge_name=bridge_name,
                                                   if_name=interface,
                                                   node_id=node_id,
                                                   phys_port_name=phys_port_name,
                                                   vlan_id=vlan)
