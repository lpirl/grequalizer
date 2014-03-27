import abc
from os import walk
from os.path import join as path_join

from grp import getgrgid

from lib.util import debug, log

class AbstractCheckBase(metaclass=abc.ABCMeta):
    """
    Base class for all checks
    """

    """
    Path to users chroot directory, not expanded yet.
    """
    chroot_path = None

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

    def __init__(self, chroot_path, users, simulate, options):
        self.chroot_path = chroot_path
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
    def group_name_for_user(cls, user):
        """
        Returns the group name of a users primary group.
        """
        return getgrgid(user.pw_gid).gr_name

    @classmethod
    def expand_string_for_user(cls, string, user):
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

    def get_chroot_for_user(self, user):
        """
        Expands variables in path to users chroot path.
        """
        return self.__class__.expand_string_for_user(
            self.chroot_path,
            user
        )

    @abc.abstractproperty
    def config_section(self):
        """
        Defines which section in the configuration belongs to this check.

        Name clashes are to be avoided ;)
        """
        pass

    def execute_safely(self, function, *args, **kwargs):
        """
        Method prints what would be done if simulating or
        does it otherwise.
        """
        def call_as_pretty_string():
            return "%s.%s(%s, %s)" % (
                function.__module__,
                function.__name__,
                ', '.join((repr(arg) for arg in args)),
                ', '.join(( "%s=%s" % (repr(k), repr(v))
                            for k, v in kwargs.items())),
            )

        if self.simulate:
            log("simulating - would execute %s otherwise" % (
                call_as_pretty_string()
            ))
            return None
        else:
            log("executing " + call_as_pretty_string())
            return function(*args, **kwargs)

    def check(self):
        """
        Executes all checks according to configuration.
        """
        if not self.options.get_bool('check'):
            debug("check skipped: disabled in configuration")
            return
        self._check()

    @abc.abstractmethod
    def _check(self):
        """
        Actually implements iteration over objects to check

        (directories, users, …)
        """
        pass

class AbstractPerDirectoryCheck(AbstractCheckBase):
    """
    Executes checks per existing directory in chroot path.
    """

    def __init__(self, *args, **kwargs):
        """
        Additionally, ensured precondition for this check method to work.
        """
        super(AbstractPerDirectoryCheck, self).__init__(*args, **kwargs)
        self.check_chroot_path()

    def check_chroot_path(self):
        """
        Checks if the chroot_path is compatible with this implementation.

        Future implementations may support a wider variety of directory
        structures - feel free to improve. :)
        """
        def chroot_path_fail():
            ValueError(
                "Sorry, at the moment checks for obsolete " +
                "diretories can only be done for chroot_path's " +
                "in the following form: /path/to/somewhere/$u"
            )

        chroot_path = self.chroot_path

        if not (chroot_path.endswith('$u') or chroot_path.endswith('$u/')):
            chroot_path_fail()

        if "$g" in chroot_path or "$h" in chroot_path:
            chroot_path_fail()

    def get_existing_directories(self):
        """
        Collects a set of all existing directories in the chroot_path.
        """
        base_chroot_path = self.chroot_path.replace("$u", "")

        assert "$h" not in base_chroot_path
        assert "$g" not in base_chroot_path

        for _, directory_names, _ in walk(base_chroot_path):
            return (path_join(base_chroot_path, name)
                        for name in directory_names)


    def _check(self):
        """
        For every existing chroot directory, check if it's correct and
        correct if required and configured.
        """
        for directory in self.get_existing_directories():
            if not self.is_correct(directory):
                if not self.options.get_bool('correct'):
                    debug("correction skipped: disabled in configuration")
                    continue
                self.correct(directory)

    @abc.abstractmethod
    def is_correct(self, directory):
        """
        Checks correctness for a single user chroot directory.
        """
        pass

    @abc.abstractmethod
    def correct(self, directory):
        """
        Corrects a users chroot directory.
        """
        pass

class AbstractPerUserCheck(AbstractCheckBase):
    """
    Executes checks per existing user.
    """

    def _check(self):
        """
        For every user, check if the chroot directory is correct and
        correct with respect to the configuration.
        """
        for user in self.users:
            if not self.is_correct(user):
                if not self.options.get_bool('correct'):
                    debug("correction skipped: disabled in configuration")
                    continue
                self.correct(user)

    @abc.abstractmethod
    def is_correct(self, user):
        """
        Checks correctness for a single user chroot directory.
        """
        pass

    @abc.abstractmethod
    def correct(self, user):
        """
        Corrects a users chroot directory.
        """
        pass

class AbstractAllUsersAndAllDirectoriesCheck(AbstractPerDirectoryCheck):
    """
    Somehow a hybrid from per user and per directory checks.

    Checks and corrections get handed a iterable of users and existing
    directories.

    Might be memory intensive in large setups.
    """

    def _check(self):
        """
        Checks correctness and corrects if configured using iterables of
        all users and existing directories.
        """
        directories = list(self.get_existing_directories() or [])
        users = self.users

        if not self.is_correct(users, directories):
            debug("correction required")
            if not self.options.get_bool('correct'):
                debug("correction skipped: disabled in configuration")
                return
            self.correct(users, directories)

    @abc.abstractmethod
    def is_correct(self, users, directories):
        """
        Checks correctness with a list of users and directories.
        """
        pass

    @abc.abstractmethod
    def correct(self, users, directories):
        """
        Corrects chroot directory for a list of users and directories..
        """
        pass

from .existence import ExistenceCheck
from .permissions import PermissionCheck
from .owner import OwnerCheck
from .group import GroupCheck
from .obsoletes import ObsoletesCheck
