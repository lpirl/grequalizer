from os import stat, chmod
from os.path import isdir

from lib.checks import AbstractPerUserCheck
from lib.util import debug

class PermissionCheck(AbstractPerUserCheck):
    """
    Checks the homes for all users for desired permissions.
    """

    config_section = "permissions"
    octal_permissions = None

    def post_init(self):
        """
        Stores some options as property for faster access.
        """
        self.octal_permissions = self.options.get_int('octal_permissions')

    @classmethod
    def octal_permissions_for_path(self, path):
        """
        Returns octal permissions (lower 3 bits) for a path
        """
        return int(oct(stat(path).st_mode)[-3:])

    def correct(self, user):
        home_path = self.get_home_for_user(user)
        debug("setting permissions for %s to %i" % (
            home_path, self.octal_permissions))
        if not isdir(home_path):
            debug("...directory does not exist. Doing nothing.")
            return
        self.execute_safely(chmod, home_path, self.octal_permissions)

    def is_correct(self, user):
        debug("checking directory permissions for %s" % user.pw_name)
        home_path = self.get_home_for_user(user)
        if not isdir(home_path):
            debug("...directory does not exist. Ignoring.")
            return True
        current = self.__class__.octal_permissions_for_path(home_path)
        return current == self.octal_permissions
