from os import stat, chmod
from os.path import isdir

from lib.checks import BaseCheck
from lib.util import debug

class PermissionCheck(BaseCheck):
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

    def correct_for_user(self, final_path, user):
        debug("setting permissions for %s to %i" % (
            final_path, self.octal_permissions))
        if not isdir(final_path):
            debug("...directory does not exist. Doing nothing.")
            return
        self.execute_safely(chmod, final_path, self.octal_permissions)

    def is_correct_for_user(self, final_path, user):
        debug("checking directory permissions for %s" % user.pw_name)
        if not isdir(final_path):
            debug("...directory does not exist. Ignoring.")
            return True
        current = self.__class__.octal_permissions_for_path(final_path)
        return current == self.octal_permissions
