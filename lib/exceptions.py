class ConfigurationException(Exception):
    """ Configuration exception """
    pass


class HookExecutionException(Exception):
    """ Failed to execute a hook """
    pass


class InvalidTemplateException(Exception):
    """ Invalid CloudFormation template """
    pass
