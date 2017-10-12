def get_vtn_interface_name(switch_id, port_name):
    """

    :param str switch_id:
    :param str port_name:
    :rtype: str
    """
    return "{}_{}".format(switch_id, port_name).replace("-", "_").replace(":", "_")
