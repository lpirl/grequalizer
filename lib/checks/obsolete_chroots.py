# encoding: utf-8

from os import chmod, listdir
from os.path import isfile, basename, dirname, join as path_join
from shutil import make_archive, rmtree
from lib.checks import AbstractAllUsersAndAllDirectoriesCheck
from lib.util import debug, log

class ObsoleteChrootsCheck(AbstractAllUsersAndAllDirectoriesCheck):
    """
    Checks if there are chroot directories that do not belong to a user anymore.
    """

    config_section = "obsolete_chroots"

    order = 500

    def post_init(self):
        """
        Stores some options as property for faster access.
        """
        self.trash_path = self.options.get_str('trash_path')
        """root directory where archived homes will be put"""

        self.octal_permissions = self.options.get_int('trash_octal_permissions')
        """octal permission mask for files in trash"""

    def obsolete_directories(self, users, directories):
        """
        Returns a set of obsolete directories.
        """
        existing_directories = set(directories)
        users_directories = set(self.get_chroot_for_user(u) for u in users)
        return existing_directories - users_directories

    def is_correct(self, users, directories):
        """
        Checks correctness with a list of users and directories.
        """
        return not bool(self.obsolete_directories(users, directories))

    def correct(self, users, directories):
        """
        Corrects chroot directory for a list of users and directories..
        """
        obsoletes = self.obsolete_directories(users, directories)
        for directory_path in obsoletes:
            self.do_trash_directory(directory_path)

    def trash_file_path(self, directory_path, suffix_number=0):
        """
        Assembles & returns the path of the trash file.
        """
        candidate = path_join(self.trash_path, basename(directory_path))

        if suffix_number:
            candidate += "_%u" % suffix_number

        if isfile(candidate):
            return self.trash_file_path(directory_path, suffix_number+1)
        else:
            return candidate

    def do_archive_directory(self, directory_path):
        """
        Archives directory contents to trash if not empty.

        Returns True on success, False otherwise
        """
        trash_file_path = self.trash_file_path(directory_path)
        archive_path = self.execute_safely(
            make_archive,
            trash_file_path,
            "bztar",
            dirname(directory_path),
            basename(directory_path)
        )

        if not archive_path and not self.simulate:
            log(u"ERROR: something went wrong - no archive " +
                "file name found after archive creation!")
            return False

        self.execute_safely(    chmod,
                                archive_path,
                                self.octal_permissions)
        return True

    def do_trash_directory(self, directory_path):
        """
        Moves directory to trash.
        """
        if listdir(directory_path):
            debug("archiving directory '%s'" % directory_path)
            if not self.do_archive_directory(directory_path):
                return
        else:
            debug("not archiving empty directory '%s'" % directory_path)

        debug("deleting directory '%s'" % directory_path)
        self.execute_safely(    rmtree,
                                directory_path,
                                ignore_errors=True)
