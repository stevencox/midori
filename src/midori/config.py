from configparser import ConfigParser
from configparser import BasicInterpolation
from configparser import ExtendedInterpolation
from typing import List
import os

#https://gist.github.com/malexer/ee2f93b1973120925e8beb3f36b184b8

class EnvInterpolation(BasicInterpolation):
    """Interpolation to expand environment variables in configuration values."""

    def before_get(self, parser, section, option, value, defaults):
        """ Expands configuration setting values based on environment variables. """
        value = super().before_get(parser, section, option, value, defaults)
        """ Expand the value based on environment variables. """
        expanded = os.path.expandvars(value)
        """ Override with environment variable if the variable is already defined. """
        name = f"{section}_{option}".upper ()
        if name in os.environ:
            """ Return the value already defined for this variable in the environment. """
            expanded = os.environ[name]
        return expanded
    
class MidoriConfig(ConfigParser):
    """ A configuration parser implementing environment variable interpolation. """
    def __init__(self, configs: List[str] = [], use_defaults=True) -> None:
        """ Initialize

        This class uses the midori.config.EnvInterpolation class to implement interpolation.

        @param configs: List of configuration files to read in order.
        @param use_defaults: Load default configuration files if not are specified.
        """        
        super().__init__(interpolation=EnvInterpolation())

        if use_defaults:
            configs = [ "midori.ini", "midori-container.ini" ]
            config_paths = [ os.path.join (os.path.dirname(__file__), f) for f in configs ]
            self.read(config_paths)

config = MidoriConfig()

if __name__ == "__main__":
    config = MidoriConfig ()
    print (config.get("midori", "midori_home"))
    print (config.get("redis", "redis_host"))
    print (config.get("onos", "onos_host"))

