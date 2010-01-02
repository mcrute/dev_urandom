from ConfigParser import SafeConfigParser, DEFAULTSECT
from ConfigParser import NoOptionError, NoSectionError


class EnvironmentConfig(object, SafeConfigParser):

    def __init__(self, **kwargs):
        SafeConfigParser.__init__(self, **kwargs)
        self._environment = None

    def set_environment(self, env):
        self._environment = env

    def get_environment(self):
        return self._environment

    environment = property(fget=get_environment, fset=set_environment)

    def get(self, section, option, raw=False, vars=None):
        if self._environment and ':' not in section:
            section = "%s:%s" % (section, self._environment)

        d = self._defaults.copy()
        try:
            if ':' in section:
                d.update(self._sections[section.split(':')[0]])

            d.update(self._sections[section])
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)

        # Update with the entry specific variables
        if vars:
            for key, value in vars.items():
                d[self.optionxform(key)] = value
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            # Try the parent container if there is one
            try:
                section = section.split(':')[0]
                d.update(self._sections[section])
                value = d[option]
            except KeyError:
                raise NoOptionError(option, section)

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        if raw:
            return value
        else:
            return self._interpolate(section, option, value, d)
