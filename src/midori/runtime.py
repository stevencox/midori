from midori.compiler import Compiler
import logging
import json
import os
import requests
import textwrap
import time
import traceback as tb
from requests.auth import HTTPBasicAuth
from midori.config import config
from midori.graph import MidoriGraph
from midori.utils import LoggingUtil, Resource
from typing import Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

class MidoriException(Exception):
    """ A general error pertaining to a simulation has occurred. """
    pass

class MidoriNetworkError(MidoriException):
    """ A simulation failed due to a network or communication error. """
    pass

class MidoriExecutionError(MidoriException):
    """ A simulation failed due to the failure of a computation or lack of computing resources. """
    pass

class Controller:
    """ Abstraction for an Openflow SDN controller. For Midori, this 
    currently means Onos. """
    def __init__(self,
                 api_host: str,
                 api_port: int,
                 username: str = None,
                 password: str = None
    ) -> None:
        self.api_host = api_host
        self.api_port = api_port
        self.username = username
        self.password = password
        
    def get_api(self, api:str = "") -> str:
        """ Build and API URL. """
        return f"http://{self.api_host}:{self.api_port}/{api}"

    def clean(self) -> None:
        """ Reset the system to a clean state. """
        pass
    
    def create_host_intent(self, ingress_device: str, egress_device: str) -> None:
        """ Create a host to host network flow intent. """
        pass
    
class Onos(Controller):
    """ An Onos Openflow SDN controller. """
    def __init__(self,
                 api_host: str = config.get("onos", "host"),
                 api_port: int = config.get("onos", "api_port"),
                 username: str = config.get("onos", "username"),
                 password: str = config.get("onos", "password")
    ) -> None:
        """ Initialize the base class """
        super().__init__(api_host=api_host, api_port=api_port,
                         username=username, password=password)

    def get(self, operation: str, args : Dict = {}, nominal=200) -> Dict:
        """ Perform a generic get operation on the API. """
        api_url = self.get_api(operation)
        logger.info(f"request ==> {api_url}: {json.dumps(args, indent=2)}")
        if len(args) > 0:
            query_parameters = "&".join ([ f"{k}={v}" for k, v in args.items () ])
            api_url = f"{api_url}?{query_parameters}"
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(self.username, self.password))
        result = None
        if response.status_code == nominal and response.text:
            result = response.json ()
        else:
            print(f"Response: {response.text}")
            print(f"Status code: {response.status_code}")
        return result

    def delete(self, operation: str, args : Dict = {}, nominal=204) -> Dict:
        """ Perform a generic delete operation on the API. """
        api_url = self.get_api(operation)
        logger.info(f"request ==> {api_url}: {json.dumps(args, indent=2)}")
        if len(args) > 0:
            query_parameters = "&".join ([ f"{k}={v}" for k, v in args.items () ])
            api_url = f"{api_url}?{query_parameters}"
        response = requests.delete(
            api_url,
            auth=HTTPBasicAuth(self.username, self.password))
        result = None
        if response.status_code == nominal and response.text:
            result = response.json ()
        else:
            print(f"Response: {response.text}")
            print(f"Status code: {response.status_code}")
        return result
    
    def clean(self) -> None:
        intents = self.get ("onos/v1/intents")
        ids = [ intent["id"] for intent in intents["intents"] ]
        for i in ids:
            logger.info(f"Deleting intent: {i}")
            operation = f"onos/v1/intents/org.onosproject.restconf/{i}"
            self.delete (operation=operation, nominal=204)
            
    def create_host_intent(self, ingress_device: str, egress_device: str) -> None:
        """ Create a host to host intent. """
        intent_json = {
            "type": "HostToHostIntent",
            "appId": "org.onosproject.restconf",
            "resources": [
                ingress_device,
                egress_device
            ],
            "selector": {
                "criteria": []
            },
            "treatment": {
                "instructions": [
                    {
                        "type": "NOACTION"
                    }
                ],
                "deferred": []
            },
            "priority": 100,
            "constraints": [
                {
                    "inclusive": False,
                    "types": [
                        "OPTICAL"
                    ],
                    "type": "LinkTypeConstraint"
                }
            ],
            "one": ingress_device,
            "two": egress_device
        }

        api_url = self.get_api("onos/v1/intents/")
        logger.info(f"intent =========> {ingress_device}-->{egress_device}\n")
        """ Note: arp forwarding in Onos was required for pings to work: https://groups.google.com/a/onosproject.org/g/onos-dev/c/GrV3xZfaEPs """
        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(self.username, self.password),
            json=intent_json)

        if response.status_code != 201:
            print(f"Response: {response.text}")
            print(f"Status code: {response.status_code}")
            raise MidoriException(f"Adding intent failed with error: {response.text} and code: {response.status_code}")

class Context:
    """ 
    An execution context for a Midori simulation. Provides acces to system 
    services including an SDN control plane, a graph database, logging services.
    """ 
    def __init__(self, controller: Controller = None,
                 graph: MidoriGraph = None
    ) -> None:
        self.controller = controller if controller else Onos ()
        self.graph = graph if graph else MidoriGraph ()
        self.messages = []

    def log (self, message: str) -> None:
        """ Log a message.

        Args:
            message (str): A log message.
        """
        self.messages.append(message)

    def clean(self) -> None:
        """ Clean up the workspace from prior runs. """
        self.controller.clean()
        self.graph.clean()

def importCode(code: str, name: str="tmp", add_to_sys_modules: int=0):
    """ code can be any object containing code -- string, file object, or
       compiled code object. Returns a new module object initialized
       by dynamically importing the given code and optionally adds it
       to sys.modules under the given name.
    """
    import imp
    module = imp.new_module(name)

    if add_to_sys_modules:
        import sys
        sys.modules[name] = module
    print(code)
    exec (code, module.__dict__)

    print (module)
    
    return module

def run_simulation(network):

    """ Create an execution context for the simulation. """
    context = Context()
    context.clean()
    exception = None
    
    try:
        start = time.time ()
        print(textwrap.dedent(f"""
        network:
          id={network.id}
          source={network.source}
          description={network.description}
        """))
        midori = Compiler()

        """ Compile the network. """
        result = midori.process(source=network.source)

        """ Load the generated network. """
        mininet_network = importCode(result)

        """ Delete all artifacts of previous simulation. """
        from mininet.clean import Cleanup
        Cleanup.cleanup()

        """ Execute the network. """
        mininet_network.run_network(context)
        
    except Exception:
        exception = tb.format_exc()
        print(exception)

    """ Generate a response. """
    return {
        "start_time" : start,
        "end_time"   : time.time (),
        #"error"      : exception,
        "log"        : context.messages
    }

def midori_job_exception_handler(job, exc_type, exc_value, traceback):
    logger.error(textwrap.dedent(f"""
       ERROR: {job}
       -type: {exc_type}
       -value: {exc_value}
       -traceback: 
       {traceback}"""))
    tb.print_traceback(traceback)
    raise exc_value
