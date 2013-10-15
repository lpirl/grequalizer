from os import walk
from os.path import join as path_join

from lib.checks import BaseCheck
from lib.util import debug

class ObsoletesCheck(BaseCheck):
    """
    Checks if there are homes that do not belong to a user anymore.
    """

    config_section = "obsoletes"

    order = 500

    def check_homes_path(self):
        """
        Checks if the homes_path is compatible with this implementation.

        Future implementations may support a wider variety of directory
        structures - feel free to improve. :)
        """
        def homes_path_fail():
            ValueError(
                "Sorry, at the moment checks for obsolete " +
                "diretories can only be done for home_path's " +
                "in the following form: /path/to/somewhere/$u"
            )

        homes_path = self.homes_path

        if not (homes_path.endswith('$u') or homes_path.endswith('$u/')):
            homes_path_fail()

        if "$g" in homes_path or "$h" in homes_path:
            homes_path_fail()

    def post_init(self):
        """
        Checks if home_path and collects all possible user directories.
        """
        self.check_homes_path()

    def get_valid_directories(self):
        """
        Collects a set of all valid user home directories.

        "valid" means: the directories can exists due to the existence
        of a specific user but they might be missing.
        """
        return set((self.get_home_for_user(u) for u in self.users))

    def get_existing_directories(self):
        """
        Collects a set of all existing directories in the homes_path.
        """
        base_homes_path = self.homes_path.replace("$u", "")

        assert "$h" not in base_homes_path
        assert "$g" not in base_homes_path

        for _, directory_names, _ in walk(base_homes_path):
            return set(
                (path_join(base_homes_path, name)
                    for name in directory_names)
            )

    def check(self):
        """
        Main function to do the check.

        list directories, check if they are obsolete
        """
        existings = self.get_existing_directories()
        valids = self.get_valid_directories()
        obsoletes =  existings - valids
        print(obsoletes)
        #TODO: go on here
