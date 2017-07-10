from abc import ABCMeta
from abc import abstractproperty


class SDNAutoloadRunner(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger, api, resource_config):
        self._logger = logger
        self._api = api
        self._resource_config = resource_config

    @abstractproperty
    def autoload_flow(self):
        """ Autoload flow property
        :return: AutoloadFlow object
        """
        pass

    def discover(self):
        """Enable and Disable SNMP communityon the device, Read it's structure and attributes: chassis, modules,
        submodules, ports, port-channels and power supplies
        :return: AutoLoadDetails object
        """
        return self.autoload_flow.execute_flow()
