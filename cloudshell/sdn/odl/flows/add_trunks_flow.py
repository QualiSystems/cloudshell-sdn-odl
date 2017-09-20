class ODLAddTrunksFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, ports):
        """

        :param list[tuple[str, str]] ports:
        :return:
        """
        # todo: check if we need to add some prefix there !!!
        self._odl_client.create_vtn(tenant_name=self._odl_client.VTN_TRUNKS_NAME)
        self._odl_client.create_vbridge(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                        bridge_name=self._odl_client.VBRIDGE_NAME)

        for node_id, port_name in ports:
            phys_port_name = port_name
            port_name = "{}_{}".format(node_id, port_name).replace("-", "_").replace(":", "_")

            self._odl_client.create_interface(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                              bridge_name=self._odl_client.VBRIDGE_NAME,
                                              if_name=port_name)

            self._odl_client.map_port_to_interface(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                                   bridge_name=self._odl_client.VBRIDGE_NAME,
                                                   if_name=port_name,
                                                   node_id=node_id,
                                                   phys_port_name=phys_port_name)

            # todo: get in_port value "openflow:1:1", generate unique flow_id, move priotity to constant
            self._odl_client.create_ctrl_flow(node_id=node_id,
                                              table_id=0,
                                              flow_id=10,
                                              in_port="??????",
                                              priority=9)
