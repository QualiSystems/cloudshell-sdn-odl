from cloudshell.sdn.runners import SDNAddRemoveTrunksRunner
from cloudshell.sdn.odl.flows import ODLAddTrunksFlow
from cloudshell.sdn.odl.flows import ODLRemoveTrunksFlow


class ODLAddRemoveTrunksRunner(SDNAddRemoveTrunksRunner):
    def __init__(self, odl_client, logger, resource_config):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        :param resource_config: cloudshell.sdn.config_attrs_structure.GenericSDNResource
        """
        super(ODLAddRemoveTrunksRunner, self).__init__(logger, resource_config)
        self._odl_client = odl_client

    @property
    def add_trunks_flow(self):
        """

        :rtype: ODLAddTrunksFlow
        """
        return ODLAddTrunksFlow(odl_client=self._odl_client,
                                logger=self._logger)

    @property
    def remove_trunks_flow(self):
        """

        :rtype: ODLRemoveTrunksFlow
        """
        return ODLRemoveTrunksFlow(odl_client=self._odl_client,
                                   logger=self._logger)
