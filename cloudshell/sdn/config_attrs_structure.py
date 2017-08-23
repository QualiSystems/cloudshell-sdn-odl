class GenericSDNResource(object):
    def __init__(self, address=None):
        """

        :param str address: SDN controller address
        """
        self.attributes = {}
        self.address = address

    @property
    def user(self):
        """SDN Controller user

        :rtype: str
        """
        return self.attributes.get("User", None)

    @property
    def password(self):
        """SDN Controller password

        :rtype: str
        """
        return self.attributes.get("Password", None)

    @property
    def port(self):
        """SDN Controller port

        :rtype: str
        """
        return self.attributes.get("Port", None)

    @classmethod
    def from_context(cls, context):
        """Create an instance of SDN Resource from the given context

        :param cloudshell.shell.core.driver_context.ResourceCommandContext context:
        :rtype: GenericSDNResource
        """
        result = cls(address=context.resource.address)
        result.attributes = context.resource.attributes.copy()

        return result
