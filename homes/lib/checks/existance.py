from os import mkdir

from lib.checks import AbstractAllUsersAndAllDirectoriesCheck
from lib.util import debug

class ExistanceCheck(AbstractAllUsersAndAllDirectoriesCheck):
    """
    Checks if a home for every user exists.
    """

    config_section = "existance"

    order = 100

    def missing_directories(self, users, directories):
        """
        Returns a set of obsolete directories.
        """
        existing_directories = set(directories)
        users_directories = set(selg.get_home_for_user(u) for u in users)
        return users_directories - existing_directories

    def correct(self, users, directories):
        for directory in self.missing_directories(users, directories):
            debug("creating missing directory '%s'" % directory)
            self.execute_safely(mkdir, final_path, mode=700)

    def is_correct(self, users, directories):
        debug("checking for missing directories")
        return self.missing_directories(users, directories) == set()
