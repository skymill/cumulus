class ConfigurationException(Exception):
    """ Configuration exception """
    pass


class HookExecutionException(Exception):
    """ Failed to execute a hook """
    pass


class InvalidTemplateException(Exception):
    """ Invalid CloudFormation template """
    pass


class UnsupportedCompression(Exception):
    """ An unsupported compression format for the bundle found """
    pass
