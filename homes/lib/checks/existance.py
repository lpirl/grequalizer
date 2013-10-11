from os import mkdir
from os.path import isdir

from lib.checks import BaseCheck
from lib.util import debug

class ExistanceCheck(BaseCheck):
    """
    Checks if a home for every user exists.
    """

    config_section = "existance"

    def correct_for_user(self, final_path, user):
        debug("creating directory for %s" % user.pw_name)
        self.execute_safely(mkdir, final_path, mode=700)

    def is_correct_for_user(self, final_path, user):
        debug("checking directory existance for %s" % user.pw_name)
        return isdir(final_path)
