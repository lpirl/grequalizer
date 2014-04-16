from os import getcwd, mkdir
from os.path import join as path_join, isfile, isdir, dirname
from filecmp import cmp as compare_files
from shutil import copy2 as copyfile, copymode

from lib.util import debug
from lib.checks import AbstractPerUserCheck

class FilesToChrootCheck(AbstractPerUserCheck):
    """
    Ensures that all files listed in the configuration are identically
    present in the chroot.
    """

    config_section = "chroot_files"

    order = 5000

    """
    List of absolute path to files that should be present in each chroot.
    """
    unexpanded_paths = []

    """
    Dictionary of {user: file_name}
    Where ``user`` is an objects in terms of Pythons built-in pwd module
    and ``file_name`` an expanded path.
    """
    missing_files = {}

    def post_init(self):
        """
        Load file paths from configured file into ``unexpanded_paths``.
        """
        paths_file_name = self.options.get_str('file_list')
        append_to_unexpanded_paths = self.unexpanded_paths.append
        for line in open(paths_file_name):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            append_to_unexpanded_paths(line)
        debug(
            "Loaded list of files for chroots: %r" % self.unexpanded_paths
        )

    def get_src_and_dst_path(self, user, path):
        """
        Returns a tuple of expanded strings:
        The first one is ``path`` relative to the real root and
        the secound one is ``path`` relative to the chroot of the user.
        """
        chroot_path = self.get_chroot_for_user(user)
        relative_path = path.lstrip('/')
        return (
            path_join(getcwd(), path),
            path_join(chroot_path, relative_path)
        )

    def is_correct(self, user):
        """
        Checks if all files listed in the configuration are identically
        present in the chroot.
        """
        self.missing_files[user] = []
        append_to_missing_files = self.missing_files[user].append

        for unexpanded_path in self.unexpanded_paths:
            file_path = self.expand_string_for_user(unexpanded_path, user)
            src_file_path, dst_file_path = self.get_src_and_dst_path(
                user, file_path
            )

            debug("Comparing '{0}s' and '{1}s'".format(
                src_file_path, dst_file_path
            ))

            equal = False
            if isfile(dst_file_path):
                equal = iscompare_files(
                    src_file_path, dst_file_path
                )

            if not equal:
                debug("...not equal.")
                append_to_missing_files(file_path)

        return not bool(self.missing_files[user])

    def ensure_parent_directories_in_chroot(self, user, path):
        """
        Ensures that all parent directories of ``path``
        exist in the chroot, including the equality of the mode.
        """
        parent = dirname(path)
        src_dir, dst_dir = self.get_src_and_dst_path(
            user,
            dirname(file_path)
        )

        if src_dir == "/":
            return

        if not isdir(dst_dir):
            self.ensure_parent_directories_in_chroot(user, parent)
            self.execute_safely(mkdir, dst_dir)

        self.execute_safely(copymode, src_dir, dst_dir)

    def correct(self, user):
        """
        Copies all missing files to the chroot,
        preserving parent direcotries, rights and ownership.
        """
        for missing_file in self.missing_files[user]:
            src_file_path, dst_file_path = self.get_src_and_dst_path(
                user, missing_file
            )

            self.ensure_parent_directories_in_chroot(user, src_file_path)

            self.execute_safely(
                copyfile,
                src_file_path,
                dst_file_path
            )
