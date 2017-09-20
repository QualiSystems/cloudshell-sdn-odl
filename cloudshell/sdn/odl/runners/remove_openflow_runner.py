from cloudshell.sdn.odl.flows import ODLRemoveOpenflowFlow
from cloudshell.sdn.runners import SDNRemoveOpenflowRunner


class ODLRemoveOpenflowRunner(SDNRemoveOpenflowRunner):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        super(ODLRemoveOpenflowRunner, self).__init__(logger)
        self._odl_client = odl_client

    @property
    def remove_openflow_flow(self):
        """

        :rtype: ODLRemoveOpenflowFlow
        """
        return ODLRemoveOpenflowFlow(odl_client=self._odl_client, logger=self._logger)
