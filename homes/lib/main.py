# encoding: utf-8

from sys import argv
from pwd import getpwall
from grp import getgrnam
from inspect import getmembers, isclass
from os.path import join as path_join, dirname

from lib.util import debug
from lib.config import ConfigDict, OptionsDict
import lib.checks as checks_module

class HomesChecker():
    """
    Class for doing all the administrative work for checking users homes.
    """

    homes_path = None
    force_lowercase = None
    limit_to_group = None
    users = None
    group = None
    simulate = None
    minimum_users_count = None

    configs = None
    configs_filename = path_join(
        dirname(argv[0]),"homes.conf"
    )

    config_section = 'main'

    def __init__(self, config_file=None):
        """
        Accepts and sets alternative config file, if provided.
        """
        if config_file:
            self.configs_filename = config_file

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
            'homes_path',
            'simulate',
            'limit_to_primary_group',
            'minimum_users_count',
            'force_lowercase'
        )

        self.homes_path = options.get_str('homes_path')
        self.force_lowercase = options.get_str('force_lowercase')
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
                        getmembers(checks_module, isclass) ]
        checks.remove(checks_module.BaseCheck)
        debug("found checks: %s" % str(
                [s.__name__ for s in checks]
            ))
        return checks

    @classmethod
    def get_checks_sorted(cls):
        """
        Sames as get_checks but checks are sorted,
        starting with most important.
        """
        checks = cls.get_checks()
        checks.sort(key=lambda check: check.order)
        debug("sorted checks: %s" % str(
                [s.__name__ for s in checks]
            ))
        return checks

    def _load_users(self):
        users = getpwall()
        if self.limit_to_group:
            users = [u for u in users if u.pw_gid == self.group.gr_gid]
        if len(users) < self.minimum_users_count:
            print("too few users found... check configuration (got %u, need %u)" % (
            len(users), self.minimum_users_count), True)
            exit(1)
        self.users = users


    def do_checks(self):
        for check_cls in HomesChecker.get_checks_sorted():
            debug("doing check for %s" % str(check_cls))
            check = check_cls(
                self.homes_path,
                self.force_lowercase,
                self.users,
                self.simulate,
                self.configs[check_cls.config_section]
            )
            check.check()
