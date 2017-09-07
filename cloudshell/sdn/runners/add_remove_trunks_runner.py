from abc import ABCMeta
from abc import abstractproperty


class SDNAddRemoveTrunksRunner(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger, resource_config):
        """

        :param logging.Logger logger:
        :param resource_config: cloudshell.sdn.config_attrs_structure.GenericSDNResource
        """
        self._logger = logger
        self._resource_config = resource_config

    @abstractproperty
    def add_trunks_flow(self):
        pass

    @abstractproperty
    def remove_trunks_flow(self):
        pass

    def add_trunks(self, ports):
        """

        :param ports:
        :return:
        """
        return self.add_trunks_flow.execute_flow(ports=ports)

    def remove_trunks(self, ports):
        """

        :param ports:
        :return:
        """
        return self.remove_trunks_flow.execute_flow(ports=ports)
