from grp import getgrgid

class BaseCheck:
    """
    Base class for all checks
    """

    """
    Path to users home directory, not expanded yet.
    """
    homes_path = None

    """
    If True, nothing should ever be done.
    """
    simulate = None

    """
    Configuration options for this check.

    All options from section defined in attribute 'config_section'.
    """
    options = None

    """
    Order when this check should be executed.

    Lower numbers are executed earlier.
    """
    order = 1000

    def __init__(self, homes_path, force_lowercase, users, simulate, options):
        self.homes_path = homes_path
        self.force_lowercase = force_lowercase
        self.users = users
        self.simulate = simulate
        self.options = options
        self.post_init()

    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """
        pass

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

    @classmethod
    def group_name_for_user(cls, user):
        """
        Returns the group name of a users primary group.
        """
        return getgrgid(user.pw_gid).gr_name

    @classmethod
    def _expand_string_for_user(cls, string, user):
        """
        Expands variables in string according to users.
        """
        return string.replace(
                    "$u", user.pw_name
                ).replace(
                    "$h", user.pw_dir
                ).replace(
                    "$g", cls.group_name_for_user(user)
                )

    def _get_home_for_user(self, user):
        """
        Expands variables in path to users home path.
        """
        path = self.__class__._expand_string_for_user(
            self.homes_path, user)
        return path.lower() if self.force_lowercase else path

    @property
    def config_section(self):
        """
        Defines which section in the configuration belongs to this check.

        Name clashes are to be avoided ;)
        """
        self.__class__._raise_subclass_error('property', 'config_section')

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
        """
        Executes (eventually) check and (eventually) corrections for all user's
        homes..
        """
        if not self.options.get_bool('check'):
            return

        correct = self.options.get_bool('correct')
        get_home_for_user = self._get_home_for_user

        for user in self.users:
            final_path = get_home_for_user(user)
            if not self.is_correct_for_user(final_path, user) and correct:
                self.correct_for_user(final_path, user)

    def is_correct_for_user(self, user):
        """
        Checks correctness for a single users home.
        """
        self.__class__._raise_subclass_error('method', 'check_for_user')

    def correct_for_user(self, user):
        """
        Corrects a single users home.
        """
        self.__class__._raise_subclass_error('method', 'correct_for_user')

from .existance import ExistanceCheck
from .permissions import PermissionCheck
from .owner import OwnerCheck
from .group import GroupCheck
