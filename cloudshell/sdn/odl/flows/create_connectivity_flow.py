class ODLCreateConnectivityFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def _add_ports_to_vtn(self, tenant_name, vlan_id, ports):
        """

        :param tenant_name:
        :param vlan_id:
        :param ports:
        :return:
        """
        for node_id, interface in ports:
            phys_port_name = interface
            # todo: replace symbols in interface in one place
            interface = "{}_{}".format(node_id, interface).replace("-", "_").replace(":", "_")

            self._odl_client.create_interface(tenant_name=tenant_name,
                                              bridge_name=self._odl_client.VBRIDGE_NAME,
                                              if_name=interface)

            self._odl_client.map_port_to_interface(tenant_name=tenant_name,
                                                   bridge_name=self._odl_client.VBRIDGE_NAME,
                                                   if_name=interface,
                                                   node_id=node_id,
                                                   phys_port_name=phys_port_name,
                                                   vlan_id=vlan_id)

    def execute_flow(self, vlan_id, qnq, c_tag, access_ports):
        """

        :param int vlan_id:
        :param bool qnq:
        :param int c_tag:
        :param list[str] access_ports:
        :return:
        """
        tenant_name = "{}{}".format(self._odl_client.VTN_NAME_PREFIX, vlan_id)

        self._odl_client.create_vtn(tenant_name=tenant_name)
        self._odl_client.create_vbridge(tenant_name=tenant_name, bridge_name=self._odl_client.VBRIDGE_NAME)

        if qnq:
            self._add_ports_to_vtn(tenant_name=tenant_name,
                                   vlan_id=c_tag,
                                   ports=access_ports)
        else:
            self._add_ports_to_vtn(tenant_name=tenant_name,
                                   vlan_id=0,
                                   ports=access_ports)

            self._add_ports_to_vtn(tenant_name=tenant_name,
                                   vlan_id=vlan_id,
                                   ports=self._odl_client.get_trunk_ports())
