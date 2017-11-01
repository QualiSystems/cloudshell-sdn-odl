from abc import ABCMeta
from abc import abstractproperty

import jsonpickle

from cloudshell.core.driver_response import DriverResponse
from cloudshell.core.driver_response_root import DriverResponseRoot
from cloudshell.devices.json_request_helper import JsonRequestDeserializer
from cloudshell.devices.networking_utils import serialize_to_json
from cloudshell.devices.networking_utils import validate_vlan_number
from cloudshell.devices.runners.interfaces.connectivity_runner_interface import ConnectivityOperationsInterface
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivityErrorResponse
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivitySuccessResponse


class SDNConnectivityRunner(ConnectivityOperationsInterface):
    __metaclass__ = ABCMeta

    APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST = ["type", "actionId",
                                                                 ("connectionParams", "mode"),
                                                                 ("actionTarget", "fullName")]

    def __init__(self, logger, resource_config):
        """

        :param logging.Logger logger:
        :param cloudshell.devices.standards.sdn.configuration_attributes_structure.GenericSDNResource resource_config:
        """
        self._logger = logger
        self._resource_config = resource_config

    @abstractproperty
    def create_connectivity_flow(self):
        pass

    @abstractproperty
    def remove_connectivity_flow(self):
        pass

    def _parse_port(self, full_name):
        """Parse port name from the resource full name

        :param str full_name:
        :rtype: str
        """
        port_name = full_name.split("/")[-1]
        return port_name.replace("_", "/")

    def _parse_switch(self, full_name):
        """Parse switch name from the resource full name

        :param str full_name:
        :rtype: str
        """
        return full_name.split("/")[-2]

    def _get_vlan_list(self, vlan_str):
        """Get VLAN list from the input string

        :param str vlan_str:
        :rtype: list[str]
        """
        result = set()

        for splitted_vlan in vlan_str.split(","):
            if "-" not in splitted_vlan:
                if validate_vlan_number(splitted_vlan):
                    result.add(int(splitted_vlan))
                else:
                    raise Exception(self.__class__.__name__, "Wrong VLAN number detected {}".format(splitted_vlan))
            else:
                start, end = map(int, splitted_vlan.split("-"))
                if validate_vlan_number(start) and validate_vlan_number(end):
                    if start > end:
                        start, end = end, start
                    for vlan in range(start, end + 1):
                        result.add(vlan)
                else:
                    raise Exception(self.__class__.__name__, "Wrong VLANs range detected {}".format(vlan_str))

        return map(str, list(result))

    def _get_json_request_deserializer(self, request):
        """Convert and validate JSON request into JsonRequestDeserializer object

        :param str request: json with all required action to configure or remove VLANs from certain port
        :rtype: JsonRequestDeserializer
        """
        if request is None or request == "":
            raise Exception(self.__class__.__name__, "request is None or empty")

        holder = JsonRequestDeserializer(jsonpickle.decode(request))

        if not holder or not hasattr(holder, "driverRequest"):
            raise Exception(self.__class__.__name__, "Deserialized request is None or empty")

        return holder

    def _get_combined_actions(self, request_deserializer):
        """Combine actions by action type and VLAN number

        :param JsonRequestDeserializer request_deserializer:
        :rtype: tuple[dict]
        """
        connects = {}
        disconnects = {}

        for action in request_deserializer.driverRequest.actions:
            for vlan_id in self._get_vlan_list(action.connectionParams.vlanId):
                if action.type == "setVlan":
                    connects.setdefault(vlan_id, []).append(action)

                elif action.type == "removeVlan":
                    disconnects.setdefault(vlan_id, []).append(action)

        return connects, disconnects

    def _process_set_vlan_actions(self, actions):
        """Process set VLAN actions and return request results

        :param list actions:
        :rtype: list[ConnectivitySuccessResponse]
        """
        request_result = []

        for vlan_id, actions in actions.iteritems():
            access_ports = []
            trunk_ports = []

            for action in actions:
                phys_port_name = self._parse_port(full_name=action.actionTarget.fullName)
                switch_id = self._parse_switch(full_name=action.actionTarget.fullName)

                if action.connectionParams.mode.lower() == "access":
                    access_ports.append((switch_id, phys_port_name))
                else:
                    trunk_ports.append((switch_id, phys_port_name))

            qnq = False
            c_tag = 0

            for attribute in action.connectionParams.vlanServiceAttributes:
                if attribute.attributeName.lower() == "qnq" and attribute.attributeValue.lower() == "true":
                    qnq = True
                if attribute.attributeName.lower() == "ctag":
                    c_tag = attribute.attributeValue

            try:
                self.create_connectivity_flow.execute_flow(vlan_id=vlan_id,
                                                           qnq=qnq,
                                                           c_tag=c_tag,
                                                           access_ports=access_ports)
            except Exception:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivityErrorResponse(
                        action=action,
                        error_string="Failed to connect {}".format(full_name))

                    request_result.append(action_result)
                    self._logger.exception("Failed to process action: {}".format(action.actionId))
            else:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivitySuccessResponse(
                        action=action,
                        result_string="Successfully connected {}".format(full_name))

                    request_result.append(action_result)
                    self._logger.info("Successfully processed action: {}".format(action.actionId))

        return request_result

    def _process_remove_vlan_actions(self, actions):
        """Process remove VLAN actions and return request results

        :param list actions:
        :rtype: list[ConnectivitySuccessResponse]
        """
        request_result = []

        for vlan_id, actions in actions.iteritems():
            ports = []

            for action in actions:
                phys_port_name = self._parse_port(full_name=action.actionTarget.fullName)
                switch_id = self._parse_switch(full_name=action.actionTarget.fullName)
                ports.append((switch_id, phys_port_name))

            try:
                self.remove_connectivity_flow.execute_flow(vlan_id=vlan_id,
                                                           ports=ports)
            except Exception:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivityErrorResponse(
                        action=action,
                        error_string="Failed to disconnect {}".format(full_name))

                    request_result.append(action_result)
                    self._logger.exception("Failed to process action: {}".format(action.actionId))
            else:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivitySuccessResponse(
                        action=action,
                        result_string="Successfully disconnected {}".format(full_name))

                    request_result.append(action_result)
                    self._logger.info("Successfully processed action: {}".format(action.actionId))

        return request_result

    def apply_connectivity_changes(self, request):
        """Handle apply connectivity changes request json, trigger add or remove VLAN methods,

        get response from them and create json response
        :param str request: json with all required action to configure or remove VLANs from certain port
        :return Serialized DriverResponseRoot to json
        :rtype: json
        """
        driver_response = DriverResponse()
        driver_response_root = DriverResponseRoot()

        request_deserializer = self._get_json_request_deserializer(request)
        set_vlan_actions, remove_vlan_actions = self._get_combined_actions(request_deserializer)

        actions_result = (self._process_set_vlan_actions(set_vlan_actions)
                          + self._process_remove_vlan_actions(remove_vlan_actions))

        driver_response.actionResults = actions_result
        driver_response_root.driverResponse = driver_response

        return serialize_to_json(driver_response_root).replace("[true]", "true")
