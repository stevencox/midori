import json
import logging
import os
import requests
import socket
import textwrap
import time
import traceback as tb
from dataclasses import dataclass, field
from midori.compiler import Compiler
from midori.config import get_config
from midori.graph import MidoriGraph
from midori.utils import LoggingUtil, Resource, Code
from requests.auth import HTTPBasicAuth
from typing import List, Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

config = get_config ()

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
        logger.error(f"intent =========> {ingress_device}-->{egress_device}\n")
        """ Note: arp forwarding in Onos was required for pings to work: https://groups.google.com/a/onosproject.org/g/onos-dev/c/GrV3xZfaEPs """
        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(self.username, self.password),
            json=intent_json)

        if response.status_code != 201:
            print(f"Response: {response.text}")
            print(f"Status code: {response.status_code}")
            raise MidoriException(f"Adding intent failed with error: {response.text} and code: {response.status_code}")

class ContainernetFactory:
    """ Abstract Containernet specific functionality not available in local dev environments. """
    def get_containernet(self, controller_host: str = config.get("onos", "host"),
                         controller_port: int = config.getint("onos", "openflow_port")):
        from mininet.net import Containernet
        from mininet.node import Controller
        from mininet.node import RemoteController
        net = Containernet()
        name = "onos"
        controller = RemoteController(name=name, ip=socket.gethostbyname(controller_host), port=controller_port)
        net.addController(controller)
        logger.info(f"*** Added RemoteController(name={name},host={controller_host},port={controller_port})\n")
        return net
    
    def cleanup_containernet (self):
        from mininet.clean import Cleanup
        Cleanup.cleanup()

@dataclass
class Node:
    node: object
    gnode: object

@dataclass
class Host(Node):
    pass

@dataclass
class Switch(Node):
    pass

class Context:
    """ 
    An execution context for a Midori simulation. Provides acces to system 
    services including an SDN control plane, a graph database, logging services.
    """ 
    def __init__(self, controller: Controller = None,
                 graph: MidoriGraph = None
    ) -> None:
        containernet_factory = ContainernetFactory() 
        self.net = containernet_factory.get_containernet()
        self.controller = controller if controller else Onos ()
        self.graph = graph if graph else MidoriGraph ()
        self.messages = []
    
    def log (self, message: str) -> None:
        """ Log a message.

        Args:
            message (str): A log message.
        """
        logger.info(message)
        self.messages.append(message)

    def clean(self) -> None:
        """ Clean up the workspace from prior runs. """
        self.controller.clean()
        self.graph.clean()

    def commit(self) -> None:
        """ Commit any pending changes. """
        self.graph.commit()

    def _get_container_properties(self,
                                  name: str,
                                  ip: str,
                                  image: str,
                                  mac: str,
                                  env: Dict[str, str] = {},
                                  ports: List[int] = [],
                                  port_bindings: Dict[int, int] = {},
                                  cmd: List[str] = []) -> None:
        return {
            "name"          : name,
            "ip"            : ip,
            "image"         : image,
            "mac"           : mac,
            "ports"         : ports,
            "port_bindings" : [ f"{k}:{v}" for k, v in port_bindings.items() ],
            "env"           : [ f"{k}:{v}" for k, v in env.items() ],
            "cmd"           : cmd
        }
    
    def add_container(self,
                      name: str,
                      ip: str,
                      image: str,
                      mac: str,
                      env: Dict[str, str] = {},
                      ports: List[int] = [],
                      port_bindings: Dict[int, int] = {},
                      cmd: List[str] = []) -> Host:        
        self.log(f"*** Adding host:{name} ip:{ip} img:{image} mac:{mac} ports:{ports} bindings:{port_bindings} env:{env}\n")
        container = self.net.addDocker(
            name, ip=ip, dimage=image, mac=mac, ports=ports, port_bindings=port_bindings, environment=env)
        node_properties = self._get_container_properties(
            name=name, ip=ip, image=image, mac=mac, env=env, ports=ports, port_bindings=port_bindings, cmd=cmd)
        graph_node = self.graph.add_host(
            alias=name, properties=node_properties)
        return Host(container, graph_node)

    def add_switch(self,                   
                   name : str) -> Switch:
        self.log(f"*** Adding switch {name}\n")
        switch = self.net.addSwitch (name)
        gnode = self.graph.add_switch(alias=name, properties={"name":name})
        return Switch(switch, gnode)

    def add_link(self,
                 src : Node,
                 dst : Node,
                 port1 : int = None,
                 port2 : int = None,
                 cls : str = None,
                 delay : str = None,
                 bw : int = None) -> object:
        self.log(f"** Adding link src:{src.node.name} dst:{dst.node.name} p1:{port1} p2:{port2} cls:{cls} del:{delay} bw:{bw}\n")
        self.net.addLink(src.node, dst.node, port1=port1, port2=port2, cls=cls, delay=delay, bw=bw)
        self.graph.add_edge(
            subject=src.gnode, predicate="linked_to", object=dst.gnode,
            properties={ "port1" : port1, "port2" : port2, "cls" : cls, "delay" : delay, "bw" : bw })

    def add_host2host_intent(self,
                             src: Host,
                             src_mac: str,
                             dst: Host,
                             dst_mac : str) -> None:
        ingress_host_id = f"{src_mac}/None"
        egress_host_id = f"{dst_mac}/None"
        self.log (f"** Adding host-to-host intent: {src.node.name}->{dst.node.name} srcmac: {ingress_host_id} dst_mac:{egress_host_id}\n")
        response = self.controller.create_host_intent(
            ingress_device=ingress_host_id,
            egress_device=egress_host_id)
        name = f"{src.node.name }_to_{dst.node.name}"
        intent_node = self.graph.add_intent(alias=name, properties={"name":name})
        self.graph.add_edge(subject=intent_node, predicate="from", object=src.gnode)
        self.graph.add_edge(subject=intent_node, predicate="to", object=dst.gnode)

def run_simulation(network):

    """ Create an execution context for the simulation. """
    context = Context()
    context.clean()
    exception = None
    
    try:
        start = time.time ()
        logger.debug(f"Simulating network: {network}")

        """ Compile the network. """
        midori = Compiler()
        network_python = midori.process(source=network["source"])

        """ Load the generated network's python implementation as a module."""
        logger.debug(f"Generated code: {network_python}")
        mininet_network = Code.importCode(network_python)

        """ Delete all Containernet artifacts of previous simulation. """
        containernet_factory = ContainernetFactory() 
        containernet_factory.cleanup_containernet()

        """ Execute the simulation network. """
        mininet_network.run_network(context)
        context.controller.clean()
        
    except Exception:
        exception = tb.format_exc()
        print(exception)

    """ Generate a response. """
    return make_result(start=start, end=time.time(),
                       error=exception, log=context.messages)

def make_result(
        start:float,
        end:float,
        error:str,
        log:List[str]
) -> Dict[str, object]:
    return {
        "start_time" : start,
        "end_time"   : time.time (),
        "error"      : error,
        "log"        : log
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

def main():
    text = None
    with open("examples/onos-alpha.midori", "r") as stream:
        text = stream.read ()
    response = run_simulation({
        "id" : 0,
        "source" : text,
        "description" : "main, test"
    })
    print (f"{json.dumps(response, indent=2)}")
    
if __name__ == '__main__':
    main ()
