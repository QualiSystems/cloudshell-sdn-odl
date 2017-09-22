from cloudshell.devices.driver_helper import get_logger_with_thread_id
from cloudshell.devices.driver_helper import get_api
from cloudshell.sdn.resource_driver_interface import SDNResourceDriverInterface
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_utils import GlobalLock

from cloudshell.sdn.odl.runners import ODLAutoloadRunner
from cloudshell.sdn.odl.runners import ODLConnectivityRunner
from cloudshell.sdn.odl.runners import ODLAddRemoveTrunksRunner
from cloudshell.sdn.odl.runners import ODLRemoveOpenflowRunner
from cloudshell.sdn.config_attrs_structure import GenericSDNResource
from cloudshell.sdn.odl.client import ODLClient


class OpendaylightResourceDriver(ResourceDriverInterface, SDNResourceDriverInterface, GlobalLock):
    def initialize(self, context):
        """Initialize method

        :type context: cloudshell.shell.core.context.driver_context.InitCommandContext
        """
        return 'Finished initializing'

    def cleanup(self):
        pass

    def ApplyConnectivityChanges(self, context, request):
        """Create vlan and add or remove it to/from network interface

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param str request: request json
        :return:
        """
        logger = get_logger_with_thread_id(context)
        api = get_api(context)

        resource_config = GenericSDNResource.from_context(context)
        password = api.DecryptPassword(resource_config.password).Value

        odl_client = ODLClient(address=resource_config.address,
                               username=resource_config.user,
                               password=password,
                               scheme=resource_config.scheme,
                               port=int(resource_config.port))

        connectivity_runner = ODLConnectivityRunner(odl_client=odl_client,
                                                    logger=logger,
                                                    resource_config=resource_config)

        logger.info('Start applying connectivity changes, request is: {0}'.format(str(request)))
        result = connectivity_runner.apply_connectivity_changes(request=request)
        logger.info('Finished applying connectivity changes, response is: {0}'.format(str(result)))
        logger.info('Apply Connectivity changes completed')

        return result

    def _parse_ports(self, ports):
        """Parse ports string into the list

        :param str ports:
        :rtype: list[tuple[str, str]]
        """
        if ports == "":
            return []

        return [tuple(port_pair.split("::")) for port_pair in ports.strip(";").split(";")]

    def add_trunk_ports(self, context, ports):
        """Mark given ports as a trunk ports on the ODL

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param ports:
        :return:
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Create Trunk Ports command started')
        api = get_api(context)
        ports = self._parse_ports(ports)

        resource_config = GenericSDNResource.from_context(context)
        password = api.DecryptPassword(resource_config.password).Value

        odl_client = ODLClient(address=resource_config.address,
                               username=resource_config.user,
                               password=password,
                               scheme=resource_config.scheme,
                               port=int(resource_config.port))

        add_remove_trunks_runner = ODLAddRemoveTrunksRunner(odl_client=odl_client,
                                                            logger=logger,
                                                            resource_config=resource_config)

        result = add_remove_trunks_runner.add_trunks(ports=ports)
        logger.info('Create Trunk Ports command completed')

        return result

    def remove_trunk_ports(self, context, ports):
        """Unmark given ports as a trunk ports on the ODL

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param ports:
        :return:
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Remove Trunk Ports command started')
        api = get_api(context)
        ports = self._parse_ports(ports)

        resource_config = GenericSDNResource.from_context(context)
        password = api.DecryptPassword(resource_config.password).Value

        odl_client = ODLClient(address=resource_config.address,
                               username=resource_config.user,
                               password=password,
                               scheme=resource_config.scheme,
                               port=int(resource_config.port))

        add_remove_trunks_runner = ODLAddRemoveTrunksRunner(odl_client=odl_client,
                                                            logger=logger,
                                                            resource_config=resource_config)

        result = add_remove_trunks_runner.remove_trunks(ports=ports)
        logger.info('Remove Trunk Ports command completed')

        return result

    @GlobalLock.lock
    def get_inventory(self, context):
        """Return device structure with all standard attributes

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: response
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Autoload started')
        api = get_api(context)

        resource_config = GenericSDNResource.from_context(context)
        password = api.DecryptPassword(resource_config.password).Value

        odl_client = ODLClient(address=resource_config.address,
                               username=resource_config.user,
                               password=password,
                               scheme=resource_config.scheme,
                               port=int(resource_config.port))

        autoload_operations = ODLAutoloadRunner(odl_client=odl_client,
                                                logger=logger,
                                                api=api,
                                                resource_config=resource_config)

        response = autoload_operations.discover()
        logger.info('Autoload completed')

        return response

    @GlobalLock.lock
    def remove_openflow(self, context, node_id, table_id, flow_id):
        """Remove openflow from controller by its id

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :param str node_id:
        :param int table_id:
        :param str flow_id:
        :return: response
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Remove openflow command started')
        api = get_api(context)

        resource_config = GenericSDNResource.from_context(context)
        password = api.DecryptPassword(resource_config.password).Value

        odl_client = ODLClient(address=resource_config.address,
                               username=resource_config.user,
                               password=password,
                               scheme=resource_config.scheme,
                               port=int(resource_config.port))

        autoload_operations = ODLRemoveOpenflowRunner(odl_client=odl_client,
                                                      logger=logger)

        response = autoload_operations.remove_openflow(node_id=node_id, table_id=table_id, flow_id=flow_id)
        logger.info('Remove openflow command completed')

        return response
