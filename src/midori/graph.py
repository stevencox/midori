import json
import jsonpickle
import redis
from midori.config import MidoriConfig
from redisgraph import Edge, Graph, Path
from redisgraph import Node as RNode
from typing import Dict, List, Union, Any
from string import Template

config = MidoriConfig()

class Node:    
    def __init__(self, name: str) -> None:
        self.name = name
    def __repr__(self):
        return f"{type(self).__name__}: name={self.name}"

class Switch(Node):
    pass

class Host(Node):    
    def __init__(self, name: str, environment: Dict) -> None:
        super().__init__(name)
        self.environment = environment
    def __repr__(self):
        return super().__repr__() + f" env={self.environment}"
    
class Link:
    def __init__(self, src: Node, dst: Node) -> None:
        self.src = src
        self.dst = dst
        
class MidoriGraph:
    """ Interface to a graph database. To support experimentation with using
    Cypher as a DSL for manipulating data networs. """
    def __init__(self,
                 graph: str = config.get("redis", "graph"),
                 host: str = config.get("redis", "host"),
                 port: int = config.getint("redis", "port")) -> None:
        """ Initialze the graph.
        
        @param graph: The name of the graph to create.
        @param host: The host Redis is on.
        @param port: The port Redis is listening on. """
        redis_graph = redis.Redis(host=host, port=port)
        self.graph = Graph(graph, redis_graph)

    def create_node(self, node: Node, label: Union[str, List] = []) -> RNode:
        """ Create a node. """
        if not label:
            label = []
        if isinstance(label, str):
            label = [label]
        if not "Node" in label:
            label.append ("Node")
        properties = jsonpickle.encode(node)
        properties = json.loads(properties)
        print(json.dumps(properties, indent=2))
        properties["py_object"] = properties["py/object"]
        del properties["py/object"]
        rnode = RNode(alias=node.name, label=label, properties=properties)
        self.graph.add_node(rnode)
        return rnode

    def create_host(self, node: Host) -> RNode:
        return graph.create_node(node, label=["Host"])
    
    def create_switch(self, node: Host) -> RNode:
        return graph.create_node(node, label=["Switch"])
    
    def create_edge(self, link: Link) -> None:
        properties = {} #jsonpickle.encode(link)
        edge = Edge(link.src, 'visited', link.dst, properties=properties)
        self.graph.add_edge(edge)
        return edge

    def commit(self) -> None:
        self.graph.commit ()

    def query(self, query: str) -> Any:
        return self.graph.query(query)

    def get_shortest_path(self, src: str, dst: str):
        
        # https://oss.redis.com/redisgraph/commands/#allshortestpaths
        #query = """MATCH (source:Host)-[v:visited]->(s1:Switch)-->(s2:Switch)-->(destination:Host)
        #RETURN source.name, s1.name, s2.name, destination.name"""
        
        query = Template(
            """MATCH (src:Host {name: "$src_name"}), (dst:Host {name: "$dst_name"})
            WITH src, dst
            MATCH p=allShortestPaths((src)-[link:visited*]->(dst))
            RETURN nodes(p) as nodes""").safe_substitute ({
                "src_name" : src,
                "dst_name" : dst
            })

        return self.graph.query(query)
