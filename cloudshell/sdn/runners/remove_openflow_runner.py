from abc import ABCMeta
from abc import abstractproperty


class SDNRemoveOpenflowRunner(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger):
        """

        :param logging.Logger logger:
        """
        self._logger = logger

    @abstractproperty
    def remove_openflow_flow(self):
        pass

    def remove_openflow(self, node_id, table_id, flow_id):
        """

        :param str node_id:
        :param int table_id:
        :param str flow_id:
        :return:
        """
        return self.remove_openflow_flow.execute_flow(node_id=node_id, table_id=table_id, flow_id=flow_id)
