class GenericSDNResource(object):
    def __init__(self, address=None, shell_name=None, name=None):
        """

        :param str address: SDN controller address
        :param str shell_name: shell Name
        :param str name: resource name
        """
        self.attributes = {}
        self.address = address
        self.shell_name = shell_name
        self.name = name

        if shell_name:
            self.namespace_prefix = "{}.".format(self.shell_name)
        else:
            self.namespace_prefix = ""

    @property
    def user(self):
        """SDN Controller user

        :rtype: str
        """
        return self.attributes.get("{}User".format(self.namespace_prefix), None)

    @property
    def password(self):
        """SDN Controller password

        :rtype: str
        """
        return self.attributes.get("{}Password".format(self.namespace_prefix), None)

    @property
    def port(self):
        """SDN Controller port

        :rtype: str
        """
        return self.attributes.get("{}Port".format(self.namespace_prefix), None)

    @property
    def scheme(self):
        """SDN Controller port

        :rtype: str
        """
        return self.attributes.get("{}Scheme".format(self.namespace_prefix), None)

    @classmethod
    def from_context(cls, context, shell_name=None):
        """Create an instance of SDN Resource from the given context

        :param cloudshell.shell.core.driver_context.ResourceCommandContext context:
        :param str shell_name: shell Name
        :rtype: GenericSDNResource
        """
        result = cls(address=context.resource.address,
                     shell_name=shell_name,
                     name=context.resource.name)

        result.attributes = context.resource.attributes.copy()

        return result
