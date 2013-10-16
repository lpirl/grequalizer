from os import stat, chown
from os.path import isdir
from grp import getgrnam

from lib.checks import AbstractPerUserCheck
from lib.util import debug

class GroupCheck(AbstractPerUserCheck):
    """
    Checks the homes for all users for desired group.
    """

    config_section = "group"
    group_unexpanded = None

    def post_init(self):
        """
        Stores some options as property for faster access.
        """
        self.group_unexpanded = self.options.get_str('group')

    def group_uid_for_user(self, user):
        """
        Returns the desired group for a certain user (expands variables
        from configuration).
        """
        return getgrnam(
            self.__class__.expand_string_for_user(
                self.group_unexpanded, user
            )
        ).gr_gid

    @classmethod
    def group_uid_for_path(self, path):
        """
        Returns group for a path
        """
        return stat(path).st_gid

    def correct(self, user):
        home_path = self.get_home_for_user(user)
        debug("setting group for %s to %s" % (home_path, user.pw_name))
        if not isdir(home_path):
            debug("...directory does not exist. Doing nothing.")
            return
        self.execute_safely(
            chown,
            home_path,
            -1,
            self.group_uid_for_user(user)
        )

    def is_correct(self, user):
        home_path = self.get_home_for_user(user)
        debug("checking directory group for %s" % user.pw_name)
        if not isdir(home_path):
            debug("...directory does not exist. Ignoring.")
            return True
        current_gid = self.__class__.group_uid_for_path(home_path)
        return current_gid == self.group_uid_for_user(user)
