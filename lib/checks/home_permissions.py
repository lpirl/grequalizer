from os import stat, chmod
from stat import S_IMODE
from os.path import isdir

from lib.checks import AbstractPerUserCheck
from lib.util import debug

class HomePermissionCheck(AbstractPerUserCheck):
    """
    Checks the home directories for all users for desired permissions.
    """

    config_section = "home_permissions"

    @property
    def permissions(self):
        """
        desired permissions for home directories

        Lazily load attribute in order to allow it to be not configured
        (when check is disabled).
        """
        return int(self.options.get_str('octal_permissions'), 8)

    def correct(self, user):
        home_path = self.get_home_for_user(user)
        debug("setting permissions for %s to %o" % (
            home_path, self.permissions))
        if not isdir(home_path):
            debug("...directory does not exist. Doing nothing.")
            return
        self.execute_safely(chmod, home_path, self.permissions)

    def is_correct(self, user):
        debug("checking directory permissions for %s" % user.pw_name)
        home_path = self.get_home_for_user(user)
        if not isdir(home_path):
            debug("...directory does not exist. Ignoring.")
            return True
        return S_IMODE(stat(home_path).st_mode) == self.permissions
