from cloudshell.sdn.odl.flows import ODLCreateConnectivityFlow
from cloudshell.sdn.odl.flows import ODLRemoveConnectivityFlow
from cloudshell.sdn.runners import SDNConnectivityRunner


class ODLConnectivityRunner(SDNConnectivityRunner):
    def __init__(self, odl_client, logger, resource_config):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        :param resource_config: cloudshell.sdn.config_attrs_structure.GenericSDNResource
        """
        super(ODLConnectivityRunner, self).__init__(logger, resource_config)
        self._odl_client = odl_client

    @property
    def create_connectivity_flow(self):
        """

        :rtype: ODLCreateConnectivityFlow
        """
        return ODLCreateConnectivityFlow(odl_client=self._odl_client, logger=self._logger)

    @property
    def remove_connectivity_flow(self):
        """

        :rtype: ODLRemoveConnectivityFlow
        """
        return ODLRemoveConnectivityFlow(odl_client=self._odl_client, logger=self._logger)
