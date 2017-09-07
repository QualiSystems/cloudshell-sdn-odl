class ODLRemoveTrunksFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, ports):
        """

        :param dict[str, list] ports:
        :return:
        """
        # todo: check if we need to add some prefix there !!!
        self._odl_client.create_vtn(tenant_name=self._odl_client.VTN_TRUNKS_NAME)
        self._odl_client.create_vbridge(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                        bridge_name=self._odl_client.VBRIDGE_NAME)

        for node_id, ports_names in ports.iteritems():
            for port_name in ports_names:
                port_name = "{}_{}".format(node_id, port_name).replace("-", "_").replace(":", "_")

                self._odl_client.delete_interface(tenant_name=self._odl_client.VTN_TRUNKS_NAME,
                                                  bridge_name=self._odl_client.VBRIDGE_NAME,
                                                  if_name=port_name)
