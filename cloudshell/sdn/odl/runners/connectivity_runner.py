from cloudshell.sdn.odl.flows.create_connectivity_flow import ODLCreateConnectivityFlow
from cloudshell.sdn.odl.flows.remove_connectivity_flow import ODLRemoveConnectivityFlow
from cloudshell.sdn.runners.connectivity_runner import SDNConnectivityRunner


class ODLConnectivityRunner(SDNConnectivityRunner):
    def __init__(self, odl_client, logger, resource_config):
        super(ODLConnectivityRunner, self).__init__(logger, resource_config)
        self._odl_client = odl_client

    @property
    def create_connectivity_flow(self):
        return ODLCreateConnectivityFlow(odl_client=self._odl_client, logger=self._logger)

    @property
    def remove_connectivity_flow(self):
        return ODLRemoveConnectivityFlow(odl_client=self._odl_client, logger=self._logger)
