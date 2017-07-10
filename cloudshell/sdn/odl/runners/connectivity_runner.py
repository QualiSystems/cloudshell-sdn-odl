from cloudshell.sdn.runners.connectivity_runner import SDNConnectivityRunner
from cloudshell.sdn.odl.flows.create_route_flow import ODLCreateRouteFlow
from cloudshell.sdn.odl.flows.delete_route_flow import ODLDeleteRouteFlow


class ODLConnectivityRunner(SDNConnectivityRunner):
    def __init__(self, odl_client, logger, resource_config):
        super(ODLConnectivityRunner, self).__init__(logger, resource_config)
        self._odl_client = odl_client

    @property
    def create_route_flow(self):
        return ODLCreateRouteFlow(odl_client=self._odl_client, logger=self._logger)

    @property
    def delete_route_flow(self):
        return ODLDeleteRouteFlow(odl_client=self._odl_client, logger=self._logger)
