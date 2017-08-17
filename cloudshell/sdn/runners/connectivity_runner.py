import jsonpickle

from abc import abstractproperty

from cloudshell.core.driver_response import DriverResponse
from cloudshell.core.driver_response_root import DriverResponseRoot
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivityErrorResponse, \
    ConnectivitySuccessResponse
from cloudshell.devices.json_request_helper import JsonRequestDeserializer
from cloudshell.devices.networking_utils import serialize_to_json
from cloudshell.devices.runners.interfaces.connectivity_runner_interface import ConnectivityOperationsInterface


class SDNConnectivityRunner(ConnectivityOperationsInterface):
    APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST = ["type", "actionId",
                                                                 ("connectionParams", "mode"),
                                                                 ("actionTarget", "fullAddress")]

    def __init__(self, logger, resource_config):
        self._logger = logger
        self._resource_config = resource_config

    @abstractproperty
    def create_route_flow(self):
        pass

    @abstractproperty
    def delete_route_flow(self):
        pass

    def _parse_port(self, full_addr):
        full_addr_parts = full_addr.split("/")
        port = full_addr_parts[-1]
        return port.replace("P", "", 1)

    def _parse_switch(self, full_name):
        full_addr_parts = full_name.split("/")
        switch_id = full_addr_parts[-2]
        switch_id = switch_id.replace("CH", "", 1)
        switch_id = switch_id.replace("openflow_", "openflow:")
        return switch_id

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
            vlan_id = action.connectionParams.vlanId

            if action.type == "setVlan":
                connects.setdefault(vlan_id, []).append(action)

            elif action.type == "removeVlan":
                disconnects.setdefault(vlan_id, []).append(action)

        for actions in connects.itervalues():
            if len(actions) != 2:
                action = actions[0]
                action_result = ConnectivityErrorResponse(action=action,
                                                          error_string="Can't find another switch to connect to")
                request_result.append(action_result)
                continue

            src_action, dst_action = actions
            src_port = self._parse_port(src_action.actionTarget.fullAddress)
            src_switch_id = self._parse_switch(src_action.actionTarget.fullName)

            dst_port = self._parse_port(dst_action.actionTarget.fullAddress)
            dst_switch_id = self._parse_switch(dst_action.actionTarget.fullName)

            try:
                self.create_route_flow.execute_flow(src_switch=src_switch_id,
                                                    src_port=src_port,
                                                    dst_switch=dst_switch_id,
                                                    dst_port=dst_port)
            except Exception:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivityErrorResponse(
                        action=action,
                        error_string="Failed to connect {}".format(full_name))

                    request_result.append(action_result)

                self._logger.exception("Failed to process actions: {}, {}".format(src_action.actionId,
                                                                                  dst_action.actionId))

            else:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivitySuccessResponse(
                        action=action,
                        result_string="Successfully connected {}".format(full_name))

                    request_result.append(action_result)

        # todo: remove duplicated code
        for actions in disconnects.itervalues():
            if len(actions) != 2:
                action = actions[0]
                action_result = ConnectivityErrorResponse(action=action,
                                                          error_string="Can't find another switch to disconnect from")
                request_result.append(action_result)
                continue

            src_action, dst_action = actions
            src_port = self._parse_port(src_action.actionTarget.fullAddress)
            src_switch_id = self._parse_switch(src_action.actionTarget.fullName)

            dst_port = self._parse_port(dst_action.actionTarget.fullAddress)
            dst_switch_id = self._parse_switch(dst_action.actionTarget.fullName)

            try:
                self.delete_route_flow.execute_flow(src_switch=src_switch_id,
                                                    src_port=src_port,
                                                    dst_switch=dst_switch_id,
                                                    dst_port=dst_port)

                self._logger.exception("Failed to process actions: {}, {}".format(src_action.actionId,
                                                                                  dst_action.actionId))
            except Exception:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivityErrorResponse(
                        action=action,
                        error_string="Failed to disconnect {}".format(full_name))

                    request_result.append(action_result)
            else:
                for action in actions:
                    full_name = action.actionTarget.fullName
                    action_result = ConnectivitySuccessResponse(
                        action=action,
                        result_string="Successfully disconnected {}".format(full_name))

                    request_result.append(action_result)

        driver_response.actionResults = request_result
        driver_response_root.driverResponse = driver_response

        return serialize_to_json(driver_response_root).replace("[true]", "true")
