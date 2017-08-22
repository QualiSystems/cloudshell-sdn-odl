import jsonpickle

from abc import abstractproperty

from cloudshell.core.driver_response import DriverResponse
from cloudshell.core.driver_response_root import DriverResponseRoot
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivityErrorResponse, \
    ConnectivitySuccessResponse
from cloudshell.devices.json_request_helper import JsonRequestDeserializer
from cloudshell.devices.networking_utils import serialize_to_json
from cloudshell.devices.networking_utils import validate_vlan_number
from cloudshell.devices.runners.interfaces.connectivity_runner_interface import ConnectivityOperationsInterface


class SDNConnectivityRunner(ConnectivityOperationsInterface):
    APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST = ["type", "actionId",
                                                                 ("connectionParams", "mode"),
                                                                 ("actionTarget", "fullAddress")]

    def __init__(self, logger, resource_config):
        self._logger = logger
        self._resource_config = resource_config

    @abstractproperty
    def create_connectivity_flow(self):
        pass

    @abstractproperty
    def remove_connectivity_flow(self):
        pass

    def _parse_port(self, full_addr):
        full_addr_parts = full_addr.split("/")
        port = full_addr_parts[-1]
        return port.replace("P", "", 1)

    def _parse_port_name(self, full_name):
        return full_name.split("/")[-1]

    def _parse_switch(self, full_name):
        full_addr_parts = full_name.split("/")
        switch_id = full_addr_parts[-2]
        switch_id = switch_id.replace("CH", "", 1)
        # todo: move ":" symbol replacing to one place
        switch_id = switch_id.replace("openflow_", "openflow:")
        return switch_id

    def _get_vlan_list(self, vlan_str):
        """Get VLAN list from input string

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

    def apply_connectivity_changes(self, request):
        """ Handle apply connectivity changes request json, trigger add or remove vlan methods,
        get responce from them and create json response

        :param request: json with all required action to configure or remove vlans from certain port
        :return Serialized DriverResponseRoot to json
        :rtype json
        """
        if request is None or request == "":
            raise Exception(self.__class__.__name__, "request is None or empty")

        holder = JsonRequestDeserializer(jsonpickle.decode(request))

        if not holder or not hasattr(holder, "driverRequest"):
            raise Exception(self.__class__.__name__, "Deserialized request is None or empty")

        driver_response = DriverResponse()
        driver_response_root = DriverResponseRoot()
        connects = {}
        disconnects = {}
        request_result = []

        for action in holder.driverRequest.actions:
            for vlan_id in self._get_vlan_list(action.connectionParams.vlanId):
                if action.type == "setVlan":
                    connects.setdefault(vlan_id, []).append(action)

                elif action.type == "removeVlan":
                    disconnects.setdefault(vlan_id, []).append(action)

        for vlan_id, actions in connects.iteritems():
            access_ports = []
            trunk_ports = []

            for action in actions:
                phys_port_name = self._parse_port_name(full_name=action.actionTarget.fullName)
                switch_id = self._parse_switch(full_name=action.actionTarget.fullName)

                if action.connectionParams.mode.lower() == "access":
                    access_ports.append((switch_id, phys_port_name))
                else:
                    trunk_ports.append((switch_id, phys_port_name))

            try:
                self.create_connectivity_flow.execute_flow(vlan_id=vlan_id,
                                                           access_ports=access_ports,
                                                           trunk_ports=trunk_ports)
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

        for vlan_id, actions in disconnects.iteritems():
            ports = []

            for action in actions:
                phys_port_name = self._parse_port_name(full_name=action.actionTarget.fullName)
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

        driver_response.actionResults = request_result
        driver_response_root.driverResponse = driver_response

        return serialize_to_json(driver_response_root).replace("[true]", "true")
