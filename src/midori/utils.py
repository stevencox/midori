import datetime
import json
import logging
import logging.config
import os
import string
import sys
import traceback
import yaml
from jinja2 import Template, Environment
from types import ModuleType

logger = logging.getLogger (__name__)

class LoggingUtil:
    """ Log configuration entrypoint. """
    @staticmethod
    def setup_logging () -> None:
        config_path = os.path.join (os.path.dirname(__file__), "logging.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

class Code:
    """ Tools for working programmatically with source code. """
    
    @staticmethod
    def importCode(code: str, name: str="tmp", add_to_sys_modules: bool=False) -> ModuleType:
        """ Import a module given its source code as a string and the name of the module.

        Args:
           code (str): The Python source code of the module. 
           name (str): The name of the module.
           add_to_sys_modules (bool): Add this module to system modules, making it visible for import by others.
        
        Returns:
           ModuleType: The newly created module.
        """
        module = ModuleType(name)
        if add_to_sys_modules:
            sys.modules[name] = module
        # populate the module with code
        logger.debug(f"importing module:=>\n{code}")
        exec(code, module.__dict__)
        logger.debug(f"module:=> {module}")
        return module
    
class Resource:

    @staticmethod
    def read_file (path:str) -> str:
        result = None
        with open (path, 'r') as stream:
            result = stream.read ()
        return result

    @staticmethod
    def write_file (path:str, data:str) -> None:
        with open (path, 'w') as stream:
            result = stream.write (data)
    
    @staticmethod
    def load_json (path:str) -> object:
        result = None
        with open (path, 'r') as stream:
            result = json.loads (stream.read ())
        return result

    @staticmethod
    def read_yaml (path:str) -> object:
        result = None
        with open (path, 'r') as stream:
            result = yaml.safe_load (stream.read ())
        return result

    @staticmethod
    def write_yaml (path:str, obj:object) -> None:
        result = None
        with open (path, 'w') as stream:
            result = yaml.dump (obj, stream)
        return result

    @staticmethod
    def render (template_path: str, context: dict) -> str:
        template_path = os.path.join (
            os.path.dirname (__file__),
            template_path)
        template_text = Resource.read_file (template_path)
        jinja_env = Environment(extensions=['jinja2.ext.do'])
        template = Template (template_text)
        template.globals['now'] = datetime.datetime.utcnow
        return template.render (**context)

    @staticmethod
    def render_file (template_path: str,
                     context: dict,
                     path: str) -> None:
        Resource.write_file (
            path=path,
            data=Resource.render (template_path, context))
