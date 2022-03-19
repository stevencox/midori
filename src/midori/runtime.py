from midori.compiler import Compiler
import logging
import json
import os
import requests
import textwrap
import time
import traceback as tb
from requests.auth import HTTPBasicAuth
from midori.utils import LoggingUtil, Resource
from midori.graph import MidoriGraph
from typing import Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

class Device:
    """ Model of a device, for the time being, used to model intents only. """
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        
class Intent:
    def __init__(self,
                 priority: int,
                 ingress: Device,
                 egress: Device,
                 protocol: int,
                 eth_type: str,
                 dest_port: int) -> None:
        self.priority = priority
        self.ingress = ingress
        self.egress = egress
        self.protocol = protocol
        self.eth_type = eth_type
        self.dest_port = dest_port        

class Controller:
    
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
        return f"http://{self.api_host}:{self.api_port}/{api}"
        
class Onos(Controller):
    def __init__(self,
                 api_host: str = "localhost",
                 api_port: int = 8181,
                 username: str = "onos",
                 password: str = "rocks"
    ) -> None:
        super().__init__(api_host=api_host, api_port=api_port,
                         username=username, password=password)
    
    def calculate_intent(self, ingress_device: str, egress_device: str) -> None:
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

        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(self.username, self.password),
            json=intent_json)

        if response.status_code != 201:
            print(f"Response: {response.text}")
            print(f"Status code: {response.status_code}")

        # wordpress-[port:3306]->mysql
        # web-[port:5000]->api

class MidoriException(Exception):
    """ A general error pertaining to a simulation has occurred. """
    pass

class MidoriNetworkError(MidoriException):
    """ A simulation failed due to a network or communication error. """
    pass

class MidoriExecutionError(MidoriException):
    """ A simulation failed due to the failure of a computation or lack of computing resources. """
    pass

class Context:
    """ 
    An execution context for a Midori simulation. Provides acces to system 
    services including 
       * An SDN control plane
       * A graph database
       * Logging
    """ 
    def __init__(self, controller: Controller, graph: MidoriGraph) -> None:
        self.controller = controller
        self.graph = graph
        self.messages = []
        
    def log (self, message):
        self.messages.append(message)

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
    result = None
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
        Cleanup.cleanup ()
        
        """ Execute the network. """
        mininet_network.run_network()
        
    except Exception:
        exception = tb.format_exc()
        print(exception)

    """ Generate a response. """
    response = {
        "start_time" : start,
        "end_time"   : time.time (),
        "result"     : result,
        "error"      : exception
    }
    return response

def midori_job_exception_handler(job, exc_type, exc_value, traceback):
    logger.error(textwrap.dedent(f"""
       ERROR: {job}
       -type: {exc_type}
       -value: {exc_value}
       -traceback: 
       {traceback}"""))
    tb.print_traceback(traceback)
    raise exc_value



'''
result = graph.query("MATCH (n) DELETE n")

wordpress_host = Host("wordpress", environment=json.dumps({ "a" : "b" }))
wordpress_node = graph.create_host(wordpress_host)

db_host = Host("db", environment=json.dumps({ "q" : "r" }))
db_node = graph.create_host(db_host)

s1 = Switch("s1")
s2 = Switch("s2")
s1_node = graph.create_switch(s1)
s2_node = graph.create_switch(s2)

l1 = Link(wordpress_node, s1_node)
l2 = Link(s1_node, s2_node)
l3 = Link(s2_node, db_node)

graph.create_edge(l1)
graph.create_edge(l2)
graph.create_edge(l3)

graph.commit()

result = graph.get_shortest_path(src="wordpress", dst="db")
result.pretty_print()

print(result.result_set)
for res in result.result_set:
    print(res)
    for nlist in res:
        for n in nlist:
            print(n)
            txt = json.dumps(json.loads(jsonpickle.encode(n, unpicklable=False)), indent=2)
            print(f"--> {txt}")

            properties = n.properties
            properties["py/object"] = properties["py_object"] 
            del properties["py_object"]
            host: Host = jsonpickle.decode(json.dumps(properties))
            print(host)
'''



if __name__ == "__main__":
    pass
    #context = Context ()
    
