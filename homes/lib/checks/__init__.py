class BaseCheck:
    """
    Base class for all checks
    """

    homes_path = None
    simulate = None
    configs = None

    def __init__(self, homes_path, force_lowercase, users, simulate, options):
        self.homes_path = homes_path
        self.force_lowercase = force_lowercase
        self.users = users
        self.simulate = simulate
        self.options = options

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

    def _get_home_for_user(self, user):
        path = self.homes_path.replace(
                    "$u", user.pw_name
                ).replace(
                    "$h", user.pw_dir
                )
        return path.lower() if self.force_lowercase else path

    @property
    def config_section(self):
        self.__class__._raise_subclass_error('property', 'config_section')

    @property
    def order(self):
        """
        Used to sort checks and run them in order.

        Lower number runs earlier.
        """
        self.__class__._raise_subclass_error('property', 'priority')

    def execute_safely(self, function, *args, **kwargs):
        """
        Method prints what would be done if simulating or
        does it otherwise.
        """
        if self.simulate:
            print("simulating - would execute %s with args %s and kwargs %s otherwise" % (
                str(function), str(args), str(kwargs)
            ))
        else:
            raise NotImplementedError()

    def check(self):

        if not self.options.get_bool('check'):
            return

        correct = self.options.get_bool('correct')
        get_home_for_user = self._get_home_for_user

        for user in self.users:
            final_path = get_home_for_user(user)
            if not self.is_correct_for_user(final_path, user) and correct:
                self.correct_for_user(final_path, user)

    def is_correct_for_user(self, user):
        self.__class__._raise_subclass_error('method', 'check_for_user')

    def correct_for_user(self, user):
        self.__class__._raise_subclass_error('method', 'correct_for_user')

from .existance import ExistanceCheck
