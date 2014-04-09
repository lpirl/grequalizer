from lib.checks import AbstractPerUserCheck

class BinariesToChrootCheck(AbstractPerDirectoryCheckCheck):
    """
    Ensures that all binaries listed in the configuration are identically
    present in the chroot.
    Further, required dynamic libraries will be copied to the chroot.
    """

    config_section = "chroot_binaries"

    order = 5000

    def is_correct(self, user):
        """
        Checks if all binaries listed in the configuration and their
        required libraries are identically present in the chroot.
        """
        # use filecmp
        # fill a cache {user: <missing binaries>}
        raise NotImplementedError

    def correct(self, user):
        """
        Copies all missing binaries and libraries to the chroot,
        preserving parent direcotries, rights and ownership.
        """
        # read cache {user: <missing binaries>}
        # eventually create missing parent directories
        # copy binaries with permissions etc
        raise NotImplementedError
