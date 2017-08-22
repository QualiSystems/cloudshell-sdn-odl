class ODLRemoveConnectivityFlow(object):
    def __init__(self, odl_client, logger):
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, vlan_id, ports):
        tenant_name = "{}{}".format(self._odl_client.VTN_NAME_PREFIX, vlan_id)
        bridge_name = "{}{}".format(self._odl_client.VBRIDGE_NAME_PREFIX, vlan_id)

        for node_id, interface in ports:
            interface = "{}_{}".format(node_id, interface).replace("-", "_").replace(":", "_")
            self._odl_client.delete_interface(tenant_name=tenant_name, bridge_name=bridge_name, if_name=interface)

        if not self._odl_client.vtn_access_interfaces_exists(tenant_name=tenant_name, bridge_name=bridge_name):
            self._odl_client.delete_vtn(tenant_name)
