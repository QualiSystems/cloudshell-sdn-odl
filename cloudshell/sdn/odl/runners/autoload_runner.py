from cloudshell.sdn.runners.autoload_runner import SDNAutoloadRunner
from cloudshell.sdn.odl.flows.autoload_flow import ODLAutoloadFlow


class ODLAutoloadRunner(SDNAutoloadRunner):
    def __init__(self, odl_client, logger, api, resource_config):
        super(ODLAutoloadRunner, self).__init__(logger, api, resource_config)
        self._odl_client = odl_client

    @property
    def autoload_flow(self):
        return ODLAutoloadFlow(odl_client=self._odl_client,
                               logger=self._logger,
                               api=self._api,
                               resource_config=self._resource_config)
