from abc import ABCMeta
from abc import abstractproperty


class SDNAutoloadRunner(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger, api, resource_config):
        """

        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :param cloudshell.devices.standards.sdn.configuration_attributes_structure.GenericSDNResource resource_config:
        """
        self._logger = logger
        self._api = api
        self._resource_config = resource_config

    @abstractproperty
    def autoload_flow(self):
        """Autoload flow property

        :return: AutoloadFlow object
        """
        pass

    def discover(self):
        """Read device structure and it's attributes (switches, ports)

        :return: AutoLoadDetails object
        """
        return self.autoload_flow.execute_flow()
