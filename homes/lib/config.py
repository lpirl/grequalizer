"""
Various classes to simplify handling of configuration.

Terminology:
    config[uration]     whole set of sections and their options
    section             set of options
    option              key, value pair
"""

from lib.util import debug

class OptionsDict(dict):
    """
    Like a dictionary, but can privede values casted to some type.
    """

    true_strings = ("yes", "true", "1", )
    false_strings = ("no", "false", "0", )

    def get_int(self, *args, **kwargs):
        """
        Returns requested value as int
        """
        return int(super(OptionsDict, self).get(*args, **kwargs))

    def get_bool(self, *args, **kwargs):
        """
        Returns requested value as int
        """
        value = str(super(OptionsDict, self).get(*args, **kwargs))
        if value.lower() in self.true_strings:
            return True
        if value.lower() in self.false_strings:
            return False
        raise ValueError("Could not convert '%s' to boolean." % value)

    def get_float(self, *args, **kwargs):
        """
        Returns requested value as int
        """
        return float(super(OptionsDict, self).get(*args, **kwargs))

    def get_str(self, *args, **kwargs):
        """
        Returns requested value as string
        """
        return str(super(OptionsDict, self).get(*args, **kwargs))

class ConfigDict(dict):
    """
    Ensures that nested dicts in FillFromFileDict are OptionsDict's.
    """

    def fill_from_file(self, filename):
        """
        Method loads configuration from file into dictionary.
        """
        debug("filling configuration from '%s'" % filename)
        fp = open(filename, "r")
        sections = dict()
        options = OptionsDict()
        for line in fp.readlines():
            line = line.strip()

            if line.startswith("#"):
                continue

            if line.startswith('[') and line.endswith(']'):
                options = OptionsDict()
                sections[line[1:-1].strip()] = options
                continue

            if '=' in line:
                key, value = tuple(line.split("=", 1))
                options[key.strip()] = value.strip()
                continue

        fp.close()
        debug("filled configuration is: '%s'" % str(sections))

        self.update(sections)
