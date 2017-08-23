import unittest

from cloudshell.sdn.odl.client import ODLClient


class TestODLClient(unittest.TestCase):
    def setUp(self):
        self.client = ODLClient(address="127.0.0.1", username="admin", password="admin", port=8181)

    def test_empty(self):
        pass
