from threading import Thread

from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails
from driver import OpendaylightResourceDriver
from mock import patch

request = """{"driverRequest": {"actions": [{"connectionId": "09faa654-9189-4b99-973c-01f5222f1db9",
                                              "connectionParams": {"vlanId": "300", "mode": "Access",
                                                                   "vlanServiceAttributes": [
                                                                       {"attributeName": "Allocation Ranges",
                                                                        "attributeValue": "2-4094",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Isolation Level",
                                                                        "attributeValue": "Exclusive",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Access Mode",
                                                                        "attributeValue": "Access",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "VLAN ID",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Pool Name",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Virtual Network",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Default VLAN",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "QnQ",
                                                                        "attributeValue": "False",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "CTag", "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"}],
                                                                   "type": "setVlanParameter"}, "connectorAttributes": [
            {"attributeName": "Selected Network", "attributeValue": "2", "type": "connectorAttribute"}],
                                              "actionId": "09faa654-9189-4b99-973c-01f5222f1db9_103b5867-caec-4c78-a891-90ae750098c4",
                                              "actionTarget": {"fullName": "SDN ODL2/openflow-1/s1-eth2",
                                                               "fullAddress": "192.168.42.157/CH2/P1",
                                                               "type": "actionTarget"}, "customActionAttributes": [],
                                              "type": "setVlan"},
                                             {"connectionId": "09faa654-9189-4b99-973c-01f5222f1db9",
                                              "connectionParams": {"vlanId": "300", "mode": "Access",
                                                                   "vlanServiceAttributes": [
                                                                       {"attributeName": "Allocation Ranges",
                                                                        "attributeValue": "2-4094",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Isolation Level",
                                                                        "attributeValue": "Exclusive",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Access Mode",
                                                                        "attributeValue": "Access",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "VLAN ID",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Pool Name",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Virtual Network",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "Default VLAN",
                                                                        "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "QnQ",
                                                                        "attributeValue": "False",
                                                                        "type": "vlanServiceAttribute"},
                                                                       {"attributeName": "CTag", "attributeValue": "",
                                                                        "type": "vlanServiceAttribute"}],
                                                                   "type": "setVlanParameter"}, "connectorAttributes": [
                                                 {"attributeName": "Selected Network", "attributeValue": "2",
                                                  "type": "connectorAttribute"}],
                                              "actionId": "09faa654-9189-4b99-973c-01f5222f1db9_884f8bbc-7984-4db6-ae10-574cfa7b31b2",
                                              "actionTarget": {"fullName": "SDN ODL2/openflow-1/s1-eth1",
                                                               "fullAddress": "192.168.42.157/CH2/P2",
                                                               "type": "actionTarget"}, "customActionAttributes": [],
                                              "type": "setVlan"}]}}"""


address = 'localhost'
# address = '192.168.73.49'
# address = '192.168.73.20'
# address = '192.168.73.56'

# address = '172.29.168.46'
# address = '172.29.168.56'
user = 'admin'
# user = 'admin'
# password = 'P0G8gOpDHL0c52ROLdsaVQ=='
# password = 'Password1'
password = 'admin'
port = 8181
enable_password = 'NuCpFxP8cJMCic8ePJokug=='
auth_key = 'h8WRxvHoWkmH8rLQz+Z/pg=='
api_port = 8029

context = ResourceCommandContext()
context.resource = ResourceContextDetails()
context.resource.name = 'dsada'
context.resource.fullname = 'TestAireOS'
context.reservation = ReservationContextDetails()
context.reservation.reservation_id = 'test_id'
context.resource.attributes = {}
context.resource.attributes['User'] = user
context.resource.attributes['Password'] = password
context.resource.attributes['host'] = address
context.resource.attributes['Enable Password'] = enable_password
context.resource.attributes['Port'] = port
# context.resource.attributes['Backup Location'] = 'tftp://172.25.10.96/AireOS_test'
context.resource.attributes['Backup Location'] = 'ftp://junos:junos@192.168.85.23'
context.resource.address = address
# context.connectivity = ConnectivityContext()
# context.connectivity.admin_auth_token = auth_key
# context.connectivity.server_address = '10.5.1.2'
# context.connectivity.cloudshell_api_port = api_port
context.resource.attributes['SNMP Version'] = '2'
context.resource.attributes['SNMP Read Community'] = 'public'
context.resource.attributes['CLI Connection Type'] = 'ssh'
context.resource.attributes['Enable SNMP'] = 'False'
context.resource.attributes['Disable SNMP'] = 'False'
context.resource.attributes['CLI Connection Type'] = 'ssh'
context.resource.attributes['Sessions Concurrency Limit'] = '1'


class MyThread(Thread):
    def __del__(self):
        print('{} deleted'.format(self.name))


if __name__ == '__main__':
    driver = OpendaylightResourceDriver()
    driver.initialize(context)
    # driver = JunosResourceDriver()

    # driver.save(context, '','')
    # print(driver.send_custom_command(context, 'show run'))
    # print(driver.send_custom_command(context, 'show interfaces'))
    # print(driver.update_firmware(context, 'tftp://yar:pass@10.2.5.6:8435/test_path/test_file/323', ''))
    with patch('driver.get_api') as get_api:
        get_api.return_value = type('api', (object,), {
            'DecryptPassword': lambda self, pw: type('Password', (object,), {'Value': pw})()})()
        # out = driver.get_inventory(context)

        # driver.ApplyConnectivityChanges(context=context, request=request)
        # print(inv)
        # out = driver.save(context, '', '', None)
        # out = driver.restore(context, 'ftp://junos:junos@192.168.85.23/dsada-running-040117-144312', None, None, None)
        # out = driver.load_firmware(context, 'dsadas', None)
        # out = driver.get_inventory(context)>
        out = driver.ApplyConnectivityChanges(context, request)
        print(out)
