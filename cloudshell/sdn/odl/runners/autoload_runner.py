from cloudshell.sdn.runners.autoload_runner import SDNAutoloadRunner
from cloudshell.sdn.odl.flows.autoload_flow import ODLAutoloadFlow


class ODLAutoloadRunner(SDNAutoloadRunner):
    def __init__(self, odl_client, logger, api, resource_config):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :param resource_config: cloudshell.sdn.config_attrs_structure.GenericSDNResource
        """
        super(ODLAutoloadRunner, self).__init__(logger, api, resource_config)
        self._odl_client = odl_client

    @property
    def autoload_flow(self):
        """

        :rtype: ODLAutoloadFlow
        """
        return ODLAutoloadFlow(odl_client=self._odl_client,
                               logger=self._logger,
                               api=self._api,
                               resource_config=self._resource_config)
