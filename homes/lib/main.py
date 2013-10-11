from sys import argv
from inspect import getmembers, isclass
from os.path import join as path_join, dirname
from lib.util import debug
from lib.config import ConfigDict, OptionsDict, ConfigurationError
import lib.checks as checks_module

class HomesChecker():
    """
    Class for doing all the administrative work for checking users homes.
    """

    configs = None
    configs_filename = path_join(
        dirname(argv[0]),"homes.conf"
    )

    configs_section = 'main'

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
        self.load_configs()
        self.do_checks()

    def load_configs(self, filename = None):
        """
        Coordinates loading of config.
        Seperates special sections.
        """
        configs = ConfigDict()
        configs.fill_from_file(
            filename or self.configs_filename
        )
        self.configs = configs
        self._check_required_configs()

    def _check_required_configs(self):
        """
        Checks if all required configurations are present.
        """
        options = self.configs[self.configs_section]
        for key in ['homes_path', 'simulate']:
            if not options[key]:
                raise ConfigurationError(self.configs_filename, key)

        # see if conversions work
        options.get_str('homes_path')
        options.get_bool('simulate')

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

    def do_checks(self):
        for check in HomesChecker.get_checks():
            print("would run", check)
