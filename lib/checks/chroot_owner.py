from os import stat, chown
from os.path import isdir
from pwd import getpwnam

from lib.checks import AbstractPerUserCheck
from lib.util import debug

class ChrootOwnerCheck(AbstractPerUserCheck):
    """
    Checks the chroot directories for all users for desired owner.
    """

    config_section = "chroot_owner"
    owner_unexpanded = None

    def post_init(self):
        """
        Stores some options as property for faster access.
        """
        self.owner_unexpanded = self.options.get_str('owner')

    def owner_uid_for_user(self, user):
        """
        Returns the desired owner for a certain user (expands variables
        from configuration).
        """
        return getpwnam(
            self.__class__.expand_string_for_user(
                self.owner_unexpanded, user
            )
        ).pw_uid

    @classmethod
    def owner_uid_for_path(self, path):
        """
        Returns owner for a path
        """
        return stat(path).st_uid

    def correct(self, user):
        chroot_path = self.get_chroot_for_user(user)
        debug("setting owner for %s to %s" % (chroot_path, user.pw_name))
        if not isdir(chroot_path):
            debug("...directory does not exist. Doing nothing.")
            return
        self.execute_safely(
            chown,
            chroot_path,
            self.owner_uid_for_user(user),
            -1
        )

    def is_correct(self, user):
        chroot_path = self.get_chroot_for_user(user)
        debug("checking directory owner for %s" % user.pw_name)
        if not isdir(chroot_path):
            debug("...directory does not exist. Ignoring.")
            return True
        current_uid = self.__class__.owner_uid_for_path(chroot_path)
        return current_uid == self.owner_uid_for_user(user)