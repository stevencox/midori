import logging
import os
from configparser import ConfigParser
from configparser import BasicInterpolation
from configparser import ExtendedInterpolation
from midori.utils import LoggingUtil
from typing import List

#https://gist.github.com/malexer/ee2f93b1973120925e8beb3f36b184b8

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

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
    def __init__(self, configs: List[str] = [ "midori.ini", "midori-container.ini" ]) -> None:
        """ Initialize

        This class uses the midori.config.EnvInterpolation class to implement interpolation.

        @param configs: List of configuration files to read in order.
        """        
        super().__init__(interpolation=EnvInterpolation())
        self.read_configs(configs)

    def read_configs(self, configs: List[str]) -> None:
        config_paths = [ os.path.join (os.path.dirname(__file__), f) for f in configs ]
        self.read(config_paths)

config = None
def get_config():
    global config
    if not config:
        env = os.environ.get("MIDORI_ENV", "dev")
        config_files = [ "midori.ini" ]
        if not env == "dev":
            config_files.append(f"midori-{env}.ini")
        logger.info(f"reading configurations: {config_files}")
        config = MidoriConfig(config_files)
    return config
    
if __name__ == "__main__":
    config = MidoriConfig ()
    print (config.get("midori", "midori_home"))
    print (config.get("redis", "redis_host"))
    print (config.get("onos", "onos_host"))

