from lib.checks import AbstractPerUserCheck

class FilesToChrootCheck(AbstractPerDirectoryCheckCheck):
    """
    Ensures that all files listed in the configuration are identically
    present in the chroot.
    """

    config_section = "chroot_files"

    order = 5000

    def is_correct(self, user):
        """
        Checks if all files listed in the configuration are identically
        present in the chroot.
        """
        # use filecmp
        # fill a cache {user: <missing files>}
        raise NotImplementedError

    def correct(self, user):
        """
        Copies all missing files to the chroot,
        preserving parent direcotries, rights and ownership.
        """
        # read cache {user: <missing files>}
        # eventually create missing parent directories
        # copy files with permissions etc
        raise NotImplementedError
