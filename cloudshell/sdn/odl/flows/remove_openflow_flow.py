class ODLRemoveOpenflowFlow(object):
    def __init__(self, odl_client, logger):
        """

        :param cloudshell.sdn.odl.client.ODLClient odl_client:
        :param logging.Logger logger:
        """
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, node_id, table_id, flow_id):
        """

        :param str node_id:
        :param int table_id:
        :param str flow_id:
        :return:
        """
        self._odl_client.delete_openflow(node_id=node_id, table_id=table_id, flow_id=flow_id)
