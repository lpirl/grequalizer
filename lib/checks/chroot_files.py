from os import getcwd, mkdir
from os.path import join as path_join, isfile, isdir, dirname
from filecmp import cmp as compare_files
from shutil import copy2 as copyfile, copymode
from functools import lru_cache
from subprocess import check_output

from lib.util import debug
from lib.checks import AbstractPerUserCheck

class FilesToChrootCheck(AbstractPerUserCheck):
    """
    Ensures that all files listed in the configuration are identically
    present in the chroot.
    """

    config_section = "chroot_files"

    order = 5000


    def load_unexpanded_paths_from_file(self, paths_file_name):
        """
        Loads lines (that do not start with an #)as paths into
        ``unexpanded_paths``.
        """

        append_to_unexpanded_paths = self.unexpanded_paths.append
        for line in open(paths_file_name):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            append_to_unexpanded_paths(line)

    def post_init(self):
        """
        Load file paths from configured file into ``unexpanded_paths``.
        """

        self.unexpanded_paths = []
        """
        List of absolute path to files that should be present in each chroot.
        """

        self.missing_files = {}
        """
        Dictionary of {user: file_name}
        Where ``user`` is an objects in terms of Pythons built-in pwd module
        and ``file_name`` an expanded path.
        """

        self.load_unexpanded_paths_from_file(
            self.options.get_str('file_list')
        )

        debug(
            "Loaded list of files for section '%s': %r" % (
                self.config_section, self.unexpanded_paths
            )
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
        Inititalized ``self.missing_files[user]`` at the beginning and
        evaluates it for its return value. The actual check is done by
        ``self.check_existance_and_fill_missing_files``.
        """
        self.missing_files[user] = []

        self.check_existance_and_fill_missing_files(user)

        return not bool(self.missing_files[user])

    def check_existance_and_fill_missing_files(self, user):
        """
        Does the actual check for ``is_correct`` and stores paths
        of missing files in ``self.missing_files``
        (what ``self.is_correct`` already initialized).
        """
        append_to_missing_files = self.missing_files[user].append
        for unexpanded_path in self.unexpanded_paths:
            file_path = self.expand_string_for_user(unexpanded_path, user)

            if not self.equal_files_for_expanded_path(user, file_path):
                debug("...not equal.")
                append_to_missing_files(file_path)

    def equal_files_for_expanded_path(self, user, file_path):
        """
        Compares the corresponding file in chroot and real root.
        Returns ``True`` if files are egual, ``False`` otherwise.
        """
        src_file_path, dst_file_path = self.get_src_and_dst_path(
            user, file_path
        )

        debug("Comparing '{0}' and '{1}'".format(
            src_file_path, dst_file_path
        ))

        if not isfile(dst_file_path):
            return False

        return compare_files(
            src_file_path, dst_file_path
        )

    def ensure_parent_directories_in_chroot(self, user, path):
        """
        Ensures that all parent directories of ``path``
        exist in the chroot, including the equality of the mode.
        """
        parent = dirname(path)
        src_dir, dst_dir = self.get_src_and_dst_path(
            user,
            dirname(path)
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

class BinariesToChrootCheck(FilesToChrootCheck):
    """
    Ensures that all binaries listed in the configuration are identically
    present in the chroot.
    Further, required dynamic libraries will be copied to the chroot.
    """

    config_section = "chroot_binaries"

    order = 5010

    @lru_cache()
    def get_dependendencies_for_expanded_path(self, binary_path):
        """
        Returns a list of paths to librarires that are required by
        """
        out = []
        ldd_out = check_output(['ldd', binary_path]).decode('utf-8')
        ldd_out_lines = ldd_out.split("\n")
        for ldd_out_line in ldd_out_lines:

            # ex:'	libacl.so.1 => /lib/x86_64-linux-gnu/libacl.so.1 (…)'
            if '=> /' in ldd_out_line:
                out.append(
                    ldd_out_line.split(' ')[2]
                )

            # ex: "	/lib64/ld-linux-x86-64.so.2 (…)"
            if ldd_out_line.startswith("\t/"):
                out.append(
                    ldd_out_line.split(" ")[0].strip()
                )

        debug("Dependencies for '{0}': {1}".format(binary_path, out))

        return out

    def check_existance_and_fill_missing_files(self, user):
        """
        Checks if all binaries listed in the configuration and their
        required libraries are identically present in the chroot.
        """
        append_to_missing_files = self.missing_files[user].append

        for unexpanded_path in self.unexpanded_paths:
            binary_path = self.expand_string_for_user(unexpanded_path, user)

            dependencies = self.get_dependendencies_for_expanded_path(
                binary_path
            )

            for path in dependencies + [binary_path]:

                if not self.equal_files_for_expanded_path(user, path):
                    debug("...not equal.")
                    append_to_missing_files(path)
