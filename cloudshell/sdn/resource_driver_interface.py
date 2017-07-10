from abc import ABCMeta
from abc import abstractmethod


class SDNResourceDriverInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_inventory(self, context):
        pass

    @abstractmethod
    def ApplyConnectivityChanges(self, context, request):
        pass
