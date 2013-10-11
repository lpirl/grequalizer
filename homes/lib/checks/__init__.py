class BaseCheck:
    """
    Base class for all checks
    """

    homes_path = None
    simulate = None
    configs = None

    def __init__(self, homes_path, simulate, configs):
        self.homes_path = homes_path
        self.simulate = simulate
        self.configs = configs

    @classmethod
    def _raise_subclass_error(cls, attr_type, attr_name):
        """
        Method provides unified "help" for implementing the interface.
        """
        raise NotImplementedError(
            "Subclass %s must provide %s '%s'" % (
                cls.__name__,
                attr_type,
                attr_name
            )
        )

    def check(self):
        self.__class__._raise_subclass_error('method', 'check')

from .existance import ExistanceCheck
