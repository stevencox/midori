Module midori.config
====================

Classes
-------

`EnvInterpolation()`
:   Interpolation to expand environment variables in configuration values.

    ### Ancestors (in MRO)

    * configparser.BasicInterpolation
    * configparser.Interpolation

    ### Methods

    `before_get(self, parser, section, option, value, defaults)`
    :   Expands configuration setting values based on environment variables.

`MidoriConfig(configs: List[str] = [], use_defaults=True)`
:   A configuration parser implementing environment variable interpolation. 
    
    Initialize
    
    This class uses the midori.config.EnvInterpolation class to implement interpolation.
    
    @param configs: List of configuration files to read in order.
    @param use_defaults: Load default configuration files if not are specified.

    ### Ancestors (in MRO)

    * configparser.ConfigParser
    * configparser.RawConfigParser
    * collections.abc.MutableMapping
    * collections.abc.Mapping
    * collections.abc.Collection
    * collections.abc.Sized
    * collections.abc.Iterable
    * collections.abc.Container