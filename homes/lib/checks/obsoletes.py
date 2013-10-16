# encoding: utf-8

from os import chmod
from os.path import isfile, basename, dirname, join as path_join
from shutil import make_archive
from lib.checks import AbstractAllUsersAndAllDirectoriesCheck
from lib.util import debug, log

class ObsoletesCheck(AbstractAllUsersAndAllDirectoriesCheck):
    """
    Checks if there are homes that do not belong to a user anymore.
    """

    config_section = "obsoletes"

    order = 500

    trash_path = None
    octal_permissions = None

    def post_init(self):
        """
        Stores some options as property for faster access.
        """
        self.trash_path = self.options.get_str('trash_path')
        self.octal_permissions = self.options.get_int('trash_octal_permissions')

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
        return not bool(self.obsolete_directories(users, directories))

    def correct(self, users, directories):
        """
        Corrects home directory for a list of users and directories..
        """
        obsoletes = self.obsolete_directories(users, directories)
        for directory_path in obsoletes:
            self.do_trash_directory(directory_path)

    def trash_file_path(self, directory_path, suffix_number=0):
        candidate = path_join(self.trash_path, basename(directory_path))

        if suffix_number:
            candidate += "_%u" % suffix_number

        if isfile(candidate):
            return self.trash_file_path(directory_path, suffix_number+1)
        else:
            return candidate

    def do_trash_directory(self, directory_path):
        """
        Moves directory to trash.
        """
        trash_file_path = self.trash_file_path(directory_path)
        debug("trashing directory '%s'" % directory_path)
        archive_path = self.execute_safely(
            make_archive,
            trash_file_path,
            "bztar",
            dirname(directory_path),
            basename(directory_path)
        )
        if archive_path:
            self.execute_safely(    chmod,
                                    trash_file_path,
                                    self.octal_permissions)
        else:
            log(u"ERROR: something apparently went wrong - no archive " +
                "file name found after archive creation!")
