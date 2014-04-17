# encoding: utf-8

from sys import argv
from pwd import getpwall
from grp import getgrnam
from inspect import getmembers, isclass
from os.path import join as path_join, dirname

from lib.util import debug, log
from lib.config import ConfigDict, OptionsDict
import lib.checks as checks_module

class ChecksRunner():
    """
    Class for doing all the administrative work for checking users homes.
    """

    config_section = 'main'
    """section where configration will be retreived from"""

    def __init__(self, config_file):
        """
        Initializes instance variables and esp. sets the config file.
        """

        self.chroot_path = None
        """see full config example for explanation"""

        self.limit_to_group = None
        """see full config example for explanation"""

        self.users = None
        """see full config example for explanation"""

        self.group = None
        """see full config example for explanation"""

        self.simulate = None
        """see full config example for explanation"""

        self.minimum_users_count = None
        """see full config example for explanation"""

        self.configs_filename = config_file
        """path to configuration file"""

        self.configs = None
        """ConfigDict with configuration loaded from self.config_section"""

    def auto(self):
        """
        Run all actions in the correct order. (Calls this from outside)
        """
        debug("started")
        self._load_configs()
        self._load_users()
        self.do_checks()

    def _load_configs(self):
        """
        Coordinates loading of config.
        Seperates special sections.
        """
        configs = ConfigDict()
        configs.fill_from_file(
            self.configs_filename
        )
        self.configs = configs
        self._check_required_configs()

    def _check_required_configs(self):
        """
        Checks if all required configurations are present.
        """
        options = self.configs[self.config_section]

        required_fields = (
            'chroot_path',
            'simulate',
            'limit_to_primary_group',
            'minimum_users_count',
        )

        self.chroot_path = options.get_str('chroot_path')
        self.simulate = options.get_bool('simulate')
        self.limit_to_group = options.get_bool('limit_to_primary_group')
        if self.limit_to_group:
            self.group = getgrnam(options.get_str('primary_group_name'))
        self.minimum_users_count = options.get_int('minimum_users_count')

    @classmethod
    def get_checks(cls):
        """
        Acquires all checks (classes) in the module 'checks'.
        """
        checks = [	t[1] for t in
                        getmembers(checks_module, isclass)
                            if not t[0].startswith("Abstract") ]
        debug("found checks: %s" % str([s.__name__ for s in checks]))
        return checks

    @classmethod
    def get_checks_sorted(cls):
        """
        Sames as get_checks but checks are sorted,
        starting with most important.
        """
        checks = cls.get_checks()
        checks.sort(key=lambda check: check.order)
        debug("sorted checks: %s" % str([s.__name__ for s in checks]))
        return checks

    def _load_users(self):
        users = getpwall()
        if self.limit_to_group:
            users = [u for u in users if u.pw_gid == self.group.gr_gid]
        if len(users) < self.minimum_users_count:
            log("too few users found... check configuration (got %u, need %u)" % (
            len(users), self.minimum_users_count))
            exit(1)
        self.users = users


    def do_checks(self):
        for check_cls in ChecksRunner.get_checks_sorted():
            debug("doing check for %s" % str(check_cls))
            check = check_cls(
                self.chroot_path,
                self.users,
                self.simulate,
                self.configs[check_cls.config_section]
            )
            check.check()
