import hashlib


def prepare_vtn_interface_name(switch_id, port_name):
    """Prepare VTN interface unique ID based on given Switch ID and Port name

    :param str switch_id:
    :param str port_name:
    :rtype: str
    """
    # max length for the interface name is 31 byte
    return hashlib.md5("{}_{}".format(switch_id, port_name)).hexdigest()[:31]
