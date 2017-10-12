from cloudshell.sdn.odl import converter


class ODLRemoveConnectivityFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, vlan_id, ports):
        """

        :param int vlan_id:
        :param list[str] ports:
        :return:
        """
        tenant_name = "{}{}".format(self._odl_client.VTN_NAME_PREFIX, vlan_id)

        for node_id, interface in ports:
            interface = converter.get_vtn_interface_name(node_id, interface)
            self._odl_client.delete_interface(tenant_name=tenant_name,
                                              bridge_name=self._odl_client.VBRIDGE_NAME,
                                              if_name=interface)

        if not self._odl_client.vtn_access_interfaces_exists(tenant_name=tenant_name,
                                                             bridge_name=self._odl_client.VBRIDGE_NAME):
            self._odl_client.delete_vtn(tenant_name)
