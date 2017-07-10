class ODLCreateRouteFlow(object):
    def __init__(self, odl_client, logger):
        self._odl_client = odl_client
        self._logger = logger

    def execute_flow(self, src_switch, src_port, dst_switch, dst_port):
        self._odl_client.create_route(src_switch, src_port, dst_switch, dst_port)
