from cloudshell.sdn.odl.flows import ODLCreateConnectivityFlow
from cloudshell.sdn.odl.flows import ODLRemoveConnectivityFlow
from cloudshell.sdn.runners import SDNConnectivityRunner


class ODLConnectivityRunner(SDNConnectivityRunner):
    def __init__(self, odl_client, logger, resource_config):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        :param cloudshell.devices.standards.sdn.configuration_attributes_structure.GenericSDNResource resource_config:
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
