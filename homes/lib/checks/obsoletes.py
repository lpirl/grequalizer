from lib.checks import AbstractAllUsersAndAllDirectoriesCheck
from lib.util import debug

class ObsoletesCheck(AbstractAllUsersAndAllDirectoriesCheck):
    """
    Checks if there are homes that do not belong to a user anymore.
    """

    config_section = "obsoletes"

    order = 500

    def obsolete_directories(self, users, directories):
        """
        Returns a set of obsolete directories.
        """
        existing_directories = set(directories)
        users_directories = set(self.get_home_for_user(u) for u in users)
        return existing_directories - users_directories

    def is_correct(self, users, directories):
        """
        Checks correctness with a list of users and directories.
        """
        return self.obsolete_directories(users, directories) == set()

    def correct(self, users, directories):
        """
        Corrects home directory for a list of users and directories..
        """
        obsoletes = self.obsolete_directories(users, directories)
        #TODO: go on here
